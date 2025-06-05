import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

xdata = np.array([-10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
ydata = np.array([1.2, 4.2, 6.7, 8.3, 10.6, 11.7, 13.5, 14.5, 15.7, 16.1, 16.6, 16.0, 15.4, 14.4, 14.2, 12.7, 10.3, 8.6, 6.1, 3.9, 2.1])

# Gaussian function
def Gauss(x, A, B):
    return A * np.exp(-B * x**2)

parameters, _ = curve_fit(Gauss, xdata, ydata)
fit_A, fit_B = parameters
fit_y = Gauss(xdata, fit_A, fit_B)

plt.plot(xdata, ydata, 'o', label='Data')
plt.plot(xdata, fit_y, '-', label='Fit')
plt.legend()
plt.show()