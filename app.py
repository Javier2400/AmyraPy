import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt

# Crear ventana principal
root = tk.Tk()
root.title("Métodos de Euler y RK4")

# Variables globales
resultado_var = tk.StringVar()

# ===== BLOQUE METODO EULER Y RK4 =====
frame_euler_rk4 = tk.LabelFrame(root, text="Método de Euler y RK4")
frame_euler_rk4.pack(padx=10, pady=5, fill="x")

tk.Label(frame_euler_rk4, text="Ecuación f(x,y)=").grid(row=0, column=0)
entry_funcion = tk.Entry(frame_euler_rk4, width=25)
entry_funcion.insert(0, "0.1*np.sqrt(y) + 0.4*x**2")  # Ejemplo
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
entry_y_real.insert(0, "np.exp(0.1*x) + x**2")  # Ejemplo
entry_y_real.grid(row=0, column=11)

# Tabla
tabla = ttk.Treeview(frame_euler_rk4, columns=("n", "xn", "Yn_euler", "Yn_rk4", "f", "Y_real", "Error_abs", "Error_rel", "Error_%"), show="headings")
for col in tabla["columns"]:
    tabla.heading(col, text=col)
tabla.grid(row=2, column=0, columnspan=12, pady=5)

def generar_tabla():
    try:
        f_str = entry_funcion.get()
        y0 = float(entry_y0_euler.get())
        a = float(entry_a.get())
        b = float(entry_b.get())
        h = float(entry_h.get())
        y_real_str = entry_y_real.get()

        f = lambda x, y: eval(f_str, {"x": x, "y": y, "np": np})
        y_real = lambda x: eval(y_real_str, {"x": x, "np": np})

        n_pasos = int((b - a) / h)
        x_vals = [a + i*h for i in range(n_pasos+1)]

        # Método de Euler
        y_euler = [y0]
        for i in range(n_pasos):
            y_euler.append(y_euler[-1] + h * f(x_vals[i], y_euler[-1]))

        # Método RK4
        y_rk4 = [y0]
        for i in range(n_pasos):
            k1 = f(x_vals[i], y_rk4[-1])
            k2 = f(x_vals[i] + h/2, y_rk4[-1] + h*k1/2)
            k3 = f(x_vals[i] + h/2, y_rk4[-1] + h*k2/2)
            k4 = f(x_vals[i] + h, y_rk4[-1] + h*k3)
            y_rk4.append(y_rk4[-1] + (h/6)*(k1 + 2*k2 + 2*k3 + k4))

        # Mostrar en tabla
        for item in tabla.get_children():
            tabla.delete(item)
        for i in range(n_pasos+1):
            y_r = y_real(x_vals[i])
            err_abs = abs(y_r - y_euler[i])
            err_rel = err_abs / abs(y_r) if y_r != 0 else 0
            err_pct = err_rel * 100
            tabla.insert("", "end", values=(i, round(x_vals[i],4), round(y_euler[i],4), round(y_rk4[i],4),
                                            round(f(x_vals[i], y_euler[i]),4), round(y_r,4),
                                            round(err_abs,4), round(err_rel,6), round(err_pct,3)))
    except Exception as e:
        resultado_var.set(f"Error en tabla: {e}")

def graficar():
    try:
        f_str = entry_funcion.get()
        y0 = float(entry_y0_euler.get())
        a = float(entry_a.get())
        b = float(entry_b.get())
        h = float(entry_h.get())
        y_real_str = entry_y_real.get()

        f = lambda x, y: eval(f_str, {"x": x, "y": y, "np": np})
        y_real = lambda x: eval(y_real_str, {"x": x, "np": np})

        n_pasos = int((b - a) / h)
        x_vals = [a + i*h for i in range(n_pasos+1)]

        y_euler = [y0]
        y_rk4 = [y0]
        for i in range(n_pasos):
            y_euler.append(y_euler[-1] + h * f(x_vals[i], y_euler[-1]))

            k1 = f(x_vals[i], y_rk4[-1])
            k2 = f(x_vals[i] + h/2, y_rk4[-1] + h*k1/2)
            k3 = f(x_vals[i] + h/2, y_rk4[-1] + h*k2/2)
            k4 = f(x_vals[i] + h, y_rk4[-1] + h*k3)
            y_rk4.append(y_rk4[-1] + (h/6)*(k1 + 2*k2 + 2*k3 + k4))

        y_real_vals = [y_real(x) for x in x_vals]

        plt.figure()
        plt.plot(x_vals, y_real_vals, label="Y real", marker="o")
        plt.plot(x_vals, y_euler, label="Euler", marker="x")
        plt.plot(x_vals, y_rk4, label="RK4", marker="s")
        plt.title("Comparación de métodos")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend()
        plt.grid(True)
        plt.show()

    except Exception as e:
        resultado_var.set(f"Error en gráfica: {e}")

btn_tabla = tk.Button(frame_euler_rk4, text="Generar Tabla", command=generar_tabla)
btn_tabla.grid(row=1, column=0, pady=5)

btn_grafica = tk.Button(frame_euler_rk4, text="Graficar", command=graficar)
btn_grafica.grid(row=1, column=1, pady=5)

# Mostrar errores si ocurren
lbl_resultado = tk.Label(root, textvariable=resultado_var, fg="red", font=("Consolas", 10))
lbl_resultado.pack(pady=5)

root.mainloop()
#pruebaa
#aaaaaaaaaaaaaa
