import numpy as np
import matplotlib.pyplot as plt

# Parámetros
k = 10           # temperatura inicial
lmbda = 0.01     # constante de enfriamiento
n_iter = 500     # numero de iteraciones
deltaE = 1       # diferencia de energia (para encontrar la probabilidad)

t = np.arange(n_iter)

# Calculo de T
T = k * np.exp(-lmbda * t)

# Probabilidad
P = np.exp(-deltaE / T)

# Gráfica
plt.figure(figsize=(8,5))
plt.plot(t, P, color='royalblue', linewidth=2)
plt.title('Evolución de la probabilidad de acceptación en Simulated Annealing', fontsize=14)
plt.xlabel('Iteración', fontsize=12)
plt.ylabel('Probabilidad de acceptación', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()
