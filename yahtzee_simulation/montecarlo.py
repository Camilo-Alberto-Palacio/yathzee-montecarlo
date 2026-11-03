"""
=============================================================================
  MOTOR DE SIMULACIÓN MONTE CARLO Y LEY DE LOS GRANDES NÚMEROS
=============================================================================
Implementa el muestreo estocástico masivo vectorizado para:
1. Comprobar la convergencia de frecuencias relativas hacia las probabilidades
   teóricas exactas en las 13 categorías (Ley Débil y Fuerte de los Grandes Números),
   identificando fase transitoria (calentamiento) vs estado estable.
2. Ejecutar pruebas estadísticas formales Chi-Cuadrado (χ²) de uniformidad del
   generador PCG64 y bondad de ajuste multinomial sobre el espacio muestral Ω.
3. Analizar el decaimiento de la varianza del estimador y el error estándar
   conforme al Teorema del Límite Central: SE ~ O(1 / sqrt(N)), con ajuste OLS log-log.
4. Evaluar la estabilización del Valor Esperado (EV) en la toma óptima de
   decisiones contrastando contra la esperanza matemática exacta e identificando
   la probabilidad de inversión de rango en muestras pequeñas.
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
import pandas as pd
from scipy import stats

from .rules import (
    CATEGORIAS,
    INDICE_CATEGORIA,
    TABLA_PUNTOS_OMEGA,
    CLASE_PARTICION_OMEGA,
    codificar_manos_base6,
)
from .theory import (
    PROBABILIDADES_TEORICAS_EXACTAS,
    CARDINALIDAD_ESPACIO_MUESTRAL,
    NOMBRES_PARTICIONES_EXCLUYENTES,
    CONTEOS_TEORICOS_PARTICIONES,
    calcular_ev_exacto_mascara,
)


def simular_tiradas_vectorizadas(n_tiradas: int, seed: Optional[int] = 42) -> np.ndarray:
    """
    Genera una matriz (n_tiradas, 5) con números pseudoaleatorios uniformes en {1..6}
    utilizando el generador PCG64 de NumPy.
    """
    rng = np.random.default_rng(seed)
    return rng.integers(1, 7, size=(n_tiradas, 5))


def evaluar_mano_rapida(dados: np.ndarray) -> Dict[str, bool]:
    """
    Evalúa de forma exacta si un vector de 5 dados obtiene puntaje positivo (> 0)
    en cada una de las 13 categorías oficiales de Yahtzee.
    Mantiene paridad exacta con 'rules.calcular_puntos'.
    """
    arr = np.asarray(dados, dtype=np.int32)
    idx = int(codificar_manos_base6(arr))
    fila_pts = TABLA_PUNTOS_OMEGA[idx]
    return {cat: bool(fila_pts[j] > 0) for j, cat in enumerate(CATEGORIAS)}


def ejecutar_convergencia_lln(
    n_total: int = 100_000,
    checkpoints: Optional[List[int]] = None,
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ejecuta una corrida masiva de Monte Carlo de n_total lanzamientos independientes
    evaluando de forma genuina las 13 categorías del juego en todos los checkpoints.
    Además calcula pruebas Chi-Cuadrado (χ²) de bondad de ajuste sobre la corrida completa.

    Retorna:
      - df_lln: evolución por checkpoint N y categoría (13 categorías, cero valores ficticios).
      - df_chi2: resultados de las pruebas formales χ² de uniformidad y partición de Ω.
    """
    if checkpoints is None:
        checkpoints = [
            10, 20, 50, 100, 200, 500, 1_000, 2_000, 5_000,
            10_000, 20_000, 50_000, 75_000, 100_000,
        ]
        checkpoints = [cp for cp in checkpoints if cp <= n_total]
        if n_total not in checkpoints:
            checkpoints.append(n_total)

    matriz_dados = simular_tiradas_vectorizadas(n_total, seed=seed)
    indices_omega = codificar_manos_base6(matriz_dados)

    # Matriz booleana (n_total, 13) de ocurrencia genuina para las 13 categorías
    indicadores_matriz = TABLA_PUNTOS_OMEGA[indices_omega] > 0
    acumulados = np.cumsum(indicadores_matriz, axis=0)  # (n_total, 13)

    registros = []
    for n in checkpoints:
        regimen = "Transitorio (Calentamiento)" if n <= 200 else "Estable (Convergencia)"
        fila_acum = acumulados[n - 1]
        for cat in CATEGORIAS:
            col_j = INDICE_CATEGORIA[cat]
            fav_n = int(fila_acum[col_j])
            frec_relativa = fav_n / n
            p_teorica = PROBABILIDADES_TEORICAS_EXACTAS[cat]["probabilidad"]
            err_abs = abs(frec_relativa - p_teorica)
            err_rel = (err_abs / p_teorica) * 100.0 if p_teorica > 0 else 0.0

            se_teorico = float(np.sqrt(p_teorica * (1.0 - p_teorica) / n))
            ci_lower = max(0.0, p_teorica - 1.96 * se_teorico)
            ci_upper = min(1.0, p_teorica + 1.96 * se_teorico)
            var_muestral = frec_relativa * (1.0 - frec_relativa) / n

            registros.append({
                "N": n,
                "regimen": regimen,
                "categoria": cat,
                "casos_favorables": fav_n,
                "frecuencia_relativa": frec_relativa,
                "probabilidad_teorica": p_teorica,
                "error_absoluto": err_abs,
                "error_relativo_pct": err_rel,
                "error_estandar": se_teorico,
                "ci_95_lower": ci_lower,
                "ci_95_upper": ci_upper,
                "varianza_estimador": var_muestral,
            })

    # Pruebas formales de Bondad de Ajuste Chi-Cuadrado (χ²)
    # 1) Uniformidad de los 5 * n_total dados individuales en caras {1..6}
    caras_obs = np.bincount(matriz_dados.ravel(), minlength=7)[1:]
    caras_esp = np.full(6, (5 * n_total) / 6.0)
    chi2_unif, pval_unif = stats.chisquare(f_obs=caras_obs, f_exp=caras_esp)

    # 2) Partición combinatoria exhaustiva de Ω en 7 clases mutuamente excluyentes
    clases_sim = CLASE_PARTICION_OMEGA[indices_omega]
    part_obs = np.bincount(clases_sim, minlength=7)
    part_esp = np.array(CONTEOS_TEORICOS_PARTICIONES, dtype=float) * (
        n_total / CARDINALIDAD_ESPACIO_MUESTRAL
    )
    chi2_part, pval_part = stats.chisquare(f_obs=part_obs, f_exp=part_esp)

    df_chi2 = pd.DataFrame([
        {
            "prueba": "Uniformidad Caras del Dado {1..6}",
            "n_muestral": 5 * n_total,
            "grados_libertad": 5,
            "estadistico_chi2": float(chi2_unif),
            "valor_critico_alfa_005": float(stats.chi2.ppf(0.95, df=5)),
            "p_valor": float(pval_unif),
            "conclusion": "No se rechaza H0 (Uniformidad validada)" if pval_unif > 0.05 else "Rechaza H0",
        },
        {
            "prueba": "Partición Combinatoria de Ω (7 Clases Excluyentes)",
            "n_muestral": n_total,
            "grados_libertad": 6,
            "estadistico_chi2": float(chi2_part),
            "valor_critico_alfa_005": float(stats.chi2.ppf(0.95, df=6)),
            "p_valor": float(pval_part),
            "conclusion": "No se rechaza H0 (Ajuste a Laplace validado)" if pval_part > 0.05 else "Rechaza H0",
        },
    ])

    return pd.DataFrame(registros), df_chi2


