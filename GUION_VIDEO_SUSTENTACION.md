# Guion de Sustentación en Video — Actividad Didáctica 1 (Módulo 1)
## Simulación Estocástica de Yahtzee con Método Monte Carlo y Comprobación Experimental de la Ley de los Grandes Números

* **Institución:** Institución Universitaria Digital de Antioquia (IU Digital) — Facultad de Ingeniería
* **Asignatura:** Simulación (`PREICA2602B020045`) — Grupo 25
* **Docente Catedrático:** Julian Andres Loaiza Lopez
* **Duración Total Estimada:** 8 a 10 minutos
* **Participantes (4 Integrantes):**
  1. **Adriana Andrea Agudelo Agudelo** (Diagnóstico Autocrítico y Ciclo USA-MODIFICA-CREA)
  2. **Camilo Alberto Palacios Turriago** (Combinatoria Exacta $|\Omega|=7,776$, LLN, $\chi^2$ y TLC)
  3. **Juan Daniel Pulgarin García** (Análisis de las 6 Figuras a 300 DPI y Torneo de 3,000 Partidas)
  4. **Ruben Dario Jaramillo Cervantes** (Reflexión de Desaprendizaje / Aprendizaje Genuino y Colab en Vivo)

---

### Escena 1: Apertura, Diagnóstico Autocrítico y Ciclo USA-MODIFICA-CREA (0:00 – 2:00)
**Voz / Pantalla:** Adriana Andrea Agudelo Agudelo  
**Recurso Visual:** Portada Institucional + Interfaz `interfaz_yahtzee.py` con ventana modal de Estadísticas Monte Carlo.

> **Adriana:**  
> "Un cordial saludo al profesor Julian Andres Loaiza. Somos el Grupo 25 de Simulación en la IU Digital de Antioquia, conformado por Camilo Palacios, Juan Daniel Pulgarin, Ruben Jaramillo y quien les habla, Adriana Agudelo.
> 
> En nuestra primera entrega obtuvimos 52 sobre 100 porque enfocamos todo el esfuerzo en construir la interfaz del juego y omitimos la esencia científica del laboratorio: utilizar el método de Monte Carlo para ejecutar corridas masivas, medir frecuencias relativas y comprobar gráficamente la **Ley de los Grandes Números**.
> 
> Asumimos esa retroalimentación para reestructurar el proyecto aplicando rigurosamente el ciclo **USA, MODIFICA y CREA**:
> * En **USA**, auditamos el código base verificando la paridad exacta de las 13 categorías sobre los 7,776 estados del espacio muestral.
> * En **MODIFICA**, vectorizamos el motor en NumPy con el generador PCG64, reduciendo el tiempo de cómputo de más de 19 minutos a solo 19 segundos.
> * Y en **CREA**, diseñamos cuatro experimentos estocásticos masivos con pruebas Chi-Cuadrado, 6 figuras a 300 DPI y un torneo de 3,000 partidas completas.
> 
> Doy paso a Camilo Palacios con la fundamentación matemática."

---

### Escena 2: Espacio Muestral Exacto, Ley de los Grandes Números y TLC (2:00 – 4:00)
**Voz / Pantalla:** Camilo Alberto Palacios Turriago  
**Recurso Visual:** Tabla Combinatoria de $\Omega$ y ecuaciones de LLN, $\chi^2$ y TLC.

> **Camilo:**  
> "Gracias, Adriana. Al lanzar 5 dados equilibrados de 6 caras, el espacio muestral tiene $|\Omega| = 6^5 = 7,776$ microestados equiprobables. Calculamos de forma cerrada los casos favorables exactos de las 13 categorías:
> * **Yahtzee** tiene 6 casos favorables ($6/7776 = 0.0772\%$); **Póker**, 156 casos ($2.0062\%$); **Full House** puro (un trío y un par distintos), **300 casos** ($300/7776 = 3.8580\%$); **Escalera Grande**, 240 ($3.0864\%$); **Escalera Pequeña**, 1,200 ($15.4321\%$); **Trío**, 1,656 ($21.2963\%$); y cada cara de la **Sección Superior**, $6^5 - 5^5 = 4,651$ casos ($59.8122\%$).
> 
> Por la **Ley Fuerte de los Grandes Números** de Kolmogorov, la frecuencia relativa acumulada $f_N(A)$ converge casi con seguridad hacia $P(A)$ cuando $N \to \infty$, transitando desde una **fase de calentamiento** volátil hacia un **estado estable**.
> 
> Y por el **Teorema del Límite Central**, el error estándar decae como $\sigma/\sqrt{N}$, lo que en escala logarítmica doble equivale a una recta de pendiente exacta **$-0.50$**. Además, sometimos el generador a pruebas formales **Chi-Cuadrado ($\chi^2$)** de uniformidad y partición multinomial. Juan Daniel nos presentará ahora la evidencia experimental."

