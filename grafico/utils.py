from sympy import symbols, Eq, solve, sympify, lambdify, latex
from sympy.core.sympify import SympifyError
import numpy as np
import plotly.graph_objects as go
import re

# Variables simbólicas globales
x, y = symbols('x y')

# Funciones auxiliares
def agregar_multiplicacion(expr_str):
    expr_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr_str)
    expr_str = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expr_str)
    return expr_str

#validamos las variables
def validar_variables(expr_str):
    if not re.fullmatch(r'[0-9xXyY+\-*/.=<>\s()*]+', expr_str):
        raise ValueError(f"Se encontraron caracteres inválidos en: '{expr_str}'")
    variables = re.findall(r'[a-zA-Z]', expr_str)
    for var in variables:
        if var.lower() not in ['x', 'y']:
            raise ValueError(f"Variable inválida: '{var}' — solo se permite 'x' y 'y'")

#Las restricciones
def parse_restricciones(texto):
    lines = texto.strip().split('\n')
    parsed = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line = line.replace('≤', '<=').replace('≥', '>=').replace(' ', '')
        match = re.match(r'^(.+?)(<=|>=|=)(.+)$', line)
        if not match:
            raise ValueError(f"Restricción inválida: '{line}'")
        left, op, right = match.groups()
        left = agregar_multiplicacion(left)
        right = agregar_multiplicacion(right)
        validar_variables(left)
        validar_variables(right)
        try:
            left_expr = sympify(left)
            right_expr = sympify(right)
        except SympifyError as e:
            raise ValueError(f"Error al interpretar: '{line}' — {e}") from e
        parsed.append((left_expr, op, right_expr))
    return parsed

#se generan las intersecciones
def generar_intersecciones(restricciones):
    puntos = []
    for i in range(len(restricciones)):
        for j in range(i + 1, len(restricciones)):
            lhs1, _, rhs1 = restricciones[i]
            lhs2, _, rhs2 = restricciones[j]
            sol = solve([Eq(lhs1, rhs1), Eq(lhs2, rhs2)], (x, y), dict=True)
            if sol:
                punto = sol[0]
                try:
                    puntos.append((float(punto[x]), float(punto[y])))
                except Exception:
                    continue
    return puntos

#El punto factible
def punto_factible(punto, restricciones):
    for lhs, op, rhs in restricciones:
        val = lhs.subs({x: punto[0], y: punto[1]})
        if op == '<=' and not val <= rhs:
            return False
        if op == '>=' and not val >= rhs:
            return False
        if op == '=' and not val == rhs:
            return False
    return True
#evalua la funcion objetivo
def evaluar_funcion_objetivo(expr, punto):
    return expr.subs({x: punto[0], y: punto[1]})

#obtenemos el despeje
def obtener_pasos_despeje(restricciones):
    pasos = []
    for i, (lhs, op, rhs) in enumerate(restricciones):
        try:
            eq = Eq(lhs, rhs)
            despeje = solve(eq, y)
            if despeje:
                pasos.append(f"Restricción {i + 1}: {lhs} {op} {rhs} ⇒ y = {despeje[0]}")
        except Exception:
            pasos.append(f"Restricción {i + 1}: No se pudo despejar.")
    return pasos