def simular_decaimiento_varianza_tlc(
    n_lista: List[int],
    replicas: int = 200,
    seed: int = 123,
) -> pd.DataFrame:
    """
    Verifica experimentalmente el Teorema del Límite Central (TLC):
    Var(bar{X}_N) = p(1-p) / N  y  SE(N) = sqrt(p(1-p)) / sqrt(N).
    Ejecuta 'replicas' corridas independientes por cada tamaño muestral N de forma
    100% vectorizada y ajusta la pendiente OLS en escala log-log (teórica = -0.50).
    """
    rng = np.random.default_rng(seed)
    p_yahtzee = PROBABILIDADES_TEORICAS_EXACTAS["yahtzee"]["probabilidad"]
    p_full = PROBABILIDADES_TEORICAS_EXACTAS["full"]["probabilidad"]

    idx_yahtzee = INDICE_CATEGORIA["yahtzee"]
    idx_full = INDICE_CATEGORIA["full"]

    filas = []
    for n in n_lista:
        # Matriz (replicas, n, 5) evaluada de golpe
        tiradas = rng.integers(1, 7, size=(replicas, n, 5))
        codigos = codificar_manos_base6(tiradas)  # (replicas, n)

        exitos_yahtzee = (TABLA_PUNTOS_OMEGA[codigos, idx_yahtzee] > 0).mean(axis=1)
        exitos_full = (TABLA_PUNTOS_OMEGA[codigos, idx_full] > 0).mean(axis=1)

        std_empirica_y = float(np.std(exitos_yahtzee, ddof=1))
        std_teorica_y = float(np.sqrt(p_yahtzee * (1.0 - p_yahtzee) / n))

        std_empirica_f = float(np.std(exitos_full, ddof=1))
        std_teorica_f = float(np.sqrt(p_full * (1.0 - p_full) / n))

        filas.append({
            "N": n,
            "replicas": replicas,
            "std_empirica_yahtzee": std_empirica_y,
            "std_teorica_yahtzee": std_teorica_y,
            "error_std_yahtzee": abs(std_empirica_y - std_teorica_y),
            "std_empirica_full": std_empirica_f,
            "std_teorica_full": std_teorica_f,
            "error_std_full": abs(std_empirica_f - std_teorica_f),
        })

    df_tlc = pd.DataFrame(filas)

    # Regresión lineal OLS en escala log10-log10: log10(SE) = intercepto + m * log10(N)
    log_n = np.log10(df_tlc["N"].values.astype(float))
    res_y = stats.linregress(log_n, np.log10(df_tlc["std_empirica_yahtzee"].values))
    res_f = stats.linregress(log_n, np.log10(df_tlc["std_empirica_full"].values))

    df_tlc["pendiente_ols_yahtzee"] = float(res_y.slope)
    df_tlc["r2_ols_yahtzee"] = float(res_y.rvalue ** 2)
    df_tlc["pendiente_ols_full"] = float(res_f.slope)
    df_tlc["r2_ols_full"] = float(res_f.rvalue ** 2)

    return df_tlc


