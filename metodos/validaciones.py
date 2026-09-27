"""Validaciones de entrada compartidas por la API y el motor de Jacobi."""

from __future__ import annotations

import math
from typing import Any


class ErrorValidacion(ValueError):
    """Error esperado de datos de entrada, apto para mostrarse al usuario."""


def _es_numero_finito(valor: Any) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool) and math.isfinite(valor)


def _validar_vector(vector: Any, nombre: str, n: int) -> list[float]:
    if vector is None:
        raise ErrorValidacion(f"Falta el vector {nombre}.")
    if not isinstance(vector, list):
        raise ErrorValidacion(f"{nombre} debe ser un vector (lista).")
    if len(vector) != n:
        raise ErrorValidacion(f"{nombre} debe contener exactamente {n} valores.")

    resultado: list[float] = []
    for indice, valor in enumerate(vector, start=1):
        if not _es_numero_finito(valor):
            raise ErrorValidacion(
                f"{nombre}[{indice}] debe ser un número real finito; no se aceptan booleanos, NaN ni Infinity."
            )
        resultado.append(float(valor))
    return resultado


def validar_sistema(A: Any, b: Any) -> tuple[list[list[float]], list[float]]:
    """Valida y normaliza una matriz cuadrada y su vector independiente."""
    if A is None:
        raise ErrorValidacion("Falta la matriz A.")
    if not isinstance(A, list):
        raise ErrorValidacion("A debe ser una matriz (lista de filas).")
    if not A:
        raise ErrorValidacion("La matriz A no puede estar vacía.")

    n = len(A)
    matriz: list[list[float]] = []
    for i, fila in enumerate(A, start=1):
        if not isinstance(fila, list):
            raise ErrorValidacion(f"La fila {i} de A debe ser una lista.")
        if not fila:
            raise ErrorValidacion(f"La fila {i} de A no puede estar vacía.")
        if len(fila) != n:
            raise ErrorValidacion(
                f"A debe ser cuadrada y sin filas desiguales: la fila {i} tiene {len(fila)} valores, se esperaban {n}."
            )

        fila_normalizada: list[float] = []
        for j, valor in enumerate(fila, start=1):
            if not _es_numero_finito(valor):
                raise ErrorValidacion(
                    f"A[{i},{j}] debe ser un número real finito; no se aceptan booleanos, NaN ni Infinity."
                )
            fila_normalizada.append(float(valor))
        matriz.append(fila_normalizada)

    vector_b = _validar_vector(b, "b", n)
    validar_diagonal(matriz)
    return matriz, vector_b


def validar_diagonal(A: list[list[float]]) -> None:
    """Rechaza pivotes cero o demasiado pequeños para una división estable."""
    escala_global = max(abs(valor) for fila in A for valor in fila)
    umbral_base = max(1.0, escala_global) * 1e-14
    for i, fila in enumerate(A, start=1):
        diagonal = abs(fila[i - 1])
        escala_fila = max(abs(valor) for valor in fila)
        umbral = max(umbral_base, max(1.0, escala_fila) * 1e-14)
        if diagonal == 0:
            raise ErrorValidacion(f"La diagonal A[{i},{i}] es cero; Jacobi no puede dividir por ese término.")
        if diagonal <= umbral:
            raise ErrorValidacion(
                f"La diagonal A[{i},{i}]={fila[i - 1]:.12g} es numéricamente inválida por ser demasiado cercana a cero."
            )


def validar_parametros(
    A: Any,
    b: Any,
    x0: Any,
    epsilon: Any,
    max_iteraciones: Any,
) -> tuple[list[list[float]], list[float], list[float], float, int]:
    matriz, vector_b = validar_sistema(A, b)
    vector_x0 = _validar_vector(x0, "x0", len(matriz))

    if not _es_numero_finito(epsilon):
        raise ErrorValidacion("epsilon debe ser un número real finito mayor que cero.")
    epsilon_normalizado = float(epsilon)
    if epsilon_normalizado <= 0:
        raise ErrorValidacion("epsilon debe ser mayor que cero.")

    if isinstance(max_iteraciones, bool) or not isinstance(max_iteraciones, int):
        raise ErrorValidacion("max_iteraciones debe ser un número entero positivo.")
    if max_iteraciones <= 0:
        raise ErrorValidacion("max_iteraciones debe ser mayor que cero.")

    return matriz, vector_b, vector_x0, epsilon_normalizado, max_iteraciones

