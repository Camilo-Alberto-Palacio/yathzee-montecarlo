"""
=============================================================================
  GENERADOR DE VISUALIZACIONES CIENTÍFICAS A 300 DPI
=============================================================================
Genera las 6 figuras analíticas requeridas por la rúbrica y retroalimentación docente:
1. Gráfica de convergencia de frecuencias relativas (Ley de los Grandes Números)
   con distinción explícita entre Fase Transitoria (Calentamiento) y Estado Estable.
2. Curvas logarítmicas de varianza y decaimiento del error estándar (TLC: O(1/sqrt(N)))
   con ajuste de regresión lineal OLS log-log y coeficiente R².
3. Histograma comparativo de distribución empírica vs probabilidad teórica exacta
   sobre las 13 categorías reales y estadístico Chi-Cuadrado (χ²) de bondad de ajuste.
4. Estabilización del Valor Esperado (EV) de las máscaras de retención contrastada
   contra la esperanza matemática exacta y la tasa de inversión de rango.
5. Densidades KDE e histogramas completos de puntajes en corridas masivas (sin truncar).
6. Descomposición analítica de puntajes por categoría y tasa de obtención de bono superior.
"""

from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# Estilo tipográfico y visual para publicaciones académicas
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 11.5,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8.5,
    "figure.titlesize": 13.5,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

# Paleta institucional
NAVY = "#1E3A8A"
TEAL = "#0F766E"
CORAL = "#DC2626"
GOLD = "#D97706"
PURPLE = "#7C3AED"
EMERALD = "#059669"
GRAY = "#64748B"


