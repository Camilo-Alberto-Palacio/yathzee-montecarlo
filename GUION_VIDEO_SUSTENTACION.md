# Guion de Sustentación en Video — Actividad Didáctica 1 (Módulo 1)
## Simulación Estocástica de Yahtzee con Método Monte Carlo y Comprobación Experimental de la Ley de los Grandes Números

* **Institución:** Institución Universitaria Digital de Antioquia (IU Digital) — Facultad de Ingeniería
* **Asignatura:** Simulación (`PREICA2602B020045`) — Grupo 25
* **Docente Catedrático:** Julian Andres Loaiza Lopez
* **Duración Total Estimada:** 8 a 10 minutos
* **Participantes (4 Integrantes):**
  1. **Adriana Andrea Agudelo Agudelo** (Introducción, Diagnóstico y Metodología USA-MODIFICA-CREA)
  2. **Camilo Alberto Palacios Turriago** (Fundamentación Matemática: Espacio Muestral, LLN y TLC)
  3. **Juan Daniel Pulgarin García** (Resultados Cuantitativos: Convergencia, Varianza y Torneo de 3,000 Partidas)
  4. **Ruben Dario Jaramillo Cervantes** (Reflexión de Desaprendizaje / Aprendizaje Genuino y Conclusiones)

---

### Escena 1: Apertura, Contexto y Diagnóstico Autocrítico (0:00 – 2:00)
**Voz / Pantalla:** Adriana Andrea Agudelo Agudelo  
**Recurso Visual:** Diapositiva de Portada Institucional + Visualización de la Interfaz Tkinter (`interfaz_yahtzee.py`).

> **Adriana:**  
> "Un cordial saludo al profesor Julian Andres Loaiza y a la comunidad académica. Somos el Grupo 25 de la asignatura Simulación en la IU Digital de Antioquia, integrado por Camilo Palacios, Juan Daniel Pulgarin, Ruben Jaramillo y mi persona, Adriana Agudelo.
> 
> En nuestra primera entrega de este laboratorio alcanzamos una calificación de 52 sobre 100. El dictamen docente reconoció la solidez en la programación del juego de Yahtzee y el desarrollo de nuestra interfaz gráfica en Tkinter; sin embargo, nos confrontó con una omisión fundamental: nos concentramos en construir el juego y dejamos por fuera la esencia del laboratorio, que era utilizar la **Simulación de Monte Carlo** para ejecutar iteraciones masivas, recolectar frecuencias relativas y generar evidencia gráfica de la **Ley de los Grandes Números**.
> 
> Lejos de desalentarnos, tomamos con máxima seriedad la oportunidad de resubmisión. Para subsanar esto de raíz, adoptamos de forma estricta el ciclo metodológico **USA, MODIFICA y CREA**:
> * En **USA**, inspeccionamos el modelo base de Yahtzee y su espacio muestral de 7,776 combinaciones.
> * En **MODIFICA**, reestructuramos el código con NumPy para permitir muestreos vectorizados de alto rendimiento y parametrizar las 32 máscaras de retención.
> * Y en **CREA**, construimos un laboratorio estocástico completo que ejecutó 100,000 tiradas individuales y un torneo de 3,000 partidas completas.
> 
> A continuación, mi compañero Camilo Palacios expondrá la base matemática que sustenta este modelo."

---

### Escena 2: Fundamentación Teórica y Formulación Estocástica (2:00 – 4:00)
**Voz / Pantalla:** Camilo Alberto Palacios Turriago  
**Recurso Visual:** Fórmulas del Espacio de Probabilidad $(\Omega, \mathcal{F}, P)$, Ecuación de la Ley de los Grandes Números y Teorema del Límite Central.