---

### Escena 3: Evidencia Experimental en las 6 Figuras a 300 DPI (4:00 – 6:45)
**Voz / Pantalla:** Juan Daniel Pulgarin García  
**Recurso Visual:** Figuras 1 a 6 en `results/`.

> **Juan Daniel:**  
> "Gracias, Camilo. En la **Figura 1**, simulamos 100,000 lanzamientos evaluando las 13 categorías reales. En la zona ámbar de calentamiento ($N \le 200$), Yahtzee presenta un error relativo del 100%, pero en el estado estable a los 100,000 tiros converge a 78 casos ($0.0780\%$, error relativo de apenas $1.09\%$) y Full House a 3,885 casos ($3.8850\%$, error relativo de $0.70\%$).
> 
> En la **Figura 2**, ejecutamos 200 réplicas independientes por nivel muestral. La regresión lineal log-log arrojó pendientes empíricas de **$-0.474$** ($R^2 = 0.9925$) en Yahtzee y **$-0.477$** ($R^2 = 0.9954$) en Full House, comprobando la ley $\mathcal{O}(1/\sqrt{N})$ del TLC.
> 
> En la **Figura 3**, validamos las **13 categorías completas**: todas las discrepancias absolutas fueron menores a **0.24 puntos porcentuales**, y las pruebas Chi-Cuadrado confirmaron tanto la uniformidad de los 500,000 dados ($p = 0.739$) como la partición combinatoria de $\Omega$ ($p = 0.973$).
> 
> En la **Figura 4**, sobre la mano táctica `[3, 4, 4, 6, 1]` sin comodín `libre`, demostramos que la jugada óptima exacta es **Retener el Par `[4, 4]`** con **EV exacto de 13.56 puntos**. Con $N=10$ simulaciones la IA se equivoca en el **31.0%** de las réplicas por ruido aleatorio, mientras que desde $N \ge 100$ (y con nuestro umbral operativo $N=250$) alcanza el **100% de precisión**.
> 
> Finalmente, en las **Figuras 5 y 6**, simulamos **3,000 partidas completas**: el Agente Aleatorio promedió **44.85 puntos**, el Heurístico **140.34 puntos**, y nuestro **Agente IA Monte Carlo alcanzó 217.38 puntos** (+54.9% sobre el Heurístico). La Figura 6 revela el porqué: mientras el Heurístico persigue ciegamente pares y tríos (obteniendo algo más en Póker y Yahtzee aislado, pero destruyendo Escalera Grande a 0.6 puntos), nuestra IA Monte Carlo domina **11 de las 13 categorías** (34.6 puntos en Escalera Grande) y multiplica por **12 veces** la obtención del Bono Superior de +35 puntos (**16.9% vs 1.4%**), generando incluso un segundo pico bimodal sobre los 255 puntos. Doy paso a Ruben."

---

### Escena 4: Desaprendizaje, Aprendizaje Genuino y Cierre en Colab (6:45 – 9:00)
**Voz / Pantalla:** Ruben Dario Jaramillo Cervantes  
**Recurso Visual:** Cuaderno `Simulacion_Yahtzee_Montecarlo_Colab.ipynb` pre-ejecutado.

> **Ruben:**  
> "Muchas gracias, Juan Daniel. Siguiendo la invitación formativa del profesor Julian Loaiza, reflexionamos en equipo sobre lo que tuvimos que **desaprender**:
> 1. **Desaprendimos el sesgo del videojuego:** Entendimos que en ingeniería de simulación el software no es el producto final, sino el instrumento de laboratorio para extraer evidencia estocástica.
> 2. **Desaprendimos la intuición de muestras pequeñas y reglas codiciosas:** Vimos con datos propios cómo $N=10$ falla el 31% de las veces y cómo una heurística intuitiva sacrifica casi 77 puntos por partida frente al Valor Esperado.
> 3. **Desaprendimos la validación superficial:** Auditamos cada tabla, gráfica y prueba unitaria (12 de 12 aprobadas) para garantizar trazabilidad matemática total.
> 
> ¿Qué **aprendizaje genuino** construimos? Vivenciamos la transición del caos transitorio al orden asintótico de la Ley de los Grandes Números, medimos el costo cuadrático de reducir el error con el TLC y diseñamos un agente inteligente capaz de optimizar decisiones bajo incertidumbre real.
> 
> Entregamos el repositorio completo, los datos CSV, el informe técnico en Word y este cuaderno de Google Colab 100% autocontenido y pre-ejecutado. ¡Muchas gracias, profesor, por impulsarnos a dar este salto de calidad científica!"
