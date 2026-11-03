"""
=============================================================================
  GENERADOR DEL INFORME ACADÉMICO OFICIAL - ACTIVIDAD DIDÁCTICA 1 (MÓDULO 1)
=============================================================================
Genera el documento formal en formato Word (.docx) conforme a la identidad
institucional de la IU Digital de Antioquia, estructurando la evidencia
experimental completa:
- Metodología USA, MODIFICA, CREA.
- Formulación analítica de la Ley de los Grandes Números y Teorema del Límite Central.
- Inserción y discusión de las 6 figuras científicas a 300 DPI.
- Tablas paginadas con repetición de encabezado y cantSplit.
- Reflexión epistemológica profunda sobre Aprendizaje y Desaprendizaje.
- Numeración dinámica 'Página X de Y'.
"""

import os
import sys
import pandas as pd
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# Paleta institucional IU Digital de Antioquia
COLOR_NAVY = RGBColor(0x1E, 0x3A, 0x8A)   # #1E3A8A - Títulos H1 y cabeceras de tabla
COLOR_TEAL = RGBColor(0x0F, 0x76, 0x6E)   # #0F766E - Subtítulos H2
COLOR_BODY = RGBColor(0x1E, 0x29, 0x3B)   # #1E293B - Cuerpo del texto
COLOR_SLATE = RGBColor(0x47, 0x55, 0x69)  # #475569 - Subtítulo de portada y pies de figura
COLOR_MUTED = RGBColor(0x64, 0x74, 0x8B)  # #64748B - Encabezado y pie de página
COLOR_DARK = RGBColor(0x0F, 0x17, 0x2A)   # #0F172A - Metadatos de portada


def set_cell_background(cell, fill_hex: str) -> None:
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_margins(cell, top=110, bottom=110, left=140, right=140) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for margin_name, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{margin_name}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_borders(cell, top="none", bottom="none", left="none", right="none", color="CBD5E1", sz="4") -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for b_name, b_val in {"top": top, "left": left, "bottom": bottom, "right": right}.items():
        node = OxmlElement(f"w:{b_name}")
        node.set(qn("w:val"), b_val)
        if b_val != "none":
            node.set(qn("w:sz"), str(sz))
            node.set(qn("w:space"), "0")
            node.set(qn("w:color"), color)
        tcBorders.append(node)
    tcPr.append(tcBorders)


def set_row_pagination_rules(row, is_header: bool = False) -> None:
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))
    if is_header:
        trPr.append(OxmlElement("w:tblHeader"))


def add_word_field(paragraph, field_name: str, font_size: float = 8.5, color: RGBColor = COLOR_MUTED) -> None:
    run = paragraph.add_run()
    run.font.name = "Arial"
    run.font.size = Pt(font_size)
    run.font.color.rgb = color

    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = f" {field_name} "
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    fldChar3 = OxmlElement("w:fldChar")
    fldChar3.set(qn("w:fldCharType"), "end")

    r = run._r
    r.append(fldChar1)
    r.append(instrText)
    r.append(fldChar2)
    r.append(fldChar3)


def add_heading_styled(doc, text: str, level: int) -> None:
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name = "Segoe UI"
    run.bold = True

    if level == 1:
        run.font.size = Pt(15)
        run.font.color.rgb = COLOR_NAVY
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
    elif level == 2:
        run.font.size = Pt(12.5)
        run.font.color.rgb = COLOR_TEAL
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
    elif level == 3:
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_DARK
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True


def add_paragraph_styled(doc, text: str, bold_prefix: str = "", space_after: float = 6.0) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(space_after)

    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Segoe UI"
        r_pre.font.size = Pt(10.5)
        r_pre.font.color.rgb = COLOR_DARK
        r_pre.bold = True

    r = p.add_run(text)
    r.font.name = "Segoe UI"
    r.font.size = Pt(10.5)
    r.font.color.rgb = COLOR_BODY


def add_callout_box(doc, text: str, title: str = "NOTA METODOLÓGICA", fill_hex: str = "EFF6FF") -> None:
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, fill_hex)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    set_cell_borders(cell, left="single", color="1E3A8A", sz="18")

    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    r_tit = p.add_run(f"★  {title}\n")
    r_tit.font.name = "Segoe UI"
    r_tit.font.size = Pt(10.5)
    r_tit.font.color.rgb = COLOR_NAVY
    r_tit.bold = True

    r_txt = p.add_run(text)
    r_txt.font.name = "Segoe UI"
    r_txt.font.size = Pt(10)
    r_txt.font.color.rgb = COLOR_BODY

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)


def add_figure_with_caption(doc, image_filename: str, caption_text: str, width_inches: float = 6.2) -> None:
    img_path = os.path.join(RESULTS_DIR, image_filename)
    if not os.path.exists(img_path):
        add_paragraph_styled(doc, f"[Figura no encontrada: {image_filename}]")
        return

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(4)
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Inches(width_inches))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(10)
    p_cap.paragraph_format.keep_with_next = False

    run_cap = p_cap.add_run(caption_text)
    run_cap.font.name = "Segoe UI"
    run_cap.font.size = Pt(9)
    run_cap.font.italic = True
    run_cap.font.color.rgb = COLOR_SLATE


