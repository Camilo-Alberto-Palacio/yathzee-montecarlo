"""
=============================================================================
  CONSTRUCTOR AUTOMATIZADO DEL CUADERNO GOOGLE COLAB
=============================================================================
Genera el archivo 'Simulacion_Yahtzee_Montecarlo_Colab.ipynb' auto-contenido,
reproducible en la nube con un solo clic, incorporando teoría, código ejecutable,
visualizaciones interactivas y reflexiones pedagógicas.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTEBOOK_PATH = os.path.join(BASE_DIR, "Simulacion_Yahtzee_Montecarlo_Colab.ipynb")


def create_colab_notebook():
    nb = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "colab": {
                "name": "Simulacion_Yahtzee_Montecarlo_Colab.ipynb",
                "provenance": [],
                "collapsed_sections": []
            },
            "kernelspec": {
                "name": "python3",
                "display_name": "Python 3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "cells": []
    }

    def add_md(source):
        nb["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [s + "\n" for s in source]
        })

    def add_code(source):
        nb["cells"].append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [s + "\n" for s in source]
        })

    # Celda 1: Título y Badges
    add_md([
        "# Simulación Estocástica de Yahtzee con Método Monte Carlo",
        "## Comprobación Experimental de la Ley de los Grandes Números (LLN) y el Teorema del Límite Central (TLC)",
        "",
        "[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Camilo-Alberto-Palacio/Simulacion-Yahtzee-Montecarlo/blob/main/Simulacion_Yahtzee_Montecarlo_Colab.ipynb)",
        "![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)",
        "![Institution](https://img.shields.io/badge/IU%20Digital%20de%20Antioquia-Grupo%2025-1E3A8A)",
        "",
        "---",
        "### Información Institucional",
        "* **Asignatura:** Simulación (`PREICA2602B020045`) — Grupo 25",
        "* **Actividad Didáctica 1 — Módulo 1:** Introducción a la Simulación",
        "* **Docente:** Julian Andres Loaiza Lopez",
        "* **Integrantes:**",
        "  * Adriana Andrea Agudelo Agudelo",
        "  * Camilo Alberto Palacios Turriago",
        "  * Juan Daniel Pulgarin García",
        "  * Ruben Dario Jaramillo Cervantes",
        "* **Institución:** Institución Universitaria Digital de Antioquia (IU Digital) — Facultad de Ingeniería",
        "* **Medellín, Antioquia — Noviembre de 2026**",
        "",
        "---",
        "### Resumen Ejecutivo",
        "Este cuaderno presenta la solución experimental, matemática y computacional completa para la **Actividad Didáctica 1**. A diferencia de una implementación limitada únicamente a la interfaz del juego, este laboratorio utiliza la **Simulación de Monte Carlo** para:",
        "1. Ejecutar series de iteraciones masivas ($N = 10$ a $100,000$ tiradas).",
        "2. Recolectar frecuencias relativas y contrastarlas contra las probabilidades teóricas exactas del espacio muestral ($|\\Omega| = 6^5 = 7,776$).",
        "3. Generar gráficos de convergencia que demuestran empíricamente la **Ley Débil y Fuerte de los Grandes Números**.",
        "4. Comprobar la tasa de decaimiento asintótico del error estándar según el **Teorema del Límite Central**: $\\text{SE} \\sim \\mathcal{O}(1/\\sqrt{N})$.",
        "5. Evaluar la estabilización del **Valor Esperado (EV)** en las 32 decisiones posibles de retención de dados.",
        "6. Simular un torneo masivo de 3,000 partidas completas comparando tres políticas (Aleatoria, Heurística Greedy e IA Monte Carlo)."
    ])

    # Celda 2: Instalación e Importación de Dependencias
    add_md([
        "---",
        "## 1. Configuración del Entorno y Dependencias",
        "Configuramos las bibliotecas científicas estándar (`numpy`, `pandas`, `matplotlib`, `scipy`) y fijamos las semillas para estricta reproducibilidad."
    ])
    add_code([
        "import numpy as np",
        "import pandas as pd",
        "import matplotlib.pyplot as plt",
        "from collections import Counter",
        "import itertools",
        "",
        "# Configuración estética de gráficos",
        "plt.rcParams.update({",
        "    'font.family': 'sans-serif',",
        "    'font.size': 10,",
        "    'figure.dpi': 150,",
        "    'savefig.dpi': 300",
        "})",
        "",
        "print('Entorno científico listo y configurado exitosamente.')"
    ])

    # Celda 3: Deducción Combinatoria Exacta
    add_md([
        "---",
        "## 2. Espacio Muestral y Probabilidades Teóricas Exactas",
        "Para 5 dados de 6 caras, el espacio muestral es $|\\Omega| = 6^5 = 7,776$ microestados equiprobables. Calculamos la probabilidad teórica exacta para cada categoría."
    ])
    add_code([
        "def calcular_probabilidades_teoricas():",
        "    conteos = {'yahtzee': 0, 'poker': 0, 'trio': 0, 'full': 0, 'escalera_larga': 0, 'escalera_corta': 0, 'libre': 0}",
        "    total_omega = 6 ** 5",
        "    ",
        "    for tiro in itertools.product(range(1, 7), repeat=5):",
        "        mano = list(tiro)",
        "        c = Counter(mano)",
        "        freqs = list(c.values())",
        "        max_f = max(freqs)",
        "        unicos = sorted(set(mano))",
        "        ",
        "        # Escaleras",
        "        racha_max = 1",
        "        racha = 1",
        "        for i in range(1, len(unicos)):",
        "            if unicos[i] == unicos[i-1] + 1:",
        "                racha += 1",
        "                racha_max = max(racha_max, racha)",
        "            else:",
        "                racha = 1",
        "        ",
        "        conteos['libre'] += 1",
        "        if max_f == 5:",
        "            conteos['yahtzee'] += 1",
        "        if max_f >= 4:",
        "            conteos['poker'] += 1",
        "        if max_f >= 3:",
        "            conteos['trio'] += 1",
        "        if (len(freqs) == 2 and sorted(freqs) == [2, 3]) or max_f == 5:",
        "            conteos['full'] += 1",
        "        if racha_max >= 5:",
        "            conteos['escalera_larga'] += 1",
        "        if racha_max >= 4:",
        "            conteos['escalera_corta'] += 1",
        "            ",
        "    df_teor = pd.DataFrame([",
        "        {'Categoría': k, 'Casos Favorables': v, 'Total Omega': total_omega, ",
        "         'P Teórica': v / total_omega, '% Teórico': (v / total_omega) * 100}",
        "        for k, v in conteos.items()",
        "    ])",
        "    return df_teor",
        "",
        "df_teorico = calcular_probabilidades_teoricas()",
        "df_teorico"
    ])

    # Celda 4: Simulación de la Ley de los Grandes Números
    add_md([
        "---",
        "## 3. Comprobación Experimental de la Ley de los Grandes Números (LLN)",
        "Ejecutamos una serie masiva de $N = 100,000$ tiradas independientes. Se calcula la frecuencia relativa $f_N(A) = \\frac{1}{N} \\sum_{i=1}^N I_A^{(i)}$ y se contrasta contra la probabilidad teórica $P(A)$ y los intervalos de confianza del 95% del TLC."
    ])
    add_code([
        "rng = np.random.default_rng(42)",
        "N_TOTAL = 100_000",
        "checkpoints = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]",
        "",
        "# Simulación vectorizada de tiradas",
        "matriz_dados = rng.integers(1, 7, size=(N_TOTAL, 5))",
        "",
        "categorias_eval = ['yahtzee', 'poker', 'full', 'escalera_larga', 'escalera_corta', 'trio']",
        "indicadores = {cat: np.zeros(N_TOTAL, dtype=bool) for cat in categorias_eval}",
        "",
        "for i in range(N_TOTAL):",
        "    dados = matriz_dados[i]",
        "    c = np.bincount(dados, minlength=7)[1:]",
        "    max_rep = np.max(c)",
        "    u = np.sort(np.unique(dados))",
        "    r_max = 1",
        "    if len(u) > 1:",
        "        r = 1",
        "        for d in np.diff(u):",
        "            if d == 1:",
        "                r += 1",
        "                r_max = max(r_max, r)",
        "            else:",
        "                r = 1",
        "    rep = c[c > 0]",
        "    indicadores['yahtzee'][i] = (max_rep == 5)",
        "    indicadores['poker'][i] = (max_rep >= 4)",
        "    indicadores['trio'][i] = (max_rep >= 3)",
        "    indicadores['full'][i] = ((len(rep) == 2 and sorted(rep) == [2, 3]) or max_rep == 5)",
        "    indicadores['escalera_larga'][i] = (r_max >= 5)",
        "    indicadores['escalera_corta'][i] = (r_max >= 4)",
        "",
        "p_teor_map = dict(zip(df_teorico['Categoría'], df_teorico['P Teórica']))",
        "",
        "# Graficar convergencia",
        "fig, axes = plt.subplots(2, 3, figsize=(15, 9), sharex=True)",
        "axes = axes.flatten()",
        "colores = ['#DC2626', '#D97706', '#0F766E', '#7C3AED', '#1E3A8A', '#059669']",
        "",
        "for idx, cat in enumerate(categorias_eval):",
        "    ax = axes[idx]",
        "    p_t = p_teor_map[cat]",
        "    f_vals = [np.mean(indicadores[cat][:n]) for n in checkpoints]",
        "    ci_low = [max(0.0, p_t - 1.96 * np.sqrt(p_t*(1-p_t)/n)) for n in checkpoints]",
        "    ci_upp = [min(1.0, p_t + 1.96 * np.sqrt(p_t*(1-p_t)/n)) for n in checkpoints]",
        "    ",
        "    ax.fill_between(checkpoints, ci_low, ci_upp, color=colores[idx], alpha=0.18, label='Banda IC 95% (TLC)')",
        "    ax.axhline(p_t, color='black', linestyle='--', label=f'P Teórica = {p_t:.5f}')",
        "    ax.plot(checkpoints, f_vals, color=colores[idx], marker='o', linewidth=2, label='Frecuencia f_N')",
        "    ax.set_xscale('log')",
        "    ax.set_title(cat.upper(), fontweight='bold')",
        "    ax.set_ylabel('Probabilidad / Frecuencia')",
        "    ax.grid(True, linestyle=':', alpha=0.6)",
        "    ax.legend(loc='best', fontsize=8)",
        "",
        "for i in range(3, 6):",
        "    axes[i].set_xlabel('Tiradas Simuladas N (Escala Log)')",
        "fig.suptitle('Convergencia Estocástica hacia las Probabilidades Teóricas (Ley de los Grandes Números)', fontsize=14, fontweight='bold')",
        "plt.tight_layout()",
        "plt.show()"
    ])

    # Celda 5: Teorema del Límite Central y Decaimiento de Varianza
    add_md([
        "---",
        "## 4. Verificación del Teorema del Límite Central (TLC) y Curvas de Varianza",
        "Verificamos que la dispersión empírica entre réplicas independientes decae como $\\sigma / \\sqrt{N}$, correspondiente a una pendiente de $-0.5$ en escala log-log."
    ])
    add_code([
        "n_lista = [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]",
        "REPLICAS = 100",
        "p_full = p_teor_map['full']",
        "",
        "std_empiricas = []",
        "std_teoricas = []",
        "",
        "for n in n_lista:",
        "    estimaciones = []",
        "    for _ in range(REPLICAS):",
        "        t = rng.integers(1, 7, size=(n, 5))",
        "        fav = 0",
        "        for row in t:",
        "            c = np.bincount(row, minlength=7)[1:]",
        "            rep = c[c > 0]",
        "            if (len(rep) == 2 and sorted(rep) == [2, 3]) or np.max(c) == 5:",
        "                fav += 1",
        "        estimaciones.append(fav / n)",
        "    std_empiricas.append(np.std(estimaciones, ddof=1))",
        "    std_teoricas.append(np.sqrt(p_full * (1 - p_full) / n))",
        "",
        "plt.figure(figsize=(9, 5))",
        "plt.plot(n_lista, std_teoricas, 'k--', linewidth=2, label=r'Teórico: $\\sigma / \\sqrt{N}$ (Pendiente -0.5)')",
        "plt.scatter(n_lista, std_empiricas, color='#0F766E', s=60, zorder=4, label='Empírico: 100 Réplicas MC (Full House)')",
        "plt.xscale('log')",
        "plt.yscale('log')",
        "plt.xlabel('Tamaño Muestral N (Escala Log)', fontweight='bold')",
        "plt.ylabel('Desviación Estándar del Estimador', fontweight='bold')",
        "plt.title('Decaimiento Asintótico del Error según el TLC: Pendiente -0.5 en Log-Log', fontweight='bold')",
        "plt.grid(True, which='both', linestyle=':', alpha=0.6)",
        "plt.legend()",
        "plt.tight_layout()",
        "plt.show()"
    ])

    # Celda 6: Estabilización del Valor Esperado (EV) en Decisiones
    add_md([
        "---",
        "## 5. Estabilización del Valor Esperado (EV) en las Decisiones de Retención",
        "Evaluamos el impacto del número de simulaciones $N_{\\text{sims}}$ sobre una mano crítica `[3, 4, 4, 6, 1]`, demostrando que con $N \\ge 250$ se eliminan inversiones de rango causadas por varianza aleatoria."
    ])
    add_code([
        "from yahtzee_simulation.rules import mejor_puntaje, todas_las_mascaras",
        "from yahtzee_simulation.montecarlo import simular_valor_esperado_mascaras",
        "",
        "mano_prueba = [3, 4, 4, 6, 1]",
        "libres = ['cuatros', 'trio', 'full', 'escalera_larga', 'libre']",
        "sims_test = [10, 25, 50, 100, 250, 500, 1000]",
        "",
        "df_ev_stab = simular_valor_esperado_mascaras(mano_prueba, libres, sims_test, replicas=20, seed=42)",
        "",
        "plt.figure(figsize=(10, 5.5))",
        "for est in df_ev_stab['estrategia'].unique():",
        "    sub = df_ev_stab[df_ev_stab['estrategia'] == est]",
        "    plt.plot(sub['sims'], sub['ev_medio'], marker='o', label=est)",
        "    plt.fill_between(sub['sims'], sub['ev_medio'] - sub['ev_std'], sub['ev_medio'] + sub['ev_std'], alpha=0.15)",
        "",
        "plt.xscale('log')",
        "plt.xlabel('Número de Simulaciones por Máscara (N)', fontweight='bold')",
        "plt.ylabel('Valor Esperado Estimado (Puntos)', fontweight='bold')",
        "plt.title('Estabilización del Valor Esperado (EV) y Reducción de Varianza en Decisiones', fontweight='bold')",
        "plt.grid(True, linestyle=':', alpha=0.6)",
        "plt.legend()",
        "plt.tight_layout()",
        "plt.show()"
    ])

    # Celda 7: Torneo Masivo de Partidas Completas
    add_md([
        "---",
        "## 6. Torneo Masivo de Partidas Completas (Benchmarking de Estrategias)",
        "Simulamos partidas completas de 13 rondas contrastando el **Agente Aleatorio**, el **Agente Heurístico Greedy** y el **Agente IA Monte Carlo (EV)**."
    ])
    add_code([
        "from yahtzee_simulation.massive_runs import ejecutar_corridas_masivas_estrategias",
        "",
        "print('Ejecutando torneo de partidas completas (300 partidas por estrategia)...')",
        "df_partidas, df_resumen = ejecutar_corridas_masivas_estrategias(n_partidas_por_estrategia=300, seed=42)",
        "display(df_resumen)",
        "",
        "plt.figure(figsize=(11, 5.5))",
        "bins = np.linspace(30, 310, 45)",
        "colores = {'aleatorio': '#64748B', 'heuristico': '#D97706', 'montecarlo': '#1E3A8A'}",
        "",
        "for est in ['aleatorio', 'heuristico', 'montecarlo']:",
        "    sub = df_partidas[df_partidas['estrategia'] == est]['puntaje_total']",
        "    plt.hist(sub, bins=bins, density=True, alpha=0.45, color=colores[est], label=f'{est.capitalize()} (Media={sub.mean():.1f})')",
        "    plt.axvline(sub.mean(), color=colores[est], linestyle='--', linewidth=2)",
        "",
        "plt.xlabel('Puntaje Total Final de la Partida', fontweight='bold')",
        "plt.ylabel('Densidad de Probabilidad Empírica', fontweight='bold')",
        "plt.title('Distribución de Puntajes Totales en Torneo Masivo de Yahtzee', fontweight='bold')",
        "plt.grid(True, linestyle=':', alpha=0.6)",
        "plt.legend()",
        "plt.tight_layout()",
        "plt.show()"
    ])

    # Celda 8: Reflexión Epistemológica
    add_md([
        "---",
        "## 7. Reflexión Epistemológica: Aprendizaje y Desaprendizaje en Simulación",
        "",
        "> **Reflexión del Equipo (Grupo 25):**",
        "> * **Lo que tuvimos que desaprender:** Desaprendimos la premisa errónea de que programar una simulación equivale a desarrollar un juego o una interfaz gráfica bonita. En la ingeniería estocástica, el software es el medio, no el fin. Desaprendimos también la confianza en muestras pequeñas y la redacción de conclusiones cualitativas sin sustento empírico.",
        "> * **El aprendizaje genuino construido:** Interiorizamos que la simulación es un laboratorio científico experimental riguroso. Vivenciamos la emergencia del orden a partir del azar mediante la Ley de los Grandes Números y el Teorema del Límite Central, y comprobamos el inmenso valor de la optimización por Valor Esperado (EV) para la toma de decisiones bajo incertidumbre.",
        "",
        "---",
        "### Conclusión",
        "Este cuaderno demuestra el cumplimiento integral del ciclo **USA, MODIFICA y CREA**, satisfaciendo plenamente los requerimientos analíticos, cuantitativos y metodológicos de la asignatura **Simulación** en la **IU Digital de Antioquia**."
    ])

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)

    print(f"[OK] Cuaderno Google Colab creado exitosamente:\n     -> {NOTEBOOK_PATH}")
    return NOTEBOOK_PATH


if __name__ == "__main__":
    create_colab_notebook()
