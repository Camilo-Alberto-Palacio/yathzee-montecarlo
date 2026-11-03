"""
=============================================================================
  MOTOR DE SIMULACIÓN MONTE CARLO Y LEY DE LOS GRANDES NÚMEROS
=============================================================================
Este módulo implementa el muestreo estocástico masivo para:
1. Estudiar la convergencia de frecuencias relativas hacia las probabilidades
   teóricas exactas (Ley Débil y Fuerte de los Grandes Números).
2. Analizar el decaimiento de la varianza del estimador y el error estándar
   conforme al Teorema del Límite Central: SE ~ O(1 / sqrt(N)).
3. Evaluar la estabilización del Valor Esperado (EV) en la toma óptima de
   decisiones (evaluación de las 32 máscaras de retención).
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from collections import Counter

from .rules import (
    CATEGORIAS,
    calcular_puntos,
    mejor_puntaje,
    todas_las_mascaras,
    hay_escalera
)
from .theory import PROBABILIDADES_TEORICAS_EXACTAS


def simular_tiradas_vectorizadas(n_tiradas: int, seed: Optional[int] = 42) -> np.ndarray:
    """
    Genera una matriz (n_tiradas, 5) con números pseudoaleatorios uniformes en [1, 6]
    utilizando el generador PCG64 de NumPy de alto rendimiento.
    """
    rng = np.random.default_rng(seed)
    return rng.integers(1, 7, size=(n_tiradas, 5))


def evaluar_mano_rapida(dados: np.ndarray) -> Dict[str, bool]:
    """
    Evalúa de forma eficiente si un vector de 5 dados satisface cada una
    de las categorías de Yahtzee en un solo lanzamiento.
    """
    # Conteo de ocurrencias de caras 1..6
    conteos = np.bincount(dados, minlength=7)[1:]  # caras 1 a 6
    repeticiones = conteos[conteos > 0]
    max_rep = np.max(conteos) if len(repeticiones) > 0 else 0

    # Búsqueda de escalera
    unicos = np.sort(np.unique(dados))
    racha_max = 1
    if len(unicos) > 1:
        diffs = np.diff(unicos)
        racha_act = 1
        for d in diffs:
            if d == 1:
                racha_act += 1
                if racha_act > racha_max:
                    racha_max = racha_act
            else:
                racha_act = 1

    return {
        "yahtzee": bool(max_rep == 5),
        "poker": bool(max_rep >= 4),
        "trio": bool(max_rep >= 3),
        "full": bool((len(repeticiones) == 2 and sorted(repeticiones) == [2, 3]) or max_rep == 5),
        "escalera_larga": bool(racha_max >= 5),
        "escalera_corta": bool(racha_max >= 4),
        "unos": bool(conteos[0] > 0),
        "doses": bool(conteos[1] > 0),
        "treses": bool(conteos[2] > 0),
        "cuatros": bool(conteos[3] > 0),
        "cincos": bool(conteos[4] > 0),
        "seises": bool(conteos[5] > 0),
        "libre": True
    }


def ejecutar_convergencia_lln(
    n_total: int = 100_000,
    checkpoints: Optional[List[int]] = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Ejecuta una corrida masiva de Monte Carlo de n_total lanzamientos y registra en
    los checkpoints especificados la frecuencia relativa acumulada, el error absoluto,
    el error relativo y los intervalos de confianza del 95% para cada categoría.
    Demuestra empíricamente la Ley de los Grandes Números (LLN).
    """
    if checkpoints is None:
        checkpoints = [
            10, 20, 50, 100, 200, 500, 1_000, 2_000, 5_000,
            10_000, 20_000, 50_000, 75_000, 100_000
        ]
        checkpoints = [cp for cp in checkpoints if cp <= n_total]
        if n_total not in checkpoints:
            checkpoints.append(n_total)

    matriz_dados = simular_tiradas_vectorizadas(n_total, seed=seed)

    categorias_interes = [
        "yahtzee", "poker", "full", "escalera_larga", "escalera_corta", "trio"
    ]

    # Pre-evaluación booleana de todas las tiradas
    indicadores = {cat: np.zeros(n_total, dtype=bool) for cat in categorias_interes}
    for i in range(n_total):
        eval_i = evaluar_mano_rapida(matriz_dados[i])
        for cat in categorias_interes:
            indicadores[cat][i] = eval_i[cat]

    registros = []
    for n in checkpoints:
        for cat in categorias_interes:
            fav_n = int(np.sum(indicadores[cat][:n]))
            frec_relativa = fav_n / n
            p_teorica = PROBABILIDADES_TEORICAS_EXACTAS[cat]["probabilidad"]
            err_abs = abs(frec_relativa - p_teorica)
            err_rel = (err_abs / p_teorica) * 100.0 if p_teorica > 0 else 0.0

            # Error estándar asintótico: SE = sqrt( p*(1-p) / N )
            se_teorico = np.sqrt(p_teorica * (1.0 - p_teorica) / n)
            ci_lower = max(0.0, p_teorica - 1.96 * se_teorico)
            ci_upper = min(1.0, p_teorica + 1.96 * se_teorico)

            # Varianza muestral del estimador Bernoulli
            var_muestral = frec_relativa * (1.0 - frec_relativa) / n

            registros.append({
                "N": n,
                "categoria": cat,
                "casos_favorables": fav_n,
                "frecuencia_relativa": frec_relativa,
                "probabilidad_teorica": p_teorica,
                "error_absoluto": err_abs,
                "error_relativo_pct": err_rel,
                "error_estandar": se_teorico,
                "ci_95_lower": ci_lower,
                "ci_95_upper": ci_upper,
                "varianza_estimador": var_muestral
            })

    return pd.DataFrame(registros)


