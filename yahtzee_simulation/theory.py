"""
=============================================================================
  MÓDULO DE PROBABILIDAD TEÓRICA EXACTA PARA YAHTZEE
=============================================================================
Cálculo analítico exacto de probabilidades combinatorias en el espacio muestral
de 5 dados de 6 caras (|Ω| = 6^5 = 7776 resultados equiprobables).
Proporciona la base teórica (verdad fundamental) para validar la
Ley de los Grandes Números (LLN) y el Teorema del Límite Central (TLC).
"""

import itertools
from typing import Dict, Tuple
from .rules import calcular_puntos, hay_escalera

# Espacio muestral total equiprobable para 5 dados estándar
CARDINALIDAD_ESPACIO_MUESTRAL = 6 ** 5  # 7776


def calcular_probabilidades_teoricas_exactas() -> Dict[str, Dict[str, float]]:
    """
    Calcula exhaustivamente sobre los 7776 elementos del espacio muestral Ω
    el número exacto de combinaciones favorables y la probabilidad teórica P(A)
    para cada categoría de Yahtzee en un solo lanzamiento (tiro inicial).

    Retorna un diccionario con:
      - 'casos_favorables': int
      - 'probabilidad': float
      - 'porcentaje': float
      - 'valor_esperado_puntos': float
    """
    conteo_favorables: Dict[str, int] = {
        "yahtzee": 0,
        "poker": 0,
        "trio": 0,
        "full": 0,
        "escalera_larga": 0,
        "escalera_corta": 0,
        "unos": 0,
        "doses": 0,
        "treses": 0,
        "cuatros": 0,
        "cincos": 0,
        "seises": 0,
        "libre": 0
    }

    suma_puntos: Dict[str, float] = {k: 0.0 for k in conteo_favorables}

    # Iteración exhaustiva sobre las 7776 micro-configuraciones de Ω
    for tiro in itertools.product(range(1, 7), repeat=5):
        mano = list(tiro)

        # Evaluación de cada categoría
        for cat in conteo_favorables:
            pts = calcular_puntos(cat, mano)
            suma_puntos[cat] += pts
            if pts > 0:
                conteo_favorables[cat] += 1

    resultados_teoricos: Dict[str, Dict[str, float]] = {}
    for cat, fav in conteo_favorables.items():
        prob = fav / CARDINALIDAD_ESPACIO_MUESTRAL
        ev = suma_puntos[cat] / CARDINALIDAD_ESPACIO_MUESTRAL
        resultados_teoricos[cat] = {
            "casos_favorables": fav,
            "total_espacio": CARDINALIDAD_ESPACIO_MUESTRAL,
            "probabilidad": prob,
            "porcentaje": prob * 100.0,
            "valor_esperado_puntos": ev
        }

    return resultados_teoricos


# Diccionario precalculado de referencia teórica exacta
PROBABILIDADES_TEORICAS_EXACTAS: Dict[str, Dict[str, float]] = calcular_probabilidades_teoricas_exactas()