#Generamos los pasos detallados
def generar_pasos_detallados(expr, restricciones, factibles, evaluados, optimo):
    pasos = []

    # Paso 1: Obtener dos puntos por restricción
    pasos.append("Paso 1: Encontrar dos puntos para cada restricción usando x = 0 y y = 0.")
    for i, (lhs, op, rhs) in enumerate(restricciones, start=1):
        pasos.append(f"\nRestricción {i}: {lhs} {op} {rhs}")
        try:
            lhs_y = lhs.subs(x, 0)
            eq_y = Eq(lhs_y, rhs)
            sol_y = solve(eq_y, y)
            if sol_y:
                pasos.append(f"  • Si x = 0 → {lhs_y} = {rhs} ⇒ y = {sol_y[0]}")
                pasos.append(f"    → Primer punto: (0, {sol_y[0]})")
        except Exception as e:
            pasos.append(f"  • Error al resolver con x = 0: {e}")
        try:
            lhs_x = lhs.subs(y, 0)
            eq_x = Eq(lhs_x, rhs)
            sol_x = solve(eq_x, x)
            if sol_x:
                pasos.append(f"  • Si y = 0 → {lhs_x} = {rhs} ⇒ x = {sol_x[0]}")
                pasos.append(f"    → Segundo punto: ({sol_x[0]}, 0)")
        except Exception as e:
            pasos.append(f"  • Error al resolver con y = 0: {e}")

    # Paso 2: Intersecciones
    pasos.append("\nPaso 2: Calcular intersecciones entre pares de restricciones.")
    intersecciones = set()
    for i, (lhs1, _, rhs1) in enumerate(restricciones):
        for j in range(i+1, len(restricciones)):
            lhs2, _, rhs2 = restricciones[j]
            try:
                eq1 = Eq(lhs1, rhs1)
                eq2 = Eq(lhs2, rhs2)
                solucion = solve((eq1, eq2), (x, y), dict=True)
                if solucion:
                    punto = solucion[0]
                    x_val = punto[x].evalf()
                    y_val = punto[y].evalf()
                    intersecciones.add((float(x_val), float(y_val)))
                    pasos.append(
                        f"  • Intersección entre restricción {i+1} y {j+1}:")
                    pasos.append(
                        f"      Resolver: {lhs1} = {rhs1} y {lhs2} = {rhs2}")
                    pasos.append(
                        f"      ⇒ x = {x_val:.2f}, y = {y_val:.2f}")
            except Exception as e:
                pasos.append(f"  • Error al resolver intersección {i+1}-{j+1}: {e}")

    pasos.append(f"\n  • Total de intersecciones factibles encontradas: {len(factibles)}")

    # Paso 3: Evaluar función objetivo
    pasos.append("\nPaso 3: Evaluar la función objetivo Z en los puntos factibles.")
    pasos.append(f"  • Expresión original: Z = {expr}")
    for punto, valor in evaluados:
        x_val, y_val = punto
        expr_str = str(expr)
        expr_sust = expr_str.replace('x', f'({x_val:.2f})').replace('y', f'({y_val:.2f})')
        pasos.append(f"  • Z({x_val:.2f}, {y_val:.2f}) = {expr_sust} = {valor:.2f}")

    # Paso 4: Mostrar óptimo
    pasos.append("\nPaso 4: Seleccionar el valor óptimo.")
    if optimo:
        pasos.append(f"  • El punto óptimo es ({optimo[0][0]:.2f}, {optimo[0][1]:.2f}) con Z = {optimo[1]:.2f}")
    else:
        pasos.append("  • No se encontró una solución óptima factible.")

    return pasos

def multiples_vertices_con_mismo_Z(puntos, expr, objetivo):
    valores_Z = [round(float(expr.evalf(subs={x: p[0], y: p[1]})), 6) for p in puntos]
    if not valores_Z:
        return False
    extremo = max(valores_Z) if objetivo == 'max' else min(valores_Z)
    return valores_Z.count(extremo) > 1

def es_region_no_acotada(puntos):
    if not puntos:
        return True
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]
    return (max(xs) > 1e6 or max(ys) > 1e6 or min(xs) < -1e6 or min(ys) < -1e6)

