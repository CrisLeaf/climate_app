import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error


# Monte Carlo Simulation
def get_monte_carlo(yearly_df, temp="tmax"):
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
	
	for i in range(50):
		X_sim = [year for year in range(yearly_df.index[-1].year + 1, 2101)]
		y_sim = linreg.predict(np.array(X_sim).reshape(-1, 1))
		epsilons = np.random.normal(0, linreg_mae, len(y_sim))
		y_sim = y_sim + epsilons
		X_sim.insert(0, yearly_df.index[-1].year)
		y_sim = list(y_sim)
		y_sim.insert(0, temperatures.values[-1])
		plt.plot(X_sim, y_sim, "grey")
		
	plt.plot(X_line, y_line, color="red")
	plt.plot(yearly_df.index.year, temperatures.values)
	plt.show()