def graficar_fig1_convergencia_lln(df_lln: pd.DataFrame, output_path: str) -> None:
    """
    Figura 1: Convergencia de Frecuencias Relativas hacia las Probabilidades Teóricas (LLN),
    resaltando la zona transitoria (calentamiento, N <= 200) frente a la estabilización.
    """
    fig, axes = plt.subplots(2, 3, figsize=(15.5, 9.2), sharex=True)
    axes = axes.flatten()

    categorias = ["yahtzee", "poker", "full", "escalera_larga", "escalera_corta", "trio"]
    titulos = [
        "YAHTZEE (5 Iguales)",
        "Póker (≥ 4 Iguales)",
        "Full House (Trío + Par)",
        "Escalera Grande (5 consec.)",
        "Escalera Pequeña (≥ 4 consec.)",
        "Trío (≥ 3 Iguales)",
    ]
    colores = [CORAL, GOLD, TEAL, PURPLE, NAVY, EMERALD]

    for idx, (cat, titulo, color) in enumerate(zip(categorias, titulos, colores)):
        ax = axes[idx]
        sub = df_lln[df_lln["categoria"] == cat].sort_values("N")

        n_vals = sub["N"].values
        frec = sub["frecuencia_relativa"].values
        p_teor = float(sub["probabilidad_teorica"].iloc[0])
        ci_low = sub["ci_95_lower"].values
        ci_upp = sub["ci_95_upper"].values

        # Zona transitoria (calentamiento N <= 200) vs Estado estable
        ax.axvspan(
            n_vals.min(),
            200,
            color="#FEF3C7",
            alpha=0.35,
            label="Fase Transitoria (N ≤ 200)" if idx == 0 else None,
        )

        # Banda asintótica de confianza del 95%
        ax.fill_between(n_vals, ci_low, ci_upp, color=color, alpha=0.18, label="Banda IC 95% (TLC)")

        # Línea de probabilidad teórica exacta
        ax.axhline(
            p_teor,
            color="#0F172A",
            linestyle="--",
            linewidth=1.5,
            label=f"P Teórica = {p_teor:.6f}",
        )

        # Frecuencia relativa empírica observada
        ax.plot(
            n_vals,
            frec,
            color=color,
            linewidth=2.0,
            marker="o",
            markersize=4,
            label=r"Frecuencia Relativa $f_N$",
        )

        ax.set_xscale("log")
        ax.set_title(titulo, fontweight="bold", color="#0F172A", pad=8)
        ax.set_ylabel("Probabilidad / Frecuencia")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper right", framealpha=0.92, fontsize=8)

        # Anotación del valor final en N=100k
        val_final = float(frec[-1])
        err_final = abs(val_final - p_teor)
        err_rel = (err_final / p_teor) * 100.0 if p_teor > 0 else 0.0
        ax.text(
            0.97,
            0.07,
            f"N=100k: {val_final:.6f}\n|Δ|: {err_final:.6f} ({err_rel:.2f}%)",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=GRAY, alpha=0.90),
            fontsize=7.8,
        )

    for i in range(3, 6):
        axes[i].set_xlabel("Número de Tiradas Simuladas N (Escala Logarítmica)")

    fig.suptitle(
        "Comprobación Experimental de la Ley de los Grandes Números (LLN) en Yahtzee\n"
        "Transición desde Fase Transitoria (Calentamiento) hacia Convergencia Asintótica (N = 10 a 100,000)",
        fontweight="bold",
        color=NAVY,
        y=0.98,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def graficar_fig2_varianza_tlc(df_tlc: pd.DataFrame, output_path: str) -> None:
    """
    Figura 2: Curvas de Decaimiento de Varianza y Error Estándar (Teorema del Límite Central)
    incluyendo pendiente empírica por Mínimos Cuadrados Ordinarios (OLS) y R².
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.5, 5.8))

    n_vals = df_tlc["N"].values.astype(float)
    replicas = int(df_tlc["replicas"].iloc[0]) if "replicas" in df_tlc.columns else 200

    # Panel A: Yahtzee
    m_y = float(df_tlc["pendiente_ols_yahtzee"].iloc[0])
    r2_y = float(df_tlc["r2_ols_yahtzee"].iloc[0])
    res_y = stats.linregress(np.log10(n_vals), np.log10(df_tlc["std_empirica_yahtzee"].values))
    ajuste_y = 10 ** (res_y.intercept + res_y.slope * np.log10(n_vals))

    ax1.plot(
        n_vals,
        df_tlc["std_teorica_yahtzee"],
        color="black",
        linestyle="--",
        linewidth=2.0,
        label=r"Teórico Exacto: $\sigma / \sqrt{N}$ ($m = -0.500$)",
    )
    ax1.plot(
        n_vals,
        ajuste_y,
        color=CORAL,
        linestyle="-",
        linewidth=1.5,
        alpha=0.8,
        label=f"Ajuste OLS Log-Log ($m = {m_y:.3f}, R^2 = {r2_y:.4f}$)",
    )
    ax1.scatter(
        n_vals,
        df_tlc["std_empirica_yahtzee"],
        color=CORAL,
        s=55,
        zorder=4,
        edgecolor="white",
        linewidth=0.7,
        label=f"Empírico ({replicas} Réplicas MC)",
    )
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_title("A. Dispersión del Estimador Monte Carlo: YAHTZEE", fontweight="bold", color=NAVY)
    ax1.set_xlabel(r"Tamaño Muestral $N$ (Escala Logarítmica)")
    ax1.set_ylabel(r"Error Estándar del Estimador $\sigma(\bar{X}_N)$")
    ax1.grid(True, which="both", linestyle=":", alpha=0.6)
    ax1.legend(framealpha=0.92)

    # Panel B: Full House
    m_f = float(df_tlc["pendiente_ols_full"].iloc[0])
    r2_f = float(df_tlc["r2_ols_full"].iloc[0])
    res_f = stats.linregress(np.log10(n_vals), np.log10(df_tlc["std_empirica_full"].values))
    ajuste_f = 10 ** (res_f.intercept + res_f.slope * np.log10(n_vals))

    ax2.plot(
        n_vals,
        df_tlc["std_teorica_full"],
        color="black",
        linestyle="--",
        linewidth=2.0,
        label=r"Teórico Exacto: $\sigma / \sqrt{N}$ ($m = -0.500$)",
    )
    ax2.plot(
        n_vals,
        ajuste_f,
        color=TEAL,
        linestyle="-",
        linewidth=1.5,
        alpha=0.8,
        label=f"Ajuste OLS Log-Log ($m = {m_f:.3f}, R^2 = {r2_f:.4f}$)",
    )
    ax2.scatter(
        n_vals,
        df_tlc["std_empirica_full"],
        color=TEAL,
        s=55,
        zorder=4,
        edgecolor="white",
        linewidth=0.7,
        label=f"Empírico ({replicas} Réplicas MC)",
    )
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_title("B. Dispersión del Estimador Monte Carlo: FULL HOUSE", fontweight="bold", color=NAVY)
    ax2.set_xlabel(r"Tamaño Muestral $N$ (Escala Logarítmica)")
    ax2.set_ylabel(r"Error Estándar del Estimador $\sigma(\bar{X}_N)$")
    ax2.grid(True, which="both", linestyle=":", alpha=0.6)
    ax2.legend(framealpha=0.92)

    fig.suptitle(
        "Comportamiento Asintótico del Error y Decaimiento de Varianza según el TLC\n"
        r"Verificación Experimental de la Tasa de Convergencia $\mathcal{O}(1/\sqrt{N})$ en Muestreo Monte Carlo",
        fontweight="bold",
        color=NAVY,
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def graficar_fig3_histogramas_empirico_vs_teorico(
    df_comparativa: pd.DataFrame,
    output_path: str,
    df_chi2: Optional[pd.DataFrame] = None,
) -> None:
    """
    Figura 3: Diagrama de Barras Comparativo sobre las 13 Categorías Reales:
    Frecuencia Observada Monte Carlo (N=100,000) vs Probabilidad Teórica Exacta de Laplace.
    Sin superposición de leyenda y con reporte de bondad de ajuste Chi-Cuadrado.
    """
    fig, ax = plt.subplots(figsize=(14, 6.8))

    categorias = df_comparativa["categoria_nombre"].tolist()
    p_teorica = (df_comparativa["probabilidad_teorica"] * 100.0).values
    f_empirica = (df_comparativa["frecuencia_empirica"] * 100.0).values

    x = np.arange(len(categorias))
    ancho = 0.38

    ax.bar(
        x - ancho / 2,
        p_teorica,
        ancho,
        label="Probabilidad Teórica Exacta de Laplace (%)",
        color=NAVY,
        alpha=0.88,
        edgecolor="black",
        linewidth=0.7,
    )
    rects2 = ax.bar(
        x + ancho / 2,
        f_empirica,
        ancho,
        label="Frecuencia Relativa Monte Carlo (%) [N = 100,000]",
        color=TEAL,
        alpha=0.88,
        edgecolor="black",
        linewidth=0.7,
    )

    ax.set_ylabel("Probabilidad / Frecuencia Relativa (%)", fontweight="bold")
    ax.set_title(
        "Validación Global del Modelo: Probabilidades Teóricas Exactas vs Frecuencias Empíricas\n"
        "(100,000 Tiradas Iniciales Independientes Simuladas sobre las 13 Categorías)",
        fontweight="bold",
        color=NAVY,
        pad=12,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(categorias, rotation=32, ha="right", fontsize=9)
    ax.set_ylim(0, 114)
    ax.legend(framealpha=0.95, loc="upper left")
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)

    # Anotar discrepancia absoluta en puntos porcentuales sobre cada par de barras
    for i, rect in enumerate(rects2):
        err = abs(f_empirica[i] - p_teorica[i])
        y_top = max(p_teorica[i], f_empirica[i])
        etiqueta_err = f"Δ={err:.3f}%" if (0 < err < 0.01) else f"Δ={err:.2f}%"
        ax.annotate(
            etiqueta_err,
            xy=(x[i], y_top),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=7.6,
            color="#0F172A",
            fontweight="bold",
        )

    if df_chi2 is not None and not df_chi2.empty:
        r_unif = df_chi2.iloc[0]
        r_part = df_chi2.iloc[1]
        texto_chi = (
            f"Pruebas de Bondad de Ajuste $\\chi^2$ (N=100,000):\n"
            f"• Uniformidad Dados: $\\chi^2={r_unif['estadistico_chi2']:.2f}$ ($p={r_unif['p_valor']:.3f}$)\n"
            f"• Partición de $\\Omega$: $\\chi^2={r_part['estadistico_chi2']:.2f}$ ($p={r_part['p_valor']:.3f}$)"
        )
        ax.text(
            0.015,
            0.74,
            texto_chi,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#F8FAFC", edgecolor=NAVY, alpha=0.92),
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def graficar_fig4_estabilizacion_ev_mascaras(
    df_ev_mascaras: pd.DataFrame,
    output_path: str,
) -> None:
    """
    Figura 4: Estabilización del Valor Esperado (EV) de las Máscaras de Retención
    frente a su esperanza analítica exacta y reducción de inversiones de rango.
    """
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(14.5, 5.8), gridspec_kw={"width_ratios": [2.1, 1.0]}
    )

    estrategias = list(df_ev_mascaras["estrategia"].unique())
    colores = [TEAL, GOLD, PURPLE, CORAL, NAVY]
    marcadores = ["o", "s", "^", "D", "v"]

    for est, color, m in zip(estrategias, colores, marcadores):
        sub = df_ev_mascaras[df_ev_mascaras["estrategia"] == est].sort_values("sims")
        sims = sub["sims"].values
        ev_mean = sub["ev_medio"].values
        ev_std = sub["ev_std"].values
        ev_ex = float(sub["ev_exacto"].iloc[0])

        ax1.axhline(ev_ex, color=color, linestyle=":", linewidth=1.2, alpha=0.75)
        ax1.plot(
            sims,
            ev_mean,
            label=f"{est} (EV exacto = {ev_ex:.2f})",
            color=color,
            linewidth=2.1,
            marker=m,
            markersize=5,
        )
        ax1.fill_between(sims, ev_mean - ev_std, ev_mean + ev_std, color=color, alpha=0.14)

    ax1.set_xscale("log")
    ax1.set_ylim(5.0, 17.6)
    ax1.set_xlabel("Simulaciones por Máscara (N)", fontweight="bold")
    ax1.set_ylabel("Valor Esperado Estimado (EV en Puntos)", fontweight="bold")
    ax1.set_title(
        "A. Convergencia del EV por Política de Retención (Mano: [3, 4, 4, 6, 1])",
        fontweight="bold",
        color=NAVY,
    )
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend(framealpha=0.95, loc="upper right", fontsize=8)

    # Panel B: Tasa de Decisión Óptima / Eliminación de Inversión de Rango
    sub_opt = (
        df_ev_mascaras[df_ev_mascaras["es_optima_teorica"] == True]
        .sort_values("sims")
    )
    sims_vals = sub_opt["sims"].values
    tasa_exito = sub_opt["tasa_decision_optima_pct"].values

    ax2.plot(
        sims_vals,
        tasa_exito,
        color=NAVY,
        linewidth=2.3,
        marker="o",
        markersize=6,
        label="Frecuencia de Elección Óptima (%)",
    )
    ax2.axvline(250, color=CORAL, linestyle="--", linewidth=1.5, label="Umbral Operativo N = 250")
    ax2.set_xscale("log")
    ax2.set_ylim(max(0.0, float(tasa_exito.min()) - 10.0), 103.0)
    ax2.set_xlabel("Simulaciones por Máscara (N)", fontweight="bold")
    ax2.set_ylabel("Precisión en la Decisión Óptima (%)", fontweight="bold")
    ax2.set_title(
        "B. Eliminación del Error por Ruido Muestral",
        fontweight="bold",
        color=NAVY,
    )
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend(framealpha=0.94, loc="lower right", fontsize=8.2)

    fig.suptitle(
        "Estabilización del Valor Esperado (EV) en la Toma Óptima de Decisiones de Retención\n"
        "Casillas Abiertas: {Cuatros, Trío, Full House, Escalera Grande, Yahtzee} — 100 Réplicas por Nivel N",
        fontweight="bold",
        color=NAVY,
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def graficar_fig5_corridas_masivas_estrategias(
    df_detalle_partidas: pd.DataFrame,
    output_path: str,
) -> None:
    """
    Figura 5: Corridas Masivas de Partidas Completas (Distribución de Puntajes Totales)
    cubriendo el rango completo [0, max + 15] sin truncamiento e incluyendo curvas KDE.
    """
    fig, ax = plt.subplots(figsize=(12.5, 6.5))

    estrategias = ["aleatorio", "heuristico", "montecarlo"]
    nombres = [
        "Agente Aleatorio (Control Ciego)",
        "Agente Heurístico (Greedy Humano)",
        "Agente IA Monte Carlo (EV Estratégico)",
    ]
    colores = [GRAY, GOLD, NAVY]

    puntaje_max_global = float(df_detalle_partidas["puntaje_total"].max())
    limite_sup = max(340.0, puntaje_max_global + 15.0)
    bins = np.linspace(0.0, limite_sup, 62)
    x_grid = np.linspace(0.0, limite_sup, 400)

    for est, nombre, color in zip(estrategias, nombres, colores):
        sub = df_detalle_partidas[df_detalle_partidas["estrategia"] == est]["puntaje_total"].values
        media = float(np.mean(sub))
        std = float(np.std(sub, ddof=1))

        ax.hist(
            sub,
            bins=bins,
            density=True,
            alpha=0.38,
            color=color,
            edgecolor="black",
            linewidth=0.5,
            label=f"{nombre} (Media = {media:.1f} ± {std:.1f} pts)",
        )
        kde = stats.gaussian_kde(sub)
        ax.plot(x_grid, kde(x_grid), color=color, linewidth=2.2)
        ax.axvline(media, color=color, linestyle="--", linewidth=1.8)

    ax.set_xlim(0.0, limite_sup)
    ax.set_xlabel("Puntaje Total Final de la Partida (13 Rondas Oficiales)", fontweight="bold")
    ax.set_ylabel("Densidad de Probabilidad Empírica", fontweight="bold")
    ax.set_title(
        "Simulación Masiva de Torneo: Comparación de Desempeño entre Políticas de Decisión\n"
        "(3,000 Partidas Completas Simuladas — 1,000 Juegos de 13 Rondas por Agente)",
        fontweight="bold",
        color=NAVY,
        pad=12,
    )
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(framealpha=0.95, loc="upper right")

    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def graficar_fig6_descomposicion_categorias_bono(
    df_detalle_partidas: pd.DataFrame,
    output_path: str,
) -> None:
    """
    Figura 6: Descomposición de Puntaje Promedio por Categoría y Tasa de Bono Superior.
    """
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(15, 6.2), gridspec_kw={"width_ratios": [2.5, 1.0]}
    )

    estrategias = ["aleatorio", "heuristico", "montecarlo"]
    nombres = ["Aleatorio", "Heurístico", "IA Monte Carlo"]
    colores = [GRAY, GOLD, NAVY]

    categorias_principales = [
        "cat_unos", "cat_doses", "cat_treses", "cat_cuatros", "cat_cincos", "cat_seises",
        "cat_trio", "cat_poker", "cat_full", "cat_escalera_corta", "cat_escalera_larga",
        "cat_yahtzee", "cat_libre",
    ]
    etiquetas = [
        "Unos", "Doses", "Treses", "Cuatros", "Cincos", "Seises",
        "Trío", "Póker", "Full", "Esc. Corta", "Esc. Larga", "Yahtzee", "Libre",
    ]

    x = np.arange(len(categorias_principales))
    ancho = 0.26

    for idx, (est, color, nom) in enumerate(zip(estrategias, colores, nombres)):
        sub = df_detalle_partidas[df_detalle_partidas["estrategia"] == est]
        promedios = [float(sub[col].mean()) for col in categorias_principales]
        ax1.bar(
            x + (idx - 1) * ancho,
            promedios,
            ancho,
            label=nom,
            color=color,
            alpha=0.88,
            edgecolor="black",
            linewidth=0.6,
        )

    ax1.set_ylabel("Puntaje Promedio Obtenido (Puntos)", fontweight="bold")
    ax1.set_title("A. Puntaje Medio por Casilla en la Tarjeta de Anotación", fontweight="bold", color=NAVY)
    ax1.set_xticks(x)
    ax1.set_xticklabels(etiquetas, rotation=32, ha="right", fontsize=9)
    ax1.legend(framealpha=0.95, loc="upper left")
    ax1.grid(True, axis="y", linestyle=":", alpha=0.6)

    # Panel B: Tasa de Consecución de Bono Superior (+35 pts)
    tasas_bono = []
    for est in estrategias:
        sub = df_detalle_partidas[df_detalle_partidas["estrategia"] == est]
        tasas_bono.append(float(sub["bono_obtenido"].mean() * 100.0))

    rects = ax2.bar(nombres, tasas_bono, color=colores, alpha=0.88, edgecolor="black", linewidth=0.8)
    ax2.set_ylabel("Tasa de Obtención del Bono (%)", fontweight="bold")
    ax2.set_title(
        "B. Eficiencia en Sección Superior\n(Bono +35 pts si suma ≥ 63)",
        fontweight="bold",
        color=NAVY,
    )
    ax2.grid(True, axis="y", linestyle=":", alpha=0.6)
    ax2.set_ylim(0, max(tasas_bono) * 1.25 if max(tasas_bono) > 0 else 100)

    for rect in rects:
        h = rect.get_height()
        ax2.annotate(
            f"{h:.1f}%",
            xy=(rect.get_x() + rect.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=10,
        )

    fig.suptitle(
        "Análisis Detallado de Decisiones Estratégicas y Rendimiento por Sección (3,000 Partidas)",
        fontweight="bold",
        color=NAVY,
        y=1.01,
    )
    fig.tight_layout()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