def simular_valor_esperado_mascaras(
    mano_actual: List[int],
    categorias_libres: List[str],
    sims_lista: List[int],
    replicas: int = 100,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Analiza la estabilización del Valor Esperado (EV) de 4 políticas de retención
    representativas sobre una mano táctica real (p. ej. [3, 4, 4, 6, 1]), contrastando:
      - El estimador Monte Carlo EV_MC(N) y su desviación estándar entre réplicas.
      - El Valor Esperado analítico exacto EV_exacto(m) sobre los 6^k estados posibles.
      - La tasa empírica de inversión de rango (probabilidad de no elegir la jugada óptima
        por ruido muestral cuando N es pequeño).
    """
    rng = np.random.default_rng(seed)
    cols_libres = [INDICE_CATEGORIA[c] for c in categorias_libres]
    mano_arr = np.array(mano_actual, dtype=np.int32)

    mascaras_clave: Dict[str, List[bool]] = {
        "Retener Par [4, 4]": [False, True, True, False, False],
        "Retener Un Dado [4]": [False, True, False, False, False],
        "Retener Secuencia [3, 4]": [True, True, False, False, False],
        "Relanzar Todo": [False, False, False, False, False],
        "Retener Todo (Plantarse)": [True, True, True, True, True],
    }

    # Valor Esperado analítico exacto de cada máscara
    ev_exactos = {
        nombre: calcular_ev_exacto_mascara(mano_actual, mask, categorias_libres)
        for nombre, mask in mascaras_clave.items()
    }
    mejor_estrategia_exacta = max(ev_exactos, key=ev_exactos.get)

    registros = []
    nombres_est = list(mascaras_clave.keys())

    for n_sim in sims_lista:
        # Matriz de resultados por réplica: (replicas, num_estrategias)
        matriz_ev_replicas = np.zeros((replicas, len(nombres_est)), dtype=float)

        for j_est, nombre_estrategia in enumerate(nombres_est):
            mask_arr = np.array(mascaras_clave[nombre_estrategia], dtype=bool)
            if np.all(mask_arr):
                matriz_ev_replicas[:, j_est] = ev_exactos[nombre_estrategia]
            else:
                azar = rng.integers(1, 7, size=(replicas, n_sim, 5))
                manos_sim = np.where(mask_arr, mano_arr, azar)
                codigos = codificar_manos_base6(manos_sim)  # (replicas, n_sim)
                pts_max = TABLA_PUNTOS_OMEGA[codigos][:, :, cols_libres].max(axis=2)
                matriz_ev_replicas[:, j_est] = pts_max.mean(axis=1)

        # Verificar en cuántas réplicas ganó realmente la estrategia óptima analítica
        idx_optimo = nombres_est.index(mejor_estrategia_exacta)
        ganadoras = np.argmax(matriz_ev_replicas, axis=1)
        tasa_decision_correcta = float(np.mean(ganadoras == idx_optimo) * 100.0)
        tasa_inversion_rango = 100.0 - tasa_decision_correcta

        for j_est, nombre_estrategia in enumerate(nombres_est):
            ev_runs = matriz_ev_replicas[:, j_est]
            registros.append({
                "sims": n_sim,
                "estrategia": nombre_estrategia,
                "ev_exacto": ev_exactos[nombre_estrategia],
                "ev_medio": float(np.mean(ev_runs)),
                "ev_std": float(np.std(ev_runs, ddof=1)),
                "ev_min": float(np.min(ev_runs)),
                "ev_max": float(np.max(ev_runs)),
                "es_optima_teorica": bool(nombre_estrategia == mejor_estrategia_exacta),
                "tasa_decision_optima_pct": tasa_decision_correcta,
                "tasa_inversion_rango_pct": tasa_inversion_rango,
            })

    return pd.DataFrame(registros)
