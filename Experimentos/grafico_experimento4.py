import matplotlib.pyplot as plt
import numpy as np

# Datos del experimento
pares = ["10-100", "20-200", "30-300", "40-400", "50-500"]
#hill climbing
tiempo_hc = np.array([4354, 66344, 291608, 742149, 2834616])
#simuated annealing
tiempo_sa = np.array([15775, 215852, 858578, 2860327, 5187502])

# Crear figura
plt.figure(figsize=(8,5))

plt.plot(pares, tiempo_hc, '-o', label="Hill Climbing", linewidth=2)
plt.plot(pares, tiempo_sa, '-o', label="Simulated Annealing", linewidth=2)


plt.title("Comparación de escalabilidad: Hill Climbing vs Simulated Annealing")
plt.xlabel("Centros - Gasolineras")
plt.ylabel("Tiempo medio (ms)")

plt.grid(linestyle='--', alpha=0.5)
plt.legend()

# Guardar en archivo PNG
plt.savefig("experimento4.png", dpi=300)

# Mostrar en pantalla
plt.show()

