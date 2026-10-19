"""
=============================================================================
  YAHTZEE MONTECARLO - INTERFAZ GRÁFICA
=============================================================================

Juega Yahtzee contra una IA que decide usando el MÉTODO MONTECARLO.

Este archivo SOLO se encarga de la parte visual (ventana, botones, tabla).
Toda la lógica de la simulación está en "yahtzee_montecarlo.py" y la
importamos desde aquí. Así se ve claramente qué es "simulación" y qué es
"interfaz".

Cómo ejecutarlo:   python interfaz_yahtzee.py

Cómo se juega:
  1. Clic en "Tirar los dados" (máximo 3 tiradas por turno).
  2. Clic en un dado para GUARDARLO (se pone amarillo) y que no se relance.
  3. Si tienes dudas, clic en "Pedir consejo a la IA".
  4. Clic en una casilla de la columna "Tú" para anotar tus puntos.
     (Los números grises te muestran cuánto ganarías en cada casilla.)
  5. Luego juega la IA sola, y te explica qué decide y por qué.
=============================================================================
"""

import random
import tkinter as tk

# Importamos la lógica de la simulación desde nuestro otro archivo
from yahtzee_montecarlo import (
    CATEGORIAS,                   # Las 13 casillas
    calcular_puntos,              # Puntos de una mano en una casilla
    mejor_puntaje,                # Mejor casilla para una mano
    relanzar_dados,               # Relanza los dados no guardados
    evaluar_todas_las_opciones,   # EL NÚCLEO MONTECARLO
)

# yahtzee_montecarlo.py fija la semilla en 42 (para la clase).
# En el juego queremos azar de verdad, así que la "reiniciamos".
random.seed()

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
SIMULACIONES_IA = 200          # Lanzamientos simulados por cada opción
TIRADAS_POR_TURNO = 3
BONO_MINIMO = 63               # Si la sección superior suma 63 o más...
BONO_PUNTOS = 35               # ...ganas 35 puntos extra

SUPERIORES = CATEGORIAS[:6]    # unos ... seises
INFERIORES = CATEGORIAS[6:]    # trio ... libre

# Nombres bonitos para mostrar en la tabla
NOMBRES = {
    "unos": "Unos", "doses": "Doses", "treses": "Treses",
    "cuatros": "Cuatros", "cincos": "Cincos", "seises": "Seises",
    "suma": "Suma", "bono": "Bonificación (+35)",
    "trio": "Trío", "poker": "Póker (4 iguales)", "full": "Full House",
    "escalera_corta": "Escalera pequeña", "escalera_larga": "Escalera grande",
    "yahtzee": "YAHTZEE", "libre": "Libre (Chance)",
    "total": "PUNTUACIÓN TOTAL",
}

# Colores
VERDE = "#1e8449"
VERDE_OSCURO = "#145a32"
AMARILLO = "#f7f48b"
AMARILLO_FUERTE = "#f5b700"
AZUL = "#29b6f6"
ROJO_PUNTO = "#c0392b"
GRIS = "#9e9e9e"
FILA_ESPECIAL = "#e8f5e9"

FUENTE = ("Segoe UI", 11)
FUENTE_NEGRITA = ("Segoe UI", 11, "bold")
FUENTE_GRANDE = ("Segoe UI", 16, "bold")
FUENTE_CURSIVA = ("Segoe UI", 11, "italic")

# Posición de los puntos de cada cara del dado (en proporción 0 a 1)
PUNTOS_DADO = {
    1: [(.5, .5)],
    2: [(.27, .27), (.73, .73)],
    3: [(.27, .27), (.5, .5), (.73, .73)],
    4: [(.27, .27), (.73, .27), (.27, .73), (.73, .73)],
    5: [(.27, .27), (.73, .27), (.5, .5), (.27, .73), (.73, .73)],
    6: [(.27, .25), (.73, .25), (.27, .5), (.73, .5), (.27, .75), (.73, .75)],
}
TAMANO_DADO = 66