> **Camilo:**  
> "Gracias, Adriana. Para entender por qué la simulación es rigurosa, debemos partir de la verdad matemática fundamental.
> 
> Al lanzar 5 dados estándar de 6 caras, el espacio muestral es $\Omega = \{1, 2, 3, 4, 5, 6\}^5$, con una cardinalidad exacta de $|\Omega| = 6^5 = 7,776$ resultados elementales equiprobables. Mediante combinatoria analítica exacta, dedujimos los casos favorables de cada categoría:
> * Por ejemplo, para **Yahtzee** (5 dados idénticos), existen únicamente 6 configuraciones favorables entre 7,776, lo que arroja una probabilidad teórica exacta de $P = 6/7776 \approx 0.0772\%$.
> * Para **Full House**, son 306 combinaciones favorables (3.9352%); para **Escalera Grande**, 240 combinaciones (3.0864%); y para **Escalera Pequeña**, 1,200 combinaciones (15.4321%).
> 
> ¿Cómo se conecta esto con Monte Carlo? A través de la **Ley de los Grandes Números (LLN)**. Cada lanzamiento se modela con una variable indicadora de Bernoulli $I_A^{(i)}$. La Ley Débil de Khinchin y la Ley Fuerte de Kolmogorov garantizan que la frecuencia relativa muestral $f_N(A) = \frac{1}{N} \sum I_A^{(i)}$ converge casi con seguridad hacia la probabilidad teórica $P(A)$ cuando $N \to \infty$.
> 
> Además, por el **Teorema del Límite Central (TLC)**, sabemos exactamente cómo se comporta el error: la varianza del estimador decae como $\text{Var}(f_N) = \frac{p(1-p)}{N}$ y el error estándar decae como $\mathcal{O}(1/\sqrt{N})$. Esto significa que para duplicar la precisión debemos cuadruplicar las muestras.
> 
> Ahora, Juan Daniel Pulgarin nos mostrará los resultados cuantitativos obtenidos en las corridas masivas."

---

### Escena 3: Evidencia Experimental y Visualizaciones a 300 DPI (4:00 – 6:30)
**Voz / Pantalla:** Juan Daniel Pulgarin García  
**Recurso Visual:** Transición por las Figuras 1, 2, 3, 4 y 5 generadas en la carpeta `results/`.

> **Juan Daniel:**  
> "Gracias, Camilo. Entrando de lleno en la evidencia cuantitativa que nos exigió el profesor, diseñamos un pipeline reproducible que generó seis figuras de alta resolución a 300 DPI y tablas exportadas en CSV.
> 
> En la **Figura 1**, observamos la comprobación directa de la Ley de los Grandes Números para 100,000 tiradas simuladas en escala logarítmica. Para muestras pequeñas de $N < 100$, el error relativo es superior al 100% debido a la alta dispersión. Sin embargo, al cruzar $N = 10,000$ y llegar a $100,000$, las frecuencias relativas colapsan limpiamente dentro de las bandas de confianza del 95%, alcanzando un error relativo inferior al 1.2% frente a la probabilidad analítica.
> 
> En la **Figura 2**, comprobamos empíricamente el Teorema del Límite Central mediante 150 réplicas independientes de Monte Carlo para cada valor de $N$. En escala log-log, la dispersión observada entre réplicas se ajusta con total precisión sobre la recta de pendiente teórica $-0.5$, demostrando la tasa de decaimiento $\mathcal{O}(1/\sqrt{N})$.
> 
> En la **Figura 3**, contrastamos el histograma empírico de las 13 categorías contra la distribución de Laplace, evidenciando discrepancias residuales menores a 0.25 puntos porcentuales.
> 
> La **Figura 4** ilustra la toma de decisiones: muestra cómo evoluciona el **Valor Esperado (EV)** de 4 opciones de retención en una mano crítica `[3, 4, 4, 6, 1]`. Con menos de 100 simulaciones, las curvas se cruzan por azar; pero con $N \ge 250$, se estabiliza con certeza que retener el par de 4s es la jugada óptima (EV ≈ 12.6 puntos).
> 
> Finalmente, en la **Figura 5**, llevamos a cabo un torneo masivo de **3,000 partidas completas** (39,000 turnos). Los resultados fueron contundentes:
> * El **Agente Aleatorio** promedió 46.6 puntos.
> * El **Agente Heurístico Greedy** promedió 140.9 puntos.
> * Y nuestro **Agente IA Monte Carlo** alcanzó **207.3 puntos**, superando al heurístico en un 47.1% y al aleatorio en más del 340%, con menor varianza relativa y duplicando la tasa de bonificación superior de 35 puntos.
> 
> Doy paso a Ruben Jaramillo para compartir nuestra reflexión sobre desaprendizaje y aprendizaje genuino."

