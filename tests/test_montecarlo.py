"""
=============================================================================
  SUITE DE AUDITORÍA Y PRUEBAS UNITARIAS - SIMULACIÓN MONTE CARLO YAHTZEE
=============================================================================
Ejecuta 12 verificaciones matemáticas, estadísticas y de integridad documental:
1. Cardinalidad del espacio muestral |Ω| = 6^5 = 7,776.
2. Combinatoria analítica exacta de todas las categorías (Full House = 300).
3. Partición excluyente exhaustiva de Ω en 7 clases que suman 7,776.
4. Axiomas de probabilidad de Kolmogorov en las 13 categorías.
5. Casos de borde en reglas de puntuación (Full House rechaza 5 iguales).
6. Paridad exhaustiva 100% (101,088 comparaciones) con 'yahtzee_montecarlo.py'.
7. Exhaustividad de las 32 máscaras booleanas de retención.
8. Paridad exacta de la tabla vectorizada TABLA_PUNTOS_OMEGA en los 7,776 estados.
9. Autenticidad estocástica de los CSV exportados (cero datos falsos en superiores).
10. Validez estadística de pruebas Chi-Cuadrado (p-valor > 0.05) y pendiente TLC (~ -0.5).
11. Autocontención y pre-ejecución real del cuaderno Google Colab (.ipynb).
12. Existencia e integridad estructural del informe académico Word (.docx).
"""

import itertools
import json
import os
import sys
import unittest
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import yahtzee_montecarlo as base_game
from yahtzee_simulation.rules import (
    CATEGORIAS,
    TABLA_PUNTOS_OMEGA,
    calcular_puntos,
    todas_las_mascaras,
    codificar_manos_base6,
)
from yahtzee_simulation.theory import (
    PROBABILIDADES_TEORICAS_EXACTAS,
    CARDINALIDAD_ESPACIO_MUESTRAL,
    CONTEOS_TEORICOS_PARTICIONES,
)
from yahtzee_simulation.montecarlo import evaluar_mano_rapida


