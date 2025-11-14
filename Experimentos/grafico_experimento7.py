import matplotlib.pyplot as plt
import numpy as np

# Datos del experimento
horas = np.array([5, 6, 7, 8, 9, 10, 11, 12])

km_tot = np.array([
    3078.4,
    3417.6,
    3604.4,
    3824.27,
    4052.8,
    4091.47,
    4521.6,
    4632.8
])

beneficio = np.array([
    87264.53,
    89107.47,
    90036.53,
    90810.13,
    89731.73,
    89803.73,
    88964.80,
    88361.07
])

# Gráfico 1: Kilometros totales

plt.figure(figsize=(8,5))
plt.plot(horas, km_tot, '-o', color='steelblue', linewidth=2, markersize=6)

plt.title("Kilometraje total medio según horas de trabajo", fontsize=14)
plt.xlabel("Horas de trabajo diario", fontsize=12)
plt.ylabel("Kilometraje total medio (km)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig("experimento7_km.png", dpi=300)
plt.show()


# Gráfico 2: Beneficio 


plt.figure(figsize=(8,5))
plt.bar(horas, beneficio, color='steelblue', edgecolor='black')

plt.title("Beneficio medio según horas de trabajo", fontsize=14)
plt.xlabel("Horas de trabajo diario", fontsize=12)
plt.ylabel("Beneficio medio (€)", fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig("experimento7_beneficio.png", dpi=300)
plt.show()

print("Gráficos generados correctamente")
