import pandas as pd
import streamlit as st
from get_daily_summaries import download_data, data_exists, insert_into_psql
from psql_config import psql_params
import psycopg2
import SessionState
import plotly.express as px
from statsmodels.tsa.ar_model import AutoReg
from sklearn.metrics import mean_absolute_error
from monte_carlo import monte_carlo_simulation
from psql_create_tables import create_tables
from sqlalchemy import create_engine


def get_graphics(city, country):
	# PSQL
	conn = psycopg2.connect(**psql_params)
	curr = conn.cursor()
	curr.execute("SELECT city_id FROM cities WHERE city = %s AND country = %s", (city, country))
	city_id = curr.fetchall()[0][0]
	curr.execute("SELECT * FROM temperatures where city_id = %s", (city_id,))
	df = pd.DataFrame(curr.fetchall())[[3, 4, 5]]
	conn.commit()
	curr.close()
	conn.close()
	
	df.columns = ["Date", "Max. Temperature", "Min. Temperature"]
	n_filas = df.shape[0]
	missing_values = df.isna().sum().sum()
	missing_values += len(df[df["Max. Temperature"] == 0])
	missing_values += len(df[df["Min. Temperature"] == 0])
	df.dropna(inplace=True)
	df.drop(index=df[df["Max. Temperature"] == 0].index, inplace=True)
	df.drop(index=df[df["Min. Temperature"] == 0].index, inplace=True)
	df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
	df.sort_values(by="Date", inplace=True)
	df.set_index("Date", inplace=True)
	
	df["Max. Temperature"] = df["Max. Temperature"].apply(lambda x: int(x))
	df["Min. Temperature"] = df["Min. Temperature"].apply(lambda x: int(x))
	
	# Diaria
	html_title1 = """<h3 style="text-align:center;">Temperatura diaria</h3>"""
	st.markdown(html_title1, unsafe_allow_html=True)
	st.write(f"Primeros datos ingresados en {city.capitalize()}, {country.capitalize()}:")
	st.write(df.head(5))
	st.write(f"Últimos datos ingresados en {city.capitalize()}, {country.capitalize()}:")
	st.write(df.tail(5))
	st.write(f"Número total de filas:", n_filas, ". Número de datos (celdas) faltantes",
			 missing_values, ".")
	
	if missing_values / (n_filas * 2) >= 0.05:
		st.warning(f"Warning: Los datos faltantes representan el "
				   f"{missing_values / (n_filas * 2):.0%} de fechas incompletas. Lo que puede "
				   f"significar la obtención de resultados erróneos.")
	elif n_filas < 3650:
		st.warning(f"Los datos no alcanzan a completar un periodo de 10 años. Lo que "
				   f"puede significar en la obtención de resultados erróneos.")
	
	# Mensual
	html_title2 = """<h3 style="text-align:center;">Temperatura Promedio Mensual</h3>"""
	st.markdown(html_title2, unsafe_allow_html=True)
	monthly_df = df.groupby(pd.Grouper(freq="M")).mean()
	
	fig1 = px.line(monthly_df["Max. Temperature"],
				   title="Temperatura Máxima:",
				   labels={"value": "Temperatura (°F)", "Date": "Año"})
	st.write(fig1)
	fig2 = px.line(monthly_df["Min. Temperature"],
				   title="Temperatura Mínima:",
				   labels={"value": "Temperatura (°F)", "Date": "Año"})
	st.write(fig2)
	
	# Anual
	html_title3 = """<h3 style="text-align:center;">Temperatura Promedio Anual</h3>"""
	st.markdown(html_title3, unsafe_allow_html=True)
	
	yearly_df = df.groupby(pd.Grouper(freq="Y")).mean()
	fig3 = px.line(yearly_df["Max. Temperature"],
				   title="Temperatura Máxima:",
				   labels={"value": "Temperatura (°F)", "Date": "Año"})
	st.write(fig3)
	fig4 = px.line(yearly_df["Min. Temperature"],
				   title="Temperatura Mínima:",
				   labels={"value": "Temperatura (°F)", "Date": "Año"})
	st.write(fig4)
	
	# Predicciones
	html_title4 = """<h3 style="text-align:center;">Apendizaje Automático</h3>"""
	st.markdown(html_title4, unsafe_allow_html=True)
	
	# Linear Regression
	linreg_title1 = """<h4 style="text-align:left;">Regresión Lineal</h4>"""
	st.markdown(linreg_title1, unsafe_allow_html=True)
	
	monthly_df["tmax_diff"] = monthly_df["Max. Temperature"].diff(1)
	monthly_df["tmax_lag"] = monthly_df["Max. Temperature"].shift(1)
	monthly_df["tmin_diff"] = monthly_df["Min. Temperature"].diff(1)
	monthly_df["tmin_lag"] = monthly_df["Min. Temperature"].shift(1)
	monthly_df.dropna(inplace=True)
	
	st.write("Entrenamos un modelo de Regresión Lineal para la temperatura máxima mensual, "
			 "y obtenemos la siguiente tendencia:")
	st.write("Temperatura Máxima:")
	reg_fig1 = px.scatter(yearly_df["Max. Temperature"], trendline="ols",
						  labels={"value": "Temperatura (°F)", "Date": "Año"})
	st.write(reg_fig1)
	
	## tmin
	st.write("Temperatura Mínima:")
	reg_fig2 = px.scatter(yearly_df["Min. Temperature"], trendline="ols",
						  labels={"value": "Temperatura (°F)", "Date": "Año"})
	st.write(reg_fig2)
	
	# Monte Carlo
	monte_carlo_title1 = """<h4 style="text-align:left;">Simulación de Monte Carlo</h4>"""
	st.markdown(monte_carlo_title1, unsafe_allow_html=True)
	
	## tmax
	st.write("Ahora que sabemos la tendencia de la temperatura, podemos hacer una simulación de "
			 "Monte Carlo:.")
	
	st.write("Temperatura Máxima:")
	monte_carlo_fig1 = monte_carlo_simulation(yearly_df, temp="tmax")
	st.write(monte_carlo_fig1)
	
	## tmax
	st.write("Temperatura Mínima:")
	
	monte_carlo_fig2 = monte_carlo_simulation(yearly_df, temp="tmin")
	st.write(monte_carlo_fig2)
	
	# Time Series
	time_series_title1 = """<h4 style="text-align:left;">Series de Tiempo</h4>"""
	st.markdown(time_series_title1, unsafe_allow_html=True)
	st.write("Entrenamos un modelo de Series de Tiempo y obtenemos lo siguiente:")
	
	tmax_model = AutoReg(monthly_df["tmax_diff"], lags=12)
	
	tmax_model_fit = tmax_model.fit()
	tmax_residuals = tmax_model_fit.resid
	tmax_res_fig = px.scatter(tmax_residuals,
							  labels={"value": "Temperatura (°F)", "Date": "Año"})
	
	tmax_resid = tmax_model_fit.predict().dropna()
	ma_tmax_predictions = monthly_df["tmax_lag"].iloc[12:] + tmax_resid
	tmax_mae = mean_absolute_error(monthly_df["Max. Temperature"].iloc[12:], ma_tmax_predictions)
	
	yearly_df = monthly_df.iloc[12:].groupby(pd.Grouper(freq="Y")).mean()
	ma_tmax_yearly_prediction = ma_tmax_predictions.groupby(pd.Grouper(freq="Y")).mean()
	tmax_pred_df = pd.concat([yearly_df["Max. Temperature"], ma_tmax_yearly_prediction], axis=1)
	tmax_pred_df.columns = ["Original", "Entrenamiento"]
	tmax_pred_fig = px.line(tmax_pred_df,
							labels={"value": "Temperatura (°F)", "index": "Año"})
	
	tmin_model = AutoReg(monthly_df["tmin_diff"], lags=12)
	tmin_model_fit = tmin_model.fit()
	tmin_residuals = tmin_model_fit.resid
	tmin_res_fig = px.scatter(tmin_residuals,
							  labels={"value": "Temperatura (°F)", "Date": "Año"})
	
	tmin_resid = tmin_model_fit.predict().dropna()
	ma_tmin_predictions = monthly_df["tmin_lag"].iloc[12:] + tmin_resid
	tmin_mae = mean_absolute_error(monthly_df["Min. Temperature"].iloc[12:], ma_tmin_predictions)
	
	yearly_df = monthly_df.iloc[12:].groupby(pd.Grouper(freq="Y")).mean()
	ma_tmin_yearly_prediction = ma_tmin_predictions.groupby(pd.Grouper(freq="Y")).mean()
	tmin_pred_df = pd.concat([yearly_df["Min. Temperature"], ma_tmin_yearly_prediction], axis=1)
	tmin_pred_df.columns = ["Original", "Entrenamiento"]
	tmin_pred_fig = px.line(tmin_pred_df,
							labels={"value": "Temperatura (°F)", "index": "Año"})
	
	st.write("Residuales de Temperatura Máxima:")
	st.write(tmax_res_fig)
	st.write(f"Promedio de Error Absoluto Mensual:", round(tmax_mae, 2))
	st.write("Residuales de Temperatura Mínima:")
	st.write(tmin_res_fig)
	st.write(f"Promedio de Error Absoluto Mensual:", round(tmin_mae, 2))
	st.write("Entrenamiento de Temperatura Máxima:")
	st.write(tmax_pred_fig)
	st.write("Entrenamiento de Temperatura Mínima:")
	st.write(tmin_pred_fig)

