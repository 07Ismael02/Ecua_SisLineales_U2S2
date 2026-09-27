import math
import unittest

from metodos.jacobi import _calcular_error, resolver_jacobi
from metodos.validaciones import ErrorValidacion


A_OFICIAL = [
    [10, -2, -1, 0],
    [-1, 8, 0, -2],
    [-2, 0, 12, -3],
    [0, -1, -2, 9],
]
B_OFICIAL = [15, 18, 25, 20]


class JacobiTests(unittest.TestCase):
    def test_caso_oficial_converge_con_traza_y_residuo(self):
        resultado = resolver_jacobi(A_OFICIAL, B_OFICIAL, [0, 0, 0, 0], 1e-4, 100)
        self.assertTrue(resultado["convergio"])
        self.assertLess(resultado["error_final"], 1e-4)
        self.assertLess(resultado["comprobacion"]["norma_infinito"], 0.01)
        self.assertEqual(resultado["iteraciones"][0]["k"], 0)
        self.assertIsNone(resultado["iteraciones"][0]["error_maximo"])
        # Referencia independiente obtenida por eliminación gaussiana.
        esperada = [2.5136959111, 3.3996294826, 3.3377001456, 3.3416699749]
        for obtenido, referencia in zip(resultado["solucion"], esperada):
            self.assertAlmostEqual(obtenido, referencia, delta=2e-4)
        componente = resultado["iteraciones"][1]["componentes"][0]
        for clave in (
            "fila", "diagonal", "b", "terminos", "suma", "numerador",
            "denominador", "resultado", "diferencia_absoluta", "error",
            "tipo_error", "formula_texto", "sustitucion_texto", "operacion_texto",
        ):
            self.assertIn(clave, componente)

    def test_primera_iteracion_es_jacobi_y_no_gauss_seidel(self):
        resultado = resolver_jacobi([[2, -1], [1, 2]], [1, 3], [0, 0], 1e-12, 1)
        self.assertEqual(resultado["iteraciones"][1]["vector"], [0.5, 1.5])
        self.assertNotEqual(resultado["iteraciones"][1]["vector"], [0.5, 1.25])

    def test_error_nuevo_y_anterior_cero(self):
        error, tipo = _calcular_error(0.0, 0.0)
        self.assertEqual(error, 0.0)
        self.assertEqual(tipo, "sin cambio")

    def test_error_nuevo_cero_anterior_no_cero(self):
        error, tipo = _calcular_error(0.0, -2.5)
        self.assertEqual(error, 2.5)
        self.assertEqual(tipo, "error absoluto por denominador cero")

    def test_limite_de_iteraciones(self):
        resultado = resolver_jacobi([[2, -1], [1, 2]], [1, 3], [0, 0], 1e-30, 1)
        self.assertFalse(resultado["convergio"])
        self.assertEqual(resultado["iteraciones_realizadas"], 1)
        self.assertEqual(resultado["estado"], "MÁXIMO DE ITERACIONES ALCANZADO")

    def test_epsilon_invalido(self):
        for epsilon in (0, -1, math.inf, math.nan, True):
            with self.subTest(epsilon=epsilon):
                with self.assertRaises(ErrorValidacion):
                    resolver_jacobi([[2, 0], [0, 2]], [1, 1], [0, 0], epsilon, 10)

    def test_max_iteraciones_invalido(self):
        for maximo in (0, -1, 1.5, "10", True):
            with self.subTest(maximo=maximo):
                with self.assertRaises(ErrorValidacion):
                    resolver_jacobi([[2, 0], [0, 2]], [1, 1], [0, 0], 1e-4, maximo)

    def test_dimensiones_invalidas(self):
        casos = [
            ([], [], [], "A"),
            ([[1, 2], [3]], [1, 2], [0, 0], "filas"),
            ([[1, 2], [3, 4]], [1], [0, 0], "b"),
            ([[1, 2], [3, 4]], [1, 2], [0], "x0"),
        ]
        for A, b, x0, _ in casos:
            with self.subTest(A=A, b=b, x0=x0):
                with self.assertRaises(ErrorValidacion):
                    resolver_jacobi(A, b, x0, 1e-4, 10)

    def test_diagonal_cero_y_casi_cero(self):
        for diagonal in (0, 1e-20):
            with self.subTest(diagonal=diagonal):
                with self.assertRaises(ErrorValidacion):
                    resolver_jacobi([[diagonal, 1], [1, 2]], [1, 1], [0, 0], 1e-4, 10)

    def test_nan_infinity_booleanos_y_texto(self):
        valores = (math.nan, math.inf, -math.inf, True, "2")
        for valor in valores:
            with self.subTest(valor=valor):
                with self.assertRaises(ErrorValidacion):
                    resolver_jacobi([[2, valor], [1, 2]], [1, 1], [0, 0], 1e-4, 10)


if __name__ == "__main__":
    unittest.main()

