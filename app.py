from flask import Flask, render_template, request
import sympy as sp
import io
import base64
import matplotlib.pyplot as plt
import numpy as np

app = Flask(__name__)

t = sp.symbols('t')

@app.route("/", methods=["GET", "POST"])
def index():
    # Cadena vacía para resultados
    resultado = ""
    grafica_aproximacion = None
    grafica_temporal = None
    grafica_frecuencias_b = None
    grafica_frecuencias_a = None

    if request.method == "POST":
        try:
            # Definiciones básicas
            user_function = sp.sympify(request.form["funcion"])
            period = float(sp.sympify(request.form["T"]))
            N = int(request.form["N"])
            half_period = period/2
            w0 = 2*sp.pi/period

            # Cálculo de coeficientes 
            a0 = (1/period) * sp.integrate(user_function, (t, -half_period, half_period))
            an = lambda n: (2/period) * sp.integrate(user_function*sp.cos(n*w0*t), (t, -half_period, half_period))
            bn = lambda n: (2/period) * sp.integrate(user_function*sp.sin(n*w0*t), (t, -half_period, half_period))

            # Texto con coeficientes
            resultado += f"<b>a0</b> = {sp.simplify(a0)}<br>"
            for n in range(1, N+1):
                resultado += f"<b>a{n}</b> = {sp.simplify(an(n))}, <b>b{n}</b> = {sp.simplify(bn(n))}<br>"

            # Gráfica de la aproximación
            ts = np.linspace(-half_period, half_period, 1000)
            ft = np.zeros_like(ts, dtype=float) + float(a0/2)
            for n in range(1, N+1):
                ft += float(an(n))*np.cos(n*2*np.pi*ts/period) + float(bn(n))*np.sin(n*2*np.pi*ts/period)

            plt.figure(figsize=(8,3))
            f_num = sp.lambdify(t, user_function, "numpy")
            plt.plot(ts, f_num(ts), label="f(t)", color="black")
            plt.plot(ts, ft, label=f"Serie con N={N}", color="red")
            plt.legend(); plt.grid(True)

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            grafica_aproximacion = base64.b64encode(buf.read()).decode("utf-8")
            plt.close()
        
            # Gráfica temporal
            plt.figure(figsize=(8,3))
            plt.plot(ts, f_num(ts), label="f(t)", color="blue")
            plt.legend(); plt.grid(True)

            buf2 = io.BytesIO()
            plt.savefig(buf2, format="png")
            buf2.seek(0)
            grafica_temporal = base64.b64encode(buf2.read()).decode("utf-8")
            plt.close()

            # Gráfica de frecuencias para bn
            plt.figure(figsize=(8,3))
            n_vals = np.arange(1, N+1)
            b_vals = [float(bn(k)) for k in n_vals]

            plt.stem(n_vals, b_vals, linefmt="g-", markerfmt="go", basefmt=" ")
            plt.xlabel("Armónico n")
            plt.ylabel("Coeficiente b_n")
            plt.title("Espectro de frecuencias (b_n)")
            plt.grid(True)

            buf3 = io.BytesIO()
            plt.savefig(buf3, format="png")
            buf3.seek(0)
            grafica_frecuencias_b = base64.b64encode(buf3.read()).decode("utf-8")
            plt.close()

            # Gráfica de frecuencias para an
            plt.figure(figsize=(8,3))
            n_vals = np.arange(1, N+1)
            a_vals = [float(an(k)) for k in n_vals]

            plt.stem(n_vals, a_vals, linefmt="g-", markerfmt="go", basefmt=" ")
            plt.xlabel("Armónico n")
            plt.ylabel("Coeficiente a_n")
            plt.title("Espectro de frecuencias (a_n)")
            plt.grid(True)

            buf3 = io.BytesIO()
            plt.savefig(buf3, format="png")
            buf3.seek(0)
            grafica_frecuencias_a = base64.b64encode(buf3.read()).decode("utf-8")
            plt.close()

        except Exception as e:
            resultado = f"Error: {e}"

    return render_template(
            "index.html", resultado=resultado, grafica_aproximacion=grafica_aproximacion, 
            grafica_temporal=grafica_temporal, grafica_frecuencias_b = grafica_frecuencias_b,
            grafica_frecuencias_a = grafica_frecuencias_a
        )

if __name__ == "__main__":
    app.run(debug=True)
