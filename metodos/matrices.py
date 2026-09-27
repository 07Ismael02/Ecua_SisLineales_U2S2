"""Operaciones matriciales elementales implementadas con ciclos explícitos."""

from __future__ import annotations


def multiplicar_matriz_vector(A: list[list[float]], x: list[float]) -> list[float]:
    resultado: list[float] = []
    for fila in A:
        acumulado = 0.0
        for j, coeficiente in enumerate(fila):
            acumulado += coeficiente * x[j]
        resultado.append(acumulado)
    return resultado


def restar_vectores(a: list[float], b: list[float]) -> list[float]:
    return [a[i] - b[i] for i in range(len(a))]


def norma_infinito(vector: list[float]) -> float:
    return max((abs(valor) for valor in vector), default=0.0)


def calcular_residuo(
    A: list[list[float]], b: list[float], x: list[float]
) -> tuple[list[float], list[float], float]:
    Ax = multiplicar_matriz_vector(A, x)
    residuo = restar_vectores(b, Ax)
    return Ax, residuo, norma_infinito(residuo)

