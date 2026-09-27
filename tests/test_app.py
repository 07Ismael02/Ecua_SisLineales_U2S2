import unittest

from backend.app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()
        self.payload = {
            "A": [[2, -1], [1, 2]],
            "b": [1, 3],
            "x0": [0, 0],
            "epsilon": 1e-4,
            "max_iteraciones": 100,
        }

    def test_inicio(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"M\xc3\xa9todo iterativo", response.data)
        self.assertIn(b"Cargar ejemplo oficial", response.data)

    def test_analizar(self):
        response = self.client.post("/api/jacobi/analizar", json={"A": self.payload["A"], "b": self.payload["b"]})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["ok"])
        self.assertIn("analisis", data)
        self.assertIn("formulas", data)

    def test_resolver(self):
        response = self.client.post("/api/jacobi/resolver", json=self.payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["iteraciones"][1]["vector"], [0.5, 1.5])
        self.assertIn("comprobacion", data)

    def test_json_invalido(self):
        response = self.client.post(
            "/api/jacobi/resolver", data="{esto no es json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("JSON inv", response.get_json()["error"])

    def test_content_type_incorrecto(self):
        response = self.client.post("/api/jacobi/analizar", data="texto")
        self.assertEqual(response.status_code, 400)
        self.assertIn("application/json", response.get_json()["error"])

    def test_errores_api_son_400_y_comprensibles(self):
        casos = [
            ("/api/jacobi/analizar", {"b": [1]}, "matriz A"),
            ("/api/jacobi/analizar", {"A": [], "b": []}, "vacía"),
            ("/api/jacobi/resolver", {**self.payload, "A": [[0, 1], [1, 2]]}, "diagonal"),
            ("/api/jacobi/resolver", {**self.payload, "epsilon": 0}, "epsilon"),
            ("/api/jacobi/resolver", {**self.payload, "max_iteraciones": 2.5}, "entero"),
        ]
        for endpoint, payload, fragmento in casos:
            with self.subTest(endpoint=endpoint, fragmento=fragmento):
                response = self.client.post(endpoint, json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn(fragmento.lower(), response.get_json()["error"].lower())


if __name__ == "__main__":
    unittest.main()

