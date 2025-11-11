import matplotlib.pyplot as plt

# Dades per cada mètode
replicas = list(range(1, 11))

# Beneficio Solución Final (€)
beneficio_base = [93092, 91568, 90584, 89888, 90708, 91784, 88688, 91564, 90732, 92112]
beneficio_greedy = [90660, 92104, 91464, 90440, 91568, 91136, 89564, 90020, 90972, 91704]
beneficio_vacia = [94908, 94436, 93924, 91248, 94148, 94176, 91536, 92216, 87696, 93688]

# Tiempo Solución Inicial (ms)
tiempo_init_base = [8.476, 6, 7.385, 8.252, 7.7, 8.007, 8.004, 6.387, 8.051, 7.591]
tiempo_init_greedy = [8.324, 9.649, 7.656, 7.752, 8.723, 7.77, 8.069, 7.051, 8.473, 6.726]
tiempo_init_vacia = [0.467, 0, 0.902, 0, 0.946, 0.512, 0.587, 0.601, 0.53, 0]

# Tiempo Solución Final (ms)
tiempo_final_base = [17396, 15834, 16052, 15172, 15560, 13147, 11353, 21858, 21220, 15558]
tiempo_final_greedy = [18546, 19041, 18058, 17394, 18616, 17726, 18320, 21704, 24442, 16885]
tiempo_final_vacia = [35947, 36413, 37514, 32528, 35095, 43022, 30233, 37736, 41038, 38515]

# --- Beneficio Boxplot ---
plt.figure(figsize=(8,5))
plt.boxplot([beneficio_vacia, beneficio_base, beneficio_greedy], labels=['Vacía','Base','Greedy'])
plt.title('Beneficio Solución Final (€)')
plt.ylabel('€')
plt.show()

# --- Tiempo Solución Inicial Boxplot ---
plt.figure(figsize=(8,5))
plt.boxplot([tiempo_init_vacia, tiempo_init_base, tiempo_init_greedy], labels=['Vacía','Base','Greedy'])
plt.title('Tiempo Solución Inicial (ms)')
plt.ylabel('ms')
plt.show()

# --- Tiempo Solución Final Boxplot ---
plt.figure(figsize=(8,5))
plt.boxplot([tiempo_final_vacia, tiempo_final_base, tiempo_final_greedy], labels=['Vacía','Base','Greedy'])
plt.title('Tiempo Solución Final (ms)')
plt.ylabel('ms')
plt.show()
