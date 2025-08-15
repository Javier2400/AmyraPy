from sympy import symbols, Function, Eq, dsolve, sympify

def resolver_simbolicamente(expr_str):
    x = symbols('x')
    y = Function('y')
    try:
        ecuacion = Eq(sympify(expr_str), 0)
        solucion = dsolve(ecuacion, y(x))
        return str(solucion)
    except Exception as e:
        return f"Error: {e}"
