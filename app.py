import tkinter as tk
from tkinter import ttk, messagebox
from sympy import symbols, Function, Eq, dsolve, sympify
from scipy.integrate import solve_ivp
import numpy as np
import matplotlib.pyplot as plt
import re

# ===========================
# Ventana principal
# ===========================
root = tk.Tk()
root.title("Resolución de Ecuaciones Diferenciales")
root.geometry("980x700")

# ===========================
# Variables globales de UI
# ===========================
resultado_var = tk.StringVar()     # Mensajes / resultados
ejemplo_var = tk.StringVar()
pvi_resultado_var = tk.StringVar() # Resultado del PVI (valor final)

mostrar_graf_var = tk.BooleanVar(value=False)  # Mostrar/no mostrar gráfica

# ===========================
# Utilidades
# ===========================
def formatear_ecuacion(expr_str: str) -> str:
    """
    Convierte atajos como y', y'' a Derivative(y(x), x) para SymPy
    y cambia 'y' solitaria por 'y(x)' cuando corresponda.
    """
    expr_str = expr_str.replace("y''", "__Y2__")
    expr_str = expr_str.replace("y'", "__Y1__")
    expr_str = re.sub(r"\by\b(?!\()", "y(x)", expr_str)
    expr_str = expr_str.replace("__Y2__", "Derivative(y(x), x, x)")
    expr_str = expr_str.replace("__Y1__", "Derivative(y(x), x)")
    return expr_str

def mk_fx_from_string(expr: str):
    """
    Compila una expresión string f(x,y) a una función Python f(x,y).
    Entorno permitido: numpy (np) y math en lo básico via numpy.
    """
    allowed = {"np": np}
    code = compile(expr, "<user-f(x,y)>", "eval")
    def f(x, y):
        return eval(code, {"__builtins__": {}}, {"x": x, "y": y, "np": np})
    return f

# ===========================
# Simbólico (SymPy)
# ===========================
def resolver_simbolicamente():
    entrada = entry_simb.get()
    try:
        entrada = formatear_ecuacion(entrada)
        if '=' in entrada:
            lhs_str, rhs_str = entrada.split('=')
            lhs = sympify(lhs_str.strip())
            rhs = sympify(rhs_str.strip())
            ecuacion = Eq(lhs, rhs)
        else:
            ecuacion = Eq(sympify(entrada), 0)

        x = symbols('x')
        y = Function('y')
        sol = dsolve(ecuacion, y(x))
        resultado_var.set(f"Solución simbólica: {sol}")

    except Exception as e:
        resultado_var.set(f"Error: {e}")

# ===========================
# Numérico “general” (SciPy solve_ivp) – se mantiene
# ===========================
def resolver_numericamente():
    try:
        expr = entry_num.get()
        # f(t,y) para solve_ivp
        f = lambda t, y: eval(expr, {"__builtins__": {}}, {"t": t, "y": y, "np": np})
        y0 = float(entry_y0.get())
        t0 = float(entry_t0.get())
        tf = float(entry_tf.get())

        sol = solve_ivp(f, (t0, tf), [y0], t_eval=np.linspace(t0, tf, 200))

        if mostrar_graf_var.get():
            plt.figure()
            plt.plot(sol.t, sol.y[0], label='y(t)')
            plt.title('Solución numérica (solve_ivp)')
            plt.xlabel('t'); plt.ylabel('y')
            plt.grid(True); plt.legend()
            plt.show()
        resultado_var.set("Solución numérica calculada (solve_ivp).")

    except Exception as e:
        resultado_var.set(f"Error numérico: {e}")

def insertar_ejemplo(event=None):
    ejemplo = ejemplo_var.get()
    if ejemplo:
        entry_simb.delete(0, tk.END)
        entry_simb.insert(0, ejemplo)

# ===========================
# PVI (Euler con tabla + errores)
# ===========================
def rk4_ref_at_nodes(fxy, x0, y0, xs):
    """
    Integra con RK4 a paso fino entre nodos para obtener y 'real'
    (referencia) en cada x de xs.
    """
    y = y0
    x = x0
    yref = [y0]
    for j in range(1, len(xs)):
        xf = xs[j]
        # subdividir en pasos pequeños para alta precisión
        h_base = min(1e-3, max(1e-4, (xf - x)/50.0))
        while x < xf - 1e-14:
            h = min(h_base, xf - x)
            k1 = fxy(x, y)
            k2 = fxy(x + 0.5*h, y + 0.5*h*k1)
            k3 = fxy(x + 0.5*h, y + 0.5*h*k2)
            k4 = fxy(x + h,     y + h*k3)
            y += (h/6.0) * (k1 + 2*k2 + 2*k3 + k4)
            x += h
        yref.append(y)
    return yref

