# Simulación Estocástica de Yahtzee con Método Monte Carlo y Ley de los Grandes Números

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Camilo-Alberto-Palacio/yathzee-montecarlo/blob/main/Simulacion_Yahtzee_Montecarlo_Colab.ipynb)
![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Tests](https://img.shields.io/badge/Tests-12%2F12%20Passing-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Institution](https://img.shields.io/badge/IU%20Digital%20de%20Antioquia-Grupo%2025-1E3A8A)

Implementación matemática, computacional y experimental de la **Simulación de Monte Carlo** aplicada al juego de **Yahtzee**, enfocada en la comprobación empírica de la **Ley de los Grandes Números (LLN)** (fase transitoria vs. estado estable), pruebas **Chi-Cuadrado ($\chi^2$)** de bondad de ajuste, el **Teorema del Límite Central (TLC)** y la optimización estocástica de decisiones mediante **Valor Esperado (EV)**.

Proyecto desarrollado para la **Actividad Didáctica 1 — Módulo 1: Introducción a la Simulación** de la asignatura **Simulación (`PREICA2602B020045`)** en la **Institución Universitaria Digital de Antioquia (IU Digital)**.

---

## Tabla de Contenidos
1. [Contexto y Corrección de Retroalimentación Docente](#contexto-y-corrección-de-retroalimentación-docente)
2. [Metodología Pedagógica: Ciclo USA, MODIFICA y CREA](#metodología-pedagógica-ciclo-usa-modifica-y-crea)
3. [Fundamentación Matemática y Modelado Estocástico](#fundamentación-matemática-y-modelado-estocástico)
4. [Estructura del Repositorio](#estructura-del-repositorio)
5. [Instalación e Instrucciones de Ejecución](#instalación-e-instrucciones-de-ejecución)
6. [Resultados Principales y Evidencias Cuantitativas](#resultados-principales-y-evidencias-cuantitativas)
7. [Reflexión Epistemológica: Aprendizaje y Desaprendizaje](#reflexión-epistemológica-aprendizaje-y-desaprendizaje)
8. [Equipo de Trabajo (Grupo 25)](#equipo-de-trabajo-grupo-25)
9. [Licencia](#licencia)

---

## Contexto y Corrección de Retroalimentación Docente

En la entrega inicial de esta actividad (calificada con 52/100), el profesor **Julian Andres Loaiza Lopez** señaló:

> *«Al evaluar su entrega de manera integral, se reconoce y valora el esfuerzo dedicado a la construcción y programación de la aplicación del juego de Yahtzee... Sin embargo, se identifica una omisión crítica: el trabajo se enfocó únicamente en la construcción del juego y omitió por completo la generación de datos estadísticos y representaciones gráficas del comportamiento de la Teoría de los Grandes Números. La meta principal del laboratorio era utilizar la simulación de Montecarlo para ejecutar series de iteraciones masivas, recolectar frecuencias relativas y generar los gráficos de convergencia que permitieran analizar la estabilización de los resultados probabilísticos... acompañar el software con gráficos (histogramas, curvas de varianza, corridas masivas) que demuestren el comportamiento del modelo.»*

Esta versión **reestructura de raíz el proyecto**, integrando un motor vectorizado de alto rendimiento (~19 segundos de ejecución total), pruebas de hipótesis $\chi^2$, 6 figuras a 300 DPI, un cuaderno Google Colab 100% autocontenido y pre-ejecutado, 12 pruebas unitarias de auditoría y un informe académico generado dinámicamente desde los CSVs reales.

---

## Metodología Pedagógica: Ciclo USA, MODIFICA y CREA

* **Fase USA (Inspección Axiomática):** Análisis de `prueba.py` y `yahtzee_montecarlo.py`, verificando el espacio muestral $|\Omega| = 6^5 = 7,776$ microestados equiprobables y garantizando paridad matemática exacta 1:1 en las 13 categorías (incluyendo *Full House* estricto `[2, 3]` con 300 estados favorables).
* **Fase MODIFICA (Vectorización PCG64 y Codificación Base 6):** Parametrización de tamaños muestrales $N \in [10, 100,000]$, codificación biyectiva sobre $\Omega$ y reducción de varianza con Números Aleatorios Comunes (CRN) sobre las $2^5 = 32$ máscaras de retención.
* **Fase CREA (Laboratorio Experimental y Agente Estratégico):**
  1. Convergencia empírica en las **13 categorías reales** ($N = 10$ a $100,000$) distinguiendo **Fase Transitoria ($N \le 200$)** y **Estado Estable**, más pruebas $\chi^2$ de uniformidad y partición multinomial.
  2. Curvas de decaimiento de varianza según el TLC ($\mathcal{O}(1/\sqrt{N})$) con regresión OLS log-log sobre 200 réplicas por nivel $N$.
  3. Estabilización del Valor Esperado (EV) frente a la esperanza exacta y medición de inversiones de rango en muestras pequeñas.
  4. Torneo masivo de **3,000 partidas completas** (39,000 turnos) comparando Agente Aleatorio, Agente Heurístico Greedy y Agente IA Monte Carlo de Valor Esperado Estratégico.

---

## Fundamentación Matemática y Modelado Estocástico

### 1. Espacio Muestral y Probabilidad Teórica Exacta
Para $X = (X_1, X_2, X_3, X_4, X_5)$ con $X_i \sim \text{Uniforme}\{1, 6\}$, $|\Omega| = 6^5 = 7,776$ microestados equiprobables:

| Categoría | Combinatoria Analítica Exacta | Casos Favorables | $P(A)$ Teórica | % Teórico |
| :--- | :--- | :---: | :---: | :---: |
| **YAHTZEE (5 Iguales)** | $\binom{6}{1}$ | $6$ | $6 / 7,776$ | **`0.0772%`** |
| **Póker ($\ge 4$ Iguales)** | $\binom{6}{1}\binom{5}{1}\binom{5}{4} + 6$ | $156$ | $156 / 7,776$ | **`2.0062%`** |
| **Full House (Trío + Par)** | $\binom{6}{1}\binom{5}{1}\binom{5}{3}$ | $300$ | $300 / 7,776$ | **`3.8580%`** |
| **Escalera Grande (5 consec.)** | $2 \times 5!$ | $240$ | $240 / 7,776$ | **`3.0864%`** |
| **Escalera Pequeña ($\ge 4$ consec.)** | $240 + 360 + 240 + 360$ | $1,200$ | $1,200 / 7,776$ | **`15.4321%`** |
| **Trío ($\ge 3$ Iguales)** | $1,200 + 300 + 150 + 6$ | $1,656$ | $1,656 / 7,776$ | **`21.2963%`** |
| **Cada Cara Superior (Unos..Seises)** | $6^5 - 5^5$ (al menos un dado $k$) | $4,651$ | $4,651 / 7,776$ | **`59.8122%`** |
| **Libre (Chance)** | $\Omega$ completo | $7,776$ | $7,776 / 7,776$ | **`100.0000%`** |

### 2. Ley de los Grandes Números (LLN) y Teorema del Límite Central (TLC)
$$P\left( \lim_{N \to \infty} f_N(A) = P(A) \right) = 1, \qquad \text{SE}(N) = \frac{\sqrt{P(A)(1 - P(A))}}{\sqrt{N}} \implies \log_{10}\text{SE}(N) = \log_{10}\sigma - 0.50\log_{10}N$$

---

## Estructura del Repositorio

```text
.
├── yahtzee_simulation/                         # Paquete modular vectorizado
│   ├── __init__.py                            # Exportación pública
│   ├── rules.py                               # Reglas oficiales y tabla exacta de los 7,776 estados
│   ├── theory.py                              # Combinatoria exacta, EV analítico y particiones de Ω
│   ├── montecarlo.py                          # Muestreo masivo LLN (13 categorías), χ², TLC y EV
│   ├── massive_runs.py                        # Torneo vectorizado de 3,000 partidas completas
│   └── visualizations.py                      # Generador de las 6 figuras científicas a 300 DPI
├── tests/
│   ├── __init__.py
│   └── test_montecarlo.py                     # 12 pruebas unitarias y de auditoría cruzada
├── results/                                   # 7 CSVs auditables y 6 figuras PNG a 300 DPI
├── main_experimentos.py                       # Pipeline maestro (~19 segundos de ejecución)
├── generate_doc.py                            # Generador dinámico del informe Word (.docx)
├── create_colab_notebook.py                   # Constructor y ejecutor del cuaderno Colab
├── Simulacion_Yahtzee_Montecarlo_Colab.ipynb  # Cuaderno 100% autocontenido y pre-ejecutado
├── Evidencia de Aprendizaje 1 - Módulo 1. Actividad didáctica 1 - Simulación Montecarlo Yahtzee.docx
├── GUION_VIDEO_SUSTENTACION.md                # Guion estructurado para la sustentación oral
├── interfaz_yahtzee.py                        # Interfaz Tkinter conectada dinámicamente a CSVs
├── yahtzee_montecarlo.py                      # Motor didáctico base en consola
├── prueba.py                                  # Script original preservado
├── requirements.txt                           # Dependencias científicas
└── README.md
```

---

## Instalación e Instrucciones de Ejecución

```bash
# 1. Instalar dependencias científicas
pip install -r requirements.txt

# 2. Ejecutar el pipeline experimental completo (~19 s)
python main_experimentos.py

# 3. Regenerar informe Word (.docx) y cuaderno Google Colab pre-ejecutado (.ipynb)
python generate_doc.py
python create_colab_notebook.py

# 4. Ejecutar las 12 pruebas de auditoría matemática y de integridad
python -m unittest discover -s tests -v

# 5. Abrir la interfaz gráfica interactiva
python interfaz_yahtzee.py
```

---

## Resultados Principales y Evidencias Cuantitativas

### 1. Bondad de Ajuste $\chi^2$ ($N = 100,000$ Tiradas, Semilla 42)
* **Uniformidad de caras del dado ($500,000$ dados, $gl=5$):** $\chi^2 = 2.7491 < 11.0705$ ($p\text{-valor} = 0.7386$) $\to$ Uniformidad validada.
* **Partición combinatoria de $\Omega$ ($100,000$ manos, $gl=6$):** $\chi^2 = 1.2740 < 12.5916$ ($p\text{-valor} = 0.9731$) $\to$ Ajuste exacto al modelo de Laplace.

### 2. Torneo Masivo de Partidas Completas (3,000 Partidas Oficiales)

| Estrategia | Partidas | Puntaje Medio | Desv. Estándar | Mediana | Tasa Bono (+35 pts) | Rango [Mín–Máx] |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Agente Aleatorio (Control Ciego)** | 1,000 | `44.85 pts` | `±17.22` | `41.0 pts` | `0.0%` | `16 – 126 pts` |
| **Agente Heurístico (Greedy Humano)** | 1,000 | `140.34 pts` | `±36.12` | `140.0 pts` | `1.4%` | `43 – 266 pts` |
| **Agente IA Monte Carlo (EV Estratégico)** | **1,000** | **`217.38 pts`** | **`±39.80`** | **`211.0 pts`** | **`16.9%`** | **`112 – 334 pts`** |

> **Conclusión Clave:** La política **IA Monte Carlo supera en un +54.9% al Agente Heurístico** y en un **+384.7% al Agente Aleatorio**, imponiéndose en 11 de las 13 categorías y multiplicando por **12.1 veces** la tasa de obtención del Bono Superior (`16.9%` vs `1.4%`).

---

### 3. Galería de Figuras Científicas (300 DPI)

#### Figura 1: Convergencia de Frecuencias Relativas (Fase Transitoria vs. Estado Estable)
![Figura 1](results/fig1_convergencia_grandes_numeros.png)

#### Figura 2: Curvas de Varianza y Regresión OLS Log-Log (Teorema del Límite Central)
![Figura 2](results/fig2_curvas_varianza_error_montecarlo.png)

#### Figura 3: Validación Global en las 13 Categorías y Pruebas $\chi^2$
![Figura 3](results/fig3_histogramas_distribucion_empirica_vs_teorica.png)

#### Figura 4: Estabilización del Valor Esperado e Inversión de Rango Muestral
![Figura 4](results/fig4_convergencia_valor_esperado_mascaras.png)

#### Figura 5: Distribuciones Completas y Curvas KDE en Torneo de 3,000 Partidas
![Figura 5](results/fig5_corridas_masivas_estrategias.png)

#### Figura 6: Descomposición de Puntajes por Categoría y Eficiencia en Bono Superior
![Figura 6](results/fig6_descomposicion_puntaje_categorias.png)

---

## Reflexión Epistemológica: Aprendizaje y Desaprendizaje

* **Lo que tuvimos que desaprender:**
  1. *El sesgo del software / videojuego:* Asumir que una interfaz funcional basta en un curso de Simulación; el software es el instrumento para recolectar evidencia estadística.
  2. *La falacia de la muestra pequeña:* Con $N = 10$ simulaciones la IA sufre un **31.0% de errores de decisión** por varianza muestral, reduciéndose a **0.0%** desde $N \ge 100$ (umbral seguro $N = 250$).
  3. *La heurística codiciosa sin horizonte:* Retener ciegamente cualquier par sacrifica escaleras y el Bono Superior frente a la optimización integral del Valor Esperado.
* **El aprendizaje genuino construido:**
  1. La simulación como laboratorio experimental riguroso (hipótesis $\chi^2$, regímenes transitorio y estable).
  2. Verificación empírica de la Ley de los Grandes Números y la pendiente $-0.50$ del TLC ($m = -0.477, R^2 = 0.9954$).
  3. Diseño de agentes de decisión bajo incertidumbre mediante Valor Esperado Estratégico.

---

## Equipo de Trabajo (Grupo 25)

* **Adriana Andrea Agudelo Agudelo**
* **Camilo Alberto Palacios Turriago**
* **Juan Daniel Pulgarin García**
* **Ruben Dario Jaramillo Cervantes**

* **Docente Catedrático:** Julian Andres Loaiza Lopez · **Asignatura:** Simulación (`PREICA2602B020045`) · **IU Digital de Antioquia**

---

## Licencia

Distribuido bajo la licencia **MIT**. Consulta el archivo `LICENSE` para más detalles.