# Función principal
def resolver_problema(funcion_objetivo_str, restricciones_str, objetivo):
    restricciones = parse_restricciones(restricciones_str)
    puntos = generar_intersecciones(restricciones)
    factibles = [p for p in puntos if punto_factible(p, restricciones)]

    mensaje_extra = ""
    optimo = None
    expr = None
    evaluados = []

    if not factibles:
        if len(restricciones) > 1:
            primera_diferencia = restricciones[0][0] - restricciones[0][2]
            es_misma_recta = all((lhs - rhs).simplify() == primera_diferencia.simplify() for lhs, _, rhs in restricciones)
        else:
            es_misma_recta = False
        if es_misma_recta:
            mensaje_extra = "El problema tiene infinitas soluciones óptimas: todas las restricciones definen la misma recta."
            pasos_despeje = obtener_pasos_despeje(restricciones)
            pasos_detallados = ["Restricciones equivalentes → Región factible sobre una línea.",
                                "Múltiples soluciones óptimas sobre la misma recta."]
            return None, [], None, restricciones, pasos_despeje, pasos_detallados, mensaje_extra
        else:
            mensaje_extra = "El problema no tiene solución factible: la región factible es vacía."
            pasos_despeje = obtener_pasos_despeje(restricciones)
            return None, [], None, restricciones, pasos_despeje, [], mensaje_extra

    expr_str = agregar_multiplicacion(funcion_objetivo_str.replace('Z=', '').strip())
    validar_variables(expr_str)
    expr = sympify(expr_str)
    evaluados = [(p, evaluar_funcion_objetivo(expr, p)) for p in factibles]
    optimo = max(evaluados, key=lambda t: t[1]) if objetivo == 'max' else min(evaluados, key=lambda t: t[1])

    if es_region_no_acotada(factibles):
        mensaje_extra += "El problema tiene solución no acotada: Z crece infinitamente.\n"
    if multiples_vertices_con_mismo_Z(factibles, expr, objetivo):
        mensaje_extra += "El problema tiene múltiples soluciones óptimas: la línea Z toca varios vértices."

    pasos_despeje = obtener_pasos_despeje(restricciones)
    pasos_detallados = generar_pasos_detallados(expr, restricciones, factibles, evaluados, optimo)

    return optimo, factibles, expr, restricciones, pasos_despeje, pasos_detallados, mensaje_extra

# Exportar figura Plotly
def generar_figura_plotly(problema, optimo, puntos, restricciones, expr):
    fig = go.Figure()

    all_x = [p[0] for p in puntos]
    all_y = [p[1] for p in puntos]
    if optimo:
        all_x.append(optimo[0][0])
        all_y.append(optimo[0][1])

    min_x = min(all_x) - 5 if all_x else 0
    max_x = max(all_x) + 5 if all_x else 25
    min_y = min(all_y) - 5 if all_y else 0
    max_y = max(all_y) + 5 if all_y else 25
    x_vals = np.linspace(min_x, max_x, 400)

    for i, (lhs, op, rhs) in enumerate(restricciones):
        try:
            eq = Eq(lhs, rhs)
            sol = solve(eq, y)
            if sol:
                f_restriccion = lambdify(x, sol[0], modules=["numpy"])
                y_vals = f_restriccion(x_vals)
                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode='lines',
                    line=dict(dash='dot', color='gray'),
                    name=f'Restricción {i+1}'
                ))
        except Exception:
            continue

    if puntos:
        fig.add_trace(go.Scatter(
            x=[p[0] for p in puntos],
            y=[p[1] for p in puntos],
            mode='markers',
            marker=dict(color='blue', size=6),
            name='Puntos factibles'
        ))
        if optimo:
            puntos_ordenados = sorted(puntos, key=lambda p: (
                np.arctan2(p[1] - optimo[0][1], p[0] - optimo[0][0])
            ))
            fig.add_trace(go.Scatter(
                x=[p[0] for p in puntos_ordenados],
                y=[p[1] for p in puntos_ordenados],
                fill='toself',
                fillcolor='rgba(0, 100, 80, 0.2)',
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='skip',
                showlegend=True,
                name='Región factible'
            ))

    if optimo:
        fig.add_trace(go.Scatter(
            x=[optimo[0][0]],
            y=[optimo[0][1]],
            mode='markers+text',
            marker=dict(color='red', size=10),
            text=[f'Óptimo\nZ = {optimo[1]}'],
            textposition='top center',
            name='Punto óptimo'
        ))
        try:
            eq_nivel = Eq(expr, optimo[1])
            sol = solve(eq_nivel, y)
            if sol:
                f_linea = lambdify(x, sol[0], modules=["numpy"])
                y_vals = f_linea(x_vals)
                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=y_vals,
                    mode='lines',
                    line=dict(color='blue', dash='dash'),
                    name=f'Línea Z = {optimo[1]}'
                ))
        except Exception:
            pass

    fig.update_layout(
        title='Gráfica del Método Gráfico',
        xaxis_title='X',
        yaxis_title='Y',
        showlegend=True
    )
    fig.update_xaxes(range=[min_x, max_x])
    fig.update_yaxes(range=[min_y, max_y])

    return fig