def resolver_pvi_euler():
    """
    Resuelve el PVI usando Euler explícito con n pasos y construye
    la tabla con errores vs. una referencia RK4.
    """
    try:
        expr = entry_fx.get().strip()           # f(x,y) del usuario
        a = float(entry_x0.get())               # a = x0
        y0 = float(entry_y00.get())             # y(a) = y0
        b = float(entry_xf.get())               # b = xf
        n = int(entry_n.get())                  # número de pasos (p. ej. 10)

        if n <= 0 or b <= a:
            messagebox.showerror("Datos inválidos", "Revisa que n>0 y xf>a.")
            return

        fxy = mk_fx_from_string(expr)

        # ------------------------------------------------------------
        # FÓRMULAS DE LA TABLA:
        #   Δx = (b - a) / n
        #   n  = 0..n
        #   x_n = a + n * Δx
        #   Y_n = Y_{n-1} + Δx * f(x_{n-1}, Y_{n-1})   (Euler explícito)
        #   f   = f(x_{n-1}, Y_{n-1})                  (columna "f= (poner ec del problema)")
        #   Y_real (referencia) = valor con RK4 (alta precisión) en x_n
        #   Error absoluto   = |Y_real - Y_n|
        #   Error relativo   = |Y_real - Y_n| / |Y_real|
        #   Error porcentual = 100 * Error relativo
        # ------------------------------------------------------------

        h = (b - a) / n

        # nodos
        xs = [a + i*h for i in range(n+1)]

        # Euler
        ys = [y0]
        fvals = [np.nan]   # f en el paso 0 no se usa (o puede quedar vacío)
        for i in range(1, n+1):
            xim1 = xs[i-1]
            yim1 = ys[i-1]
            fim1 = fxy(xim1, yim1)
            yn = yim1 + h * fim1
            ys.append(yn)
            fvals.append(fim1)

        # Referencia con RK4 en los nodos
        yref = rk4_ref_at_nodes(fxy, a, y0, xs)

        # Errores
        abs_err = [abs(yref[i] - ys[i]) for i in range(n+1)]
        rel_err = [ (abs_err[i] / abs(yref[i])) if yref[i] != 0 else np.nan for i in range(n+1)]
        rel_pct = [ (e*100.0) if (not np.isnan(e)) else np.nan for e in rel_err ]

        # Valor final
        pvi_resultado_var.set(f"y({b}) ≈ {ys[-1]:.10g}  (Euler, n={n}, Δx={h:.5g})")

        # Poblar tabla
        for row in tree_pvi.get_children():
            tree_pvi.delete(row)

        for i in range(n+1):
            # Para que se vea igual que en tu pizarrón, normalmente muestras n=0..10,
            # pero si quieres ver solo 1..10, cambia el rango de arriba.
            vals = [
                i,
                f"{xs[i]:.10f}",
                f"{ys[i]:.10f}",
                f"{fvals[i]:.10f}" if i>0 else "",  # f(x_{n-1}, y_{n-1})
                f"{yref[i]:.10f}",
                f"{abs_err[i]:.10f}",
                f"{rel_err[i]:.10f}",
                f"{rel_pct[i]:.10f}"
            ]
            tree_pvi.insert("", "end", values=vals)

        # Gráfico opcional (no interfiere; solo si está activado)
        if mostrar_graf_var.get():
            plt.figure()
            plt.plot(xs, ys, marker='o', label='Euler')
            plt.plot(xs, yref, marker='.', linestyle='--', label='Referencia (RK4)')
            plt.title('PVI: Euler vs Referencia')
            plt.xlabel('x'); plt.ylabel('y')
            plt.grid(True); plt.legend()
            plt.tight_layout()
            plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# ===========================
# Título / encabezado
# ===========================
lbl_titulo = tk.Label(root, text="RESOLVER ECUACIONES DIFERENCIALES", font=("Arial", 16, "bold"))
lbl_titulo.pack(pady=8)

# Mensajes/resultados generales
lbl_resultado = tk.Label(root, textvariable=resultado_var, fg="red", font=("Consolas", 10))
lbl_resultado.pack(pady=2)

# ===========================
# Marco Simbólico
# ===========================
frame_simb = tk.LabelFrame(root, text="Simbólico (SymPy)")
frame_simb.pack(padx=10, pady=5, fill="x")

entry_simb = tk.Entry(frame_simb, width=60)
entry_simb.pack(side="left", padx=5, pady=5)

btn_resolver_simb = tk.Button(frame_simb, text="Resolver simbólicamente", command=resolver_simbolicamente)
btn_resolver_simb.pack(side="right", padx=5, pady=5)

ejemplos = [
    "y' + y = exp(x)",
    "y'' - y = sin(x)",
    "y' + 2*y = 0",
    "y'' + 3*y' + 2*y = 0"
]
ejemplo_var.set("")
menu_ejemplos = ttk.Combobox(frame_simb, textvariable=ejemplo_var, values=ejemplos, state="readonly", width=30)
menu_ejemplos.pack(side="left", padx=5)
menu_ejemplos.bind("<<ComboboxSelected>>", insertar_ejemplo)

