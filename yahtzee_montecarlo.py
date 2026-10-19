"""
=============================================================================
  SIMULACIÓN DE YAHTZEE CON EL MÉTODO MONTECARLO  (versión en español)
=============================================================================

¿Qué hace este programa?
------------------------
Recibe una mano de 5 dados y responde la pregunta:

    "¿Qué dados me conviene GUARDAR y cuáles RELANZAR?"

¿Cómo lo decide? (Método Montecarlo)
------------------------------------
En vez de calcular probabilidades con fórmulas complicadas, hacemos lo que
haría una persona con mucha paciencia:

    1. Elegimos una forma de guardar dados (por ejemplo: guardar los dos 4).
    2. Relanzamos los demás dados MUCHAS veces (ej. 250 veces).
    3. Anotamos cuántos puntos sacamos en cada intento.
    4. Sacamos el PROMEDIO  -> eso es el "Valor Esperado".

Repetimos esto para TODAS las formas posibles de guardar dados (son 32)
y nos quedamos con la que tenga el promedio más alto.

Mientras más simulaciones hagamos, más confiable es el promedio
(Ley de los Grandes Números).

Vocabulario clave
-----------------
  - mano:            lista con los 5 dados, ej. [3, 4, 4, 6, 1]
  - mascara:         lista de 5 True/False que dice qué dados se guardan.
                     ej. [False, True, True, False, False] = guardo el 2.º y 3.º
  - valor_esperado:  puntaje promedio que esperamos obtener.

Cómo ejecutarlo:   python yahtzee_montecarlo.py
=============================================================================
"""

import random                       # Para generar números al azar (los dados)
from collections import Counter     # Para contar cuántas veces sale cada número

# =============================================================================
# 1. CONFIGURACIÓN
# =============================================================================

# SEMILLA: fija el "azar" para que cada ejecución dé los mismos resultados.
# Muy útil para comparar y explicar en clase. Con None, cada vez cambia.
SEMILLA = 42
if SEMILLA is not None:
    random.seed(SEMILLA)

# Las 13 casillas de la hoja de puntaje de Yahtzee
CATEGORIAS = [
    "unos", "doses", "treses", "cuatros", "cincos", "seises",  # Sección superior
    "trio",            # 3 dados iguales        -> suma todos los dados
    "poker",           # 4 dados iguales        -> suma todos los dados
    "full",            # trío + pareja          -> 25 puntos
    "escalera_corta",  # 4 números seguidos     -> 30 puntos
    "escalera_larga",  # 5 números seguidos     -> 40 puntos
    "yahtzee",         # 5 dados iguales        -> 50 puntos
    "libre",           # sin condición          -> suma todos los dados
]

# Para la sección superior: qué número corresponde a cada casilla
NUMERO_DE_CATEGORIA = {
    "unos": 1, "doses": 2, "treses": 3, "cuatros": 4, "cincos": 5, "seises": 6
}


# =============================================================================
# 2. DADOS
# =============================================================================
def lanzar_un_dado():
    """Lanza UN dado: devuelve un número al azar entre 1 y 6."""
    return random.randint(1, 6)


def relanzar_dados(mano, mascara):
    """
    Relanza los dados que NO están guardados.

    - mano:    los 5 dados actuales (se modifica directamente).
    - mascara: True = guardar ese dado, False = relanzarlo.

    Ejemplo:
        mano    = [3, 4, 4, 6, 1]
        mascara = [False, True, True, False, False]
        -> los dos 4 se quedan; los demás cambian por números nuevos.
    """
    for posicion in range(5):
        if not mascara[posicion]:              # Si este dado NO está guardado...
            mano[posicion] = lanzar_un_dado()  # ...lo volvemos a lanzar


def hay_escalera(mano, largo_necesario):
    """
    Revisa si hay 'largo_necesario' números seguidos (para las escaleras).

    Ejemplo: [1, 3, 2, 4, 4] -> sin repetidos y ordenado: [1, 2, 3, 4]
             Hay 4 seguidos -> sí sirve para escalera corta.
    """
    numeros = sorted(set(mano))   # set() quita repetidos; sorted() ordena

    racha_actual = 1              # Cuántos seguidos llevamos ahora
    mejor_racha = 1               # La racha más larga encontrada
    for i in range(1, len(numeros)):
        if numeros[i] == numeros[i - 1] + 1:   # ¿Es el anterior + 1?
            racha_actual += 1                  #   Sí: la racha crece
            mejor_racha = max(mejor_racha, racha_actual)
        else:
            racha_actual = 1                   #   No: empieza de nuevo
    return mejor_racha >= largo_necesario


# =============================================================================
# 3. PUNTUACIÓN (las reglas del juego)
# =============================================================================
def calcular_puntos(categoria, mano):
    """
    Calcula cuántos puntos da una mano en UNA casilla.

    Ejemplo: calcular_puntos("cuatros", [3, 4, 4, 6, 1]) -> 8  (4 + 4)
    """
    conteo = Counter(mano)               # [3,4,4,6,1] -> {4: 2, 3: 1, 6: 1, 1: 1}
    repeticiones = conteo.values()       # solo las cantidades -> 2, 1, 1, 1
    suma_total = sum(mano)               # suma de todos los dados

    # --- Sección superior: (cuántos hay de ese número) x (el número) ---
    if categoria in NUMERO_DE_CATEGORIA:
        numero = NUMERO_DE_CATEGORIA[categoria]
        return conteo[numero] * numero

    # --- Sección inferior: combinaciones especiales ---
    if categoria == "trio":
        return suma_total if max(repeticiones) >= 3 else 0
    if categoria == "poker":
        return suma_total if max(repeticiones) >= 4 else 0
    if categoria == "full":
        return 25 if sorted(repeticiones) == [2, 3] else 0
    if categoria == "escalera_corta":
        return 30 if hay_escalera(mano, 4) else 0
    if categoria == "escalera_larga":
        return 40 if hay_escalera(mano, 5) else 0
    if categoria == "yahtzee":
        return 50 if max(repeticiones) == 5 else 0
    if categoria == "libre":
        return suma_total
    return 0


