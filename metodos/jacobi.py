"""Método de Jacobi con trazabilidad académica completa."""

from __future__ import annotations

from .convergencia import (
    analizar_dominancia_diagonal,
    formatear_numero,
    generar_formulas_jacobi,
    texto_formula_iteracion,
)
from .matrices import calcular_residuo
from .validaciones import validar_parametros


def _calcular_error(nuevo: float, anterior: float) -> tuple[float, str]:
    diferencia = abs(nuevo - anterior)
    if nuevo != 0:
        return abs((nuevo - anterior) / nuevo), "error relativo"
    if anterior == 0:
        return 0.0, "sin cambio"
    return diferencia, "error absoluto por denominador cero"


def _texto_sustitucion(
    variable: int,
    k: int,
    b_i: float,
    terminos: list[dict],
    denominador: float,
) -> str:
    texto = formatear_numero(b_i)
    for termino in terminos:
        coef_despejado = -termino["coeficiente"]
        signo = " + " if coef_despejado >= 0 else " - "
        magnitud = abs(coef_despejado)
        coef_texto = "" if magnitud == 1 else formatear_numero(magnitud)
        texto += f"{signo}{coef_texto}({formatear_numero(termino['valor_anterior'])})"
    return f"x{variable}^({k}) = ({texto}) / {formatear_numero(denominador)}"


def resolver_jacobi(A, b, x0, epsilon, max_iteraciones) -> dict:
    """Resuelve Ax=b mediante Jacobi sin actualizar componentes en caliente."""
    A, b, x_actual, epsilon, max_iteraciones = validar_parametros(
        A, b, x0, epsilon, max_iteraciones
    )
    n = len(A)
    analisis = analizar_dominancia_diagonal(A)
    formulas = generar_formulas_jacobi(A, b)

    iteraciones: list[dict] = [
        {
            "k": 0,
            "vector_anterior": None,
            "vector": x_actual.copy(),
            "componentes": [],
            "error_maximo": None,
            "error_porcentual": None,
            "convergio": False,
        }
    ]
    convergio = False

    for k in range(1, max_iteraciones + 1):
        anterior = x_actual.copy()
        nuevo = [0.0 for _ in range(n)]
        componentes: list[dict] = []
        errores: list[float] = []

        for i in range(n):
            suma = 0.0
            terminos: list[dict] = []
            for j in range(n):
                if j == i:
                    continue
                producto = A[i][j] * anterior[j]
                suma += producto
                terminos.append(
                    {
                        "variable": j + 1,
                        "coeficiente": A[i][j],
                        "valor_anterior": anterior[j],
                        "producto": producto,
                    }
                )

            numerador = b[i] - suma
            resultado = numerador / A[i][i]
            nuevo[i] = resultado
            error, tipo_error = _calcular_error(resultado, anterior[i])
            diferencia = abs(resultado - anterior[i])
            errores.append(error)

            terminos_visibles = [termino for termino in terminos if termino["coeficiente"] != 0]
            componentes.append(
                {
                    "fila": i + 1,
                    "variable": i + 1,
                    "diagonal": A[i][i],
                    "b": b[i],
                    "terminos": terminos,
                    "suma": suma,
                    "numerador": numerador,
                    "denominador": A[i][i],
                    "resultado": resultado,
                    "diferencia_absoluta": diferencia,
                    "error": error,
                    "error_porcentual": error * 100,
                    "tipo_error": tipo_error,
                    "formula_texto": texto_formula_iteracion(formulas[i], k),
                    "sustitucion_texto": _texto_sustitucion(
                        i + 1, k, b[i], terminos_visibles, A[i][i]
                    ),
                    "operacion_texto": (
                        f"x{i + 1}^({k}) = {formatear_numero(numerador)} / "
                        f"{formatear_numero(A[i][i])}"
                    ),
                }
            )

        error_maximo = max(errores)
        convergio = error_maximo < epsilon
        iteraciones.append(
            {
                "k": k,
                "vector_anterior": anterior,
                "vector": nuevo.copy(),
                "componentes": componentes,
                "error_maximo": error_maximo,
                "error_porcentual": error_maximo * 100,
                "convergio": convergio,
            }
        )
        x_actual = nuevo
        if convergio:
            break

    Ax, residuo, norma_residuo = calcular_residuo(A, b, x_actual)
    ultima = iteraciones[-1]
    estado = "CONVERGIÓ" if convergio else "MÁXIMO DE ITERACIONES ALCANZADO"
    return {
        "A": A,
        "b": b,
        "x0": iteraciones[0]["vector"],
        "epsilon": epsilon,
        "epsilon_porcentual": epsilon * 100,
        "max_iteraciones": max_iteraciones,
        "analisis": analisis,
        "formulas": formulas,
        "iteraciones": iteraciones,
        "solucion": x_actual,
        "iteraciones_realizadas": len(iteraciones) - 1,
        "error_final": ultima["error_maximo"],
        "error_porcentual_final": ultima["error_porcentual"],
        "convergio": convergio,
        "estado": estado,
        "comprobacion": {
            "Ax": Ax,
            "b": b,
            "residuo": residuo,
            "norma_infinito": norma_residuo,
            "nota": "Comprobación adicional; no forma parte del criterio de parada E < epsilon.",
        },
    }


__all__ = ["resolver_jacobi", "_calcular_error"]