---

### Escena 4: Reflexión de Aprendizaje, Desaprendizaje y Cierre (6:30 – 9:00)
**Voz / Pantalla:** Ruben Dario Jaramillo Cervantes  
**Recurso Visual:** Diapositiva con el Cuadro de Aprendizaje / Desaprendizaje + Cuaderno de Google Colab ejecutado en vivo.

> **Ruben:**  
> "Muchas gracias, Juan Daniel. Llegamos a la parte más formativa y enriquecedora de este trabajo: la reflexión sobre aquello que tuvimos que **desaprender** para construir un **aprendizaje genuino**, tal como nos lo sugirió el profesor Julian Loaiza.
> 
> En nuestro equipo tuvimos que desaprender tres premisas muy arraigadas:
> 1. **Primero, desaprendimos la 'ilusión del videojuego':** Como estudiantes de ingeniería informática solemos pensar que un proyecto está listo cuando la interfaz se ve bien y el juego es divertido. Desaprendimos ese sesgo al comprender que en la ingeniería de simulación el juego es solo el dominio del problema; el núcleo verdadero es el modelado estocástico, el muestreo masivo y la inferencia estadística.
> 2. **Segundo, desaprendimos la falacia de la muestra pequeña:** Antes creíamos intuitivamente que 20 o 30 corridas bastaban para ver si algo funcionaba. La evidencia de la Figura 4 nos enseñó que la varianza en muestras pequeñas engaña y produce decisiones erráticas.
> 3. **Tercero, desaprendimos las conclusiones estáticas:** Abandonamos las afirmaciones vagas para sustentar cada conclusión con medias, desviaciones estándar, intervalos de confianza y gráficas de convergencia.
> 
> ¿Y qué aprendimos genuinamente?
> * Aprendimos que la simulación es un **laboratorio experimental de ciencia de datos**.
> * Comprendimos cómo la certidumbre matemática de la **Ley de los Grandes Números** emerge del caos aparente gracias a la agregación estocástica.
> * Dominamos el **Valor Esperado** como criterio riguroso para la toma de decisiones bajo incertidumbre en espacios NP-difíciles.
> 
> Nuestro proyecto entrega un ecosistema reproducible completo: el paquete en Python, la suite de pruebas unitarias con 100% de éxito, los conjuntos de datos en CSV, el informe técnico oficial de 24 páginas en Word con formato institucional y un cuaderno en Google Colab ejecutable en la nube con un solo clic.
> 
> Agradecemos al profesor Julian Andres Loaiza por la exigencia y la retroalimentación que nos impulsó a transformar una simple aplicación en una verdadera investigación aplicada de ingeniería estocástica. ¡Muchas gracias!"

---

### Consejos Técnicos para la Grabación del Video
1. **Resolución y Audio:** Grabar a 1080p con micrófono claro sin eco (usar OBS Studio, Teams o Zoom).
2. **Distribución de Roles:** Cada integrante interviene aproximadamente 2 minutos, manteniendo fluidez en las transiciones.
3. **Apoyo Visual:** Compartir pantalla alternando entre las diapositivas de presentación, las 6 figuras de la carpeta `results/` y el cuaderno de Google Colab en vivo.
