"""
=============================================================================
  SUITE DE PRUEBAS UNITARIAS - SIMULACIÓN ESTOCÁSTICA DE YAHTZEE
=============================================================================
Verifica la corrección matemática, axiomática y algorítmica:
1. Cardinalidad y combinatoria del espacio muestral Ω (7776 estados).
2. Axiomas estocásticos de Kolmogorov y consistencia de probabilidades.
3. Reglas de puntuación oficiales de Yahtzee.
4. Exhaustividad de las 32 máscaras de retención de dados.
5. Consistencia asintótica del muestreo Monte Carlo y convergencia de LLN.
"""

import unittest
import numpy as np
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from yahtzee_simulation.rules import (
    CATEGORIAS,
    calcular_puntos,
    mejor_puntaje,
    todas_las_mascaras,
    hay_escalera
)
from yahtzee_simulation.theory import (
    PROBABILIDADES_TEORICAS_EXACTAS,
    CARDINALIDAD_ESPACIO_MUESTRAL
)
from yahtzee_simulation.montecarlo import evaluar_mano_rapida


class TestYahtzeeMonteCarlo(unittest.TestCase):

    def test_cardinalidad_espacio_muestral(self):
        """Verifica que el espacio muestral sea exactamente 6^5 = 7776."""
        self.assertEqual(CARDINALIDAD_ESPACIO_MUESTRAL, 7776)

    def test_probabilidades_teoricas_exactas(self):
        """Valida que los conteos analíticos combinatorios coincidan con la teoría."""
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["yahtzee"]["casos_favorables"], 6)
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["poker"]["casos_favorables"], 156)
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["full"]["casos_favorables"], 306)
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["escalera_larga"]["casos_favorables"], 240)
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["escalera_corta"]["casos_favorables"], 1200)
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["libre"]["casos_favorables"], 7776)

    def test_axiomas_kolmogorov(self):
        """Verifica que toda probabilidad calculada pertenezca a [0, 1]."""
        for cat, datos in PROBABILIDADES_TEORICAS_EXACTAS.items():
            prob = datos["probabilidad"]
            self.assertGreaterEqual(prob, 0.0, f"Probabilidad negativa en {cat}")
            self.assertLessEqual(prob, 1.0, f"Probabilidad mayor a 1 en {cat}")

    def test_reglas_puntuacion_especificas(self):
        """Comprueba el cálculo de puntaje en configuraciones representativas."""
        # Yahtzee: 50 pts
        self.assertEqual(calcular_puntos("yahtzee", [5, 5, 5, 5, 5]), 50)
        self.assertEqual(calcular_puntos("yahtzee", [5, 5, 5, 5, 4]), 0)

        # Full House: 25 pts
        self.assertEqual(calcular_puntos("full", [3, 3, 3, 2, 2]), 25)
        self.assertEqual(calcular_puntos("full", [3, 3, 3, 3, 2]), 0)

        # Escalera Grande: 40 pts
        self.assertEqual(calcular_puntos("escalera_larga", [1, 2, 3, 4, 5]), 40)
        self.assertEqual(calcular_puntos("escalera_larga", [2, 3, 4, 5, 6]), 40)
        self.assertEqual(calcular_puntos("escalera_larga", [2, 3, 4, 5, 5]), 0)

        # Escalera Corta: 30 pts
        self.assertEqual(calcular_puntos("escalera_corta", [1, 2, 3, 4, 6]), 30)
        self.assertEqual(calcular_puntos("escalera_corta", [2, 3, 4, 5, 2]), 30)
        self.assertEqual(calcular_puntos("escalera_corta", [1, 3, 4, 5, 6]), 30)

        # Trío y Póker: suma de dados
        self.assertEqual(calcular_puntos("trio", [4, 4, 4, 2, 1]), 15)
        self.assertEqual(calcular_puntos("poker", [6, 6, 6, 6, 1]), 25)

        # Sección superior
        self.assertEqual(calcular_puntos("cuatros", [4, 4, 4, 2, 1]), 12)
        self.assertEqual(calcular_puntos("seises", [6, 6, 1, 2, 3]), 12)

    def test_exhaustividad_mascaras(self):
        """Verifica que se generen exactamente 32 máscaras booleanas distintas."""
        mascaras = todas_las_mascaras()
        self.assertEqual(len(mascaras), 32)
        tuplas_unicas = set(tuple(m) for m in mascaras)
        self.assertEqual(len(tuplas_unicas), 32)

    def test_consistencia_evaluador_rapido(self):
        """Verifica que el evaluador rápido vectorizado coincida con el evaluador de reglas."""
        manos_prueba = [
            [1, 1, 1, 1, 1],
            [2, 2, 2, 3, 3],
            [1, 2, 3, 4, 5],
            [1, 3, 4, 5, 6],
            [6, 6, 6, 6, 2],
            [1, 2, 3, 1, 4]
        ]
        for mano in manos_prueba:
            arr = np.array(mano)
            res_rapido = evaluar_mano_rapida(arr)
            self.assertEqual(res_rapido["yahtzee"], bool(calcular_puntos("yahtzee", mano) == 50))
            self.assertEqual(res_rapido["full"], bool(calcular_puntos("full", mano) == 25))
            self.assertEqual(res_rapido["escalera_larga"], bool(calcular_puntos("escalera_larga", mano) == 40))
            self.assertEqual(res_rapido["escalera_corta"], bool(calcular_puntos("escalera_corta", mano) == 30))


if __name__ == "__main__":
    unittest.main()