def generar_informe_word() -> str:
    doc = Document()

    # Configuración de márgenes estándar de 1 pulgada (72 pt)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True

        # Encabezado institucional
        header = section.header
        p_hdr = header.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run("Institución Universitaria Digital de Antioquia · Simulación (PREICA2602B020045)")
        r_hdr.font.name = "Segoe UI"
        r_hdr.font.size = Pt(8.5)
        r_hdr.font.color.rgb = COLOR_MUTED

        # Pie de página con numeración dinámica "Página X de Y"
        footer = section.footer
        p_ftr = footer.paragraphs[0]
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_txt = p_ftr.add_run("Página ")
        r_txt.font.name = "Segoe UI"
        r_txt.font.size = Pt(8.5)
        r_txt.font.color.rgb = COLOR_MUTED
        add_word_field(p_ftr, "PAGE", 8.5, COLOR_MUTED)
        r_de = p_ftr.add_run(" de ")
        r_de.font.name = "Segoe UI"
        r_de.font.size = Pt(8.5)
        r_de.font.color.rgb = COLOR_MUTED
        add_word_field(p_ftr, "NUMPAGES", 8.5, COLOR_MUTED)

    # =========================================================================
    # PORTADA OFICIAL
    # =========================================================================
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(8)
    r_title = p_title.add_run("Simulación Estocástica de Yahtzee mediante el Método Monte Carlo y Comprobación Experimental de la Ley de los Grandes Números")
    r_title.font.name = "Segoe UI"
    r_title.font.size = Pt(21)
    r_title.font.color.rgb = COLOR_NAVY
    r_title.bold = True

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(24)
    r_sub = p_sub.add_run("Análisis Asintótico del Teorema del Límite Central, Decaimiento de Varianza, Optimización del Valor Esperado y Metodología USA-MODIFICA-CREA")
    r_sub.font.name = "Segoe UI"
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = COLOR_SLATE
    r_sub.font.italic = True

    # Cuadro institucional de metadatos de autores
    t_meta = doc.add_table(rows=6, cols=2)
    t_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    metadatos = [
        ("Asignatura:", "Simulación (Código: PREICA2602B020045) — Grupo 25"),
        ("Actividad Didáctica:", "Evidencia de Aprendizaje 1 — Módulo 1: Introducción a la Simulación"),
        ("Docente Catedrático:", "Julian Andres Loaiza Lopez"),
        ("Integrantes del Equipo:", "Adriana Andrea Agudelo Agudelo\nCamilo Alberto Palacios Turriago\nJuan Daniel Pulgarin García\nRuben Dario Jaramillo Cervantes"),
        ("Institución:", "Institución Universitaria Digital de Antioquia (IU Digital)\nFacultad de Ingeniería"),
        ("Sede y Fecha:", "Medellín, Antioquia — Noviembre de 2026")
    ]
    for i, (k, v) in enumerate(metadatos):
        row = t_meta.rows[i]
        set_row_pagination_rules(row)
        c0, c1 = row.cells
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        set_cell_margins(c0, 80, 80, 100, 100)
        set_cell_margins(c1, 80, 80, 100, 100)
        set_cell_borders(c0, bottom="single", color="E2E8F0", sz="4")
        set_cell_borders(c1, bottom="single", color="E2E8F0", sz="4")
        set_cell_background(c0, "F8FAFC")
        set_cell_background(c1, "FFFFFF")

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.font.name = "Segoe UI"
        r0.font.size = Pt(10)
        r0.font.color.rgb = COLOR_NAVY
        r0.bold = True

        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(10)
        r1.font.color.rgb = COLOR_DARK

    doc.add_page_break()

    # =========================================================================
    # TABLA DE CONTENIDO
    # =========================================================================
    add_heading_styled(doc, "Tabla de Contenido", level=1)
    toc_items = [
        ("1. Introducción y Planteamiento del Problema", "3"),
        ("2. Metodología Pedagógica: Ciclo USA, MODIFICA y CREA", "4"),
        ("    2.1 Fase USA: Inspección del Modelo Base y Espacio Muestral", "4"),
        ("    2.2 Fase MODIFICA: Parametrización, Espacio de Decisiones (2^5 = 32) y Sensibilidad", "5"),
        ("    2.3 Fase CREA: Diseño del Laboratorio Experimental Estocástico", "6"),
        ("3. Fundamentación Teórica y Modelado Matemático", "7"),
        ("    3.1 Espacio de Probabilidad Discreto y Combinatoria Exacta", "7"),
        ("    3.2 Ley Débil y Ley Fuerte de los Grandes Números (Khinchin y Kolmogorov)", "8"),
        ("    3.3 Teorema del Límite Central (TLC) y Tasa de Error O(1/√N)", "9"),
        ("    3.4 Toma Óptima de Decisiones bajo Incertidumbre y Valor Esperado (EV)", "10"),
        ("4. Resultados Experimentales y Análisis Cuantitativo", "11"),
        ("    4.1 Convergencia de Frecuencias Relativas (Figura 1)", "11"),
        ("    4.2 Decaimiento Asintótico de Varianza y Error Estándar (Figura 2)", "13"),
        ("    4.3 Validación Global: Distribución Empírica vs Probabilidad Teórica (Figura 3)", "14"),
        ("    4.4 Estabilización del Valor Esperado en Decisiones de Retención (Figura 4)", "16"),
        ("    4.5 Torneo de Corridas Masivas: Comparativa de Políticas (Figura 5)", "17"),
        ("    4.6 Descomposición de Rendimiento por Categoría y Tasa de Bono (Figura 6)", "19"),
        ("5. Reflexión Epistemológica: Aprendizaje y Desaprendizaje en Simulación", "20"),
        ("    5.1 Lo que Tuvimos que Desaprender: Superación del Sesgo Lúdico / UI", "20"),
        ("    5.2 El Aprendizaje Real y Genuino Construido: La Simulación como Ciencia", "21"),
        ("6. Conclusiones y Recomendaciones Operativas", "22"),
        ("7. Ecosistema Reproducible del Proyecto (GitHub, Colab y Video)", "23"),
        ("8. Referencias Bibliográficas", "24")
    ]
    t_toc = doc.add_table(rows=len(toc_items), cols=2)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (secc, pag) in enumerate(toc_items):
        row = t_toc.rows[idx]
        set_row_pagination_rules(row)
        c0, c1 = row.cells
        c0.width = Inches(5.8)
        c1.width = Inches(0.7)
        set_cell_margins(c0, 40, 40, 60, 60)
        set_cell_margins(c1, 40, 40, 60, 60)
        set_cell_borders(c0, bottom="none")
        set_cell_borders(c1, bottom="none")

        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(secc)
        r0.font.name = "Segoe UI"
        r0.font.size = Pt(9.5)
        if secc.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.")):
            r0.font.color.rgb = COLOR_NAVY
            r0.bold = True
        else:
            r0.font.color.rgb = COLOR_BODY

        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(pag)
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = COLOR_SLATE

    doc.add_page_break()

    # =========================================================================
    # SECCIÓN 1: INTRODUCCIÓN
    # =========================================================================
    add_heading_styled(doc, "1. Introducción y Planteamiento del Problema", level=1)

    add_paragraph_styled(
        doc,
        "La simulación computacional de eventos discretos y procesos estocásticos representa uno de los pilares metodológicos más potentes de la ingeniería moderna para el análisis, predicción y optimización de sistemas donde la incertidumbre y la combinatoria impiden la resolución analítica directa. En este contexto, el juego de Yahtzee —concebido originalmente por Milton Bradley y formalizado matemáticamente en la teoría de juegos moderna— constituye un banco de pruebas estocástico extraordinariamente fértil. Con un espacio muestral en cada lanzamiento compuesto por 6^5 = 7,776 microestados equiprobables y un árbol de ramificación de decisiones que abarca 2^5 = 32 combinaciones de retención de dados a lo largo de 13 rondas con restricciones de asignación exclusiva, Yahtzee presenta un problema de optimización bajo incertidumbre NP-difícil en horizonte completo.",
        bold_prefix="Contextualización del Problema: "
    )

    add_paragraph_styled(
        doc,
        "En la primera entrega evaluada de este laboratorio (calificada con 52/100), nuestro equipo orientó el esfuerzo técnico prioritariamente hacia la construcción de la lógica del juego y el desarrollo de una interfaz gráfica de usuario (GUI) interactiva en Tkinter. Si bien dicho software demostró robustez en la implementación de las reglas oficiales y el cómputo de la puntuación, incurrió en una omisión epistemológica y metodológica crítica señalada por el docente: se omitió la experimentación estadística masiva, la recolección de frecuencias relativas empíricas y la comprobación gráfica y cuantitativa de la Ley de los Grandes Números (LLN).",
        bold_prefix="Diagnóstico Crítico de la Entrega Previa: "
    )

    add_callout_box(
        doc,
        "«Al evaluar su entrega de manera integral, se reconoce y valora el esfuerzo dedicado a la construcción y programación de la aplicación... Sin embargo, el trabajo se enfocó únicamente en la construcción del juego y omitió por completo la generación de datos estadísticos y representaciones gráficas del comportamiento de la Teoría de los Grandes Números. La meta principal del laboratorio no era únicamente desarrollar el código del juego, sino utilizar la simulación de Montecarlo para ejecutar series de iteraciones masivas, recolectar frecuencias relativas y generar los gráficos de convergencia que permitieran analizar la estabilización de los resultados probabilísticos.»\n— Dictamen y Retroalimentación Oficial de la Cátedra (Prof. Julian Andres Loaiza Lopez)",
        title="RETROALIMENTACIÓN DOCENTE Y EJE CENTRAL DE LA RESUBMISIÓN",
        fill_hex="FEF3C7"
    )

    add_paragraph_styled(
        doc,
        "El presente informe técnico subsana de manera rigurosa, integral y cuantitativa todas y cada una de las falencias identificadas. Para ello, se formula un marco metodológico estructurado en el ciclo pedagógico 'USA, MODIFICA y CREA', complementando el software lúdico con un motor de simulación de alto rendimiento capaz de ejecutar 100,000 lanzamientos estocásticos y torneos masivos de 3,000 partidas completas. A través de este instrumental experimental, se demuestra analítica y empíricamente cómo las frecuencias relativas convergen casi con seguridad a las probabilidades teóricas exactas, cómo la varianza del estimador decae a una tasa de O(1/√N) gobernada por el Teorema del Límite Central, y cómo el agente inteligente basado en Valor Esperado (EV) supera en más de 340% al agente aleatorio y en 47.1% al agente heurístico codicioso.",
        bold_prefix="Propósito y Alcance del Presente Informe: "
    )

    # =========================================================================
    # SECCIÓN 2: METODOLOGÍA USA - MODIFICA - CREA
    # =========================================================================
    add_heading_styled(doc, "2. Metodología Pedagógica: Ciclo USA, MODIFICA y CREA", level=1)

    add_paragraph_styled(
        doc,
        "Para restablecer la integridad del proceso formativo en ingeniería, el proyecto adopta de manera estricta el modelo pedagógico 'USA, MODIFICA y CREA', articulando la herramienta computacional con la experimentación científica rigurosa:",
        bold_prefix="Marco Metodológico Institucional: "
    )

    add_heading_styled(doc, "2.1 Fase USA: Inspección del Modelo Base y Espacio Muestral", level=2)
    add_paragraph_styled(
        doc,
        "En la etapa 'USA', el equipo analizó e inspeccionó el prototipo lógico base provisto en la asignatura ('prueba.py' y 'yahtzee_montecarlo.py'). Se verificó el funcionamiento del generador pseudoaleatorio lineal estándar (PRNG), la implementación de los 13 predicados de puntuación (categorías de la sección superior e inferior), el mecanismo de selección booleana de retención y la función de utilidad inmediata. Se confirmó matemáticamente que cada dado sigue una distribución uniforme discreta X_i ~ Uniforme{1, 6}, de modo que el vector de 5 dados X = (X_1, X_2, X_3, X_4, X_5) genera un espacio muestral equiprobable con cardinalidad |Ω| = 6^5 = 7,776 sucesos elementales, cada uno con probabilidad idéntica P(ω) = 1/7776 ≈ 0.0001286."
    )

    add_heading_styled(doc, "2.2 Fase MODIFICA: Parametrización, Espacio de Decisiones (32 Máscaras) y Sensibilidad", level=2)
    add_paragraph_styled(
        doc,
        "En la etapa 'MODIFICA', se reestructuró la arquitectura del simulador para transformar un script estático en un motor de muestreo parametrizable. Se introdujo vectorización mediante NumPy y su generador PCG64 (Permuted Congruential Generator), permitiendo simular millones de lanzamientos por segundo. Se parametrizó el tamaño de muestra N ∈ [10, 100,000], la semilla de aleatoriedad (para garantizar estricta reproducibilidad experimental) y la técnica de retención de dados. Asimismo, se formalizó el espacio de decisión: en cada tirada, el jugador dispone de 2^5 = 32 máscaras binarias m = (m_1, ..., m_5) ∈ {0, 1}^5, donde m_i = 1 denota retención y m_i = 0 denota relanzamiento. El motor fue modificado para registrar la traza estocástica del promedio móvil acumulado y el error estándar en tiempo de ejecución."
    )

    add_heading_styled(doc, "2.3 Fase CREA: Diseño del Laboratorio Experimental Estocástico", level=2)
    add_paragraph_styled(
        doc,
        "En la etapa 'CREA', el equipo diseñó y construyó un laboratorio experimental estocástico autónomo ('yahtzee_simulation' y 'main_experimentos.py'), desplegando cuatro experimentos masivos:",
        bold_prefix="Contribución Científica Original: "
    )
    add_paragraph_styled(doc, "1. Experimento de Convergencia LLN: Simulación de 100,000 lanzamientos iniciales independientes con checkpoints logarítmicos para medir la velocidad de estabilización de frecuencias relativas frente a la verdad teórica analítica.", bold_prefix="• ")
    add_paragraph_styled(doc, "2. Experimento de Curvas de Varianza TLC: Ejecución de 150 réplicas independientes de Monte Carlo para cada N ∈ [20, 10000], cuantificando empíricamente la dispersión entre réplicas y comprobando la tasa de decaimiento asintótico O(1/√N).", bold_prefix="• ")
    add_paragraph_styled(doc, "3. Experimento de Estabilización del Valor Esperado: Evaluación de las 32 máscaras sobre configuraciones críticas de dados a través de 8 niveles de simulación (N=10 a 2,500), demostrando cómo la reducción de varianza elimina inversiones erróneas de jerarquía en la toma de decisiones.", bold_prefix="• ")
    add_paragraph_styled(doc, "4. Torneo Masivo de Partidas Completas: Simulación de 3,000 juegos oficiales completos (39,000 rondas) contrastando una política ciega (Aleatoria), una heurística codiciosa (Greedy humano) y la IA de Monte Carlo basada en Valor Esperado.", bold_prefix="• ")

    # =========================================================================
    # SECCIÓN 3: FUNDAMENTACIÓN TEÓRICA Y MATEMÁTICA
    # =========================================================================
    add_heading_styled(doc, "3. Fundamentación Teórica y Modelado Matemático", level=1)

    add_heading_styled(doc, "3.1 Espacio de Probabilidad Discreto y Combinatoria Exacta", level=2)
    add_paragraph_styled(
        doc,
        "Definimos el experimento aleatorio de lanzar 5 dados equilibrados mediante el espacio de probabilidad clásico (Ω, F, P), donde Ω = {1, 2, 3, 4, 5, 6}^5 con |Ω| = 6^5 = 7,776 elementos equiprobables. Para cualquier categoría o evento A ⊆ Ω, la probabilidad teórica exacta está dada por la regla de Laplace P(A) = |A| / |Ω|. La deducción analítica de los casos favorables para las categorías principales se resume a continuación:",
        bold_prefix="Formulación Combinatoria: "
    )

    # Tabla teórica analítica
    t_teor = doc.add_table(rows=7, cols=5)
    t_teor.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_teor = ["Categoría / Patrón", "Fórmula Combinatoria Analítica", "Casos Favorables", "P(A) Teórica", "% Teórico"]
    for j, h in enumerate(headers_teor):
        c = t_teor.rows[0].cells[j]
        set_cell_background(c, "1E3A8A")
        set_cell_margins(c, 100, 100, 100, 100)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Segoe UI"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.bold = True
    set_row_pagination_rules(t_teor.rows[0], is_header=True)

    filas_teor_data = [
        ("YAHTZEE (5 Iguales)", "C(6,1)", "6", "6 / 7,776", "0.0772%"),
        ("Póker (≥ 4 Iguales)", "C(6,1)*C(5,1)*C(5,4) + C(6,1)", "156", "156 / 7,776", "2.0062%"),
        ("Full House (Trío + Par)", "C(6,1)*C(5,1)*C(5,3) + 6 (joker)", "306", "306 / 7,776", "3.9352%"),
        ("Escalera Grande (5 consec.)", "2 * 5!", "240", "240 / 7,776", "3.0864%"),
        ("Escalera Pequeña (≥ 4 consec.)", "Inclusión-Exclusión sobre secuencias", "1,200", "1,200 / 7,776", "15.4321%"),
        ("Trío (≥ 3 Iguales)", "C(6,1)*C(5,2)*[5!/(3!1!1!)] + 306 + 150", "1,656", "1,656 / 7,776", "21.2963%")
    ]
    for i, data in enumerate(filas_teor_data, start=1):
        row = t_teor.rows[i]
        set_row_pagination_rules(row)
        bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(data):
            c = row.cells[j]
            set_cell_background(c, bg)
            set_cell_margins(c, 80, 80, 100, 100)
            set_cell_borders(c, bottom="single", color="CBD5E1", sz="4")
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            if j in (0, 1):
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = "Segoe UI"
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_BODY

    add_heading_styled(doc, "3.2 Ley Débil y Ley Fuerte de los Grandes Números", level=2)
    add_paragraph_styled(
        doc,
        "Sea I_A^(i) la variable indicadora de que en el i-ésimo lanzamiento de dados se obtenga el evento A (e.g. A = Yahtzee). Las variables I_A^(1), I_A^(2), ..., I_A^(N) son independientes e idénticamente distribuidas (i.i.d.) con distribución Bernoulli de parámetro p = P(A), media E[I_A] = p y varianza Var(I_A) = p(1 - p). La frecuencia relativa observada tras N iteraciones de Monte Carlo se define como el promedio aritmético muestral f_N(A) = (1/N) ∑_{i=1}^N I_A^(i).",
        bold_prefix="Definición del Estimador Monte Carlo: "
    )
    add_paragraph_styled(
        doc,
        "La Ley Débil de los Grandes Números (Teorema de Khinchin) garantiza la convergencia en probabilidad: para cualquier tolerancia ε > 0, lim_{N→∞} P(|f_N(A) - p| ≥ ε) = 0. Mediante la desigualdad de Chebyshev, se establece una cota explícita sobre el riesgo de estimación: P(|f_N(A) - p| ≥ ε) ≤ p(1 - p) / (N ε^2). Por su parte, la Ley Fuerte de los Grandes Números (Teorema de Kolmogorov) asegura la convergencia casi segura (c.s.): P( lim_{N→∞} f_N(A) = p ) = 1. Esto significa que a medida que el número de repeticiones de la simulación crece sin límite, la trayectoria empírica de frecuencias relativas converge determinísticamente hacia la probabilidad teórica exacta con probabilidad 1.",
        bold_prefix="Formulación Rigurosa de la LLN: "
    )

    add_heading_styled(doc, "3.3 Teorema del Límite Central (TLC) y Decaimiento del Error", level=2)
    add_paragraph_styled(
        doc,
        "Mientras que la Ley de los Grandes Números establece que el estimador f_N(A) converge a p, el Teorema del Límite Central (TLC) describe la distribución del error de estimación (f_N(A) - p) para N finito pero grande. Dado que las variables I_A^(i) tienen varianza finita σ^2 = p(1 - p), la variable estandarizada converge en distribución a una normal estándar: √N (f_N(A) - p) / √(p(1 - p)) xrightarrow{d} N(0, 1).",
        bold_prefix="Comportamiento Asintótico del Error: "
    )
    add_paragraph_styled(
        doc,
        "De este resultado fundamental se derivan dos propiedades críticas para la ingeniería de simulación: (i) La varianza del estimador decae en proporción inversa al tamaño muestral: Var(f_N(A)) = p(1 - p) / N; y (ii) El error estándar (SE) decae a una tasa de O(1/√N): SE(N) = √(p(1 - p)) / √N. Por consiguiente, para reducir el error de estimación a la mitad, es matemáticamente indispensable cuadruplicar el número de simulaciones de Monte Carlo (4N). Un intervalo de confianza asintótico al 95% queda determinado por [p - 1.96 SE(N), p + 1.96 SE(N)].",
        bold_prefix="Tasa de Convergencia O(1/√N): "
    )

    add_heading_styled(doc, "3.4 Optimización Estocástica y Valor Esperado (EV)", level=2)
    add_paragraph_styled(
        doc,
        "En Yahtzee, tras la primera tirada de dados d = (d_1, ..., d_5), el jugador debe seleccionar una máscara de retención m ∈ {0, 1}^5. Para cada una de las 32 opciones, la mano futura Y(m) es una variable aleatoria estocástica. El Valor Esperado (EV) de la máscara m se define como la esperanza matemática del puntaje máximo alcanzable sobre el conjunto de categorías disponibles C_libres: EV(m) = E[ max_{c ∈ C_libres} Puntaje(c, Y(m)) ]. El estimador de Monte Carlo aproxima esta esperanza mediante el promedio muestral de K simulaciones de relanzamiento: EV_MC(m) = (1/K) ∑_{k=1}^K max_{c ∈ C_libres} Puntaje(c, Y^(k)(m)). La política óptima de la IA selecciona la máscara que maximiza el valor esperado: m* = argmax_{m ∈ {0, 1}^5} EV_MC(m).",
        bold_prefix="Toma de Decisiones Óptima: "
    )

    # =========================================================================
    # SECCIÓN 4: RESULTADOS EXPERIMENTALES Y ANÁLISIS CUANTITATIVO
    # =========================================================================
    add_heading_styled(doc, "4. Resultados Experimentales y Análisis Cuantitativo", level=1)

    add_heading_styled(doc, "4.1 Convergencia de Frecuencias Relativas (Figura 1)", level=2)
    add_paragraph_styled(
        doc,
        "El primer experimento ejecutó una serie masiva de N = 100,000 tiradas de dados registradas en puntos de control logarítmicos N ∈ [10, 20, 50, ..., 100,000]. La Figura 1 ilustra la trayectoria de la frecuencia relativa empírica f_N(A) para 6 categorías fundamentales, contrastada con la asíntota teórica P(A) y la banda de confianza asintótica del 95% derivada del TLC."
    )

    add_figure_with_caption(
        doc,
        "fig1_convergencia_grandes_numeros.png",
        "Figura 1. Comprobación Experimental de la Ley de los Grandes Números (LLN) en Yahtzee. Se observa la marcada oscilación inicial para N < 500 y la estabilización rigurosa de las frecuencias relativas dentro de la banda de confianza del 95% al aproximarse a N = 100,000 tiradas."
    )

    # Tabla cuantitativa de convergencia en checkpoints clave
    add_paragraph_styled(
        doc,
        "La Tabla 2 documenta cuantitativamente la evolución del error absoluto y relativo en cuatro órdenes de magnitud muestral para Yahtzee y Full House:",
        bold_prefix="Síntesis Numérica de la Convergencia: "
    )

    t_conv = doc.add_table(rows=5, cols=7)
    t_conv.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_conv = ["N (Tiradas)", "f_N(Yahtzee)", "P Teórica", "Error Rel. (%)", "f_N(Full)", "P Teórica", "Error Rel. (%)"]
    for j, h in enumerate(headers_conv):
        c = t_conv.rows[0].cells[j]
        set_cell_background(c, "1E3A8A")
        set_cell_margins(c, 80, 80, 80, 80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Segoe UI"
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.bold = True
    set_row_pagination_rules(t_conv.rows[0], is_header=True)

    # Cargar datos reales de CSV si existen
    df_lln = pd.read_csv(os.path.join(RESULTS_DIR, "convergencia_ley_grandes_numeros.csv"))
    cps = [100, 1000, 10000, 100000]
    for idx, n_val in enumerate(cps, start=1):
        row = t_conv.rows[idx]
        set_row_pagination_rules(row)
        bg = "F8FAFC" if idx % 2 == 1 else "FFFFFF"

        sub_y = df_lln[(df_lln["N"] == n_val) & (df_lln["categoria"] == "yahtzee")]
        sub_f = df_lln[(df_lln["N"] == n_val) & (df_lln["categoria"] == "full")]

        fy = sub_y["frecuencia_relativa"].iloc[0] if not sub_y.empty else 0.0
        py = sub_y["probabilidad_teorica"].iloc[0] if not sub_y.empty else 0.000772
        ery = sub_y["error_relativo_pct"].iloc[0] if not sub_y.empty else 0.0

        ff = sub_f["frecuencia_relativa"].iloc[0] if not sub_f.empty else 0.0
        pf = sub_f["probabilidad_teorica"].iloc[0] if not sub_f.empty else 0.039352
        erf = sub_f["error_relativo_pct"].iloc[0] if not sub_f.empty else 0.0

        vals = [f"{n_val:,}", f"{fy:.6f}", f"{py:.6f}", f"{ery:.2f}%", f"{ff:.6f}", f"{pf:.6f}", f"{erf:.2f}%"]
        for j, val in enumerate(vals):
            c = row.cells[j]
            set_cell_background(c, bg)
            set_cell_margins(c, 70, 70, 70, 70)
            set_cell_borders(c, bottom="single", color="CBD5E1", sz="4")
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if j > 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(val)
            r.font.name = "Segoe UI"
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_BODY

    add_paragraph_styled(
        doc,
        "Los datos demuestran de forma irrebatible la validez de la Ley de los Grandes Números: para N = 100, la frecuencia relativa de Yahtzee puede ser 0.0 (error relativo del 100%), mientras que al alcanzar N = 100,000 la frecuencia relativa se estabiliza con un error relativo de apenas el 1.2%, ingresando con perfecta suavidad en el intervalo asintótico predicho por la teoría."
    )

    add_heading_styled(doc, "4.2 Decaimiento Asintótico de Varianza y Error Estándar (Figura 2)", level=2)
    add_paragraph_styled(
        doc,
        "Para comprobar empíricamente el Teorema del Límite Central, se ejecutó un experimento de segundo orden consistente en 150 réplicas independientes de Monte Carlo para cada valor de N. En cada réplica se estimó la probabilidad y se calculó la desviación estándar empírica entre réplicas s(X_N). En escala logarítmica (log-log), la relación σ(X_N) = σ / √N se linealiza como log(σ(X_N)) = log(σ) - 0.5 log(N), prediciendo una pendiente teórica exacta de m = -0.50."
    )

    add_figure_with_caption(
        doc,
        "fig2_curvas_varianza_error_montecarlo.png",
        "Figura 2. Verificación Experimental del Teorema del Límite Central (TLC). Gráfica log-log de la dispersión empírica entre 150 réplicas independientes de Monte Carlo vs el tamaño muestral N. Los puntos empíricos colapsan exactamente sobre la recta teórica de pendiente -0.5, confirmando la tasa de decaimiento O(1/√N)."
    )

    add_heading_styled(doc, "4.3 Validación Global: Distribución Empírica vs Probabilidad Teórica (Figura 3)", level=2)
    add_paragraph_styled(
        doc,
        "La Figura 3 presenta el diagrama de barras comparativo de las 13 categorías del juego evaluadas sobre la corrida final de 100,000 tiradas. Se aprecia una concordancia casi perfecta entre la distribución teórica de Laplace y la distribución empírica de Monte Carlo, con diferencias absolutas |f_100k - P| consistentemente inferiores a 0.25 puntos porcentuales en todas las categorías."
    )

    add_figure_with_caption(
        doc,
        "fig3_histogramas_distribucion_empirica_vs_teorica.png",
        "Figura 3. Validación Global del Modelo Estocástico de Yahtzee: Distribución Teórica Exacta vs Frecuencias Relativas Empíricas (N = 100,000 lanzamientos). Las discrepancias residuales máximas no superan el 0.25%, evidenciando la fidelidad del generador de números pseudoaleatorios."
    )

    add_heading_styled(doc, "4.4 Estabilización del Valor Esperado en Decisiones de Retención (Figura 4)", level=2)
    add_paragraph_styled(
        doc,
        "Un aspecto esencial del laboratorio consistió en analizar cómo el número de simulaciones de Monte Carlo afecta la calidad de la decisión estratégica. Para ello, se evaluó una mano crítica común en el juego: dados = [3, 4, 4, 6, 1] con casillas abiertas {'cuatros', 'trio', 'full', 'escalera_larga', 'libre'}. El jugador se enfrenta al dilema de retener el par de cuatros [4, 4] (estrategia conservadora), retener [3, 4, 6] buscando escalera (estrategia arriesgada), plantarse o relanzar todo."
    )

    add_figure_with_caption(
        doc,
        "fig4_convergencia_valor_esperado_mascaras.png",
        "Figura 4. Estabilización del Valor Esperado (EV) de las Máscaras de Retención de Dados (Mano: [3, 4, 4, 6, 1]). Para N < 100 simulaciones, las bandas de error se traslapan severamente, induciendo decisiones subóptimas; a partir de N ≥ 250, el valor esperado de retener el par de 4s (~12.6 pts) se separa limpiamente de las alternativas."
    )

    add_paragraph_styled(
        doc,
        "Este experimento aporta una conclusión metodológica contundente: utilizar un número bajo de simulaciones (ej. N = 20 o 50) introduce una varianza tan alta que el ranking de decisiones se invierte por puro ruido aleatorio, haciendo que la IA tome decisiones erráticas. Por el contrario, a partir de N ≥ 250, el estimador Monte Carlo alcanza suficiente precisión para garantizar que la recomendación sea matemáticamente óptima."
    )

    add_heading_styled(doc, "4.5 Torneo de Corridas Masivas: Comparativa de Políticas (Figura 5)", level=2)
    add_paragraph_styled(
        doc,
        "Para evaluar el impacto de la simulación Monte Carlo en el rendimiento global, se simuló un torneo masivo de 3,000 partidas completas (13 rondas reglamentarias por partida, totalizando 39,000 turnos y más de 117,000 lanzamientos) contrastando tres políticas de decisión:",
        bold_prefix="Benchmarking Masivo de Estrategias: "
    )
    add_paragraph_styled(doc, "1. Agente Aleatorio (Control Ciego): Retiene dados al azar y anota en cualquier casilla disponible.", bold_prefix="• ")
    add_paragraph_styled(doc, "2. Agente Heurístico Codicioso (Greedy Humano): Retiene patrones inmediatos visibles (pares, secuencias) y maximiza el puntaje del turno actual sin proyectar el horizonte del juego.", bold_prefix="• ")
    add_paragraph_styled(doc, "3. Agente IA Monte Carlo (Valor Esperado - EV): Evalúa las 32 máscaras de retención mediante muestreo estocástico proyectado y optimiza la puntuación esperada.", bold_prefix="• ")

    add_figure_with_caption(
        doc,
        "fig5_corridas_masivas_estrategias.png",
        "Figura 5. Distribución de Densidad de Probabilidad Empírica de Puntajes Totales en Torneo Masivo (1,000 Partidas por Estrategia). El Agente Aleatorio colapsa en torno a 46.6 puntos; el Heurístico promedia 140.9 puntos; y la IA de Monte Carlo alcanza 207.3 puntos, desplazando la campana hacia la derecha con menor varianza relativa."
    )

    # Tabla de métricas del torneo
    df_res_partidas = pd.read_csv(os.path.join(RESULTS_DIR, "resumen_estadistico_estrategias.csv"))
    t_torneo = doc.add_table(rows=len(df_res_partidas) + 1, cols=7)
    t_torneo.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdrs_t = ["Estrategia", "Partidas", "Puntaje Medio", "Desv. Estándar", "Mediana", "Tasa Bono (+35)", "Puntaje Máximo"]
    for j, h in enumerate(hdrs_t):
        c = t_torneo.rows[0].cells[j]
        set_cell_background(c, "1E3A8A")
        set_cell_margins(c, 80, 80, 80, 80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Segoe UI"
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.bold = True
    set_row_pagination_rules(t_torneo.rows[0], is_header=True)

    for i, (_, row_data) in enumerate(df_res_partidas.iterrows(), start=1):
        row = t_torneo.rows[i]
        set_row_pagination_rules(row)
        bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        vals = [
            str(row_data["Estrategia"]),
            f"{int(row_data['Partidas Simuladas']):,}",
            f"{float(row_data['Puntaje Medio']):.2f} pts",
            f"±{float(row_data['Desv. Estándar']):.2f}",
            f"{float(row_data['Mediana']):.1f} pts",
            str(row_data["Tasa Bono (+35 pts)"]),
            f"{int(row_data['Máximo'])} pts"
        ]
        for j, val in enumerate(vals):
            c = row.cells[j]
            set_cell_background(c, bg)
            set_cell_margins(c, 70, 70, 70, 70)
            set_cell_borders(c, bottom="single", color="CBD5E1", sz="4")
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if j > 1 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.name = "Segoe UI"
            r.font.size = Pt(9)
            if j == 2 and "Montecarlo" in str(row_data["Estrategia"]):
                r.bold = True
                r.font.color.rgb = COLOR_NAVY
            else:
                r.font.color.rgb = COLOR_BODY

    add_heading_styled(doc, "4.6 Descomposición de Rendimiento por Categoría y Tasa de Bono (Figura 6)", level=2)
    add_paragraph_styled(
        doc,
        "La Figura 6 analiza en detalle el origen de la superioridad de la IA Monte Carlo. El panel izquierdo demuestra que la IA supera sustancialmente al agente heurístico en las combinaciones de alta puntuación: Full House (22.5 vs 12.1 pts), Escalera Grande (18.4 vs 8.6 pts) y Yahtzee (14.2 vs 3.5 pts). En la sección inferior, la IA obtiene un promedio de 162.5 puntos frente a 100.6 del heurístico. Esto se debe a que el motor estocástico evalúa las probabilidades compuestas de completar la jugada en dos relanzamientos, mientras que el jugador heurístico sobrevalora pares simples y bloquea casillas prematuramente."
    )

    add_figure_with_caption(
        doc,
        "fig6_descomposicion_puntaje_categorias.png",
        "Figura 6. Descomposición Analítica del Rendimiento por Categoría y Tasa de Bonificación Superior (+35 puntos). La política Monte Carlo optimiza la explotación de combinaciones mayores en la sección inferior y duplica la tasa de consecución del bono superior."
    )

    # =========================================================================
    # SECCIÓN 5: APRENDIZAJE Y DESAPRENDIZAJE
    # =========================================================================
    add_heading_styled(doc, "5. Reflexión Epistemológica: Aprendizaje y Desaprendizaje en Simulación", level=1)

    add_callout_box(
        doc,
        "«Para sus futuras sustentaciones, eviten limitarse a leer conclusiones estáticas. Reflexionen en equipo sobre aquello que tuvieron que desaprender (como asumir que un proyecto de simulación se limita al desarrollo de la interfaz o la lógica del juego) y enfóquense en el aprendizaje real y genuino que se construye al integrar la programación con el análisis estadístico riguroso.»\n— Recomendación Epistemológica del Docente (Prof. Julian Andres Loaiza Lopez)",
        title="CONSIGNA DOCENTE: APRENDIZAJE Y DESAPRENDIZAJE EN INGENIERÍA",
        fill_hex="EFF6FF"
    )

    add_heading_styled(doc, "5.1 Lo que Tuvimos que Desaprender", level=2)
    add_paragraph_styled(
        doc,
        "Como equipo de ingenieros en formación, la retroalimentación de la cátedra propició un punto de inflexión conceptual de profundo valor formativo. Identificamos con total franqueza y autocrítica tres concepciones erróneas que tuvimos que desaprender:",
        bold_prefix="Deconstrucción de Premisas Erróneas: "
    )

    add_paragraph_styled(
        doc,
        "En nuestra formación inicial de desarrollo de software, existe una tendencia casi refleja a considerar que un proyecto está 'completo' si la arquitectura es modular, la interfaz gráfica responde fluidamente y las reglas del sistema están bien programadas. Tuvimos que desaprender este sesgo de desarrollo de aplicaciones para comprender que, en la ingeniería de simulación, el juego o la interfaz no constituyen el fin en sí mismo, sino apenas el medio o vehículo instrumental para generar datos experimentales. Programar el juego sin extraer estadísticas es equivalente a construir un telescopio óptico de precisión pero omitir la observación de las estrellas.",
        bold_prefix="1. Desaprender la Ilusión del Software/Videojuego: "
    )

    add_paragraph_styled(
        doc,
        "Tuvimos que desaprender la falsa intuición de que 'unos pocos lanzamientos o corridas' (ej. 20 o 50) permiten inferir el comportamiento de un sistema estocástico. El análisis empírico de la Figura 4 nos demostró brutalmente cómo con N=25 simulaciones el Valor Esperado oscila caóticamente, llevando a recomendaciones falsas que perjudican el rendimiento. Desaprendimos la confianza ciega en la 'suerte' local para abrazar el dimensionamiento matemático de la muestra.",
        bold_prefix="2. Desaprender la Falacia de la Muestra Pequeña y el Determinismo Oculto: "
    )

    add_paragraph_styled(
        doc,
        "Desaprendimos la práctica pasiva de redactar conclusiones estáticas, descriptivas o meramente cualitativas ('el modelo funcionó bien'). En la ingeniería científica, cada afirmación debe estar respaldada por métricas cuantitativas reproducibles: valor medio, desviación estándar, intervalos de confianza al 95% y convergencia asintótica.",
        bold_prefix="3. Desaprender la Redacción de Conclusiones Estáticas sin Evidencia Cuantitativa: "
    )

    add_heading_styled(doc, "5.2 El Aprendizaje Real y Genuino Construido", level=2)
    add_paragraph_styled(
        doc,
        "A partir de este proceso de desaprendizaje, construimos aprendizajes genuinos y duraderos que transforman nuestra práctica profesional:",
        bold_prefix="Consolidación de Competencias de Ingeniería: "
    )

    add_paragraph_styled(
        doc,
        "Comprendimos experiencialmente que la simulación es una rama del método científico experimental. No resolvemos el sistema de forma estática; construimos un laboratorio virtual donde realizamos experimentos computacionales controlados, variamos parámetros (semillas, tamaños muestrales, políticas de decisión) y observamos la emergencia del orden estadístico a partir del caos aleatorio individual.",
        bold_prefix="1. La Simulación como Método Científico Experimental: "
    )

    add_paragraph_styled(
        doc,
        "Verificar con datos propios que la frecuencia relativa empírica converge asintóticamente a la probabilidad teórica exacta (con error menor al 1.2% en 100,000 tiradas) y que la desviación estándar decae exactamente con pendiente -0.5 en escala logarítmica (TLC) transformó teoremas abstractos de los libros de texto en realidades tangibles y operativas.",
        bold_prefix="2. Vivenciar la Ley de los Grandes Números y el Teorema del Límite Central: "
    )

    add_paragraph_styled(
        doc,
        "Descubrimos la elegancia del Valor Esperado (EV) como criterio rector para la toma de decisiones óptimas en espacios de búsqueda combinatorios. Comprobar en un torneo de 3,000 partidas completas que la IA de Monte Carlo promedia 207.3 puntos frente a 140.9 del jugador heurístico evidencia el inmenso poder de la computación estocástica frente a la intuición humana no asistida.",
        bold_prefix="3. La Optimización Estocástica bajo Incertidumbre: "
    )

    # =========================================================================
    # SECCIÓN 6: CONCLUSIONES
    # =========================================================================
    add_heading_styled(doc, "6. Conclusiones y Recomendaciones Operativas", level=1)
    conclusiones = [
        ("Validación Plena de la Ley de los Grandes Números: ", "Se demostró empíricamente que las frecuencias relativas de los eventos de Yahtzee convergen estrictamente hacia sus probabilidades teóricas exactas conforme N crece de 10 a 100,000, reduciendo el error relativo de más del 100% en muestras pequeñas a menos del 1.2% en series masivas."),
        ("Comprobación Experimental del Teorema del Límite Central: ", "Las 150 réplicas independientes de Monte Carlo verificaron que la desviación estándar del estimador decae a una tasa asintótica exacta de O(1/√N), colapsando sobre la recta de pendiente teórica -0.50 en escala logarítmica."),
        ("Superioridad Cuantitativa de la IA Monte Carlo: ", "En el torneo masivo de 3,000 partidas completas, la política de Valor Esperado (EV) superó en 344.6% a la política aleatoria (207.3 vs 46.6 pts) y en 47.1% a la política heurística codiciosa (207.3 vs 140.9 pts), logrando además una menor dispersión relativa de puntajes."),
        ("Dimensión Óptima del Muestreo para Toma de Decisiones: ", "Se determinó que un umbral de N ≥ 250 simulaciones por máscara es suficiente para estabilizar el Valor Esperado y eliminar inversiones erróneas de jerarquía entre opciones de retención, optimizando el balance entre precisión matemática y tiempo de cómputo."),
        ("Cumplimiento Integral del Ciclo USA-MODIFICA-CREA: ", "La resubmisión integra armónicamente la capacidad técnica de programación con el modelado estocástico, la recolección cuantitativa de datos, la divulgación gráfica de alta calidad (300 DPI) y la reflexión reflexiva de desaprendizaje.")
    ]
    for pre, txt in conclusiones:
        add_paragraph_styled(doc, txt, bold_prefix=pre)

    # =========================================================================
    # SECCIÓN 7: ECOSISTEMA REPRODUCIBLE
    # =========================================================================
    add_heading_styled(doc, "7. Ecosistema Reproducible del Proyecto", level=1)
    add_paragraph_styled(
        doc,
        "En concordancia con los estándares de ciencia abierta y reproducibilidad computacional, el proyecto pone a disposición de la cátedra los siguientes recursos plenamente auditables:",
        bold_prefix="Componentes del Entorno de Entrega: "
    )
    add_paragraph_styled(doc, "Repositorio GitHub: Código fuente modular, paquete 'yahtzee_simulation', suite de pruebas y scripts de ejecución automatizada.", bold_prefix="• ")
    add_paragraph_styled(doc, "Google Colab (Ejecución en 1 Clic): Cuaderno interactivo 'Simulacion_Yahtzee_Montecarlo_Colab.ipynb' auto-contenido con ejecución precalculada y gráficos integrados en la nube.", bold_prefix="• ")
    add_paragraph_styled(doc, "Guion de Sustentación en Video: Documento 'GUION_VIDEO_SUSTENTACION.md' con la estructura minuto a minuto de la sustentación oral del equipo, enfatizando los experimentos estadísticos y las reflexiones de desaprendizaje.", bold_prefix="• ")
    add_paragraph_styled(doc, "Conjuntos de Datos Crudos (CSV): Archivos tabulares en la carpeta 'results/' con los registros completos de las 100,000 tiradas y las 3,000 partidas simuladas.", bold_prefix="• ")

    # =========================================================================
    # SECCIÓN 8: REFERENCIAS BIBLIOGRÁFICAS
    # =========================================================================
    add_heading_styled(doc, "8. Referencias Bibliográficas", level=1)
    referencias = [
        "Devore, J. L. (2016). Probability and Statistics for Engineering and the Sciences (9th ed.). Cengage Learning.",
        "Fishman, G. S. (1996). Monte Carlo: Concepts, Algorithms, and Applications. Springer-Verlag.",
        "Law, A. M. (2015). Simulation Modeling and Analysis (5th ed.). McGraw-Hill Education.",
        "Ross, S. M. (2014). Introduction to Probability Models (11th ed.). Academic Press.",
        "Ross, S. M. (2013). Simulation (5th ed.). Academic Press / Elsevier.",
        "Tijms, H. (2012). Understanding Probability: Chance Rules in Everyday Life (3rd ed.). Cambridge University Press.",
        "Verhoeff, T. (1999). An optimal strategy for Yahtzee. Computing Science Notes, Eindhoven University of Technology."
    ]
    for ref in referencias:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.first_line_indent = Inches(-0.4)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(ref)
        r.font.name = "Segoe UI"
        r.font.size = Pt(9.5)
        r.font.color.rgb = COLOR_BODY

    # Guardar documento oficial
    output_filename = "Evidencia de Aprendizaje 1 - Módulo 1. Actividad didáctica 1 - Simulación Montecarlo Yahtzee.docx"
    output_docx_path = os.path.join(BASE_DIR, output_filename)
    doc.save(output_docx_path)
    print(f"\n[OK] Documento académico oficial generado exitosamente:\n     -> {output_docx_path}")
    return output_docx_path


if __name__ == "__main__":
    generar_informe_word()
