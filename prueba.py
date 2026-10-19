"""
=============================================================================
  SIMULACIÓN DE YAHTZEE CON EL MÉTODO MONTECARLO
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
    4. Sacamos el PROMEDIO  -> eso es el "Valor Esperado" (EV).

Repetimos esto para TODAS las formas posibles de guardar dados (son 32)
y nos quedamos con la que tenga el promedio más alto.

Mientras más simulaciones hagamos, más confiable es el promedio
(Ley de los Grandes Números).

Vocabulario clave
-----------------
  - Mano:     lista con los 5 dados, ej. [3, 4, 4, 6, 1]
  - Máscara:  lista de 5 True/False que dice qué dados se guardan.
              ej. [False, True, True, False, False] = guardo el 2.º y 3.º dado
  - EV:       Valor Esperado = puntaje promedio que esperamos obtener.
=============================================================================
"""

import random                       # Para generar números al azar (los dados)
from collections import Counter     # Para contar cuántas veces sale cada número
from typing import List, Tuple      # Solo para documentar los tipos de datos

# =============================================================================
# 1. PARÁMETROS GLOBALES Y UTILIDADES DE DADOS
# =============================================================================

# SEMILLA: fija el "azar" para que cada vez que ejecutemos el programa
# salgan los mismos resultados. Muy útil para comparar y explicar en clase.
# Si la cambias a None, cada ejecución dará resultados distintos.
SEED = 42
if SEED is not None:
    random.seed(SEED)

# Las 13 categorías de la hoja de puntaje de Yahtzee:
#   ones..sixes    -> suma solo los dados de ese número (sección superior)
#   threeOfKind    -> Trío: 3 dados iguales, suma todos los dados
#   fourOfKind     -> Póker: 4 dados iguales, suma todos los dados
#   fullHouse      -> Full: un trío + una pareja = 25 puntos
#   smallStraight  -> Escalera corta: 4 números seguidos = 30 puntos
#   largeStraight  -> Escalera larga: 5 números seguidos = 40 puntos
#   yahtzee        -> 5 dados iguales = 50 puntos
#   chance         -> Libre: suma todos los dados, sin condición
CATEGORIES_ORDER = [
    "ones", "twos", "threes", "fours", "fives", "sixes",
    "threeOfKind", "fourOfKind", "fullHouse", "smallStraight",
    "largeStraight", "yahtzee", "chance"
]


def roll_single_die() -> int:
    """Lanza UN dado: devuelve un número al azar entre 1 y 6 (todos igual de probables)."""
    return random.randint(1, 6)


def roll_dice(values: List[int], locked: List[bool]) -> None:
    """
    Relanza los dados que NO están guardados.

    - values: la mano actual (se modifica directamente, no se crea una nueva).
    - locked: máscara; True = dado guardado (no se toca), False = se relanza.

    Ejemplo:
        values = [3, 4, 4, 6, 1]
        locked = [False, True, True, False, False]
        -> los 4 se quedan; los demás se reemplazan por números nuevos.
    """
    for i, is_locked in enumerate(locked):
        if not is_locked:
            values[i] = roll_single_die()


def has_sequence(values: List[int], needed_len: int) -> bool:
    """
    Revisa si en la mano hay 'needed_len' números seguidos (para las escaleras).

    Ejemplo: [1, 3, 2, 4, 4] -> sin repetidos y ordenado: [1, 2, 3, 4]
             Hay 4 seguidos -> sirve para escalera corta (needed_len = 4).
    """
    uniq = sorted(set(values))   # set() quita repetidos; sorted() los ordena
    if not uniq:
        return False

    longest = curr = 1           # curr = racha actual, longest = mejor racha
    for i in range(1, len(uniq)):
        if uniq[i] == uniq[i - 1] + 1:   # ¿Este número es el anterior + 1?
            curr += 1                    #   Sí: la racha crece
            longest = max(longest, curr)
        else:
            curr = 1                     #   No: la racha se rompe, empieza de nuevo
    return longest >= needed_len


