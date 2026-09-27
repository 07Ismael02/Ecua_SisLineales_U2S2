"""API Flask y página principal del proyecto Jacobi."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import BadRequest

from metodos.convergencia import analizar_dominancia_diagonal, generar_formulas_jacobi
from metodos.jacobi import resolver_jacobi
from metodos.validaciones import ErrorValidacion, validar_sistema


app = Flask(__name__)


def _leer_json() -> dict:
    if not request.is_json:
        raise ErrorValidacion("La solicitud debe enviar JSON con Content-Type application/json.")
    try:
        datos = request.get_json(silent=False)
    except BadRequest as exc:
        raise ErrorValidacion("El cuerpo contiene JSON inválido.") from exc
    if not isinstance(datos, dict):
        raise ErrorValidacion("El cuerpo JSON debe ser un objeto.")
    return datos


@app.get("/")
def inicio():
    return render_template("index.html")


@app.post("/api/jacobi/analizar")
def analizar():
    try:
        datos = _leer_json()
        A, b = validar_sistema(datos.get("A"), datos.get("b"))
        return jsonify(
            {
                "ok": True,
                "A": A,
                "b": b,
                "analisis": analizar_dominancia_diagonal(A),
                "formulas": generar_formulas_jacobi(A, b),
            }
        )
    except ErrorValidacion as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.post("/api/jacobi/resolver")
def resolver():
    try:
        datos = _leer_json()
        resultado = resolver_jacobi(
            datos.get("A"),
            datos.get("b"),
            datos.get("x0"),
            datos.get("epsilon"),
            datos.get("max_iteraciones"),
        )
        return jsonify({"ok": True, **resultado})
    except ErrorValidacion as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


if __name__ == "__main__":
    app.run(debug=True)