def main():
	# engine = create_engine("postgresql://<username>:<password>@localhost:5432/<database name>")
	
	create_tables()
	
	html_header = """
		<head>
		<link rel="stylesheet"href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"integrity="sha512-Fo3rlrZj/k7ujTnHg4CGR2D7kSs0v4LLanw2qksYuRlEzO+tcaEPQogQ0KaoGN26/zrn20ImR1DfuLWnOo7aBA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
		</head>
		<a href="https://crisleaf.github.io/apps.html">
			<i class="fas fa-arrow-left"></i>
		</a>
		<h2 style="text-align:center;">Simulador de Temperaturas</h2>
		<style>
			i {
				font-size: 30px;
				color: #222;
			}
			i:hover {
				color: cornflowerblue;
				transition: color 0.3s ease;
			}
		</style>
	"""
	st.markdown(html_header, unsafe_allow_html=True)
	
	city = st.text_input("Ciudad:", placeholder="Ingrese la ciudad... (ex: New York)").lower()
	country = st.text_input("País:", placeholder="Ingrese el país... (ex: United States)").lower()
	
	obtener_btn = st.empty()
	ss = SessionState.get(obtener_btn=False)
	
	if obtener_btn.button("Obtener"):
		ss.obtener_btn = True
		
		if data_exists(city, country):
			try:
				get_graphics(city, country)
			except:
				st.error(f"Ha habido un error al procesar los datos de {city.capitalize()}, "
						 f"{country.capitalize()}. Las posibles causas son: Los datos no están "
						 f"disponibles, están incompletos o son incoherentes.")
			more_info_html = """
				<a class="aqui" href="https://github.com/CrisLeaf/ny_is_burning/blob/master/temperature_analysis.ipynb">
				Más información
				</a>
			"""
			st.markdown(more_info_html, unsafe_allow_html=True)
		else:
			st.write("Obteniendo datos...")
			new_data = download_data(city, country)
			if new_data is None:
				st.error(
					f"{city.capitalize()}, {country.capitalize()} no se encuentra disponible. "
					f"Para más información visite "
					f"https://www.ncei.noaa.gov/access/search/dataset-search?text=daily%20summaries"
				)
			else:
				try:
					insert_into_psql(city, country, new_data)
					get_graphics(city, country)
				except:
					st.error(f"Ha habido un error al procesar los datos de {city.capitalize()}, "
							 f"{country.capitalize()}. Las posibles causas son: Los datos no están "
							 f"disponibles, están incompletos o son incoherentes.")
				more_info_html = """
					<a class="aqui" href="https://github.com/CrisLeaf/ny_is_burning/blob/master/temperature_analysis.ipynb">
					Más información
					</a>
				"""
				st.markdown(more_info_html, unsafe_allow_html=True)
	
	html_source_code = """
		<p class="source-code">Código Fuente:
		<a href="https://github.com/CrisLeaf/temperature_app">
		<i class="fab fa-github"></i></a></p>
		<style>
			.source-code {
				text-align: right;
			}
		</style>
	"""
	st.markdown(html_source_code, unsafe_allow_html=True)
	
if __name__ == "__main__":
    main()