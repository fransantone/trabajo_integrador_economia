import matplotlib.pyplot as plt
import numpy as np

#declarar vectores de la tabla
X = [173, 171, 180, 189]
y = [81, 72, 96, 94]

# agregar termino bias
X_ones = np.c_[np.ones(4), X]
print(X_ones)

# aplicar la ecuacion normal
theta = np.linalg.inv(X_ones.T.dot(X_ones)).dot(X_ones.T).dot(y)
print(theta)

#aproximacion de punto desconocido
punto_desconocido = theta[0] + (theta[1] * 179)
print(punto_desconocido)

#graficar valores ya conocidos
plt.scatter(X, y, s=40, c="#06d6a0")
# dibujar linea
X_lim = [170, 190]
X_lim_ones = np.c_[np.ones(2), X_lim]
Y_lim = X_lim_ones.dot(theta)
plt.plot(X_lim, Y_lim, 'r-')

# agregar cuadricula, titulo y leyenda
plt.axis([170,190, 70, 100])
plt.xlabel('Altura')
plt.ylabel('Peso')
plt.title('Altura x Peso')
plt.grid
plt.show()

