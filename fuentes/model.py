"""Equivalente de Thévenin de generadores de tensión continua."""
from dataclasses import dataclass, field
from math import fsum, isfinite
from uuid import uuid4

VOLTAGE_UNITS = {"mV": 0.001, "V": 1.0, "kV": 1000.0}


def parse_number(text, multiplier=1.0):
    try:
        value = float(text.strip().replace(",", ".")) * multiplier
    except (ValueError, OverflowError) as exc:
        raise ValueError("Introduce valores numéricos válidos.") from exc
    if not isfinite(value) or value < 0:
        raise ValueError("Los valores deben ser finitos y no negativos. Usa la polaridad para invertir la fuente.")
    return value


def volts(value):
    return f"{value:.8g} V"


def ohms(value):
    return f"{value:.8g} Ω"


@dataclass
class Generator:
    name: str
    voltage: float
    resistance: float = 0.0
    polarity: int = 1
    id: str = field(default_factory=lambda: uuid4().hex)

    @property
    def emf(self):
        return self.voltage * self.polarity


@dataclass
class Association:
    voltage: float
    resistance: float
    steps: list[str]
    current: float = 0.0
    terminal_voltage: float = 0.0
    load: float | None = None


def associate(generators: list[Generator], mode: str, load: float | None = None) -> Association:
    if load is not None and (not isfinite(load) or load < 0):
        raise ValueError("La resistencia de carga RL debe ser finita y no negativa.")
    if not generators:
        raise ValueError("Añade al menos un generador antes de calcular.")
    if mode not in ("serie", "paralelo"):
        raise ValueError("Elige conexión en serie o en paralelo.")
    for g in generators:
        if not isfinite(g.voltage) or g.voltage < 0 or not isfinite(g.resistance) or g.resistance < 0 or g.polarity not in (-1, 1):
            raise ValueError(f"{g.name}: valores de generador no válidos.")
    components = "\n".join(f"  • {g.name}: E = {volts(g.emf)}; r = {ohms(g.resistance)}" for g in generators)
    steps = ["Paso 1 · Polaridad y datos\nTomamos como positiva la tensión de A respecto de B.\nLa polaridad inversa cambia el signo de la fuerza electromotriz (E).\n\nComponentes\n" + components]
    if mode == "serie":
        try:
            voltage = fsum(g.emf for g in generators)
            resistance = fsum(g.resistance for g in generators)
        except OverflowError as exc:
            raise ValueError("El resultado supera el rango numérico admitido.") from exc
        symbolic = " + ".join(f"E({g.name})" for g in generators)
        numeric = " + ".join(f"({g.emf:.8g})" for g in generators)
        steps.append(f"Paso 2 · Tensión en serie\nLas fuentes a favor se suman y las fuentes en oposición se restan.\n\nFórmula\nEeq = {symbolic}\n\nSustitución\nEeq = [{numeric}] V\n\nResultado: Eeq = {volts(voltage)}")
        r_numeric = " + ".join(f"{g.resistance:.8g}" for g in generators)
        steps.append(f"Paso 3 · Resistencia interna en serie\nLas resistencias internas se suman, cualquiera que sea la polaridad.\n\nFórmula\nreq = r1 + r2 + … + rn\n\nSustitución\nreq = ({r_numeric}) Ω\n\nResultado: req = {ohms(resistance)}")
    else:
        ideal = [g for g in generators if g.resistance == 0]
        if ideal:
            voltage = ideal[0].emf
            if any(g.emf != voltage for g in ideal[1:]):
                raise ValueError("Conexión incompatible: dos fuentes ideales en paralelo imponen tensiones distintas (o polaridades opuestas). Indica sus resistencias internas reales o corrige la tensión/polaridad.")
            resistance = 0.0
            steps.append(f"Paso 2 · Fuentes ideales en paralelo\nUna fuente ideal (r = 0 Ω) fija la tensión entre A y B. Todas las fuentes ideales deben imponer la misma tensión.\n\nResultado: Eeq = {volts(voltage)}\nResultado: req = 0 Ω\n\nLas ramas reales conservan su resistencia interna. El reparto de corriente entre varias fuentes ideales no queda determinado por este modelo.")
        else:
            minimum = min(g.resistance for g in generators)
            weights = [minimum / g.resistance for g in generators]
            total_weight = fsum(weights)
            voltage_scale = max(g.voltage for g in generators)
            voltage = voltage_scale * (fsum((g.emf / voltage_scale) * w for g, w in zip(generators, weights)) / total_weight) if voltage_scale else 0.0
            resistance = minimum / total_weight
            if resistance == 0:
                raise ValueError("La resistencia equivalente es demasiado pequeña para representarla.")
            numerator = " + ".join(f"({g.emf:.8g}/{g.resistance:.8g})" for g in generators)
            denominator = " + ".join(f"1/{g.resistance:.8g}" for g in generators)
            steps.append(f"Paso 2 · Tensión de fuentes reales en paralelo\nTodas las ramas comparten la tensión entre A y B. La tensión equivalente se pondera según las resistencias internas.\n\nFórmula\nEeq = (E1/r1 + … + En/rn) / (1/r1 + … + 1/rn)\n\nSustitución (E en V y r en Ω)\nEeq = ({numerator}) / ({denominator})\n\nResultado: Eeq = {volts(voltage)}")
            steps.append(f"Paso 3 · Resistencia interna en paralelo\nAl sustituir cada fuente ideal de tensión por un cortocircuito, las resistencias internas quedan en paralelo.\n\nFórmula\nreq = 1 / (1/r1 + … + 1/rn)\n\nSustitución\nreq = [1 / ({denominator})] Ω\n\nResultado: req = {ohms(resistance)}")
    if not isfinite(voltage) or not isfinite(resistance):
        raise ValueError("El resultado supera el rango numérico admitido.")
    if load is None:
        current, terminal_voltage = 0.0, voltage
        steps.append(f"Paso {len(steps)+1} · Circuito abierto\nNo se ha conectado una carga entre A y B.\n\nResultado: I de carga = 0 A\nResultado: Vbornes = {volts(voltage)}\n\nEn paralelo puede haber corrientes internas entre generadores reales; esta I corresponde a la carga externa.")
    else:
        scale = max(resistance, load)
        if scale == 0:
            raise ValueError("Cortocircuito ideal: req + RL = 0 Ω. El modelo no determina una intensidad finita. Introduce una resistencia interna o de carga positiva.")
        denominator = resistance/scale + load/scale
        current = (voltage/scale)/denominator
        terminal_voltage = voltage*((load/scale)/denominator)
        if not isfinite(current) or not isfinite(terminal_voltage):
            raise ValueError("La intensidad supera el rango numérico admitido.")
        steps.append(f"Paso {len(steps)+1} · Intensidad de la carga\nConectamos RL = {ohms(load)} entre A y B. La carga y la resistencia interna equivalente quedan en serie.\n\nFórmula\nI = Eeq / (req + RL)\nVcarga = I × RL\n\nSustitución\nI = {voltage:.8g} / ({resistance:.8g} + {load:.8g}) A\nVcarga = {current:.8g} × {load:.8g} V\n\nResultado: I = {current:.8g} A\nResultado: Vcarga = {volts(terminal_voltage)}")
    steps.append(f"EQUIVALENTE FINAL\nEeq = {volts(voltage)}\nreq = {ohms(resistance)}\nI de carga = {current:.8g} A\nVbornes = {volts(terminal_voltage)}\n\nEeq es la tensión en vacío. La intensidad indicada es la de la carga externa, positiva de A a B. Un valor negativo indica sentido inverso.")
    return Association(voltage, resistance, steps, current, terminal_voltage, load)