# ===========================
# Marco Numérico general (solve_ivp)
# ===========================
frame_num = tk.LabelFrame(root, text="Numérico general (SciPy)")
frame_num.pack(padx=10, pady=5, fill="x")

entry_num = tk.Entry(frame_num, width=40)
entry_num.insert(0, "-2*y")
entry_num.grid(row=0, column=0, padx=5, pady=5)

tk.Label(frame_num, text="y(0)=").grid(row=0, column=1)
entry_y0 = tk.Entry(frame_num, width=7)
entry_y0.insert(0, "1")
entry_y0.grid(row=0, column=2)

tk.Label(frame_num, text="t0=").grid(row=0, column=3)
entry_t0 = tk.Entry(frame_num, width=7)
entry_t0.insert(0, "0")
entry_t0.grid(row=0, column=4)

tk.Label(frame_num, text="tf=").grid(row=0, column=5)
entry_tf = tk.Entry(frame_num, width=7)
entry_tf.insert(0, "5")
entry_tf.grid(row=0, column=6)

btn_resolver_num = tk.Button(frame_num, text="Resolver numéricamente", command=resolver_numericamente)
btn_resolver_num.grid(row=0, column=7, padx=5)

# Checkbox global para gráficos
chk_graf = tk.Checkbutton(frame_num, text="Mostrar gráficas", variable=mostrar_graf_var)
chk_graf.grid(row=0, column=8, padx=8)

# ===========================
# Marco PVI con Euler (nuevo)
# ===========================
frame_pvi = tk.LabelFrame(root, text="PVI de 1er orden (Euler + Tabla de errores)")
frame_pvi.pack(padx=10, pady=8, fill="both", expand=True)

# Entradas
rowi = 0
tk.Label(frame_pvi, text="f(x,y) =").grid(row=rowi, column=0, sticky="e")
entry_fx = tk.Entry(frame_pvi, width=40)
entry_fx.insert(0, "0.1*np.sqrt(y) + 0.4*x**2")
entry_fx.grid(row=rowi, column=1, padx=5, pady=4, sticky="w")

tk.Label(frame_pvi, text="x0 = a").grid(row=rowi, column=2, sticky="e")
entry_x0 = tk.Entry(frame_pvi, width=10)
entry_x0.insert(0, "2")
entry_x0.grid(row=rowi, column=3, padx=5, pady=4)

tk.Label(frame_pvi, text="y(x0) =").grid(row=rowi, column=4, sticky="e")
entry_y00 = tk.Entry(frame_pvi, width=10)
entry_y00.insert(0, "4")
entry_y00.grid(row=rowi, column=5, padx=5, pady=4)

rowi += 1
tk.Label(frame_pvi, text="xf = b").grid(row=rowi, column=0, sticky="e")
entry_xf = tk.Entry(frame_pvi, width=10)
entry_xf.insert(0, "2.5")
entry_xf.grid(row=rowi, column=1, padx=5, pady=4, sticky="w")

tk.Label(frame_pvi, text="n (pasos)").grid(row=rowi, column=2, sticky="e")
entry_n = tk.Entry(frame_pvi, width=10)
entry_n.insert(0, "10")
entry_n.grid(row=rowi, column=3, padx=5, pady=4)

btn_resolver_pvi = tk.Button(frame_pvi, text="Resolver PVI (Euler + Tabla)", command=resolver_pvi_euler)
btn_resolver_pvi.grid(row=rowi, column=4, padx=10, pady=4, sticky="w")

lbl_pvi_res = tk.Label(frame_pvi, textvariable=pvi_resultado_var, fg="blue", font=("Consolas", 10))
lbl_pvi_res.grid(row=rowi, column=5, padx=5, pady=4, sticky="w")

# Tabla (Treeview)
cols = (
    "n",
    "xn = a + n*Δx",
    "Yn (Euler)",
    "f = f(xn-1, Yn-1)",
    "Y real (ref.)",
    "Error absoluto",
    "Error relativo",
    "Error %"
)
tree_pvi = ttk.Treeview(frame_pvi, columns=cols, show="headings", height=14)
for c in cols:
    tree_pvi.heading(c, text=c)
    tree_pvi.column(c, width=130, anchor="center")

# Scrollbars
scroll_y = ttk.Scrollbar(frame_pvi, orient="vertical", command=tree_pvi.yview)
scroll_x = ttk.Scrollbar(frame_pvi, orient="horizontal", command=tree_pvi.xview)
tree_pvi.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

tree_pvi.grid(row=rowi+1, column=0, columnspan=6, sticky="nsew", padx=5, pady=8)
scroll_y.grid(row=rowi+1, column=6, sticky="ns")
scroll_x.grid(row=rowi+2, column=0, columnspan=6, sticky="ew", padx=5)

# Expandir tabla al redimensionar
frame_pvi.grid_rowconfigure(rowi+1, weight=1)
frame_pvi.grid_columnconfigure(1, weight=1)

# Ejecutar app
root.mainloop()