# =============================================================================
# 2. MOTOR DE REGLAS Y PUNTUACIÓN DE YAHTZEE
# =============================================================================
def score_hand(category: str, dice: List[int]) -> int:
    """
    Calcula cuántos puntos da una mano en UNA categoría.

    Ejemplo: score_hand("fours", [3, 4, 4, 6, 1]) -> 8  (dos 4 = 4 + 4)
    """
    counts = Counter(dice)        # ej. [3,4,4,6,1] -> {4: 2, 3: 1, 6: 1, 1: 1}
    freqs = list(counts.values()) # solo las cantidades -> [2, 1, 1, 1]
    total = sum(dice)             # suma de todos los dados

    # --- Sección superior: suma solo los dados del número pedido ---
    if category in ["ones", "twos", "threes", "fours", "fives", "sixes"]:
        num = {"ones": 1, "twos": 2, "threes": 3, "fours": 4, "fives": 5, "sixes": 6}[category]
        return counts.get(num, 0) * num   # (cuántos hay) x (su valor)

    # --- Sección inferior: combinaciones especiales ---
    if category == "threeOfKind":          # Algún número aparece 3+ veces
        return total if any(f >= 3 for f in freqs) else 0
    if category == "fourOfKind":           # Algún número aparece 4+ veces
        return total if any(f >= 4 for f in freqs) else 0
    if category == "fullHouse":            # Exactamente un trío y una pareja
        return 25 if (2 in freqs and 3 in freqs) else 0
    if category == "smallStraight":        # 4 números seguidos
        return 30 if has_sequence(dice, 4) else 0
    if category == "largeStraight":        # 5 números seguidos
        return 40 if has_sequence(dice, 5) else 0
    if category == "yahtzee":              # Los 5 dados iguales
        return 50 if 5 in freqs else 0
    if category == "chance":               # Siempre vale la suma
        return total
    return 0                               # Categoría desconocida


def best_category_score(dice: List[int], available: List[str]) -> Tuple[str, int]:
    """
    Prueba la mano en TODAS las categorías libres y devuelve la que más puntos da.

    Retorna: (nombre_de_la_mejor_categoría, puntos)
    """
    best_cat, best = None, -1
    for cat in available:
        sc = score_hand(cat, dice)
        if sc > best:              # Si esta categoría supera a la mejor hasta ahora...
            best = sc              # ...la guardamos como nueva mejor
            best_cat = cat
    return best_cat, best


def all_keep_masks() -> List[List[bool]]:
    """
    Genera las 32 formas posibles de guardar/relanzar 5 dados.

    Cada dado tiene 2 opciones (guardar o relanzar) -> 2^5 = 32 combinaciones.

    Truco: los números del 0 al 31 escritos en binario (5 cifras) son
    exactamente esas 32 combinaciones. Cada cifra 1 = guardar, 0 = relanzar.
        m = 0  -> 00000 -> relanzo todo
        m = 6  -> 00110 -> guardo el 2.º y 3.º dado
        m = 31 -> 11111 -> guardo todo
    La expresión (m >> i) & 1 simplemente lee la cifra número i de m.
    """
    return [[(m >> i) & 1 == 1 for i in range(5)] for m in range(32)]


