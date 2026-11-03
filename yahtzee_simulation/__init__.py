"""
Paquete de Simulación Estocástica de Yahtzee con Método Monte Carlo.
Desarrollado para la Actividad Didáctica 1 de Simulación (IU Digital de Antioquia).
"""

from .rules import (
    CATEGORIAS,
    CATEGORIAS_SUPERIORES,
    CATEGORIAS_INFERIORES,
    NOMBRES_CATEGORIAS,
    calcular_puntos,
    mejor_puntaje,
    todas_las_mascaras,
    hay_escalera
)
from .theory import PROBABILIDADES_TEORICAS_EXACTAS, CARDINALIDAD_ESPACIO_MUESTRAL
from .montecarlo import (
    ejecutar_convergencia_lln,
    simular_decaimiento_varianza_tlc,
    simular_valor_esperado_mascaras
)
from .massive_runs import ejecutar_corridas_masivas_estrategias

__all__ = [
    "CATEGORIAS",
    "CATEGORIAS_SUPERIORES",
    "CATEGORIAS_INFERIORES",
    "NOMBRES_CATEGORIAS",
    "calcular_puntos",
    "mejor_puntaje",
    "todas_las_mascaras",
    "hay_escalera",
    "PROBABILIDADES_TEORICAS_EXACTAS",
    "CARDINALIDAD_ESPACIO_MUESTRAL",
    "ejecutar_convergencia_lln",
    "simular_decaimiento_varianza_tlc",
    "simular_valor_esperado_mascaras",
    "ejecutar_corridas_masivas_estrategias"
]
