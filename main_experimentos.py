"""
=============================================================================
  PIPELINE PRINCIPAL DE EXPERIMENTACIÓN MONTE CARLO Y VALIDACIÓN TEÓRICA
=============================================================================
Ejecuta la suite integral de simulación estocástica para la Actividad 1:
- Comprobación empírica de la Ley de los Grandes Números en las 13 categorías (N = 10 a 100,000).
- Pruebas Chi-Cuadrado (χ²) de uniformidad del PRNG y bondad de ajuste multinomial.
- Validación del Teorema del Límite Central (decaimiento O(1/sqrt(N)) con ajuste OLS log-log).
- Análisis de estabilización del Valor Esperado (EV) y eliminación de inversiones de rango.
- Torneo masivo de 3,000 partidas completas (Aleatorio vs Heurístico vs IA Monte Carlo EV).
- Exportación de datasets CSV auditables a 'results/' y generación de 6 figuras a 300 DPI.
"""

import os
import sys
import time
import pandas as pd

# Soporte completo UTF-8 para consola de Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Asegurar importación del paquete local
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from yahtzee_simulation.rules import NOMBRES_CATEGORIAS
from yahtzee_simulation.theory import PROBABILIDADES_TEORICAS_EXACTAS
from yahtzee_simulation.montecarlo import (
    ejecutar_convergencia_lln,
    simular_decaimiento_varianza_tlc,
    simular_valor_esperado_mascaras,
)
from yahtzee_simulation.massive_runs import ejecutar_corridas_masivas_estrategias
from yahtzee_simulation.visualizations import (
    graficar_fig1_convergencia_lln,
    graficar_fig2_varianza_tlc,
    graficar_fig3_histogramas_empirico_vs_teorico,
    graficar_fig4_estabilizacion_ev_mascaras,
    graficar_fig5_corridas_masivas_estrategias,
    graficar_fig6_descomposicion_categorias_bono,
)

RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def main() -> None:
    print("=" * 78)
    print("  SIMULACIÓN MONTE CARLO DE YAHTZEE Y TEORÍA DE LOS GRANDES NÚMEROS")
    print("  Institución Universitaria Digital de Antioquia - Simulación (Grupo 25)")
    print("=" * 78)

    tiempo_inicio_total = time.time()

    # -------------------------------------------------------------------------
    # EXPERIMENTO 1: LEY DE LOS GRANDES NÚMEROS Y BONDAD DE AJUSTE CHI-CUADRADO
    # -------------------------------------------------------------------------
    print("\n[1/4] Ejecutando simulación masiva de la Ley de los Grandes Números...")
    print("      Tiradas totales: 100,000 | Evaluando genuinamente las 13 categorías")
    t0 = time.time()
    df_lln, df_chi2 = ejecutar_convergencia_lln(n_total=100_000, seed=42)

    csv_lln = os.path.join(RESULTS_DIR, "convergencia_ley_grandes_numeros.csv")
    df_lln.to_csv(csv_lln, index=False)

    csv_chi2 = os.path.join(RESULTS_DIR, "pruebas_bondad_ajuste_chi2.csv")
    df_chi2.to_csv(csv_chi2, index=False)
    print(f"      -> Guardado CSV LLN: {csv_lln} ({len(df_lln)} filas) [{time.time() - t0:.2f}s]")
    print(f"      -> Guardado CSV Chi²: {csv_chi2}")

    # Generar Figura 1
    fig1_path = os.path.join(RESULTS_DIR, "fig1_convergencia_grandes_numeros.png")
    graficar_fig1_convergencia_lln(df_lln, fig1_path)
    print(f"      -> Figura 1 generada a 300 DPI: {fig1_path}")

    # Tabla comparativa teórica vs empírica genuina en N=100,000 (las 13 categorías)
    df_100k = df_lln[df_lln["N"] == 100_000].set_index("categoria")
    comparativa_rows = []
    for cat, teor in PROBABILIDADES_TEORICAS_EXACTAS.items():
        if cat not in df_100k.index:
            raise RuntimeError(f"Categoría '{cat}' ausente en la simulación empírica N=100,000.")
        fila_mc = df_100k.loc[cat]
        f_emp = float(fila_mc["frecuencia_relativa"])
        fav_emp = int(fila_mc["casos_favorables"])
        err_abs = abs(f_emp - teor["probabilidad"])
        err_rel = (err_abs / teor["probabilidad"]) * 100.0 if teor["probabilidad"] > 0 else 0.0

        comparativa_rows.append({
            "categoria_clave": cat,
            "categoria_nombre": NOMBRES_CATEGORIAS.get(cat, cat),
            "casos_favorables_espacio": int(teor["casos_favorables"]),
            "total_espacio": int(teor["total_espacio"]),
            "probabilidad_teorica": float(teor["probabilidad"]),
            "porcentaje_teorico": float(teor["porcentaje"]),
            "casos_favorables_mc_100k": fav_emp,
            "frecuencia_empirica": f_emp,
            "porcentaje_empirico": f_emp * 100.0,
            "error_absoluto": err_abs,
            "error_relativo_pct": err_rel,
            "error_estandar_100k": float(fila_mc["error_estandar"]),
        })

    df_comp = pd.DataFrame(comparativa_rows)
    csv_comp = os.path.join(RESULTS_DIR, "probabilidades_teoricas_vs_empiricas.csv")
    df_comp.to_csv(csv_comp, index=False)
    print(f"      -> Guardado CSV comparativa global: {csv_comp}")

    # Generar Figura 3
    fig3_path = os.path.join(RESULTS_DIR, "fig3_histogramas_distribucion_empirica_vs_teorica.png")
    graficar_fig3_histogramas_empirico_vs_teorico(df_comp, fig3_path, df_chi2=df_chi2)
    print(f"      -> Figura 3 generada a 300 DPI: {fig3_path}")

    # -------------------------------------------------------------------------
    # EXPERIMENTO 2: TEOREMA DEL LÍMITE CENTRAL Y DECAIMIENTO DE VARIANZA
    # -------------------------------------------------------------------------
    print("\n[2/4] Verificando Teorema del Límite Central (Curvas de Varianza y OLS)...")
    print("      N ∈ [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000] | 200 réplicas por N")
    t0 = time.time()
    n_lista_tlc = [20, 50, 100, 200, 500, 1_000, 2_000, 5_000, 10_000]
    df_tlc = simular_decaimiento_varianza_tlc(n_lista=n_lista_tlc, replicas=200, seed=123)
    csv_tlc = os.path.join(RESULTS_DIR, "decaimiento_varianza_tlc.csv")
    df_tlc.to_csv(csv_tlc, index=False)
    print(f"      -> Guardado CSV TLC: {csv_tlc} [{time.time() - t0:.2f}s]")

    fig2_path = os.path.join(RESULTS_DIR, "fig2_curvas_varianza_error_montecarlo.png")
    graficar_fig2_varianza_tlc(df_tlc, fig2_path)
    print(f"      -> Figura 2 generada a 300 DPI: {fig2_path}")

    # -------------------------------------------------------------------------
    # EXPERIMENTO 3: ESTABILIZACIÓN DEL VALOR ESPERADO (EV) EN MÁSCARAS
    # -------------------------------------------------------------------------
    print("\n[3/4] Analizando estabilización del Valor Esperado (EV) de las decisiones...")
    print("      Mano táctica: [3, 4, 4, 6, 1] | Casillas abiertas sin comodín 'libre'")
    t0 = time.time()
    sims_lista = [10, 25, 50, 100, 250, 500, 1_000, 2_500]
    categorias_libres_prueba = ["cuatros", "trio", "full", "escalera_larga", "yahtzee"]
    df_ev = simular_valor_esperado_mascaras(
        mano_actual=[3, 4, 4, 6, 1],
        categorias_libres=categorias_libres_prueba,
        sims_lista=sims_lista,
        replicas=100,
        seed=42,
    )
    csv_ev = os.path.join(RESULTS_DIR, "estabilizacion_ev_mascaras.csv")
    df_ev.to_csv(csv_ev, index=False)
    print(f"      -> Guardado CSV EV máscaras: {csv_ev} [{time.time() - t0:.2f}s]")

    fig4_path = os.path.join(RESULTS_DIR, "fig4_convergencia_valor_esperado_mascaras.png")
    graficar_fig4_estabilizacion_ev_mascaras(df_ev, fig4_path)
    print(f"      -> Figura 4 generada a 300 DPI: {fig4_path}")

    # -------------------------------------------------------------------------
    # EXPERIMENTO 4: CORRIDAS MASIVAS DE PARTIDAS COMPLETAS (BENCHMARKING)
    # -------------------------------------------------------------------------
    print("\n[4/4] Ejecutando torneo masivo vectorizado de 3,000 partidas completas...")
    print("      1,000 partidas: Agente Aleatorio (Control Ciego)")
    print("      1,000 partidas: Agente Heurístico Greedy")
    print("      1,000 partidas: Agente IA Monte Carlo (EV Estratégico, 100 sims/máscara)")
    t0 = time.time()
    df_partidas_detalle, df_partidas_resumen = ejecutar_corridas_masivas_estrategias(
        n_partidas_por_estrategia=1_000,
        sims_ev_montecarlo=100,
        seed=42,
    )
    csv_partidas = os.path.join(RESULTS_DIR, "comparativa_estrategias_partidas.csv")
    df_partidas_detalle.to_csv(csv_partidas, index=False)
    csv_resumen = os.path.join(RESULTS_DIR, "resumen_estadistico_estrategias.csv")
    df_partidas_resumen.to_csv(csv_resumen, index=False)
    print(f"      -> Guardado CSV detalle: {csv_partidas}")
    print(f"      -> Guardado CSV resumen: {csv_resumen} [{time.time() - t0:.2f}s]")

    # Generar Figuras 5 y 6
    fig5_path = os.path.join(RESULTS_DIR, "fig5_corridas_masivas_estrategias.png")
    graficar_fig5_corridas_masivas_estrategias(df_partidas_detalle, fig5_path)
    print(f"      -> Figura 5 generada a 300 DPI: {fig5_path}")

    fig6_path = os.path.join(RESULTS_DIR, "fig6_descomposicion_puntaje_categorias.png")
    graficar_fig6_descomposicion_categorias_bono(df_partidas_detalle, fig6_path)
    print(f"      -> Figura 6 generada a 300 DPI: {fig6_path}")

    # Resumen impreso en consola
    print("\n" + "=" * 78)
    print("  PRUEBAS DE BONDAD DE AJUSTE CHI-CUADRADO (χ²)")
    print("=" * 78)
    print(df_chi2.to_string(index=False))

    print("\n" + "=" * 78)
    print("  SÍNTESIS DE RESULTADOS EXPERIMENTALES (TORNEO DE 3,000 PARTIDAS)")
    print("=" * 78)
    cols_mostrar = [
        "Estrategia", "Partidas Simuladas", "Puntaje Medio", "Desv. Estándar",
        "Mediana", "Mínimo", "Máximo", "Tasa Bono (+35 pts)",
    ]
    print(df_partidas_resumen[cols_mostrar].to_string(index=False))

    duracion_total = time.time() - tiempo_inicio_total
    print("\n" + "=" * 78)
    print(f"  PIPELINE COMPLETADO CON ÉXITO EN {duracion_total:.2f} SEGUNDOS")
    print(f"  Todas las evidencias cuantitativas y gráficas están en '{RESULTS_DIR}'")
    print("=" * 78)


if __name__ == "__main__":
    main()
