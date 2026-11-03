"""
=============================================================================
  MÓDULO DE PROBABILIDAD TEÓRICA EXACTA PARA YAHTZEE
=============================================================================
Cálculo analítico exacto de probabilidades combinatorias en el espacio muestral
de 5 dados de 6 caras (|Ω| = 6^5 = 7,776 resultados equiprobables).
Proporciona la verdad matemática fundamental para validar:
1. La Ley Débil y Fuerte de los Grandes Números (LLN).
2. El Teorema del Límite Central (TLC).
3. El Valor Esperado (EV) exacto de cualquier máscara de retención.
4. Pruebas Chi-Cuadrado (χ²) de bondad de ajuste multinomial.
"""

import itertools
from typing import Dict, List
from .rules import (
    CATEGORIAS,
    calcular_puntos,
    mejor_puntaje,
    TABLA_PUNTOS_OMEGA,
    CLASE_PARTICION_OMEGA,
)

# Espacio muestral total equiprobable para 5 dados estándar
CARDINALIDAD_ESPACIO_MUESTRAL = 6 ** 5  # 7,776

NOMBRES_PARTICIONES_EXCLUYENTES: List[str] = [
    "Yahtzee [5]",
    "Póker Estricto [1,4]",
    "Full House [2,3]",
    "Trío Estricto [1,1,3]",
    "Doble Par [1,2,2]",
    "Par Simple [1,1,1,2]",
    "Todos Distintos [1,1,1,1,1]",
]

CONTEOS_TEORICOS_PARTICIONES: List[int] = [6, 150, 300, 1200, 1800, 3600, 720]


def calcular_probabilidades_teoricas_exactas() -> Dict[str, Dict[str, float]]:
    """
    Calcula exhaustivamente sobre los 7,776 elementos del espacio muestral Ω
    el número exacto de combinaciones favorables, la probabilidad teórica P(A),
    la varianza Bernoulli p(1-p) y el puntaje esperado en un lanzamiento.
    """
    orden_reporte = [
        "yahtzee",
        "poker",
        "trio",
        "full",
        "escalera_larga",
        "escalera_corta",
        "unos",
        "doses",
        "treses",
        "cuatros",
        "cincos",
        "seises",
        "libre",
    ]

    resultados_teoricos: Dict[str, Dict[str, float]] = {}
    for cat in orden_reporte:
        col_idx = CATEGORIAS.index(cat)
        puntos_col = TABLA_PUNTOS_OMEGA[:, col_idx]
        fav = int((puntos_col > 0).sum())
        prob = fav / CARDINALIDAD_ESPACIO_MUESTRAL
        ev = float(puntos_col.sum()) / CARDINALIDAD_ESPACIO_MUESTRAL
        resultados_teoricos[cat] = {
            "casos_favorables": fav,
            "total_espacio": CARDINALIDAD_ESPACIO_MUESTRAL,
            "probabilidad": prob,
            "porcentaje": prob * 100.0,
            "varianza_bernoulli": prob * (1.0 - prob),
            "valor_esperado_puntos": ev,
        }

    return resultados_teoricos


def calcular_ev_exacto_mascara(
    mano_actual: List[int],
    mascara: List[bool],
    categorias_libres: List[str],
) -> float:
    """
    Calcula la esperanza matemática analítica exacta E[max_{c in libres} Puntaje(c, Y(m))]
    enumerando exhaustivamente los 6^k resultados equiprobables de los k dados relanzados.
    """
    pos_relanzar = [i for i in range(5) if not mascara[i]]
    k = len(pos_relanzar)
    if k == 0:
        _, pts = mejor_puntaje(mano_actual, categorias_libres)
        return float(pts)

    total_outcomes = 6 ** k
    suma_pts = 0
    mano_base = list(mano_actual)
    for nuevos in itertools.product(range(1, 7), repeat=k):
        for idx_pos, cara in zip(pos_relanzar, nuevos):
            mano_base[idx_pos] = cara
        _, pts = mejor_puntaje(mano_base, categorias_libres)
        suma_pts += pts

    return suma_pts / total_outcomes


# Diccionario precalculado de referencia teórica exacta
PROBABILIDADES_TEORICAS_EXACTAS: Dict[str, Dict[str, float]] = calcular_probabilidades_teoricas_exactas()
