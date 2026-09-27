"""Dominancia diagonal y generación dinámica de despejes para Jacobi."""

from __future__ import annotations


def formatear_numero(valor: float) -> str:
    if valor == 0:
        return "0"
    return f"{valor:.12g}"


def analizar_dominancia_diagonal(A: list[list[float]]) -> dict:
    filas: list[dict] = []
    for i, fila in enumerate(A):
        diagonal = fila[i]
        terminos_externos = [fila[j] for j in range(len(fila)) if j != i]
        absolutos = [abs(valor) for valor in terminos_externos]
        suma = sum(absolutos)
        cumple = abs(diagonal) > suma
        filas.append(
            {
                "fila": i + 1,
                "diagonal": diagonal,
                "diagonal_absoluta": abs(diagonal),
                "terminos_externos": terminos_externos,
                "valores_absolutos": absolutos,
                "suma_externos": suma,
                "margen": abs(diagonal) - suma,
                "comparacion": f"{formatear_numero(abs(diagonal))} > {formatear_numero(suma)}",
                "cumple": cumple,
            }
        )

    es_edd = all(fila["cumple"] for fila in filas)
    if es_edd:
        conclusion = "La matriz es estrictamente diagonal dominante por filas."
        explicacion = (
            "La dominancia diagonal estricta es una condición suficiente para garantizar "
            "la convergencia del método de Jacobi."
        )
    else:
        conclusion = (
            "No se garantiza la convergencia mediante el criterio de dominancia diagonal estricta."
        )
        explicacion = (
            "El criterio no se cumple en todas las filas; esto no demuestra divergencia. "
            "Jacobi puede ejecutarse mientras la diagonal sea válida."
        )

    return {
        "es_estrictamente_dominante": es_edd,
        "filas": filas,
        "conclusion": conclusion,
        "explicacion": explicacion,
    }


def _texto_numerador(b_i: float, terminos: list[dict], con_iteracion: int | None = None) -> str:
    texto = formatear_numero(b_i)
    for termino in terminos:
        coeficiente = termino["coeficiente_despejado"]
        signo = " + " if coeficiente >= 0 else " - "
        magnitud = abs(coeficiente)
        coef_texto = "" if magnitud == 1 else formatear_numero(magnitud)
        variable = f"x{termino['variable']}"
        if con_iteracion is not None:
            variable += f"^({con_iteracion})"
        texto += f"{signo}{coef_texto}{variable}"
    return texto


def generar_formulas_jacobi(A: list[list[float]], b: list[float]) -> list[dict]:
    formulas: list[dict] = []
    for i, fila in enumerate(A):
        terminos: list[dict] = []
        for j, coeficiente_original in enumerate(fila):
            if j == i or coeficiente_original == 0:
                continue
            terminos.append(
                {
                    "variable": j + 1,
                    "coeficiente_original": coeficiente_original,
                    "coeficiente_despejado": -coeficiente_original,
                }
            )
        numerador = _texto_numerador(b[i], terminos)
        formulas.append(
            {
                "variable": i + 1,
                "b": b[i],
                "denominador": fila[i],
                "terminos": terminos,
                "numerador_texto": numerador,
                "texto": f"x{i + 1} = ({numerador}) / {formatear_numero(fila[i])}",
            }
        )
    return formulas


def texto_formula_iteracion(formula: dict, iteracion_nueva: int) -> str:
    numerador = _texto_numerador(
        formula["b"], formula["terminos"], con_iteracion=iteracion_nueva - 1
    )
    return (
        f"x{formula['variable']}^({iteracion_nueva}) = ({numerador}) / "
        f"{formatear_numero(formula['denominador'])}"
    )

