"""Modelo y cálculo independientes de la interfaz gráfica."""
from dataclasses import dataclass, field
from math import fsum, isfinite
from uuid import uuid4

UNITS = {"Ω": 1.0, "kΩ": 1_000.0, "MΩ": 1_000_000.0}


def parse_resistance(text: str, unit: str = "Ω") -> float:
    try:
        value = float(text.strip().replace(",", ".")) * UNITS[unit]
    except (ValueError, KeyError, OverflowError) as exc:
        raise ValueError("Introduce un número válido y una unidad admitida.") from exc
    if not isfinite(value) or value < 0:
        raise ValueError("La resistencia debe ser finita y mayor o igual que cero.")
    return value


def ohms(value: float) -> str:
    return f"{value:.8g} Ω"


@dataclass
class Resistor:
    name: str
    value: float
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class Group:
    name: str
    mode: str = "serie"
    children: list["Resistor | Group"] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class Calculation:
    value: float
    steps: list[str]


def calculate(node: Resistor | Group) -> Calculation:
    """Reduce recursivamente una red serie/paralelo y explica cada paso."""
    if isinstance(node, Resistor):
        if not isfinite(node.value) or node.value < 0:
            raise ValueError(f"{node.name}: resistencia no válida.")
        return Calculation(node.value, [])
    if node.mode not in ("serie", "paralelo"):
        raise ValueError(f"{node.name}: tipo de conexión no válido.")
    if not node.children:
        raise ValueError(f"El grupo «{node.name}» está vacío. Añade resistencias o elimínalo.")
    results = [calculate(child) for child in node.children]
    values = [result.value for result in results]
    steps = [step for result in results for step in result.steps]
    names = [f"Req({child.name})" if isinstance(child, Group) else child.name for child in node.children]
    number = lambda v: format(v, ".8g")
    if node.mode == "serie":
        try:
            value = fsum(values)
        except OverflowError as exc:
            raise ValueError("El resultado supera el rango numérico admitido.") from exc
        explanation = "En serie, las resistencias se suman."
        formula = "Req = " + " + ".join(names)
        substitution = "Req = (" + " + ".join(number(v) for v in values) + ") Ω"
    else:
        explanation = "En paralelo, se suman los inversos y después se invierte el resultado."
        formula = "Req = 1 / (" + " + ".join(f"1/{name}" for name in names) + ")"
        if 0 in values:
            value = 0.0
            explanation = "Una rama de 0 Ω une directamente los extremos del grupo: es un cortocircuito."
            formula = "Req = 0 Ω (rama en cortocircuito)"
            substitution = "Hay una rama de 0 Ω; no es necesario dividir entre cero."
        else:
            # Escalado para evitar desbordamientos al invertir valores muy pequeños.
            minimum = min(values)
            value = minimum / fsum(minimum / v for v in values)
            substitution = "Req = [1 / (" + " + ".join(f"1/{number(v)}" for v in values) + ")] Ω"
            if len(values) == 2:
                explanation = "Para dos resistencias en paralelo, divide su producto entre su suma."
                formula = f"Req = ({names[0]} × {names[1]}) / ({names[0]} + {names[1]})"
                a, b = (number(v) for v in values)
                substitution = f"Req = [({a} × {b}) / ({a} + {b})] Ω"
            if value == 0:
                raise ValueError("El resultado es demasiado pequeño para representarlo.")
    if not isfinite(value):
        raise ValueError("El resultado supera el rango numérico admitido.")
    components = "\n".join(f"  • {name} = {ohms(v)}" for name, v in zip(names, values))
    steps.append(
        f"{node.name} · {node.mode.capitalize()}\n"
        f"{explanation}\n\n"
        f"Componentes de este grupo\n{components}\n\n"
        f"Fórmula\n{formula}\n\n"
        f"Sustituimos los valores en ohmios\n{substitution}\n\n"
        f"Resultado del grupo: Req({node.name}) = {ohms(value)}"
    )
    return Calculation(value, steps)
