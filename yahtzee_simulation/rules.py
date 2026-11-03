"""
=============================================================================
  MÓDULO DE REGLAS Y EVALUACIÓN VECTORIZADA DE YAHTZEE
=============================================================================
Implementación rigurosa de la lógica del juego de Yahtzee conforme a las
reglas estándar en un lanzamiento y en completa paridad matemática con el
prototipo base ('yahtzee_montecarlo.py' y 'prueba.py').
Incluye tablas de búsqueda precalculadas sobre los |Ω| = 6^5 = 7,776 estados
para acelerar las corridas masivas de Monte Carlo en órdenes de magnitud.
"""

import itertools
from collections import Counter
from typing import List, Tuple, Dict, Optional
import numpy as np

# Las 13 categorías estándar divididas en Sección Superior e Inferior
CATEGORIAS_SUPERIORES: List[str] = ["unos", "doses", "treses", "cuatros", "cincos", "seises"]
CATEGORIAS_INFERIORES: List[str] = [
    "trio",
    "poker",
    "full",
    "escalera_corta",
    "escalera_larga",
    "yahtzee",
    "libre"
]
CATEGORIAS: List[str] = CATEGORIAS_SUPERIORES + CATEGORIAS_INFERIORES
INDICE_CATEGORIA: Dict[str, int] = {cat: idx for idx, cat in enumerate(CATEGORIAS)}

# Mapeo a valores numéricos de la sección superior
NUMERO_DE_CATEGORIA: Dict[str, int] = {
    "unos": 1, "doses": 2, "treses": 3, "cuatros": 4, "cincos": 5, "seises": 6
}

# Reglas de bonificación y puntajes fijos estándar
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
    "full": "Full House (Trío + Par)",
    "escalera_corta": "Escalera Pequeña (Small Straight)",
    "escalera_larga": "Escalera Grande (Large Straight)",
    "yahtzee": "YAHTZEE (5 Iguales)",
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
    Calcula el puntaje exacto obtenido por una mano de 5 dados en una categoría.
    Mantiene paridad exacta 1:1 con 'yahtzee_montecarlo.py': Full House exige
    estrictamente un trío y una pareja distintos (multiplicidades [2, 3]).
    """
    conteo = Counter(mano)
    frecuencias = list(conteo.values())
    suma_total = sum(mano)

    # Sección Superior: suma únicamente los dados que coinciden con la cara objetivo
    if categoria in NUMERO_DE_CATEGORIA:
        num = NUMERO_DE_CATEGORIA[categoria]
        return conteo.get(num, 0) * num

    # Sección Inferior: combinaciones especiales
    if categoria == "trio":
        return suma_total if max(frecuencias) >= 3 else 0

    if categoria == "poker":
        return suma_total if max(frecuencias) >= 4 else 0

    if categoria == "full":
        return PUNTOS_FULL if sorted(frecuencias) == [2, 3] else 0

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
    True indica retener el dado y False indica relanzarlo.
    """
    mascaras: List[List[bool]] = []
    for num in range(32):
        mascaras.append([(num >> i) & 1 == 1 for i in range(5)])
    return mascaras


# =============================================================================
# TABLAS VECTORIZADAS PRECALCULADAS SOBRE Ω (|Ω| = 6^5 = 7,776 MICROESTADOS)
# =============================================================================
PESOS_BASE6 = np.array([1296, 216, 36, 6, 1], dtype=np.int32)
MASCARAS_ARRAY = np.array(todas_las_mascaras(), dtype=bool)  # (32, 5)


def _construir_tablas_omega() -> Tuple[np.ndarray, np.ndarray]:
    """
    Precalcula para cada una de las 7,776 configuraciones posibles de 5 dados:
      - tabla_puntos: matriz (7776, 13) con el puntaje exacto en cada categoría.
      - clase_particion: vector (7776,) con el índice de partición excluyente (0..6):
            0: Yahtzee [5]               (6 estados)
            1: Póker estricto [1,4]      (150 estados)
            2: Full House [2,3]          (300 estados)
            3: Trío estricto [1,1,3]     (1200 estados)
            4: Doble Par [1,2,2]         (1800 estados)
            5: Un Par [1,1,1,2]          (3600 estados)
            6: Todos Distintos [1,1,1,1,1] (720 estados)
    """
    tabla_puntos = np.zeros((7776, len(CATEGORIAS)), dtype=np.int32)
    clase_particion = np.zeros(7776, dtype=np.int8)

    mapa_particion = {
        (5,): 0,
        (1, 4): 1,
        (2, 3): 2,
        (1, 1, 3): 3,
        (1, 2, 2): 4,
        (1, 1, 1, 2): 5,
        (1, 1, 1, 1, 1): 6,
    }

    for idx, tiro in enumerate(itertools.product(range(1, 7), repeat=5)):
        mano = list(tiro)
        part = tuple(sorted(Counter(mano).values()))
        clase_particion[idx] = mapa_particion[part]
        for j, cat in enumerate(CATEGORIAS):
            tabla_puntos[idx, j] = calcular_puntos(cat, mano)

    return tabla_puntos, clase_particion


TABLA_PUNTOS_OMEGA, CLASE_PARTICION_OMEGA = _construir_tablas_omega()


def codificar_manos_base6(matriz_dados: np.ndarray) -> np.ndarray:
    """
    Convierte un arreglo de manos con valores en {1..6} de forma (..., 5)
    en sus índices biyectivos en {0..7775}.
    """
    return np.tensordot(matriz_dados - 1, PESOS_BASE6, axes=([-1], [0])).astype(np.int32)
