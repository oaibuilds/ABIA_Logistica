import matplotlib.pyplot as plt

replicas = list(range(1, 11))

semillas = [2548,9493,4496,2944,829,4649,4864,3339,5555,9677]

# Beneficio Solución Final (€)
beneficio_5 = [89860,99740,95300,100140,97640,98440,88820,99940,99800,99880]
beneficio_10 = [95760,99900,99320,96020,99500,99460,99760,90820,97940,99780]

# Km totales
km_5 = [4390,4384,3876,4322,4178,3774,4222,3966,4002,4008]
km_10 = [3822,3774,3246,3822,3316,3790,3406,4022,3766,3772]


# Peticiones Atendidas
peticiones_5 = [90,100,96,100,98,99,89,100,100,100]
peticiones_10 = [96,100,100,96,100,100,100,91,98,100]

# --- Beneficio Boxplot ---
plt.figure(figsize=(8,5))
plt.boxplot([beneficio_5,beneficio_10], labels=['5 Centros', '10 Centros'])
plt.title('Beneficio Solución (€)')
plt.ylabel('€')
plt.show()

# --- Tiempo Solución Inicial Boxplot ---
plt.figure(figsize=(8,5))
plt.boxplot([km_5,km_10], labels=['km_totales 5 centros', 'km_totales 10 centros'])
plt.title('Distancia total recorrida (km)')
plt.ylabel('km')
plt.show()

# --- Tiempo Solución Final Boxplot ---
plt.figure(figsize=(8,5))
plt.boxplot([peticiones_5,peticiones_10], labels=['n de peticiones atendidas_5','n de peticiones atendidas_10'])
plt.title('Numero total de peticiones atendidas')
plt.ylabel('n')
plt.show()
