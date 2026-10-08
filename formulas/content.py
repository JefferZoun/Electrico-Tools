"""Fichas educativas: texto original y ejemplos con unidades explícitas."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Topic:
    key: str
    title: str
    subtitle: str
    blocks: tuple[tuple[str, str], ...]
    reference: str


TOPICS = (
    Topic("vir", "Pirámide VIR · Ley de Ohm", "Relaciona tensión, intensidad y resistencia.", (
        ("heading", "Tres magnitudes, una relación"),
        ("body", "V es la tensión o voltaje, medida en voltios (V). I es la intensidad de corriente, medida en amperios (A). R es la resistencia, medida en ohmios (Ω)."),
        ("formula", "V = I × R\nI = V / R\nR = V / I"),
        ("note", "En la pirámide, tapa la magnitud que buscas. Si quedan I y R juntas, multiplica; si queda V encima de otra, divide. Pulsa V, I o R en el dibujo para verlo."),
        ("heading", "Ejemplo · una resistencia de 6 Ω conectada a 12 V"),
        ("example", "1. Buscamos la intensidad: I = V / R.\n2. Sustituimos: I = 12 V / 6 Ω.\n3. Resultado: I = 2 A."),
        ("result", "Comprobación: V = 2 A × 6 Ω = 12 V."),
        ("heading", "Otro ejemplo · hallar la resistencia"),
        ("example", "Si V = 24 V e I = 3 A: R = 24 / 3 = 8 Ω."),
        ("note", "La relación describe una resistencia óhmica en las condiciones consideradas. Para dividir, el denominador debe ser distinto de cero."),
    ), "https://openstax.org/books/college-physics/pages/20-2-ohms-law-resistance-and-simple-circuits"),
    Topic("conductor", "Resistencia de un conductor", "La longitud aumenta R; la sección la reduce.", (
        ("heading", "Fórmula con conductividad"),
        ("formula", "R = L / (c × S)"),
        ("body", "L es la longitud del conductor; S es el área de su sección; c es la conductividad del material. La sección y la conductividad van juntas en el denominador."),
        ("note", "Escribe L/(c×S). Escribir L/c×S sin paréntesis puede interpretarse como (L/c)×S, que no es la fórmula de resistencia."),
        ("heading", "La misma fórmula con resistividad"),
        ("formula", "R = ρ × L / S\nρ = 1 / c"),
        ("body", "ρ (rho) es la resistividad: cuanto mayor sea, peor conduce el material. c también se representa con σ (sigma)."),
        ("heading", "Unidades que deben coincidir"),
        ("body", "Puedes usar L en m, S en m² y c en S/m (siemens por metro). También L en m, S en mm² y c en m/(Ω·mm²). Si usas ρ con sección en mm², expresa ρ en Ω·mm²/m. No mezcles ambos sistemas."),
        ("heading", "Ejemplo · longitud 10 m, sección 2,5 mm²"),
        ("example", "Tomamos c = 56 m/(Ω·mm²) como dato del ejemplo.\n1. R = L / (c × S).\n2. R = 10 / (56 × 2,5).\n3. R = 10 / 140."),
        ("result", "R ≈ 0,0714 Ω."),
        ("note", "Si duplicas L, R se duplica. Si duplicas S, R se reduce a la mitad. L es la longitud total recorrida: si un circuito tiene ida y vuelta, debes contar ambos conductores. La conductividad depende del material y de la temperatura."),
    ), "https://openstax.org/books/university-physics-volume-2/pages/9-3-resistivity-and-resistance"),
    Topic("power", "Potencia eléctrica", "La potencia indica cuánta energía se transforma cada segundo.", (
        ("heading", "Potencia en corriente continua"),
        ("formula", "P = V × I\nP = V² / R\nP = I² × R"),
        ("body", "P se mide en vatios (W). V en voltios, I en amperios y R en ohmios. P = V×I relaciona tensión y corriente; las otras dos expresiones se obtienen con la ley de Ohm y se aplican a la potencia disipada en una resistencia."),
        ("heading", "Ejemplo · 12 V, 2 A y 6 Ω"),
        ("example", "Por tensión e intensidad: P = 12 × 2 = 24 W.\nPor tensión y resistencia: P = 12² / 6 = 144 / 6 = 24 W.\nPor intensidad y resistencia: P = 2² × 6 = 4 × 6 = 24 W."),
        ("result", "Las tres fórmulas dan la misma potencia: 24 W."),
        ("heading", "Despejes útiles"),
        ("formula", "V = P / I\nI = P / V\nP = E / t"),
        ("note", "Potencia y energía no son lo mismo: 1 W = 1 J/s. En corriente alterna general, P = V×I requiere considerar también el factor de potencia; esta ficha usa corriente continua y cargas resistivas."),
    ), "https://openstax.org/books/university-physics-volume-2/pages/9-5-electrical-energy-and-power"),
    Topic("energy", "Energía eléctrica", "Relaciona la potencia con el tiempo durante el que actúa.", (
        ("heading", "Energía a potencia constante"),
        ("formula", "E = P × t\nP = E / t\nt = E / P"),
        ("body", "E es la energía, P la potencia y t el tiempo. Si P está en W y t en segundos, E se obtiene en julios (J = W·s). Si t está en horas, E queda en Wh; con P en kW y t en horas, queda en kWh."),
        ("heading", "Ejemplo · una lámpara de 60 W durante 3 h"),
        ("example", "1. E = P × t.\n2. E = 60 W × 3 h = 180 Wh.\n3. Pasamos a kWh: 180 / 1000 = 0,18 kWh.\n4. En julios: 180 × 3600 = 648 000 J."),
        ("result", "180 Wh = 0,18 kWh = 648 000 J."),
        ("heading", "Ejemplo · misma potencia, más tiempo"),
        ("example", "60 W durante 6 h: E = 60 × 6 = 360 Wh. La potencia sigue siendo 60 W; se ha consumido el doble de energía."),
        ("note", "Usa W·s, no W/s, para expresar energía. Usa kWh, no kW/h. Si la potencia cambia, suma la energía de cada intervalo o integra P respecto del tiempo."),
    ), "https://openstax.org/books/college-physics-2e/pages/20-4-electric-power-and-energy"),
    Topic("joule", "Efecto Joule · Energía en forma de calor", "Una resistencia transforma energía eléctrica en calor.", (
        ("heading", "Ley de Joule"),
        ("formula", "Ecalor = I² × R × t"),
        ("body", "I es la intensidad en A; R la resistencia en Ω; t el tiempo en segundos. Ecalor resulta en J, equivalentes a W·s. Se usa aquí una corriente y una resistencia constantes."),
        ("heading", "Ejemplo · 2 A, 5 Ω y 60 s"),
        ("example", "1. Potencia disipada: P = I² × R = 2² × 5 = 20 W.\n2. Energía en calor: Ecalor = 20 × 60 = 1200 J.\n3. En Wh: 1200 / 3600 ≈ 0,333 Wh."),
        ("result", "Se transforman 1200 J de energía eléctrica en calor."),
        ("heading", "Por qué la corriente influye tanto"),
        ("example", "Si I sube de 2 A a 4 A, con la misma R y el mismo tiempo: Ecalor = 4² × 5 × 60 = 4800 J. Duplicar I multiplica el calor por cuatro."),
        ("note", "La fórmula proporciona energía, no temperatura. Para hallar cuánto sube la temperatura hacen falta otros datos, como masa, capacidad calorífica y pérdidas térmicas."),
    ), "https://openstax.org/books/university-physics-volume-2/pages/9-5-electrical-energy-and-power"),
    Topic("units", "Unidades y conversiones", "Convierte las unidades antes de sustituir en una fórmula.", (
        ("heading", "Magnitudes principales"),
        ("body", "Tensión V → voltios (V)\nIntensidad I → amperios (A)\nResistencia R → ohmios (Ω)\nPotencia P → vatios (W)\nEnergía E → julios (J), Wh o kWh\nTiempo t → segundos (s) u horas (h)"),
        ("heading", "Conversiones habituales"),
        ("formula", "1 kΩ = 1000 Ω\n1 mA = 0,001 A\n1 kW = 1000 W\n1 h = 3600 s\n1 Wh = 3600 J\n1 kWh = 1000 Wh = 3 600 000 J\n1 mm² = 0,000001 m²"),
        ("heading", "Ejemplo · corriente expresada en mA"),
        ("example", "V = 5 V e I = 250 mA.\nPrimero: 250 mA = 0,25 A.\nDespués: R = 5 / 0,25 = 20 Ω."),
        ("result", "Usar 250 directamente daría un resultado mil veces menor."),
        ("note", "S puede significar sección dentro de una fórmula, mientras que S como unidad significa siemens. Lee siempre qué representa cada símbolo. En energía, el punto de W·h o W·s significa multiplicación."),
    ), "https://openstax.org/books/university-physics-volume-2/pages/9-key-equations"),
)
