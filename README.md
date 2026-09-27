# Métodos Numéricos — Jacobi

Aplicación web educativa que resuelve sistemas lineales mediante el método iterativo de Jacobi. Además del resultado, presenta la dominancia diagonal, los despejes, cada sustitución, los errores y el residuo para que el procedimiento pueda estudiarse y documentarse.

## Contexto

Este proyecto corresponde a la Unidad 2 de Métodos Numéricos y toma como caso oficial un sistema asociado al análisis de un clúster de cuatro servidores. Cada incógnita representa una variable del sistema y las relaciones se modelan mediante `Ax = b`:

```text
10x1 - 2x2 -  x3       = 15
 -x1 + 8x2       - 2x4 = 18
-2x1       + 12x3 - 3x4 = 25
      -x2 -  2x3 + 9x4 = 20
```

Con `x^(0) = [0, 0, 0, 0]`, `epsilon = 0.0001` y un máximo de 100 iteraciones.

## Fundamento matemático

Para cada componente, Jacobi calcula:

```text
x_i^(k+1) = (b_i - suma(a_ij x_j^(k), j != i)) / a_ii
```

Todos los componentes nuevos usan exclusivamente el vector anterior `x^(k)`. El vector no se actualiza dentro del ciclo de componentes; esta diferencia evita convertir accidentalmente el algoritmo en Gauss-Seidel.

El error de cada componente es `| (x_i nuevo - x_i anterior) / x_i nuevo |` cuando el valor nuevo no es cero. El criterio de parada usa el máximo de esos errores en forma adimensional:

```text
E < epsilon
```

El porcentaje `E × 100` se muestra solo como información. Si el valor nuevo es cero, el programa usa cero cuando no hubo cambio o la diferencia absoluta cuando el valor anterior era distinto de cero.

### Dominancia diagonal estricta

Se verifica por fila si:

```text
|a_ii| > suma(|a_ij|, j != i)
```

La dominancia diagonal estricta es una condición **suficiente**, no necesaria, para garantizar la convergencia de Jacobi. Si no se cumple, la aplicación advierte que el criterio no garantiza convergencia, pero no afirma que el método diverja.

## Funcionalidades

- Editor de matrices cuadradas entre 2×2 y 8×8.
- Ejemplo oficial precargable y opción de limpiar.
- Análisis EDD detallado por fila.
- Fórmulas despejadas generadas dinámicamente.
- Tabla que incluye `k = 0` y procedimiento completo por iteración.
- Errores relativos adimensionales y porcentajes informativos.
- Resultado, estado de convergencia y comprobación mediante `r = b - Ax`.
- Procedimiento académico copiable como texto, no como JSON.
- Validaciones de dimensiones, tipos, finitud, diagonal y parámetros.

## Estructura

```text
backend/                 Aplicación Flask, plantilla y archivos estáticos
metodos/                 Validaciones y motor matemático sin NumPy
tests/                   Pruebas unittest del algoritmo, EDD y API
requirements.txt         Dependencias mínimas
render.yaml              Configuración preparada para uso futuro
```

## Ejecución local

En PowerShell, desde la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m backend.app
```

Abra `http://127.0.0.1:5000`.

También puede usar un servidor WSGI compatible en Linux:

```bash
gunicorn backend.app:app
```

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas cubren el caso oficial, la distinción Jacobi/Gauss-Seidel, EDD, fórmulas, validaciones, error con denominador cero, límite de iteraciones y endpoints.

## API

- `GET /`: interfaz educativa.
- `POST /api/jacobi/analizar`: recibe `A` y `b`; devuelve EDD y despejes.
- `POST /api/jacobi/resolver`: recibe `A`, `b`, `x0`, `epsilon` y `max_iteraciones`; devuelve trazabilidad, resultado y residuo.

Ejemplo de cuerpo JSON:

```json
{
  "A": [[2, -1], [1, 2]],
  "b": [1, 3],
  "x0": [0, 0],
  "epsilon": 0.0001,
  "max_iteraciones": 100
}
```

## Residuo y limitaciones

La norma infinita del residuo `||b - Ax||∞` es una comprobación adicional y no reemplaza el criterio de parada requerido `E < epsilon`. El método requiere una diagonal no nula y numéricamente válida. En sistemas sin una condición suficiente de convergencia, puede alcanzar el límite de iteraciones. La aplicación trabaja con aritmética de punto flotante estándar y no usa NumPy, SciPy, SymPy, inversas matriciales ni solvers externos.

`render.yaml` queda preparado únicamente para un despliegue futuro; este proyecto no realiza despliegues ni conexiones con GitHub por sí mismo.

