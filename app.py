import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
import re

# ==========================
# Convertir símbolos
# ==========================
def convertir_formula(expr: str) -> str:
    expr = expr.replace("√", "np.sqrt")
    expr = re.sub(r"(\w+)\^(\d+)", r"\1**\2", expr)
    expr = re.sub(r"(\d)([a-zA-Z\(])", r"\1*\2", expr)
    expr = re.sub(r"\)([a-zA-Z0-9\(])", r")*\1", expr)
    return expr

def insertar_simbolo(entry, simbolo):
    pos = entry.index(tk.INSERT)
    entry.insert(pos, simbolo)

# Crear ventana principal 
root = tk.Tk()
root.title("Métodos de Euler y RK4")

resultado_var = tk.StringVar()

# ===== BLOQUE METODO EULER =====
frame_euler_rk4 = tk.LabelFrame(root, text="Método de Euler y RK4")
frame_euler_rk4.pack(padx=10, pady=5, fill="x")

tk.Label(frame_euler_rk4, text="Ecuación f(x,y)=").grid(row=0, column=0)
entry_funcion = tk.Entry(frame_euler_rk4, width=25)
entry_funcion.insert(0, "0.1*√(y) + 0.4*x^2")
entry_funcion.grid(row=0, column=1)

tk.Label(frame_euler_rk4, text="Y0=").grid(row=0, column=2)
entry_y0_euler = tk.Entry(frame_euler_rk4, width=5)
entry_y0_euler.insert(0, "1")
entry_y0_euler.grid(row=0, column=3)

tk.Label(frame_euler_rk4, text="a=").grid(row=0, column=4)
entry_a = tk.Entry(frame_euler_rk4, width=5)
entry_a.insert(0, "0")
entry_a.grid(row=0, column=5)

tk.Label(frame_euler_rk4, text="b=").grid(row=0, column=6)
entry_b = tk.Entry(frame_euler_rk4, width=5)
entry_b.insert(0, "10")
entry_b.grid(row=0, column=7)

tk.Label(frame_euler_rk4, text="h=").grid(row=0, column=8)
entry_h = tk.Entry(frame_euler_rk4, width=5)
entry_h.insert(0, "1")
entry_h.grid(row=0, column=9)

tk.Label(frame_euler_rk4, text="Y real=").grid(row=0, column=10)
entry_y_real = tk.Entry(frame_euler_rk4, width=25)
entry_y_real.insert(0, "√(0.1*x) + x^2")
entry_y_real.grid(row=0, column=11)

# ===== Tabla =====
frame_tabla = tk.Frame(frame_euler_rk4)
frame_tabla.grid(row=2, column=0, columnspan=12, pady=5)

scroll_x = ttk.Scrollbar(frame_tabla, orient="horizontal")
scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical")

tabla = ttk.Treeview(
    frame_tabla,
    columns=("n", "xn", "Yn", "f", "Y_real", "Error_abs", "Error_rel", "Error_%"),
    show="headings",
    xscrollcommand=scroll_x.set,
    yscrollcommand=scroll_y.set
)
tabla.heading("Error_%", text="Error %")

for col in tabla["columns"]:
    tabla.heading(col, text=col)

scroll_x.config(command=tabla.xview)
scroll_y.config(command=tabla.yview)

tabla.grid(row=0, column=0, sticky="nsew")
scroll_x.grid(row=1, column=0, sticky="ew")
scroll_y.grid(row=0, column=1, sticky="ns")

frame_tabla.grid_rowconfigure(0, weight=1)
frame_tabla.grid_columnconfigure(0, weight=1)

# ==========================
# GENERAR TABLA
# ==========================
def generar_tabla():
    try:
        f_str = convertir_formula(entry_funcion.get())
        y0 = float(entry_y0_euler.get())
        a = float(entry_a.get())
        b = float(entry_b.get())
        h = float(entry_h.get())
        y_real_str = convertir_formula(entry_y_real.get())

        f = lambda x, y: eval(f_str, {"x": x, "y": y, "np": np})
        y_real = lambda x: eval(y_real_str, {"x": x, "np": np})

        n_pasos = int((b - a) / h)
        x_vals = [a + i*h for i in range(n_pasos+1)]

        y_euler = [y0]
        for i in range(n_pasos):
            y_euler.append(y_euler[-1] + h * f(x_vals[i], y_euler[-1]))

        y_rk4 = [y0]
        for i in range(n_pasos):
            k1 = f(x_vals[i], y_rk4[-1])
            k2 = f(x_vals[i] + h/2, y_rk4[-1] + h*k1/2)
            k3 = f(x_vals[i] + h/2, y_rk4[-1] + h*k2/2)
            k4 = f(x_vals[i] + h, y_rk4[-1] + h*k3)
            y_rk4.append(y_rk4[-1] + (h/6)*(k1 + 2*k2 + 2*k3 + k4))

        for item in tabla.get_children():
            tabla.delete(item)

        for i in range(n_pasos+1):
            xn = x_vals[i]
            Yn = y_euler[i]
            f_col = "" if i == 0 else f(x_vals[i-1], y_euler[i-1])
            Y_real_val = y_real(xn)
            err_abs = abs(Y_real_val - Yn)
            err_rel = (err_abs / abs(Y_real_val)) if Y_real_val != 0 else 0.0
            err_pct = err_rel * 100.0
            tabla.insert("", "end",
                    values=(i, round(xn, 4), round(Yn, 4),
                            ("" if i == 0 else round(f_col, 4)),
                            round(Y_real_val, 4),
                            round(err_abs, 4),
                            round(err_rel, 6),
                            round(err_pct, 3)))
    except Exception as e:
        resultado_var.set(f"Error en tabla: {e}")