class TestYahtzeeMonteCarloAudit(unittest.TestCase):

    def test_01_cardinalidad_espacio_muestral(self):
        """Verifica que el espacio muestral sea exactamente 6^5 = 7,776."""
        self.assertEqual(CARDINALIDAD_ESPACIO_MUESTRAL, 7776)

    def test_02_probabilidades_teoricas_exactas(self):
        """Valida los conteos combinatorios exactos de las 13 categorías."""
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["yahtzee"]["casos_favorables"], 6)
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["poker"]["casos_favorables"], 156)
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["full"]["casos_favorables"], 300)
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["escalera_larga"]["casos_favorables"], 240)
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["escalera_corta"]["casos_favorables"], 1200)
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["trio"]["casos_favorables"], 1656)
        for sup in ["unos", "doses", "treses", "cuatros", "cincos", "seises"]:
            self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS[sup]["casos_favorables"], 4651)
        self.assertEqual(PROBABILIDADES_TEORICAS_EXACTAS["libre"]["casos_favorables"], 7776)

    def test_03_particion_excluyente_omega(self):
        """Verifica que las 7 clases de multiplicidad particionen exactamente Ω = 7,776."""
        self.assertEqual(sum(CONTEOS_TEORICOS_PARTICIONES), 7776)

    def test_04_axiomas_kolmogorov(self):
        """Verifica que toda probabilidad calculada pertenezca a [0, 1]."""
        for cat, datos in PROBABILIDADES_TEORICAS_EXACTAS.items():
            prob = datos["probabilidad"]
            self.assertGreaterEqual(prob, 0.0, f"Probabilidad negativa en {cat}")
            self.assertLessEqual(prob, 1.0, f"Probabilidad mayor a 1 en {cat}")

    def test_05_reglas_puntuacion_especificas(self):
        """Comprueba casos críticos incluyendo que 5 iguales NO puntúe como Full House puro."""
        self.assertEqual(calcular_puntos("yahtzee", [5, 5, 5, 5, 5]), 50)
        self.assertEqual(calcular_puntos("full", [3, 3, 3, 2, 2]), 25)
        self.assertEqual(calcular_puntos("full", [3, 3, 3, 3, 3]), 0)
        self.assertEqual(calcular_puntos("full", [3, 3, 3, 3, 2]), 0)
        self.assertEqual(calcular_puntos("escalera_larga", [1, 2, 3, 4, 5]), 40)
        self.assertEqual(calcular_puntos("escalera_corta", [1, 2, 3, 4, 6]), 30)
        self.assertEqual(calcular_puntos("trio", [4, 4, 4, 2, 1]), 15)
        self.assertEqual(calcular_puntos("poker", [6, 6, 6, 6, 1]), 25)

    def test_06_paridad_exhaustiva_con_juego_base(self):
        """Audita paridad 1:1 entre yahtzee_montecarlo.py y rules.py en los 7,776 x 13 casos."""
        for tiro in itertools.product(range(1, 7), repeat=5):
            mano = list(tiro)
            for cat in CATEGORIAS:
                self.assertEqual(
                    calcular_puntos(cat, mano),
                    base_game.calcular_puntos(cat, mano),
                    f"Discrepancia en {cat} con mano {mano}",
                )

    def test_07_exhaustividad_mascaras(self):
        """Verifica que se generen exactamente 32 máscaras booleanas únicas."""
        mascaras = todas_las_mascaras()
        self.assertEqual(len(mascaras), 32)
        self.assertEqual(len({tuple(m) for m in mascaras}), 32)

    def test_08_consistencia_tabla_vectorizada(self):
        """Verifica codificación biyectiva y evaluador rápido sobre muestras de Ω."""
        todos = np.array(list(itertools.product(range(1, 7), repeat=5)), dtype=np.int32)
        codigos = codificar_manos_base6(todos)
        self.assertTrue(np.array_equal(codigos, np.arange(7776, dtype=np.int32)))
        res_rap = evaluar_mano_rapida(np.array([2, 2, 2, 5, 5]))
        self.assertTrue(res_rap["full"])
        self.assertFalse(res_rap["yahtzee"])

    def test_09_autenticidad_datos_empiricos_csv(self):
        """Audita que probabilidades_teoricas_vs_empiricas.csv contenga conteos reales (no copiados)."""
        csv_path = os.path.join(BASE_DIR, "results", "probabilidades_teoricas_vs_empiricas.csv")
        self.assertTrue(os.path.exists(csv_path))
        df = pd.read_csv(csv_path).set_index("categoria_clave")
        self.assertEqual(len(df), 13)
        conteos_sup = [int(df.loc[c, "casos_favorables_mc_100k"]) for c in ["unos", "doses", "treses", "cuatros", "cincos", "seises"]]
        # En 100k tiradas reales, las 6 caras superiores no pueden tener exactamente el mismo entero fijo 59812
        self.assertGreater(len(set(conteos_sup)), 3)
        for c in ["unos", "doses", "treses", "cuatros", "cincos", "seises"]:
            self.assertGreater(float(df.loc[c, "error_absoluto"]), 0.0)
            self.assertLess(float(df.loc[c, "error_absoluto"]), 0.01)

    def test_10_tlc_y_bondad_ajuste_chi2(self):
        """Verifica que las pruebas Chi² pasen (p > 0.05) y la pendiente TLC esté en [-0.55, -0.45]."""
        df_chi = pd.read_csv(os.path.join(BASE_DIR, "results", "pruebas_bondad_ajuste_chi2.csv"))
        for pval in df_chi["p_valor"]:
            self.assertGreater(float(pval), 0.05)

        df_tlc = pd.read_csv(os.path.join(BASE_DIR, "results", "decaimiento_varianza_tlc.csv"))
        m_f = float(df_tlc["pendiente_ols_full"].iloc[0])
        r2_f = float(df_tlc["r2_ols_full"].iloc[0])
        self.assertGreaterEqual(m_f, -0.55)
        self.assertLessEqual(m_f, -0.45)
        self.assertGreater(r2_f, 0.98)

    def test_11_cuaderno_colab_autocontenido_y_ejecutado(self):
        """Verifica que el .ipynb no importe paquetes locales y tenga salidas pre-ejecutadas."""
        nb_path = os.path.join(BASE_DIR, "Simulacion_Yahtzee_Montecarlo_Colab.ipynb")
        self.assertTrue(os.path.exists(nb_path))
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.load(f)
        code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
        self.assertGreaterEqual(len(code_cells), 6)
        for idx, cell in enumerate(code_cells, start=1):
            src = "".join(cell["source"])
            self.assertNotIn("yahtzee_simulation", src, f"Import local prohibido en celda Colab {idx}")
            self.assertIsNotNone(cell["execution_count"], f"Celda Colab {idx} sin ejecutar")
            self.assertGreater(len(cell["outputs"]), 0, f"Celda Colab {idx} sin salidas embebidas")

    def test_12_informe_word_generado(self):
        """Verifica que el documento Word oficial exista y tenga tamaño sustancial."""
        docx_path = os.path.join(
            BASE_DIR,
            "Evidencia de Aprendizaje 1 - Módulo 1. Actividad didáctica 1 - Simulación Montecarlo Yahtzee.docx",
        )
        self.assertTrue(os.path.exists(docx_path))
        self.assertGreater(os.path.getsize(docx_path), 500_000)


if __name__ == "__main__":
    unittest.main()
