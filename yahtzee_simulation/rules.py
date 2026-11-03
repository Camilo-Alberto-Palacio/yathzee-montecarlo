"""
=============================================================================
  MÓDULO DE REGLAS Y EVALUACIÓN DE YAHTZEE
=============================================================================
Implementación rigurosa de la lógica del juego de Yahtzee conforme a las
reglas oficiales de Milton Bradley / Hasbro.
Define las 13 categorías estándar, funciones de validación de patrones,
cálculo de puntuación y generación de las 32 máscaras de retención de dados.
"""

from collections import Counter
from typing import List, Tuple, Dict, Optional

# Las 13 categorías estándar divididas en Sección Superior e Inferior
CATEGORIAS_SUPERIORES = ["unos", "doses", "treses", "cuatros", "cincos", "seises"]
CATEGORIAS_INFERIORES = [
    "trio",
    "poker",
    "full",
    "escalera_corta",
    "escalera_larga",
    "yahtzee",
    "libre"
]
CATEGORIAS: List[str] = CATEGORIAS_SUPERIORES + CATEGORIAS_INFERIORES

# Mapeo a valores numéricos de la sección superior
NUMERO_DE_CATEGORIA: Dict[str, int] = {
    "unos": 1, "doses": 2, "treses": 3, "cuatros": 4, "cincos": 5, "seises": 6
}

# Reglas de bonificación estándar
UMBRAL_BONO_SUPERIOR = 63
PUNTOS_BONO_SUPERIOR = 35
PUNTOS_YAHTZEE = 50
PUNTOS_FULL = 25
PUNTOS_ESCALERA_CORTA = 30
PUNTOS_ESCALERA_LARGA = 40

# Nombres descriptivos para reportes e interfaz gráfica
NOMBRES_CATEGORIAS: Dict[str, str] = {
    "unos": "Unos (Aces)",
    "doses": "Doses (Twos)",
    "treses": "Treses (Threes)",
    "cuatros": "Cuatros (Fours)",
    "cincos": "Cincos (Fives)",
    "seises": "Seises (Sixes)",
    "trio": "Trío (Three of a Kind)",
    "poker": "Póker (Four of a Kind)",
    "full": "Full House",
    "escalera_corta": "Escalera Pequeña (Small Straight)",
    "escalera_larga": "Escalera Grande (Large Straight)",
    "yahtzee": "YAHTZEE (5 iguales)",
    "libre": "Libre (Chance)",
    "suma_superior": "Subtotal Superior",
    "bono": "Bonificación Superior (+35)",
    "total": "Puntaje Total Final"
}


def hay_escalera(mano: List[int], longitud_requerida: int) -> bool:
    """
    Determina si existe una subsecuencia consecutiva de longitud dada en la mano.
    Para Escalera Corta: longitud_requerida = 4 (e.g. 1-2-3-4, 2-3-4-5, 3-4-5-6).
    Para Escalera Larga: longitud_requerida = 5 (e.g. 1-2-3-4-5, 2-3-4-5-6).
    """
    unicos = sorted(set(mano))
    if len(unicos) < longitud_requerida:
        return False

    racha_actual = 1
    racha_maxima = 1
    for i in range(1, len(unicos)):
        if unicos[i] == unicos[i - 1] + 1:
            racha_actual += 1
            if racha_actual > racha_maxima:
                racha_maxima = racha_actual
        else:
            racha_actual = 1
    return racha_maxima >= longitud_requerida


def calcular_puntos(categoria: str, mano: List[int]) -> int:
    """
    Calcula el puntaje exacto obtenido por una mano de 5 dados en una categoría específica.
    """
    conteo = Counter(mano)
    frecuencias = list(conteo.values())
    suma_total = sum(mano)

    # Sección Superior: suma únicamente los dados que coinciden con el valor solicitado
    if categoria in NUMERO_DE_CATEGORIA:
        num = NUMERO_DE_CATEGORIA[categoria]
        return conteo.get(num, 0) * num

    # Sección Inferior: patrones y combinaciones de póker de dados
    if categoria == "trio":
        return suma_total if any(f >= 3 for f in frecuencias) else 0

    if categoria == "poker":
        return suma_total if any(f >= 4 for f in frecuencias) else 0

    if categoria == "full":
        # Exactamente un trío y una pareja, o Yahtzee con comodín oficial
        return PUNTOS_FULL if (sorted(frecuencias) == [2, 3] or max(frecuencias) == 5) else 0

    if categoria == "escalera_corta":
        return PUNTOS_ESCALERA_CORTA if hay_escalera(mano, 4) else 0

    if categoria == "escalera_larga":
        return PUNTOS_ESCALERA_LARGA if hay_escalera(mano, 5) else 0

    if categoria == "yahtzee":
        return PUNTOS_YAHTZEE if max(frecuencias) == 5 else 0

    if categoria == "libre":
        return suma_total

    return 0


def mejor_puntaje(mano: List[int], categorias_libres: List[str]) -> Tuple[Optional[str], int]:
    """
    Evalúa la mano actual sobre el conjunto de categorías disponibles en la tarjeta
    y retorna la categoría que maximiza el puntaje inmediato, junto con los puntos obtenidos.
    """
    if not categorias_libres:
        return None, 0

    mejor_cat: Optional[str] = None
    mejor_pt = -1

    for cat in categorias_libres:
        pts = calcular_puntos(cat, mano)
        if pts > mejor_pt:
            mejor_pt = pts
            mejor_cat = cat

    return mejor_cat, mejor_pt


def todas_las_mascaras() -> List[List[bool]]:
    """
    Genera el espacio exhaustivo de las 2^5 = 32 máscaras booleanas de retención de dados.
    Cada elemento es una tupla/lista de 5 booleanos donde True indica retener el dado
    y False indica relanzarlo en el turno.
    """
    mascaras: List[List[bool]] = []
    for num in range(32):
        mascaras.append([(num >> i) & 1 == 1 for i in range(5)])
    return mascaras