tabla.column("n", width=100, anchor="center")
tabla.column("xn", width=100, anchor="center")
tabla.column("Yn", width=100, anchor="center")
tabla.column("f", width=100, anchor="center")
tabla.column("Y_real", width=100, anchor="center")
tabla.column("Error_abs", width=100, anchor="center")
tabla.column("Error_rel", width=100, anchor="center")
tabla.column("Error_%", width=100, anchor="center")


# ==========================
# SIMULACIÓN DE USUARIOS 
# ==========================
frame_params = tk.LabelFrame(root, text="Parámetros del modelo (Usuarios)")
frame_params.pack(fill="x", padx=10, pady=5)

tk.Label(frame_params, text="Tiempo inicial T0:").grid(row=0, column=0)
entry_T0 = tk.Entry(frame_params); entry_T0.insert(0, "0.1"); entry_T0.grid(row=0, column=1)

tk.Label(frame_params, text="Tasa r:").grid(row=0, column=2)
entry_r = tk.Entry(frame_params); entry_r.insert(0, "0.05"); entry_r.grid(row=0, column=3)

tk.Label(frame_params, text="Tiempo máximo K:").grid(row=0, column=4)
entry_K = tk.Entry(frame_params); entry_K.insert(0, "300"); entry_K.grid(row=0, column=5)

tk.Label(frame_params, text="Usuarios máx Umax:").grid(row=1, column=0)
entry_Umax = tk.Entry(frame_params); entry_Umax.insert(0, "500"); entry_Umax.grid(row=1, column=1)

tk.Label(frame_params, text="ΔU:").grid(row=1, column=2)
entry_dU = tk.Entry(frame_params); entry_dU.insert(0, "1"); entry_dU.grid(row=1, column=3)

# Tabla resultados usuarios
frame_tabla_usuarios = tk.Frame(root)
frame_tabla_usuarios.pack(fill="both", expand=True)

tabla_usuarios = ttk.Treeview(
    frame_tabla_usuarios,
    columns=("U", "T_aprox", "Error"),
    show="headings"
)
for col in ("U", "T_aprox", "Error"):
    tabla_usuarios.heading(col, text=col)
tabla_usuarios.pack(fill="both", expand=True)

#grafica

def graficar():
    try:
        f_str = convertir_formula(entry_funcion.get())
        y0 = float(entry_y0_euler.get())
        a = float(entry_a.get())
        b = float(entry_b.get())
        h = float(entry_h.get())
        y_real_str = convertir_formula(entry_y_real.get())

        # Definición de funciones
        f = lambda x, y: eval(f_str, {"x": x, "y": y, "np": np})
        y_real = lambda x: eval(y_real_str, {"x": x, "np": np})

        # Rango de valores
        n_pasos = int((b - a) / h)
        x_vals = [a + i*h for i in range(n_pasos+1)]

        # Método de Euler
        y_euler = [y0]
        for i in range(n_pasos):
            y_euler.append(y_euler[-1] + h * f(x_vals[i], y_euler[-1]))

        # Solución real
        y_real_vals = [y_real(x) for x in x_vals]

        # Gráfica
        plt.figure()
        plt.plot(x_vals, y_real_vals, label="Y real", marker="o")
        plt.plot(x_vals, y_euler, label="Euler", marker="x")
        plt.title("Método de Euler vs Solución Real")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend()
        plt.grid(True)
        plt.show()

    except Exception as e:
        resultado_var.set(f"Error en gráfica: {e}")




def simular_usuarios():
    try:
        T0 = float(entry_T0.get())
        r = float(entry_r.get())
        K = float(entry_K.get())
        Umax = int(entry_Umax.get())
        dU = int(entry_dU.get())

        U_vals = [0]
        T_vals = [T0]

        f = lambda U, T: r * T * (1 - T/K)

        for U in range(dU, Umax+dU, dU):
            Tn = T_vals[-1] + dU * f(U, T_vals[-1])
            U_vals.append(U)
            T_vals.append(Tn)

        for item in tabla_usuarios.get_children():
            tabla_usuarios.delete(item)

        for i in range(len(U_vals)):
            err_pct = (abs(T_vals[i] - T_vals[0]) / T_vals[0]) * 100 if i > 0 else 0
            tabla_usuarios.insert("", "end",
            values=(U_vals[i], round(T_vals[i], 4), round(err_pct, 3)))

        plt.figure()
        plt.plot(U_vals, T_vals, marker="o", label="T aproximado")
        plt.title("Crecimiento de usuarios")
        plt.xlabel("Usuarios (U)")
        plt.ylabel("Tiempo (T)")
        plt.legend()
        plt.grid(True)
        plt.show()

    except Exception as e:
        resultado_var.set(f"Error en simulación: {e}")

# Botones
btn_tabla = tk.Button(frame_euler_rk4, text="Generar Tabla", command=generar_tabla)
btn_tabla.grid(row=1, column=0, pady=5)

btn_grafica = tk.Button(frame_euler_rk4, text="Graficar", command=lambda: graficar())
btn_grafica.grid(row=1, column=1, pady=5)

btn_simular_usuarios = tk.Button(frame_params, text="Simular Usuarios", command=simular_usuarios)
btn_simular_usuarios.grid(row=2, column=0, columnspan=2, pady=5)

# Mostrar errores
lbl_resultado = tk.Label(root, textvariable=resultado_var, fg="red", font=("Consolas", 10))
lbl_resultado.pack(pady=5)

root.mainloop()
