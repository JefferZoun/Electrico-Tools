# Electrico Tools

Aplicación de escritorio en Python y Tkinter, en español, con un menú inspirado en Windows XP y un fondo original de acuarela y pixelart. Incluye las appXP de resistencias, asociación de generadores de tensión continua y consulta de fórmulas eléctricas, con esquemas, ejemplos y explicaciones, y los juegos Pong, Pinball y Flappy Volt.

## Inicio rápido en Windows

1. Descarga el ZIP completo del repositorio y extráelo en una carpeta. No abras el .bat desde dentro del ZIP.
2. Haz doble clic en **Iniciar_Electrico_Tools.bat**. En el primer inicio, el lanzador comprueba Python de 64 bits, Tkinter y pygame-ce; si falta Python, descarga Python 3.13.16 desde python.org, comprueba su SHA-256 y lo instala para el usuario actual. Después crea .venv, instala pygame-ce 2.5.8 y abre el escritorio XP.
3. Las siguientes veces, vuelve a usar el mismo .bat. Si el entorno ya está listo, abre la aplicación directamente.

Se necesita Windows de 64 bits. La primera instalación requiere Internet si faltan Python o pygame-ce; los siguientes arranques no requieren descargar nada. Para comprobar el entorno sin abrir la ventana, ejecuta Iniciar_Electrico_Tools.bat /verificar desde una consola. Si la instalación falla, el .bat muestra el error y espera a que pulses una tecla antes de cerrarse. El lanzador es para Windows moderno: la apariencia imita Windows XP, pero el programa no se ejecuta en un Windows XP real.