# =============================================================================
# 3. NÚCLEO MONTECARLO: CÁLCULO DE VALOR ESPERADO (EV)
# =============================================================================
def simulate_expected_value_after_keeps(
    current_values: List[int],
    keep_mask: List[bool],
    rolls_remaining: int,
    available_categories: List[str],
    sims: int = 300
) -> float:
    """
    Responde: "Si guardo estos dados (keep_mask), ¿cuántos puntos saco en promedio?"

    Lo estima simulando 'sims' relanzamientos y promediando el mejor puntaje
    de cada uno.

    NOTA (simplificación): solo se simula UNA tirada hacia adelante, aunque
    queden 2. Es decir, la IA evalúa "qué pasa si relanzo ahora y me planto".
    Esto mantiene el código rápido y fácil de entender.
    """
    # Caso base: si ya no quedan tiradas, no hay nada que simular.
    # Simplemente anotamos la mano actual en su mejor categoría.
    if rolls_remaining <= 0:
        _, sc = best_category_score(current_values, available_categories)
        return float(sc)

    # =========================================================================
    # TODO [15% NÚCLEO LÓGICO]: Motor de Muestreo Estocástico Montecarlo
    # -------------------------------------------------------------------------
    # Variables de entrada:
    #   - current_values: List[int]       -> Mano actual de 5 dados (ej. [3, 4, 4, 6, 4])
    #   - keep_mask: List[bool]           -> 5 booleanos (True = fijar dado, False = relanzar)
    #   - rolls_remaining: int            -> Tiradas restantes para completar el turno (1 o 2)
    #   - available_categories: List[str] -> Categorías disponibles en la tarjeta del jugador
    #   - sims: int                       -> Número de iteraciones a simular (ej. 300)
    #
    # Retorno esperado:
    #   - float: Promedio aritmético de los mejores puntajes obtenidos en las 'sims' corridas.
    #
    # Pista conceptual:
    #   Ejecuta un bucle de N simulaciones. En cada una, clona 'current_values', reemplaza
    #   únicamente las posiciones donde keep_mask[i] es False llamando a roll_single_die(),
    #   obtén el puntaje óptimo con best_category_score() y acumúlalo para promediar.
    # =========================================================================

    total_score = 0.0                          # Acumulador de puntos de todas las simulaciones

    for _ in range(sims):                      # Repetimos el experimento 'sims' veces
        next_hand = list(current_values)       # 1. Copiamos la mano (para NO dañar la original)
        roll_dice(next_hand, keep_mask)        # 2. Relanzamos solo los dados no guardados
        _, sc = best_category_score(           # 3. ¿Cuántos puntos vale esta nueva mano?
            next_hand, available_categories
        )
        total_score += sc                      # 4. Sumamos al acumulador

    return total_score / sims                  # 5. Promedio = Valor Esperado (EV)


# =============================================================================
# 4. TOMA DE DECISIONES Y RUNNER DE PRUEBA
# =============================================================================
def choose_keep_mask_montecarlo(
    current_values: List[int],
    rolls_remaining: int,
    available_categories: List[str],
    sims_per_mask: int = 200
) -> Tuple[List[bool], float]:
    """
    El "cerebro" de la IA: prueba las 32 formas de guardar dados y elige la mejor.

    Para cada máscara calcula su EV con Montecarlo y se queda con la de EV más alto.

    Retorna: (mejor_máscara, su_EV)
    """
    best_mask = None
    best_ev = -1.0

    for mask in all_keep_masks():              # Recorremos las 32 opciones
        ev = simulate_expected_value_after_keeps(
            current_values, mask, rolls_remaining, available_categories, sims_per_mask
        )
        # Protección: si alguien deja el TODO sin hacer, la función devuelve None
        if ev is None:
            raise NotImplementedError("Debes completar el bloque TODO antes de ejecutar.")

        if ev > best_ev:                       # ¿Esta opción es mejor que la mejor hasta ahora?
            best_ev = ev
            best_mask = mask

    return best_mask, best_ev


# =============================================================================
# PROGRAMA PRINCIPAL (solo se ejecuta si corres este archivo directamente)
# =============================================================================
if __name__ == "__main__":
    # Escenario de prueba: mano con un par de 4s y categorías críticas abiertas
    mano_actual = [3, 4, 4, 6, 1]
    categorias_libres = ["fours", "threeOfKind", "fullHouse", "largeStraight", "chance"]
    tiradas_restantes = 2

    print(f"Mano inicial: {mano_actual}")
    print(f"Categorías libres: {categorias_libres}")

    # Le pedimos a la IA que analice las 32 opciones (250 simulaciones cada una)
    mascara_optima, ev_maximo = choose_keep_mask_montecarlo(
        mano_actual, tiradas_restantes, categorias_libres, sims_per_mask=250
    )

    # Traducimos la máscara a algo legible: qué dados se quedan
    dados_retenidos = [mano_actual[i] for i, k in enumerate(mascara_optima) if k]

    print(f"\nMáscara óptima sugerida por IA: {mascara_optima}")
    print(f"Dados retenidos: {dados_retenidos}")
    print(f"Valor Esperado (EV) estimado: {ev_maximo:.2f} pts")