# =============================================================================
# FUNCIONES DE AYUDA (texto)
# =============================================================================
def texto_jugada(mano, mascara):
    """Convierte una máscara en texto: 'Guarda 4, 6  ·  Relanza 3, 4, 1'."""
    guardados = [str(mano[i]) for i in range(5) if mascara[i]]
    relanzados = [str(mano[i]) for i in range(5) if not mascara[i]]
    guarda = ", ".join(guardados) if guardados else "nada"
    relanza = ", ".join(relanzados) if relanzados else "nada"
    return f"Guarda {guarda}  ·  Relanza {relanza}"


def mejores_distintas(mano, resultados, cantidad=3):
    """
    Toma la lista de resultados Montecarlo y devuelve las 'cantidad' mejores
    jugadas SIN repetir (guardar "el primer 4" o "el segundo 4" es lo mismo).
    """
    elegidas, vistas = [], []
    for promedio, mascara in resultados:
        guardados = sorted(mano[i] for i in range(5) if mascara[i])
        if guardados not in vistas:
            vistas.append(guardados)
            elegidas.append((promedio, mascara))
        if len(elegidas) == cantidad:
            break
    return elegidas


# =============================================================================
# LA VENTANA DEL JUEGO
# =============================================================================
class JuegoYahtzee:

    def __init__(self, ventana):
        self.ventana = ventana
        ventana.title("Yahtzee Montecarlo")
        ventana.configure(bg=VERDE)
        ventana.resizable(False, False)

        self.construir_mesa()
        self.construir_tabla()
        self.nueva_partida()

    # -------------------------------------------------------------------------
    # ESTADO DEL JUEGO
    # -------------------------------------------------------------------------
    def nueva_partida(self):
        """Pone todo en cero para empezar a jugar."""
        self.puntos = {"tu": {}, "ia": {}}   # Casillas ya anotadas de cada jugador
        self.ronda = 1
        self.empezar_turno("tu")
        self.mostrar_mensaje('Haz clic en "Tirar los dados" para comenzar.')
        self.texto_consejo.config(
            text="Aquí verás cómo piensa la IA.\n\n"
                 "Cuando tengas dados en la mesa, pulsa\n"
                 '"Pedir consejo a la IA".'
        )

    def empezar_turno(self, jugador):
        """Prepara un turno nuevo: dados vacíos, nada guardado, 0 tiradas."""
        self.turno = jugador
        self.dados = [0, 0, 0, 0, 0]          # 0 = todavía no se ha lanzado
        self.guardados = [False] * 5
        self.tiradas_usadas = 0
        self.mascara_sugerida = None
        self.animando = False
        self.actualizar_todo()

    def casillas_libres(self, jugador):
        """Casillas que ese jugador todavía no ha usado."""
        return [c for c in CATEGORIAS if c not in self.puntos[jugador]]

    def totales(self, jugador):
        """Calcula (suma superior, bono, total) de un jugador."""
        p = self.puntos[jugador]
        suma = sum(p.get(c, 0) for c in SUPERIORES)
        bono = BONO_PUNTOS if suma >= BONO_MINIMO else 0
        total = suma + bono + sum(p.get(c, 0) for c in INFERIORES)
        return suma, bono, total

    # -------------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA PARTE IZQUIERDA (la mesa)
    # -------------------------------------------------------------------------
    def construir_mesa(self):
        mesa = tk.Frame(self.ventana, bg=VERDE, padx=25, pady=20)
        mesa.grid(row=0, column=0, sticky="n")

        # --- Jugador IA (arriba) ---
        self.etiqueta_ia = tk.Label(mesa, text="🤖  IA Montecarlo",
                                    font=FUENTE_GRANDE, bg=VERDE, fg="white")
        self.etiqueta_ia.pack()

        # --- Ronda ---
        self.etiqueta_ronda = tk.Label(mesa, font=FUENTE, bg=VERDE, fg="#d5f5e3")
        self.etiqueta_ronda.pack(pady=(2, 10))

        # --- Mensaje amarillo (qué está pasando) ---
        self.mensaje = tk.Label(mesa, font=FUENTE, bg=AMARILLO, fg="#333",
                                wraplength=430, justify="left",
                                padx=12, pady=8, width=48, anchor="w")
        self.mensaje.pack(pady=(0, 12))

        # --- Panel "Cerebro de la IA" (resultados Montecarlo) ---
        panel = tk.Frame(mesa, bg=VERDE_OSCURO, padx=12, pady=10)
        panel.pack(fill="x")
        tk.Label(panel, text="🧠  Cerebro de la IA (Montecarlo)",
                 font=FUENTE_NEGRITA, bg=VERDE_OSCURO, fg=AMARILLO).pack(anchor="w")
        self.texto_consejo = tk.Label(panel, font=FUENTE, bg=VERDE_OSCURO,
                                      fg="white", justify="left", anchor="w",
                                      height=7, width=48)
        self.texto_consejo.pack(anchor="w", pady=(6, 0))

        # --- Dados ---
        zona_dados = tk.Frame(mesa, bg=VERDE)
        zona_dados.pack(pady=(22, 4))
        self.lienzos_dados = []
        self.etiquetas_guardado = []
        for i in range(5):
            columna = tk.Frame(zona_dados, bg=VERDE)
            columna.grid(row=0, column=i, padx=6)
            lienzo = tk.Canvas(columna, width=TAMANO_DADO, height=TAMANO_DADO,
                               bg=VERDE, highlightthickness=0, cursor="hand2")
            lienzo.pack()
            lienzo.bind("<Button-1>", lambda e, pos=i: self.clic_en_dado(pos))
            etiqueta = tk.Label(columna, text="", font=("Segoe UI", 9, "bold"),
                                bg=VERDE, fg=AMARILLO)
            etiqueta.pack()
            self.lienzos_dados.append(lienzo)
            self.etiquetas_guardado.append(etiqueta)

        # --- Indicador de tiradas ---
        self.etiqueta_tiradas = tk.Label(mesa, font=FUENTE, bg=VERDE, fg="white")
        self.etiqueta_tiradas.pack(pady=(0, 8))

        # --- Botones ---
        botones = tk.Frame(mesa, bg=VERDE)
        botones.pack()
        self.boton_tirar = self.crear_boton(botones, "🎲  Tirar los dados",
                                            self.tirar_dados, ancho=18)
        self.boton_tirar.grid(row=0, column=0, padx=5)
        self.boton_consejo = self.crear_boton(botones, "💡  Pedir consejo a la IA",
                                              self.pedir_consejo, ancho=22)
        self.boton_consejo.grid(row=0, column=1, padx=5)
        self.boton_usar = self.crear_boton(mesa, "Usar este consejo",
                                           self.usar_consejo, ancho=18)
        self.boton_usar.pack(pady=(8, 0))

        # --- Jugador humano (abajo) ---
        self.etiqueta_tu = tk.Label(mesa, text="🙂  Tú", font=FUENTE_GRANDE,
                                    bg=VERDE, fg="white")
        self.etiqueta_tu.pack(pady=(14, 0))

    def crear_boton(self, padre, texto, accion, ancho):
        """Crea un botón con estilo y efecto al pasar el mouse."""
        boton = tk.Button(padre, text=texto, command=accion, font=FUENTE_NEGRITA,
                          width=ancho, bg="#fdfefe", fg="#1b2631",
                          activebackground=AMARILLO, relief="raised", bd=2,
                          cursor="hand2", disabledforeground="#aab7b8")
        boton.bind("<Enter>", lambda e: boton.config(bg=AMARILLO)
                   if boton["state"] == "normal" else None)
        boton.bind("<Leave>", lambda e: boton.config(bg="#fdfefe"))
        return boton

    # -------------------------------------------------------------------------
    # CONSTRUCCIÓN DE LA PARTE DERECHA (la tabla de puntajes)
    # -------------------------------------------------------------------------
    def construir_tabla(self):
        contenedor = tk.Frame(self.ventana, bg=VERDE, padx=20, pady=20)
        contenedor.grid(row=0, column=1, sticky="n")

        tabla = tk.Frame(contenedor, bg="black", bd=2, relief="solid")
        tabla.pack()

        # Encabezado
        for col, titulo in enumerate(["", "Tú", "IA"]):
            tk.Label(tabla, text=titulo, font=FUENTE_NEGRITA, bg="white",
                     relief="solid", bd=1, padx=6, pady=4,
                     width=20 if col == 0 else 6).grid(row=0, column=col, sticky="nsew")

        # Filas: superiores, suma, bono, inferiores, total
        filas = SUPERIORES + ["suma", "bono"] + INFERIORES + ["total"]
        self.celdas = {"tu": {}, "ia": {}}

        for fila, clave in enumerate(filas, start=1):
            especial = clave in ("suma", "bono", "total")
            fondo = FILA_ESPECIAL if especial else "white"
            fuente = FUENTE_NEGRITA if especial or clave == "yahtzee" else FUENTE

            tk.Label(tabla, text=NOMBRES[clave], font=fuente, bg=fondo,
                     anchor="w", relief="solid", bd=1, padx=8, pady=4,
                     width=20).grid(row=fila, column=0, sticky="nsew")

            for col, jugador in enumerate(["tu", "ia"], start=1):
                celda = tk.Label(tabla, text="", font=FUENTE, bg=fondo,
                                 relief="solid", bd=1, width=6)
                celda.grid(row=fila, column=col, sticky="nsew")
                celda.fondo_original = fondo
                self.celdas[jugador][clave] = celda

                # Solo las casillas normales de "Tú" se pueden pulsar
                if jugador == "tu" and not especial:
                    celda.bind("<Button-1>", lambda e, c=clave: self.anotar(c))
                    celda.bind("<Enter>", lambda e, c=clave: self.resaltar_celda(c, True))
                    celda.bind("<Leave>", lambda e, c=clave: self.resaltar_celda(c, False))

        tk.Label(contenedor, font=("Segoe UI", 9), bg=VERDE, fg="#d5f5e3",
                 justify="left", wraplength=280,
                 text="• Clic en una casilla de la columna \"Tú\" para anotar.\n"
                      "• Los números grises son lo que ganarías ahí.\n"
                      f"• Bonificación: +{BONO_PUNTOS} si Unos→Seises suman {BONO_MINIMO} o más."
                 ).pack(anchor="w", pady=(10, 0))

        self.crear_boton(contenedor, "🔄  Nueva partida",
                         self.nueva_partida, ancho=16).pack(pady=(14, 0))

    # -------------------------------------------------------------------------
    # DIBUJAR / ACTUALIZAR LA PANTALLA
    # -------------------------------------------------------------------------
    def actualizar_todo(self):
        self.dibujar_dados()
        self.actualizar_tabla()
        self.actualizar_controles()

    def dibujar_dados(self):
        """Dibuja los 5 dados. Amarillo = guardado, azul = sugerido por la IA."""
        t = TAMANO_DADO
        for i, lienzo in enumerate(self.lienzos_dados):
            lienzo.delete("all")
            valor = self.dados[i]
            guardado = self.guardados[i]
            sugerido = self.mascara_sugerida is not None and self.mascara_sugerida[i]

            fondo = "#fff6c7" if guardado else ("white" if valor else "#d5dbdb")
            borde = AMARILLO_FUERTE if guardado else (AZUL if sugerido else "#7f8c8d")
            grosor = 4 if (guardado or sugerido) else 2
            lienzo.create_rectangle(3, 3, t - 3, t - 3, fill=fondo,
                                    outline=borde, width=grosor)

            if valor == 0:
                lienzo.create_text(t / 2, t / 2, text="?", fill=GRIS,
                                   font=("Segoe UI", 20, "bold"))
            else:
                r = 6
                for (px, py) in PUNTOS_DADO[valor]:
                    x, y = px * t, py * t
                    lienzo.create_oval(x - r, y - r, x + r, y + r,
                                       fill=ROJO_PUNTO, outline="")

            self.etiquetas_guardado[i].config(text="GUARDADO" if guardado else "")

    def actualizar_tabla(self):
        """Escribe los puntajes en la tabla (y la vista previa en gris)."""
        mostrar_previa = (self.turno == "tu" and self.tiradas_usadas > 0
                          and not self.animando)

        for jugador in ("tu", "ia"):
            anotados = self.puntos[jugador]
            for cat in CATEGORIAS:
                celda = self.celdas[jugador][cat]
                if cat in anotados:                       # Ya anotada: negro
                    celda.config(text=str(anotados[cat]), fg="#1b2631",
                                 font=FUENTE_NEGRITA)
                elif jugador == "tu" and mostrar_previa:   # Vista previa: gris
                    celda.config(text=str(calcular_puntos(cat, self.dados)),
                                 fg=GRIS, font=FUENTE_CURSIVA)
                else:
                    celda.config(text="")

            suma, bono, total = self.totales(jugador)
            self.celdas[jugador]["suma"].config(text=str(suma), font=FUENTE_NEGRITA)
            self.celdas[jugador]["bono"].config(text=str(bono), font=FUENTE_NEGRITA)
            self.celdas[jugador]["total"].config(text=str(total), font=FUENTE_GRANDE)

    def actualizar_controles(self):
        """Activa o desactiva botones según el momento del juego."""
        es_mi_turno = self.turno == "tu" and not self.animando
        puede_tirar = es_mi_turno and self.tiradas_usadas < TIRADAS_POR_TURNO
        self.boton_tirar.config(state="normal" if puede_tirar else "disabled")
        self.boton_consejo.config(
            state="normal" if es_mi_turno and self.tiradas_usadas > 0 else "disabled")
        self.boton_usar.config(
            state="normal" if es_mi_turno and self.mascara_sugerida else "disabled")

        # Tiradas: ● usada, ○ disponible
        circulos = "● " * self.tiradas_usadas + "○ " * (TIRADAS_POR_TURNO - self.tiradas_usadas)
        self.etiqueta_tiradas.config(text=f"Tiradas:  {circulos}")
        self.etiqueta_ronda.config(text=f"Ronda {min(self.ronda, 13)} de 13")

        # Resaltar de quién es el turno
        self.etiqueta_tu.config(fg=AMARILLO if self.turno == "tu" else "white",
                                text="🙂  Tú  ◀ tu turno" if self.turno == "tu" else "🙂  Tú")
        self.etiqueta_ia.config(fg=AMARILLO if self.turno == "ia" else "white",
                                text="🤖  IA Montecarlo  ◀ jugando" if self.turno == "ia"
                                else "🤖  IA Montecarlo")

    def resaltar_celda(self, categoria, encima):
        """Efecto hover: pinta la casilla si se puede anotar ahí."""
        celda = self.celdas["tu"][categoria]
        se_puede = (self.turno == "tu" and self.tiradas_usadas > 0
                    and categoria not in self.puntos["tu"] and not self.animando)
        celda.config(bg=AMARILLO if (encima and se_puede) else celda.fondo_original,
                     cursor="hand2" if se_puede else "")

    def mostrar_mensaje(self, texto):
        self.mensaje.config(text=texto)

    def destellar(self, jugador, categoria):
        """Pinta un momento la casilla recién anotada para que se note."""
        celda = self.celdas[jugador][categoria]
        celda.config(bg=AMARILLO)
        self.ventana.after(1500, lambda: celda.config(bg=celda.fondo_original))

    # -------------------------------------------------------------------------
    # LANZAR DADOS (con animación)
    # -------------------------------------------------------------------------
    def animar_tirada(self, al_terminar, vueltas=8):
        """Muestra caras al azar unas cuantas veces y luego el resultado real."""
        self.animando = True
        if vueltas > 0:
            for i in range(5):
                if not self.guardados[i]:
                    self.dados[i] = random.randint(1, 6)
            self.dibujar_dados()
            self.ventana.after(60, lambda: self.animar_tirada(al_terminar, vueltas - 1))
        else:
            relanzar_dados(self.dados, self.guardados)   # Tirada REAL (función del simulador)
            self.tiradas_usadas += 1
            self.animando = False
            self.actualizar_todo()
            al_terminar()

    # -------------------------------------------------------------------------
    # ACCIONES DEL JUGADOR HUMANO
    # -------------------------------------------------------------------------
    def tirar_dados(self):
        if self.turno != "tu" or self.animando or self.tiradas_usadas >= TIRADAS_POR_TURNO:
            return
        self.mascara_sugerida = None
        self.actualizar_controles()
        self.animar_tirada(self.despues_de_mi_tirada)

    def despues_de_mi_tirada(self):
        restantes = TIRADAS_POR_TURNO - self.tiradas_usadas
        if restantes > 0:
            self.mostrar_mensaje(
                f"Te quedan {restantes} tirada(s). Haz clic en los dados que quieras "
                "GUARDAR, o elige una casilla en la tabla.")
        else:
            self.mostrar_mensaje("No quedan tiradas. Elige una casilla de la columna \"Tú\".")

    def clic_en_dado(self, posicion):
        """Guardar / soltar un dado (solo entre la 1.ª y la 3.ª tirada)."""
        if (self.turno != "tu" or self.animando or self.tiradas_usadas == 0
                or self.tiradas_usadas >= TIRADAS_POR_TURNO):
            return
        self.guardados[posicion] = not self.guardados[posicion]
        self.dibujar_dados()

    def pedir_consejo(self):
        """Ejecuta la simulación Montecarlo para la mano del jugador."""
        libres = self.casillas_libres("tu")

        if self.tiradas_usadas >= TIRADAS_POR_TURNO:
            cat, pts = mejor_puntaje(self.dados, libres)
            self.texto_consejo.config(
                text=f"Ya no puedes relanzar.\n\nLa casilla que más puntos te da ahora es:\n"
                     f"   ★  {NOMBRES[cat]}  →  {pts} pts")
            return

        self.mostrar_mensaje("La IA está simulando miles de lanzamientos...")
        self.ventana.update_idletasks()

        resultados = evaluar_todas_las_opciones(self.dados, libres, SIMULACIONES_IA)
        self.mostrar_razonamiento(resultados, "Si yo fuera tú:")
        self.mascara_sugerida = resultados[0][1]
        self.mostrar_mensaje('Los dados con borde AZUL son los que te sugiero guardar. '
                             'Pulsa "Usar este consejo" o elige tú mismo.')
        self.actualizar_todo()

    def usar_consejo(self):
        if self.mascara_sugerida:
            self.guardados = list(self.mascara_sugerida)
            self.dibujar_dados()

    def anotar(self, categoria):
        """El jugador anota sus puntos en una casilla."""
        if self.turno != "tu" or self.animando:
            return
        if self.tiradas_usadas == 0:
            self.mostrar_mensaje("Primero tira los dados.")
            return
        if categoria in self.puntos["tu"]:
            self.mostrar_mensaje("Esa casilla ya está usada. Elige otra.")
            return

        puntos = calcular_puntos(categoria, self.dados)
        self.puntos["tu"][categoria] = puntos
        self.resaltar_celda(categoria, False)
        self.destellar("tu", categoria)
        self.mostrar_mensaje(f"Anotaste {puntos} pts en {NOMBRES[categoria]}. Ahora juega la IA...")

        self.empezar_turno("ia")
        self.ventana.after(1200, self.ia_tirar)

    # -------------------------------------------------------------------------
    # TURNO DE LA IA (juega sola, paso a paso)
    # -------------------------------------------------------------------------
    def ia_tirar(self):
        self.animar_tirada(self.ia_decidir)

    def ia_decidir(self):
        """Después de cada tirada la IA usa Montecarlo para decidir qué guardar."""
        if self.tiradas_usadas >= TIRADAS_POR_TURNO:
            self.ventana.after(1000, self.ia_anotar)
            return

        self.mostrar_mensaje(f"La IA sacó {self.dados}. Simulando opciones...")
        self.ventana.update_idletasks()

        resultados = evaluar_todas_las_opciones(
            self.dados, self.casillas_libres("ia"), SIMULACIONES_IA)
        self.mostrar_razonamiento(resultados, "La IA piensa:")
        promedio, mascara = resultados[0]

        if all(mascara):   # La mejor opción es guardar TODO -> se planta
            self.mostrar_mensaje(f"La IA se planta con {self.dados}.")
            self.ventana.after(1500, self.ia_anotar)
        else:
            self.guardados = list(mascara)
            self.dibujar_dados()
            self.mostrar_mensaje(f"IA: {texto_jugada(self.dados, mascara)}  "
                                 f"(espera ~{promedio:.1f} pts)")
            self.ventana.after(2000, self.ia_tirar)

    def ia_anotar(self):
        cat, pts = mejor_puntaje(self.dados, self.casillas_libres("ia"))
        self.puntos["ia"][cat] = pts
        self.actualizar_tabla()
        self.destellar("ia", cat)

        if len(self.puntos["ia"]) == len(CATEGORIAS):
            self.fin_del_juego()
            return

        self.ronda += 1
        self.empezar_turno("tu")
        self.mostrar_mensaje(f"La IA anotó {pts} pts en {NOMBRES[cat]}.  "
                             f"¡Tu turno! Haz clic en \"Tirar los dados\".")

    # -------------------------------------------------------------------------
    # PANEL "CEREBRO DE LA IA"
    # -------------------------------------------------------------------------
    def mostrar_razonamiento(self, resultados, titulo):
        """Muestra las 3 mejores jugadas encontradas por Montecarlo."""
        total_simulaciones = 32 * SIMULACIONES_IA
        lineas = [
            f"Probé las 32 formas de guardar dados, {SIMULACIONES_IA} veces cada una",
            f"({total_simulaciones:,} lanzamientos simulados).".replace(",", "."),
            "",
            titulo,
        ]
        for puesto, (promedio, mascara) in enumerate(
                mejores_distintas(self.dados, resultados), start=1):
            estrella = "★" if puesto == 1 else "  "
            lineas.append(f" {estrella} {puesto}. {texto_jugada(self.dados, mascara)}"
                          f"  →  {promedio:.1f} pts")
        self.texto_consejo.config(text="\n".join(lineas))

    # -------------------------------------------------------------------------
    # FIN DEL JUEGO
    # -------------------------------------------------------------------------
    def fin_del_juego(self):
        self.turno = "fin"
        self.dados = [0] * 5
        self.guardados = [False] * 5
        self.actualizar_todo()

        _, _, total_tu = self.totales("tu")
        _, _, total_ia = self.totales("ia")
        if total_tu > total_ia:
            resultado = "🎉 ¡GANASTE!"
        elif total_tu < total_ia:
            resultado = "🤖 Ganó la IA."
        else:
            resultado = "🤝 ¡Empate!"
        self.mostrar_mensaje(f"FIN DEL JUEGO — Tú: {total_tu}  |  IA: {total_ia}.   "
                             f"{resultado}   Pulsa \"Nueva partida\" para jugar otra vez.")


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================
if __name__ == "__main__":
    ventana = tk.Tk()
    JuegoYahtzee(ventana)
    ventana.mainloop()
