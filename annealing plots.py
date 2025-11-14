import matplotlib.pyplot as plt
import numpy as np

#Datos obtenidos con los experimentos
ref = -10787 #87760, 
uno_uno = -8455 #5 y 0.001, 86775,58s
uno_dos = -8532 #5 y 0.005, 86504,63s
uno_tres = -8240 #5 y 0.01, 86681,74s
uno_cuatro = -7972 #5 y 0.1, 85188, 81s
dos_uno = -7949 #10 y 0.001, 85690, 61s
dos_dos = -8697 #10 y 0.005, 86560, 51s
dos_tres = -8745 #10 y 0.01, 86710, 48s
dos_cuatro = -8421 #10 y 0.1, 86389, 54s
tres_uno = -8116 #20 y 0.001, 85448, 51s
tres_dos = -7932 #20 y 0.005, 85283, 57s
tres_tres = -8517 #20 y 0.01, 86527, 53s
tres_cuatro = -8132 #20 y 0.1, 86081, 48s
cuatro_uno = -8548 #50 y 0.001, 87248, 49s
cuatro_dos = -8036 #50 y 0.005, 86125, 51s
cuatro_tres = -7932 #50 y 0.01, 85862, 65s
cuatro_cuatro = -8084 #50 y 0.1, 86059, 68s
cinco_uno = -7070 #150 y 0.001, 83931, 82s
cinco_dos = -7743 #150 y 0.005, 85541, 58s
cinco_tres = -7673 #150 y 0.01, 84822, 50s
cinco_cuatro = -81780 #150 y 0.1, 85634, 64s

#Heuristica
resultats = {
    5:   {"0.001": -8455, "0.005": -8532, "0.01": -8240, "0.1": -7972},
    10:  {"0.001": -7949, "0.005": -8697, "0.01": -8745, "0.1": -8421},
    20:  {"0.001": -8116, "0.005": -7932, "0.01": -8517, "0.1": -8132},
    50:  {"0.001": -8548, "0.005": -8036, "0.01": -7932, "0.1": -8084},
    150: {"0.001": -7070, "0.005": -7743, "0.01": -7673, "0.1": -8178}
}

#Beneficio
resultatsb = [
    (5, 0.001, 86775),
    (5, 0.005, 86504),
    (5, 0.01, 86681),
    (5, 0.1, 85188),
    (10, 0.001, 85690),
    (10, 0.005, 86560),
    (10, 0.01, 86710),
    (10, 0.1, 86389),
    (20, 0.001, 85448),
    (20, 0.005, 85283),
    (20, 0.01, 86527),
    (20, 0.1, 86081),
    (50, 0.001, 87248),
    (50, 0.005, 86125),
    (50, 0.01, 85862),
    (50, 0.1, 86059),
    (150, 0.001, 83931),
    (150, 0.005, 85541),
    (150, 0.01, 84822),
    (150, 0.1, 85634)
]

beneficis_per_k = {}
for k, lam, b in resultatsb:
    if k not in beneficis_per_k:
        beneficis_per_k[k] = []
    beneficis_per_k[k].append(b)

# Boxplot beneficio
fig, ax = plt.subplots(figsize=(8, 5))
ax.boxplot(beneficis_per_k.values(), labels=[f'k={k}' for k in beneficis_per_k.keys()])

ax.set_title("Distribucion del beneficio obtenido para cada valor de k")
ax.set_xlabel("Valor de k")
ax.set_ylabel("Beneficio (mas es mejor)")
ax.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()
#Resultados tiempo
resultats_temps = [
    (5, 0.001, 58),
    (5, 0.005, 63),
    (5, 0.01, 74),
    (5, 0.1, 81),
    (10, 0.001, 61),
    (10, 0.005, 51),
    (10, 0.01, 48),
    (10, 0.1, 54),
    (20, 0.001, 51),
    (20, 0.005, 57),
    (20, 0.01, 53),
    (20, 0.1, 48),
    (50, 0.001, 49),
    (50, 0.005, 51),
    (50, 0.01, 65),
    (50, 0.1, 68),
    (150, 0.001, 82),
    (150, 0.005, 58),
    (150, 0.01, 50),
    (150, 0.1, 64),
]

# Agrupar tiempos por valor de k
tiempos_per_k = {}
for k, lam, t in resultats_temps:
    if k not in tiempos_per_k:
        tiempos_per_k[k] = []
    tiempos_per_k[k].append(t)

#Boxplot tiempo
fig, ax = plt.subplots(figsize=(8, 5))
ax.boxplot(tiempos_per_k.values(), labels=[f'k={k}' for k in tiempos_per_k.keys()])

ax.set_title("Distribución del tiempo de ejecución para cada valor de k")
ax.set_xlabel("Valor de k")
ax.set_ylabel("Tiempo de ejecución (s)")
ax.grid(True, linestyle='--', alpha=0.6)

plt.show()

ks = sorted(resultats.keys())
lambdas = ["0.001", "0.005", "0.01", "0.1"]


data = np.array([[resultats[k][lam] for lam in lambdas] for k in ks])

# Heatmap heurística
plt.figure(figsize=(8, 6))
im = plt.imshow(data, cmap="viridis", aspect="auto")

for i in range(len(ks)):
    for j in range(len(lambdas)):
        plt.text(j, i, f"{data[i, j]:.0f}", ha="center", va="center", color="white", fontsize=9)


plt.title("Heatmap de la heurística para combinaciones de k i λ")
plt.xlabel("λ")
plt.ylabel("k")
plt.xticks(ticks=range(len(lambdas)), labels=lambdas)
plt.yticks(ticks=range(len(ks)), labels=ks)
plt.colorbar(im, label="Valor heurístico")
plt.tight_layout()
plt.show()