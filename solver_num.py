from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import numpy as np

def resolver_numericamente(dydx_func, y0, t0, tf, mostrar_graf=True):
    t_eval = np.linspace(t0, tf, 200)

    def wrapper(t, y):
        return eval(dydx_func, {"__builtins__": {}}, {"t": t, "y": y, "np": np})

    sol = solve_ivp(wrapper, (t0, tf), [y0], t_eval=t_eval)

    if mostrar_graf:
        plt.figure()
        plt.plot(sol.t, sol.y[0], label="y(t)")
        plt.title("Solución numérica")
        plt.xlabel("t"); plt.ylabel("y(t)")
        plt.grid(True); plt.legend()
        plt.show()
    return sol
