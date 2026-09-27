import unittest

from metodos.convergencia import analizar_dominancia_diagonal, generar_formulas_jacobi


class ConvergenciaTests(unittest.TestCase):
    def test_edd_oficial_fila_por_fila(self):
        A = [
            [10, -2, -1, 0],
            [-1, 8, 0, -2],
            [-2, 0, 12, -3],
            [0, -1, -2, 9],
        ]
        analisis = analizar_dominancia_diagonal(A)
        self.assertTrue(analisis["es_estrictamente_dominante"])
        self.assertEqual(
            [(fila["diagonal_absoluta"], fila["suma_externos"]) for fila in analisis["filas"]],
            [(10, 3), (8, 3), (12, 5), (9, 3)],
        )
        self.assertIn("condición suficiente", analisis["explicacion"])

    def test_no_edd_no_afirma_divergencia(self):
        analisis = analizar_dominancia_diagonal([[1, 2], [3, 1]])
        texto = f"{analisis['conclusion']} {analisis['explicacion']}".lower()
        self.assertFalse(analisis["es_estrictamente_dominante"])
        self.assertIn("no se garantiza", texto)
        self.assertNotIn("el método diverge", texto)
        self.assertNotIn("divergirá", texto)

    def test_formulas_oficiales(self):
        A = [[10, -2, -1, 0], [-1, 8, 0, -2], [-2, 0, 12, -3], [0, -1, -2, 9]]
        textos = [f["texto"] for f in generar_formulas_jacobi(A, [15, 18, 25, 20])]
        self.assertEqual(textos[0], "x1 = (15 + 2x2 + x3) / 10")
        self.assertEqual(textos[1], "x2 = (18 + x1 + 2x4) / 8")
        self.assertEqual(textos[2], "x3 = (25 + 2x1 + 3x4) / 12")
        self.assertEqual(textos[3], "x4 = (20 + x2 + 2x3) / 9")

    def test_formulas_signos_unidad_ceros_decimales_y_denominador_negativo(self):
        formulas = generar_formulas_jacobi([[-2, 1, 0], [-1, 4, 2.5], [0, -1, 3]], [5.5, -2, 7])
        self.assertEqual(formulas[0]["texto"], "x1 = (5.5 - x2) / -2")
        self.assertEqual(formulas[1]["texto"], "x2 = (-2 + x1 - 2.5x3) / 4")
        self.assertNotIn("x3", formulas[0]["texto"])


if __name__ == "__main__":
    unittest.main()