El instalador de Python y su SHA-256 proceden de la [página oficial de Python 3.13.16](https://www.python.org/downloads/release/python-31316/). Los parámetros de instalación por usuario y con Tkinter siguen la [documentación oficial de Python para Windows](https://docs.python.org/3/using/windows.html#installing-without-ui). pygame-ce se instala desde [PyPI](https://pypi.org/project/pygame-ce/2.5.8/) en el entorno virtual del proyecto.

Para ejecutar el código manualmente si ya tienes Python 3.10–3.14 con Tkinter:

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
~~~

## Escritorio inicial

Al ejecutar main.py se abre el escritorio de Electrico Tools directamente a pantalla completa y sin bordes. Puedes volver al modo ventana desde Inicio, con F11 en el escritorio o con Escape si Inicio está cerrado. Un clic en cada icono abre su herramienta; también puedes abrirlas desde Inicio. Tab y Enter permiten elegir los iconos con el teclado.

Arrastra cualquier icono con el botón izquierdo para moverlo. Un clic sin arrastrar abre la appXP. Los iconos permanecen dentro del escritorio y por encima de la barra de tareas. Sus posiciones se guardan en .local/desktop.json y se recuperan al iniciar; este archivo de preferencias se excluye del control de versiones. Al reducir la ventana se ajusta su posición visible y al ampliarla se recupera la ubicación preferida.

Cada appXP tiene un botón «← Escritorio» que vuelve al menú y conserva los datos mientras la aplicación permanece abierta. El icono y su botón de la barra de tareas recuperan la misma ventana. Puedes usar las calculadoras junto con un juego. Al abrir Pong, Pinball o Flappy Volt se cierra cualquier otro juego Pygame abierto, también si está minimizado. Abrir de nuevo el mismo juego recupera su ventana y conserva la partida. Cerrar una ventana con la X descarta los datos de esa herramienta; al cerrar el escritorio se cierra toda la aplicación. Los datos de las calculadoras y las partidas no se guardan entre sesiones; las posiciones de los iconos sí.

Inicio incluye «Pantalla completa» y «Salir de pantalla completa» según el modo actual. En el escritorio, F11 alterna entre ambos modos. Escape cierra Inicio y, si el menú está cerrado, sale de pantalla completa. Al salir se recupera el tamaño y estado anteriores de la ventana. Las appXP siguen disponibles y conservan sus datos.

«Apagar» cierra todas las appXP, las ventanas ocultas, los diálogos y el escritorio de Electrico Tools. Cerrar la ventana principal con la X produce el mismo cierre completo. La barra de tareas mide 40 px y su borde superior está alineado con Inicio.

El fondo se adapta a la ventana manteniendo su proporción y recortando el sobrante. Se carga desde assets/xp-watercolor-pixel.png, independientemente del directorio desde el que ejecutes la aplicación. No requiere Pillow ni paquetes externos.

Cada appXP tiene una barra de título azul estilo XP con icono, minimizar, maximizar/restaurar y cerrar. Arrastra la barra para mover la ventana y la esquina inferior derecha para redimensionarla. Un doble clic en el título alterna maximizar/restaurar. Maximizar ocupa el escritorio y deja visible la barra de tareas.

Un clic en el botón de una appXP visible de la barra de tareas la minimiza; otro clic la restaura conservando datos y el estado de maximización. Los iconos del escritorio y el menú Inicio siempre abren o recuperan la appXP.

## Inicio y Juegos

Inicio tiene una cabecera azul con avatar, dos columnas, accesos con iconos, Todos los programas y un submenú Juegos. Apagar usa un icono rojo dibujado con bisel y símbolo blanco al estilo XP, sin depender de caracteres especiales de la fuente.

## AppXP Pong

Abre Pong desde su icono del escritorio o Inicio → Juegos → Pong. Es una partida contra la CPU; gana quien consiga siete puntos. Elige Fácil, Normal o Difícil en el selector.

- W/S o las flechas arriba/abajo mueven tu pala izquierda.
- Espacio o Jugar/Pausar alternan la pausa.
- Nueva partida reinicia el marcador. Tras terminar, Jugar inicia otra partida.

El campo se adapta al tamaño de la ventana conservando sus proporciones. El campo utiliza pygame-ce/SDL integrado dentro de la ventana XP en Windows. Cada fotograma se compone en un backbuffer y se presenta completo, solicitando aceleración gráfica y sincronización vertical. Si el renderer acelerado no está disponible, SDL elige otro renderer y el bucle limita la frecuencia a 60 fotogramas/s. La suavidad y el refresco efectivos dependen del controlador y del monitor. La pelota es redonda, tiene bordes suavizados y no incorpora estelas. Empieza a 360 unidades/s y los impactos la aceleran hasta un máximo de 720 unidades/s; el ángulo depende del punto donde toca la pala. La física usa el tiempo transcurrido, por lo que la velocidad no depende de los fotogramas. Al minimizar, regresar al escritorio o activar otra appXP, el juego se pausa y conserva el marcador. La pausa no depende de avisos de foco de SDL, que pueden ser imprecisos en una ventana integrada. Al volver, pulsa Espacio para continuar.

## AppXP Pinball

Abre Pinball desde el escritorio o Inicio → Juegos → Pinball. La mesa «Órbita espacial» es un diseño original de tema espacial inspirado en el pinball de Windows XP. Utiliza el mismo motor pygame-ce/SDL integrado que Pong.

- Flechas izquierda/derecha o A/D: activar las palas.
- Mantén Espacio para cargar el muelle y suéltalo para lanzar; Lanzar usa una fuerza inicial suficiente para entrar en la mesa.
- P o Pausar/Continuar: pausar y reanudar.
- Nueva partida: empezar de nuevo con tres bolas.

Los bumpers dan 100 puntos y cada objetivo 50, multiplicados por el bonus actual. Activar los cuatro objetivos añade 500 puntos con el multiplicador actual y aumenta el multiplicador hasta ×5. Una bola que cae por la parte inferior se pierde; tras tres bolas termina la partida. Mejor partida conserva el récord mientras esta appXP permanece abierta.

El modelo aplica gravedad, rebotes en paredes y bumpers, y contactos con las palas en movimiento en subpasos de 1/240 s. Al minimizar, volver al escritorio o activar otra appXP, la partida se pausa y conserva la puntuación. Se anula la carga del muelle al pausar para evitar lanzamientos accidentales al regresar. Pulsa P o Continuar para reanudar.

Solo puede permanecer abierto un juego Pygame. Al cambiar de juego se destruyen la ventana, el renderer y los temporizadores del anterior antes de abrir el siguiente. Esto descarta la partida del juego anterior. Las calculadoras siguen disponibles. Al restaurar un juego minimizado se vuelve a mostrar su ventana SDL, se actualiza su tamaño y se repinta el campo también mientras la partida está pausada, para evitar que desaparezca la mesa.

## AppXP Flappy Volt

Abre Flappy Volt desde el icono del pájaro y el poste, o Inicio → Juegos → Flappy Volt. Es un juego de vuelo con gráficos originales: atraviesa los huecos entre postes eléctricos con crucetas y aisladores. Cada poste superado da un punto.

- Espacio, flecha arriba, W o clic izquierdo sobre el campo: aletear. El primer aleteo inicia el vuelo.
- P o Pausar/Continuar: pausar y reanudar.
- Nueva partida: volver a la pantalla inicial.
- Tras perder, un aleteo comienza otra partida.

Chocar con un mástil, cruceta, aislador, suelo o techo termina el vuelo. La colisión utiliza las piezas del poste y un círculo para el cuerpo del pájaro; las zonas de aire junto al mástil no son obstáculos invisibles. Los nuevos postes empiezan con un hueco de 155 unidades. Cada cinco postes aumenta el nivel: el vuelo se acelera gradualmente, los nuevos huecos se estrechan y los postes aparecen algo más juntos, con límites de dificultad. Los postes que ya están en pantalla conservan su hueco; el siguiente hueco solo puede variar moderadamente de altura. El juego prepara siempre los próximos postes fuera del borde derecho, para que no aparezca un tramo vacío de improviso. El movimiento usa el tiempo transcurrido y pequeños subpasos, sin estelas ni sacudidas de cámara.

Dos cables combados unen las crucetas superiores e inferiores de cada pareja de postes. Su recorrido es decorativo; las colisiones siguen correspondiendo al mástil, las crucetas y los aisladores. En las capas del paisaje aparecen de vez en cuando una central eléctrica asentada en una ladera con un camino de tierra que llega hasta su entrada, y grupos de viviendas unifamiliares con paneles solares, antenas, cajas de contador y un RITU común, que representa el [recinto de instalaciones de telecomunicaciones único](https://www.boe.es/buscar/act.php?id=BOE-A-2011-5834).

Mejor conserva el récord mientras esta appXP sigue abierta. Minimizar o volver al escritorio pausa el vuelo y mantiene la puntuación; al restaurar, pulsa Continuar o P. Flappy Volt también respeta la exclusividad de juegos: abrir otro juego lo cierra y descarta su partida. No se requieren dependencias adicionales a pygame-ce.

## Calculadora de resistencias

1. Selecciona «Circuito» y elige su conexión: serie o paralelo.
2. Introduce el nombre opcional, valor y unidad (Ω, kΩ o MΩ). Pulsa «Añadir resistencia» o Enter en el campo de valor.
3. Para un circuito mixto, selecciona un grupo y pulsa «+ Grupo serie» o «+ Grupo paralelo». Las resistencias se añaden dentro del grupo seleccionado. Si seleccionas una resistencia, se añaden a su grupo padre.
4. Usa «Editar» o doble clic para modificar un componente. Las resistencias se editan en ohmios. El selector de conexión modifica el grupo seleccionado. Para eliminar, selecciona un componente en la lista y pulsa Supr/Del o «Eliminar (Supr)». Los grupos con contenido piden confirmación.
5. Pulsa «Calcular circuito». La pestaña «Pasos» muestra cada grupo con sus componentes, fórmula, sustitución y resultado. Los grupos interiores se resuelven primero. «Fórmulas» explica cada tipo de conexión.
6. Los botones de ejemplo cargan circuitos de serie, paralelo y mixto. «Nuevo circuito» limpia el editor.

Admite coma decimal, notación científica y resistencias de 0 Ω. Rechaza valores negativos, no finitos y grupos vacíos. Se muestran ocho cifras significativas; el cálculo conserva la precisión de punto flotante de Python. Una rama de 0 Ω en paralelo representa un cortocircuito y produce 0 Ω.

## Interfaz adaptable y esquema

En ventanas anchas, el constructor y el resultado se muestran juntos. En ventanas estrechas aparecen las pestañas Constructor y Resultado. La cabecera se compacta en ventanas bajas y la barra de ejemplos y Nuevo permanece visible. La ventana admite tamaños desde 480 × 540.

La pestaña Esquema dibuja las resistencias y las conexiones reales de los grupos: azul para serie y verde para paralelo. Pulsa un símbolo o el título de un grupo para seleccionarlo. Puedes eliminar esa selección con Supr/Del. Los circuitos grandes tienen desplazamiento horizontal y vertical. Al calcular, las conexiones muestran un breve pulso de color decorativo; no es una simulación de corriente. «Ver pasos» abre la resolución.

## Fórmulas

- Serie: **Req = R1 + R2 + … + Rn**.
- Paralelo: **Req = 1 / (1/R1 + 1/R2 + … + 1/Rn)** para resistencias distintas de cero.
- Dos resistencias en paralelo: **Req = (R1 × R2) / (R1 + R2)**; si ambas son cero, Req = 0 Ω.
- Mixto: sustituir cada grupo interior por su resistencia equivalente y repetir hasta resolver el circuito completo.

Ejemplo mixto incluido: R1 = 100 Ω en serie con R2 = 200 Ω y R3 = 300 Ω en paralelo. El paralelo vale 120 Ω y el total es **220 Ω**.

El editor representa redes reducibles por grupos de serie/paralelo. Un puente de Wheatstone general necesita otro modelo de cálculo y no puede representarse mediante estos grupos.

## Calculadora de asociación de fuentes

Introduce el nombre opcional, la tensión (mV, V o kV), la resistencia interna en Ω y la polaridad de cada generador. Elige serie o paralelo, pulsa Añadir generador y luego Calcular asociación. Se muestran la tensión equivalente en vacío Eeq, la resistencia interna equivalente req, la intensidad de carga y la tensión en bornes.

La lista y el esquema permiten seleccionar fuentes; puedes editarlas, eliminarlas con el botón o con Supr/Del y cargar ejemplos de serie, paralelo y oposición. La pestaña Pasos separa datos, fórmulas, sustituciones y resultados. Las fuentes con r = 0 Ω son ideales.

- Serie: **Eeq = ΣEi**, respetando la polaridad; **req = Σri**.
- Paralelo con todas las resistencias internas positivas: **Eeq = Σ(Ei/ri) / Σ(1/ri)** y **req = 1 / Σ(1/ri)**.
- Paralelo con alguna fuente ideal: la fuente ideal fija Eeq y req = 0 Ω. Si hay varias fuentes ideales, todas deben imponer exactamente la misma tensión con la misma referencia de polaridad. Tensiones ideales distintas se rechazan, sin devolver un promedio.
- Una fuente ideal en paralelo con una rama real de diferente tensión sí tiene un equivalente en este modelo: la resistencia interna de la rama real limita la corriente entre fuentes.

La polaridad normal representa E positiva entre A y B; la inversa representa E negativa. Un equivalente negativo indica polaridad invertida. El modelo calcula fuentes de tensión DC lineales, no fuentes de corriente, alterna ni capacidad en Ah. Con una carga RL positiva: I = Eeq / (req + RL), Vcarga = I × RL. Introduce la resistencia de carga en el campo RL (Ω) para calcular la intensidad externa y la tensión en bornes. RL vacía representa circuito abierto (I de carga = 0 A). RL = 0 representa un cortocircuito: sólo da una corriente finita si req es positiva. Un cortocircuito ideal se rechaza. En paralelo puede haber corrientes internas entre fuentes aunque no haya carga; la intensidad mostrada es la de la carga externa.

Los ejemplos conectan RL = 10 Ω. En el paralelo de 12 V/1 Ω y 6 V/2 Ω: Eeq = 10 V, req = 2/3 Ω, I = 10/(10 + 2/3) = 0,9375 A y Vbornes = 9,375 V. Las pestañas Pasos y Fórmulas explican el cálculo, y el esquema dibuja la carga cerrando el circuito.

Ejemplos incluidos: dos fuentes de 12 V y 0,5 Ω en serie → 24 V y 1 Ω; fuentes de 12 V/1 Ω y 6 V/2 Ω en paralelo → 10 V y 0,66666667 Ω; fuentes de 12 V y 6 V en oposición → 6 V.

El modelo de fuente ideal con resistencia interna se basa en [OpenStax, fuerza electromotriz](https://openstax.org/books/university-physics-volume-2/pages/10-1-electromotive-force). La fórmula ponderada del paralelo se deriva de las [leyes de Kirchhoff](https://openstax.org/books/university-physics-volume-2/pages/10-3-kirchhoffs-rules): en vacío, Σ((Ei − Eeq)/ri) = 0. Las pruebas verifican también esta igualdad.

## AppXP Fórmulas eléctricas

Abre el icono del libro «Fórmulas eléctricas» o su entrada en Inicio. Esta appXP es una biblioteca de consulta, con el mismo tema visual que las calculadoras. No necesita introducir datos.

Selecciona un tema en la lista superior o usa las flechas. Alt + izquierda/derecha cambia de ficha. El texto tiene desplazamiento vertical. En ventanas anchas el dibujo queda junto al texto; en pequeñas se coloca encima. El botón «← Escritorio» conserva la ficha seleccionada al volver al menú.

Incluye:

- Pirámide VIR: V = I × R, I = V/R, R = V/I. Pulsa las letras del dibujo para mostrar el despeje.
- Resistencia de conductores: R = L/(c × S), y su forma equivalente R = ρL/S. S es el área de la sección y c la conductividad. La sección va en el denominador; no se interpreta como (L/c) × S.
- Potencia en DC: P = V × I, P = V²/R y P = I²R. Las dos últimas expresiones corresponden a una resistencia óhmica.
- Energía a potencia constante: E = P × t y sus despejes. Distingue J = W·s, Wh y kWh.
- Efecto Joule: Ecalor = I²Rt, con t en segundos para obtener julios.
- Unidades y conversiones: voltios, amperios, ohmios, vatios, julios, horas, Wh y kWh.

Cada ficha define símbolos y unidades y contiene ejemplos resueltos. El ejemplo de conductor supone c = 56 m/(Ω·mm²), L = 10 m y S = 2,5 mm², dando R ≈ 0,0714 Ω. El de energía usa una lámpara de 60 W durante 3 h: 180 Wh = 0,18 kWh = 648 000 J. El de Joule usa 2 A, 5 Ω y 60 s: 1200 J.

El botón Referencia abre una fuente educativa de la ficha. Se han contrastado las relaciones con [la ley de Ohm de OpenStax](https://openstax.org/books/college-physics/pages/20-2-ohms-law-resistance-and-simple-circuits), [resistividad y resistencia](https://openstax.org/books/university-physics-volume-2/pages/9-3-resistivity-and-resistance), [potencia eléctrica](https://openstax.org/books/university-physics-volume-2/pages/9-5-electrical-energy-and-power) y [energía eléctrica](https://openstax.org/books/college-physics-2e/pages/20-4-electric-power-and-energy). Las fichas de potencia, energía y Joule incluyen las relaciones de la captura del libro proporcionada por el usuario, con redacción y ejemplos propios.

## Estructura

~~~text
Electrico_Tools/
├── Iniciar_Electrico_Tools.bat # Lanzador con comprobación automática
├── scripts/bootstrap.ps1      # Instala Python y pygame-ce si faltan
├── main.py                    # Abre el escritorio
├── electrico/
│   ├── desktop.py             # Iconos, barra de tareas y ventanas
│   ├── start_menu.py          # Inicio Luna, iconos y submenús
│   ├── icons.py               # Arrastre, límites y posiciones guardadas
│   ├── wallpaper.py           # Fondo adaptable, sin dependencias
│   ├── window.py              # Marco XP y controles de ventana
│   ├── theme.py               # Tema compartido
│   └── layout.py              # Distribución adaptable compartida
├── resistencias/
│   ├── circuit.py             # Lógica de serie/paralelo/mixto
│   ├── gui.py                 # Calculadora gráfica
│   └── diagram.py             # Esquema interactivo
├── fuentes/
│   ├── model.py               # Equivalente de generadores DC
│   ├── gui.py                 # Calculadora gráfica
│   └── diagram.py             # Generadores y resistencias internas
├── formulas/
│   ├── content.py             # Fichas, ejemplos y referencias
│   └── gui.py                 # Biblioteca visual con pirámide VIR
├── juegos/
│   ├── pong_model.py          # Física, puntuación y rival CPU
│   ├── pong.py                # AppXP, controles y bucle de juego
│   ├── pong_renderer.py       # Renderer del campo de Pong
│   ├── sdl_viewport.py        # Motor SDL, eventos y ventanas compartidos
│   ├── pinball_model.py       # Física, palas, misión y puntuación
│   ├── pinball_renderer.py    # Mesa y gráficos de Pinball
│   ├── pinball.py             # AppXP y controles del Pinball
│   ├── flappy_model.py        # Vuelo, postes, colisiones y puntuación
│   ├── flappy_renderer.py     # Ave y paisaje eléctrico
│   └── flappy.py              # AppXP Flappy Volt
├── assets/
│   ├── xp-watercolor-pixel.png
│   └── README.md              # Procedencia y prompt del fondo
├── tests/
│   ├── test_circuit.py
│   ├── test_sources.py
│   ├── test_pong.py
│   ├── test_pinball.py
│   ├── test_flappy.py
│   ├── test_icons.py
│   └── test_game_windows.py  # Regresiones SDL en Windows
├── requirements.txt
└── README.md
~~~

## Pruebas

~~~powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
~~~
