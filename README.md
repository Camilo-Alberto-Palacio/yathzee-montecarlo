# Simulación de Yahtzee con Método Montecarlo

Proyecto de simulación estocástica para el juego **Yahtzee**, aplicando el **Método Montecarlo** para la toma óptima de decisiones (selección de dados a retener/relanzar según el valor esperado - EV).

## 🎲 Estructura del Proyecto

* **`interfaz_yahtzee.py`**: Interfaz gráfica interactiva desarrollada en Tkinter. Permite jugar una partida completa contra la IA, visualizar lanzamientos de dados, solicitar recomendaciones y registrar puntajes.
* **`yahtzee_montecarlo.py`**: Motor principal de simulación Montecarlo. Evalúa las 32 combinaciones posibles de retención de dados y calcula el valor esperado promedio de cada jugada.
* **`prueba.py`**: Script de pruebas y prototipo del núcleo lógico estocástico.

## 🚀 Requisitos y Ejecución

* **Python 3.10 o superior** (incluye `tkinter` y la biblioteca estándar).

### Ejecutar la Interfaz Gráfica:
```bash
python interfaz_yahtzee.py
```

### Ejecutar la Simulación en Consola:
```bash
python yahtzee_montecarlo.py
```
