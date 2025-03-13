import numpy as np
import matplotlib.pyplot as plt
import sympy as sym

# Define symbols
epsilon, x, p, c, tau = sym.symbols('epsilon x p c tau')

####### NACA 4-SERIES AIRFOIL - CHANGE STRING TO DESIRED AIRFOIL
NACA_string = input("Enter desired NACA airfoil (numbers only): ")

# Extract numerical values from string
eps = float(NACA_string[0]) / 100  # Convert to percentage of chord length
p_num = float(NACA_string[1]) / 10  # Camber position
tau_num = float(NACA_string[2] + NACA_string[3]) / 100  # Thickness as percentage

# Define chord length
c_value = 1  # Assume chord length is 1 for simplicity

# Define camber line equations using sym.Piecewise for conditional expression
ybar1 = eps * x / p_num**2 * (2 * p_num - x / c)
ybar2 = (eps * (c - x)) / (1 - p_num)**2 * (1 + x / c - 2 * p_num)
ybar = sym.Piecewise((ybar1, (x / c) < p_num), (ybar2, (x / c) >= p_num))

# Define thickness distribution equation
T_x = 10 * tau_num * c * (0.2969 * (x / c)**0.5 - 0.126 * (x / c) - 0.3537 * (x / c)**2 + 0.2843 * (x / c)**3 - 0.1015 * (x / c)**4)

# Generate x values along the chord
x_vals = np.linspace(0, c_value, 100)  # 100 points from 0 to chord length

# Calculate y values for camber line and thickness distribution
ybar_vals = [ybar.subs({c: c_value, x: xi}).evalf() for xi in x_vals]
T_x_vals = [T_x.subs({c: c_value, x: xi}).evalf() for xi in x_vals]

# Calculate upper and lower surfaces of the airfoil
upper_surface = [y + t/2 for y, t in zip(ybar_vals, T_x_vals)]
lower_surface = [y - t/2 for y, t in zip(ybar_vals, T_x_vals)]

# Plot the airfoil
plt.figure(figsize=(12, 6))
plt.plot(x_vals, upper_surface, label='Upper Surface')
plt.plot(x_vals, lower_surface, label='Lower Surface')
plt.plot(x_vals, ybar_vals, '--', color='gray', label='Camber Line')
plt.xlabel('x (Chord Position)')
plt.ylabel('y (Airfoil Height)')
plt.title(f'NACA {NACA_string} Airfoil')
plt.legend()
plt.axis('equal')
plt.grid(True)
plt.show()