def simular_decaimiento_varianza_tlc(
    n_lista: List[int],
    replicas: int = 150,
    seed: int = 123
) -> pd.DataFrame:
    """
    Verifica experimentalmente el Teorema del Límite Central (TLC):
    Var(bar{X}_N) = sigma^2 / N  y  SE = sigma / sqrt(N).
    Para cada N, ejecuta 'replicas' estimaciones independientes de Monte Carlo
    y calcula la dispersión empírica (desviación estándar empírica entre réplicas).
    """
    rng = np.random.default_rng(seed)
    p_yahtzee = PROBABILIDADES_TEORICAS_EXACTAS["yahtzee"]["probabilidad"]
    p_full = PROBABILIDADES_TEORICAS_EXACTAS["full"]["probabilidad"]

    filas = []
    for n in n_lista:
        estimaciones_yahtzee = []
        estimaciones_full = []

        for _ in range(replicas):
            tiradas = rng.integers(1, 7, size=(n, 5))
            fav_yahtzee = 0
            fav_full = 0
            for i in range(n):
                ev = evaluar_mano_rapida(tiradas[i])
                if ev["yahtzee"]:
                    fav_yahtzee += 1
                if ev["full"]:
                    fav_full += 1

            estimaciones_yahtzee.append(fav_yahtzee / n)
            estimaciones_full.append(fav_full / n)

        std_empirica_y = float(np.std(estimaciones_yahtzee, ddof=1))
        std_teorica_y = float(np.sqrt(p_yahtzee * (1.0 - p_yahtzee) / n))

        std_empirica_f = float(np.std(estimaciones_full, ddof=1))
        std_teorica_f = float(np.sqrt(p_full * (1.0 - p_full) / n))

        filas.append({
            "N": n,
            "std_empirica_yahtzee": std_empirica_y,
            "std_teorica_yahtzee": std_teorica_y,
            "error_std_yahtzee": abs(std_empirica_y - std_teorica_y),
            "std_empirica_full": std_empirica_f,
            "std_teorica_full": std_teorica_f,
            "error_std_full": abs(std_empirica_f - std_teorica_f)
        })

    return pd.DataFrame(filas)


def simular_valor_esperado_mascaras(
    mano_actual: List[int],
    categorias_libres: List[str],
    sims_lista: List[int],
    replicas: int = 30,
    seed: int = 42
) -> pd.DataFrame:
    """
    Analiza la estabilización del Valor Esperado (EV) de las decisiones
    de retención de dados en función del número de iteraciones de Monte Carlo.
    Permite demostrar cómo un número bajo de simulaciones (ej. 10 o 50) induce
    alta varianza e inestabilidad en la recomendación de la IA, mientras que
    N >= 250 estabiliza inequívocamente el orden jerárquico de las jugadas.
    """
    rng = np.random.default_rng(seed)
    mascaras = todas_las_mascaras()

    # Seleccionamos 4 máscaras representativas para análisis detallado:
    # 1. Retener todo (plantarse)
    # 2. Retener el par de 4s (estrategia natural si mano=[3, 4, 4, 6, 1])
    # 3. Retener [3, 4] buscando escalera
    # 4. Relanzar todo
    mascaras_clave = {
        "Retener Par [4, 4]": [False, True, True, False, False],
        "Retener Escalera [3, 4, 6]": [True, True, False, True, False],
        "Retener Todo (Plantarse)": [True, True, True, True, True],
        "Relanzar Todo": [False, False, False, False, False]
    }

    registros = []
    for n_sim in sims_lista:
        for nombre_estrategia, mask in mascaras_clave.items():
            ev_runs = []
            for _ in range(replicas):
                puntos_acum = 0.0
                for _ in range(n_sim):
                    mano_sim = list(mano_actual)
                    for pos in range(5):
                        if not mask[pos]:
                            mano_sim[pos] = int(rng.integers(1, 7))
                    _, sc = mejor_puntaje(mano_sim, categorias_libres)
                    puntos_acum += sc
                ev_runs.append(puntos_acum / n_sim)

            registros.append({
                "sims": n_sim,
                "estrategia": nombre_estrategia,
                "ev_medio": float(np.mean(ev_runs)),
                "ev_std": float(np.std(ev_runs, ddof=1)),
                "ev_min": float(np.min(ev_runs)),
                "ev_max": float(np.max(ev_runs))
            })

    return pd.DataFrame(registros)
