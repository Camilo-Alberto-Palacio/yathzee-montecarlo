"""
=============================================================================
  GENERADOR DE VISUALIZACIONES CIENTÍFICAS A 300 DPI
=============================================================================
Genera las 6 figuras analíticas requeridas por la rúbrica y retroalimentación docente:
1. Gráfica de convergencia de frecuencias relativas (Ley de los Grandes Números).
2. Curvas logarítmicas de varianza y decaimiento del error estándar (TLC: O(1/sqrt(N))).
3. Histograma comparativo de distribución empírica vs probabilidad teórica exacta.
4. Estabilización del Valor Esperado (EV) de las máscaras de retención de dados.
5. Densidades y distribución de puntajes en corridas masivas de partidas completas.
6. Descomposición analítica de puntajes por categoría y tasa de obtención de bono.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Estilo tipográfico y visual para publicaciones académicas
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 12,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 14,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight"
})

# Paleta institucional
NAVY = "#1E3A8A"
TEAL = "#0F766E"
CORAL = "#DC2626"
GOLD = "#D97706"
PURPLE = "#7C3AED"
GRAY = "#64748B"
LIGHT_BG = "#F8FAFC"


def graficar_fig1_convergencia_lln(df_lln: pd.DataFrame, output_path: str) -> None:
    """
    Figura 1: Convergencia de Frecuencias Relativas hacia las Probabilidades Teóricas.
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 9), sharex=True)
    axes = axes.flatten()

    categorias = ["yahtzee", "poker", "full", "escalera_larga", "escalera_corta", "trio"]
    titulos = [
        "YAHTZEE (5 Iguales)", "Póker (4 Iguales)", "Full House (Trío + Par)",
        "Escalera Grande (5 consec.)", "Escalera Pequeña (4 consec.)", "Trío (3 Iguales)"
    ]
    colores = [CORAL, GOLD, TEAL, PURPLE, NAVY, "#059669"]

    for idx, (cat, titulo, color) in enumerate(zip(categorias, titulos, colores)):
        ax = axes[idx]
        sub = df_lln[df_lln["categoria"] == cat].sort_values("N")

        n_vals = sub["N"].values
        frec = sub["frecuencia_relativa"].values
        p_teor = sub["probabilidad_teorica"].iloc[0]
        ci_low = sub["ci_95_lower"].values
        ci_upp = sub["ci_95_upper"].values

        # Banda asintótica de confianza del 95%
        ax.fill_between(n_vals, ci_low, ci_upp, color=color, alpha=0.18, label="Banda IC 95% (TLC)")

        # Línea de probabilidad teórica
        ax.axhline(p_teor, color="black", linestyle="--", linewidth=1.5,
                   label=f"P Teórica = {p_teor:.6f}")

        # Frecuencia relativa empírica observada
        ax.plot(n_vals, frec, color=color, linewidth=2.0, marker="o", markersize=4,
                label=f"Frecuencia Relativa f_N")

        ax.set_xscale("log")
        ax.set_title(f"{titulo}", fontweight="bold", color="#0F172A", pad=8)
        ax.set_ylabel("Probabilidad / Frecuencia")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="best", framealpha=0.9)

        # Anotación del valor final en N=100k
        val_final = frec[-1]
        err_final = abs(val_final - p_teor)
        ax.text(0.97, 0.08, f"N=100k: {val_final:.6f}\nError: {err_final:.6f}",
                transform=ax.transAxes, ha="right", va="bottom",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=GRAY, alpha=0.85),
                fontsize=8)

    for i in range(3, 6):
        axes[i].set_xlabel("Número de Tiradas Simuladas N (Escala Logarítmica)")

    fig.suptitle("Comprobación Experimental de la Ley de los Grandes Números (LLN) en Yahtzee\n"
                 "Estabilización Estocástica de Frecuencias Relativas hacia las Probabilidades Teóricas Exactas (N = 10 a 100,000)",
                 fontweight="bold", color=NAVY, y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def graficar_fig2_varianza_tlc(df_tlc: pd.DataFrame, output_path: str) -> None:
    """
    Figura 2: Curvas de Decaimiento de Varianza y Error Estándar (Teorema del Límite Central).
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    n_vals = df_tlc["N"].values

    # Panel A: Desviación Estándar Empírica vs Teórica para Yahtzee
    ax1.plot(n_vals, df_tlc["std_teorica_yahtzee"], color="black", linestyle="--",
             linewidth=2.0, label=r"Teórico: $\sigma / \sqrt{N}$ (Pendiente -0.5)")
    ax1.scatter(n_vals, df_tlc["std_empirica_yahtzee"], color=CORAL, s=55, zorder=4,
                label="Empírico: DE entre 150 Réplicas MC")
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_title("A. Dispersión del Estimador Monte Carlo: YAHTZEE", fontweight="bold", color=NAVY)
    ax1.set_xlabel(r"Tamaño Muestral $N$ (Escala Logarítmica)")
    ax1.set_ylabel(r"Desviación Estándar del Estimador $\sigma(\bar{X}_N)$")
    ax1.grid(True, which="both", linestyle=":", alpha=0.6)
    ax1.legend(framealpha=0.9)

    # Panel B: Full House
    ax2.plot(n_vals, df_tlc["std_teorica_full"], color="black", linestyle="--",
             linewidth=2.0, label=r"Teórico: $\sigma / \sqrt{N}$ (Pendiente -0.5)")
    ax2.scatter(n_vals, df_tlc["std_empirica_full"], color=TEAL, s=55, zorder=4,
                label="Empírico: DE entre 150 Réplicas MC")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_title("B. Dispersión del Estimador Monte Carlo: FULL HOUSE", fontweight="bold", color=NAVY)
    ax2.set_xlabel(r"Tamaño Muestral $N$ (Escala Logarítmica)")
    ax2.set_ylabel(r"Desviación Estándar del Estimador $\sigma(\bar{X}_N)$")
    ax2.grid(True, which="both", linestyle=":", alpha=0.6)
    ax2.legend(framealpha=0.9)

    fig.suptitle("Comportamiento Asintótico del Error y Decaimiento de Varianza según el TLC\n"
                 r"Verificación Experimental de la Tasa de Convergencia $\mathcal{O}(1/\sqrt{N})$ en Muestreo Monte Carlo",
                 fontweight="bold", color=NAVY, y=1.02)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def graficar_fig3_histogramas_empirico_vs_teorico(
    df_comparativa: pd.DataFrame,
    output_path: str
) -> None:
    """
    Figura 3: Histograma y Diagrama de Barras Comparativo: Frecuencia Observada vs Probabilidad Teórica.
    """
    fig, ax = plt.subplots(figsize=(13, 6.5))

    categorias = df_comparativa["categoria_nombre"].tolist()
    p_teorica = (df_comparativa["probabilidad_teorica"] * 100).values
    f_empirica = (df_comparativa["frecuencia_empirica"] * 100).values

    x = np.arange(len(categorias))
    ancho = 0.38

    rects1 = ax.bar(x - ancho/2, p_teorica, ancho, label="Probabilidad Teórica Exacta (%)",
                    color=NAVY, alpha=0.88, edgecolor="black", linewidth=0.8)
    rects2 = ax.bar(x + ancho/2, f_empirica, ancho, label="Frecuencia Relativa Monte Carlo (%) [N=100,000]",
                    color=TEAL, alpha=0.88, edgecolor="black", linewidth=0.8)

    ax.set_ylabel("Probabilidad / Frecuencia Relativa (%)", fontweight="bold")
    ax.set_title("Validación Global del Modelo: Probabilidades Teóricas Exactas vs Frecuencias Relativas Empíricas\n"
                 "(100,000 Tiradas Iniciales Independientes)", fontweight="bold", color=NAVY, pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(categorias, rotation=35, ha="right", fontsize=9)
    ax.legend(framealpha=0.95, loc="upper right")
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)

    # Anotar error porcentual sobre las barras
    for i, rect in enumerate(rects2):
        err = abs(f_empirica[i] - p_teorica[i])
        ax.annotate(f"Δ={err:.2f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, rect.get_height()),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7.5, color="#1E293B",
                    fontweight="bold")

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def graficar_fig4_estabilizacion_ev_mascaras(
    df_ev_mascaras: pd.DataFrame,
    output_path: str
) -> None:
    """
    Figura 4: Estabilización del Valor Esperado (EV) de las Máscaras de Retención.
    """
    fig, ax = plt.subplots(figsize=(11, 6))

    estrategias = df_ev_mascaras["estrategia"].unique()
    colores = [TEAL, GOLD, NAVY, CORAL]
    marcadores = ["o", "s", "^", "D"]

    for est, color, m in zip(estrategias, colores, marcadores):
        sub = df_ev_mascaras[df_ev_mascaras["estrategia"] == est].sort_values("sims")
        sims = sub["sims"].values
        ev_mean = sub["ev_medio"].values
        ev_std = sub["ev_std"].values

        ax.plot(sims, ev_mean, label=est, color=color, linewidth=2.2, marker=m, markersize=5)
        ax.fill_between(sims, ev_mean - ev_std, ev_mean + ev_std, color=color, alpha=0.15)

    ax.set_xscale("log")
    ax.set_xlabel("Número de Simulaciones por Máscara (N)", fontweight="bold")
    ax.set_ylabel("Valor Esperado Estimado (EV en Puntos)", fontweight="bold")
    ax.set_title("Estabilización del Valor Esperado (EV) en la Decisión Óptima de Retención de Dados\n"
                 "Mano de Prueba: [3, 4, 4, 6, 1] — Disminución de la Varianza y Estabilidad del Rango",
                 fontweight="bold", color=NAVY, pad=12)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(framealpha=0.95, loc="center right")

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def graficar_fig5_corridas_masivas_estrategias(
    df_detalle_partidas: pd.DataFrame,
    output_path: str
) -> None:
    """
    Figura 5: Corridas Masivas de Partidas Completas (Distribución de Puntajes Totales).
    """
    fig, ax = plt.subplots(figsize=(12, 6.5))

    estrategias = ["aleatorio", "heuristico", "montecarlo"]
    nombres = ["Agente Aleatorio (Ciego)", "Agente Heurístico (Greedy Humano)", "Agente IA Monte Carlo (EV)"]
    colores = [GRAY, GOLD, NAVY]

    bins = np.linspace(40, 320, 55)

    for est, nombre, color in zip(estrategias, nombres, colores):
        sub = df_detalle_partidas[df_detalle_partidas["estrategia"] == est]["puntaje_total"]
        media = sub.mean()
        mediana = sub.median()

        ax.hist(sub, bins=bins, density=True, alpha=0.45, color=color,
                edgecolor="black", linewidth=0.6, label=f"{nombre} (Media = {media:.1f} pts)")
        ax.axvline(media, color=color, linestyle="--", linewidth=2.0)

    ax.set_xlabel("Puntaje Total Final de la Partida (13 Rondas)", fontweight="bold")
    ax.set_ylabel("Densidad de Probabilidad Empírica", fontweight="bold")
    ax.set_title("Simulación Masiva de Torneo: Comparación de Desempeño entre Estrategias\n"
                 "(1,000 Partidas Completas Simuladas por Cada Política de Decisión)",
                 fontweight="bold", color=NAVY, pad=12)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(framealpha=0.95, loc="upper right")

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def graficar_fig6_descomposicion_categorias_bono(
    df_detalle_partidas: pd.DataFrame,
    output_path: str
) -> None:
    """
    Figura 6: Descomposición de Puntaje Promedio por Categoría y Tasa de Bono.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={"width_ratios": [2.5, 1]})

    estrategias = ["aleatorio", "heuristico", "montecarlo"]
    nombres = ["Aleatorio", "Heurístico", "Monte Carlo"]
    colores = [GRAY, GOLD, NAVY]

    categorias_principales = [
        "cat_unos", "cat_doses", "cat_treses", "cat_cuatros", "cat_cincos", "cat_seises",
        "cat_trio", "cat_poker", "cat_full", "cat_escalera_corta", "cat_escalera_larga",
        "cat_yahtzee", "cat_libre"
    ]
    etiquetas = [
        "Unos", "Doses", "Treses", "Cuatros", "Cincos", "Seises",
        "Trío", "Póker", "Full", "Esc. Corta", "Esc. Larga", "Yahtzee", "Libre"
    ]

    x = np.arange(len(categorias_principales))
    ancho = 0.25

    for idx, (est, color, nom) in enumerate(zip(estrategias, colores, nombres)):
        sub = df_detalle_partidas[df_detalle_partidas["estrategia"] == est]
        promedios = [sub[col].mean() for col in categorias_principales]
        ax1.bar(x + (idx - 1)*ancho, promedios, ancho, label=nom, color=color, alpha=0.85,
                edgecolor="black", linewidth=0.6)

    ax1.set_ylabel("Puntaje Promedio Obtenido", fontweight="bold")
    ax1.set_title("A. Puntaje Medio por Casilla en la Tarjeta de Anotación", fontweight="bold", color=NAVY)
    ax1.set_xticks(x)
    ax1.set_xticklabels(etiquetas, rotation=35, ha="right", fontsize=9)
    ax1.legend(framealpha=0.95)
    ax1.grid(True, axis="y", linestyle=":", alpha=0.6)

    # Panel B: Tasa de Consecución de Bono Superior (+35 pts)
    tasas_bono = []
    for est in estrategias:
        sub = df_detalle_partidas[df_detalle_partidas["estrategia"] == est]
        tasas_bono.append(sub["bono_obtenido"].mean() * 100)

    rects = ax2.bar(nombres, tasas_bono, color=colores, alpha=0.85, edgecolor="black", linewidth=0.8)
    ax2.set_ylabel("Tasa de Obtención del Bono (%)", fontweight="bold")
    ax2.set_title("B. Eficiencia en Sección Superior\n(Bono +35 pts si suma ≥ 63)", fontweight="bold", color=NAVY)
    ax2.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax2.set_ylim(0, max(tasas_bono) * 1.25 if max(tasas_bono) > 0 else 100)

    for rect in rects:
        h = rect.get_height()
        ax2.annotate(f"{h:.1f}%",
                     xy=(rect.get_x() + rect.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points",
                     ha="center", va="bottom", fontweight="bold", fontsize=10)

    fig.suptitle("Análisis Detallado de Decisiones Estratégicas y Rendimiento por Sección",
                 fontweight="bold", color=NAVY, y=1.01)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