def mejor_puntaje(mano, categorias_libres):
    """
    Prueba la mano en TODAS las casillas libres y devuelve la mejor.

    Retorna: (nombre_de_la_casilla, puntos)
    """
    mejor_categoria = None
    mejores_puntos = -1
    for categoria in categorias_libres:
        puntos = calcular_puntos(categoria, mano)
        if puntos > mejores_puntos:      # ¿Supera a la mejor hasta ahora?
            mejores_puntos = puntos
            mejor_categoria = categoria
    return mejor_categoria, mejores_puntos


def todas_las_mascaras():
    """
    Genera las 32 formas de guardar/relanzar 5 dados.

    Cada dado tiene 2 opciones (guardar o relanzar) -> 2^5 = 32.

    Truco: los números del 0 al 31 en binario (5 cifras) son justo esas
    32 combinaciones. Cifra 1 = guardar, cifra 0 = relanzar.
        0  -> 00000 -> relanzo todo
        31 -> 11111 -> guardo todo
    """
    mascaras = []
    for numero in range(32):
        mascara = [(numero >> posicion) & 1 == 1 for posicion in range(5)]
        mascaras.append(mascara)
    return mascaras


# =============================================================================
# 4. NÚCLEO MONTECARLO
# =============================================================================
def valor_esperado(mano, mascara, categorias_libres, simulaciones=250):
    """
    Responde: "Si guardo estos dados, ¿cuántos puntos saco en promedio?"

    NOTA (simplificación): se simula UNA sola relanzada y luego se anota.
    """
    puntos_acumulados = 0

    for _ in range(simulaciones):              # Repetimos el experimento muchas veces
        mano_simulada = list(mano)             # 1. Copiamos la mano (no dañamos la original)
        relanzar_dados(mano_simulada, mascara) # 2. Relanzamos los no guardados
        _, puntos = mejor_puntaje(             # 3. ¿Cuánto vale esta mano?
            mano_simulada, categorias_libres
        )
        puntos_acumulados += puntos            # 4. Lo sumamos

    return puntos_acumulados / simulaciones    # 5. Promedio = valor esperado


def evaluar_todas_las_opciones(mano, categorias_libres, simulaciones=250):
    """
    El "cerebro" de la IA: calcula el valor esperado de las 32 opciones.

    Retorna una lista de (valor_esperado, mascara) ordenada de mejor a peor.
    """
    resultados = []
    for mascara in todas_las_mascaras():
        promedio = valor_esperado(mano, mascara, categorias_libres, simulaciones)
        resultados.append((promedio, mascara))

    resultados.sort(key=lambda r: r[0], reverse=True)   # Mejor primero
    return resultados


# =============================================================================
# 5. MOSTRAR RESULTADOS DE FORMA CLARA
# =============================================================================
def describir_jugada(mano, mascara):
    """Convierte una máscara en una frase: 'Guarda [4, 6] | Relanza [3, 4, 1]'."""
    guardados = [mano[i] for i in range(5) if mascara[i]]
    relanzados = [mano[i] for i in range(5) if not mascara[i]]
    texto_guardar = str(guardados) if guardados else "nada"
    texto_relanzar = str(relanzados) if relanzados else "nada"
    return f"Guarda {texto_guardar:<16} | Relanza {texto_relanzar}"


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    # ---- Puedes cambiar estos valores para probar otras situaciones ----
    mano_actual = [3, 4, 4, 6, 1]
    categorias_libres = ["cuatros", "trio", "full", "escalera_larga", "libre"]
    simulaciones = 250
    # --------------------------------------------------------------------

    print("=" * 60)
    print("  YAHTZEE - ASISTENTE MONTECARLO")
    print("=" * 60)
    print(f"Tus dados:         {mano_actual}")
    print(f"Casillas libres:   {', '.join(categorias_libres)}")
    print(f"\nProbando las 32 opciones ({simulaciones} simulaciones cada una)...")
    print("(esto puede tardar unos segundos)\n")

    resultados = evaluar_todas_las_opciones(mano_actual, categorias_libres, simulaciones)

    # Mostramos las 5 mejores opciones
    print("TOP 5 JUGADAS:")
    print("-" * 60)
    for puesto, (promedio, mascara) in enumerate(resultados[:5], start=1):
        print(f" {puesto}. {describir_jugada(mano_actual, mascara)}  ->  {promedio:5.2f} pts")

    # Recomendación final
    mejor_promedio, mejor_mascara = resultados[0]
    print("-" * 60)
    print(f"\nRECOMENDACIÓN: {describir_jugada(mano_actual, mejor_mascara)}")
    print(f"En promedio obtendrás unos {mejor_promedio:.1f} puntos.")
    print("\nOjo: si las primeras opciones tienen puntajes muy parecidos,")
    print("son prácticamente igual de buenas (la diferencia es azar).")
