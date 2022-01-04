import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error


def monte_carlo_simulation(yearly_df, temp="tmax"):
	if temp == "tmax":
		temperatures = yearly_df["Max. Temperature"]
	elif temp == "tmin":
		temperatures = yearly_df["Min. Temperature"]
	else:
		print("temp ingresado no es válido. Posibles valores: 'tmax' y 'tmin'.")
		return
	
	linreg = LinearRegression()
	linreg.fit(np.array(yearly_df.index.year).reshape(-1, 1), temperatures.values)

	X_line = [year for year in range(min(yearly_df.index).year, 2101)]
	y_line = linreg.predict(np.array(X_line).reshape(-1, 1))
	
	X = [year for year in range(min(yearly_df.index).year, yearly_df.index[-1].year + 1)]
	y = linreg.predict(np.array(X).reshape(-1, 1))
	
	linreg_mae = mean_absolute_error(temperatures.values, y)
	
	fig = plt.figure(figsize=(12, 6))
	
	for i in range(50):
		X_sim = [year for year in range(yearly_df.index[-1].year + 1, 2101)]
		y_sim = linreg.predict(np.array(X_sim).reshape(-1, 1))
		epsilons = np.random.normal(0, linreg_mae, len(y_sim))
		y_sim = y_sim + epsilons
		X_sim.insert(0, yearly_df.index[-1].year)
		y_sim = list(y_sim)
		y_sim.insert(0, temperatures.values[-1])
		plt.plot(X_sim, y_sim, "grey")
		
	plt.plot(yearly_df.index.year, temperatures.values, label="Original")
	plt.plot(X_sim, y_sim, "grey", label="Simulaciones")
	plt.plot(X_line, y_line, color="red", label="Tendencia")
	plt.ylabel("Temperatura (°K)")
	if temp == "tmax":
		plt.title("Simulación de Monte Carlo para Temperatura Máxima")
	elif temp == "tmin":
		plt.title("Simulación de Monte Carlo para Temperatura Mínima")
	plt.legend()
	plt.xlabel("Año")
	
	return fig