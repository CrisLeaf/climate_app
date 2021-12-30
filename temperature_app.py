import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")
import streamlit as st
from get_daily_summaries import download_data, data_exists, insert_into_psql
from psql_config import psql_params
import psycopg2
import SessionState
import plotly.express as px
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error


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

sarimax_iterations = 100

def get_graphics(city, country):
	# PSQL
	conn = psycopg2.connect(**psql_params)
	curr = conn.cursor()
	curr.execute("""SELECT * FROM temperatures""")
	df = pd.DataFrame(curr.fetchall())[[3, 4, 5]]
	df.columns = ["Date", "Max. Temperature", "Min. Temperature"]
	df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
	df.set_index("Date", inplace=True)
	df["Max. Temperature"] = df["Max. Temperature"].apply(lambda x: int(x))
	df["Min. Temperature"] = df["Min. Temperature"].apply(lambda x: int(x))
	conn.commit()
	curr.close()
	conn.close()
	
	# Diaria
	html_title1 = """<h3 style="text-align:center;">Temperatura diaria</h3>"""
	st.markdown(html_title1, unsafe_allow_html=True)
	st.write(f"Primeros datos ingresados en {city.capitalize()}, {country.capitalize()}:")
	st.write(df.head(5))
	st.write(f"Últimos datos ingresados en {city.capitalize()}, {country.capitalize()}:")
	st.write(df.tail(5))
	st.write(f"Número total de filas:", df.shape[0])
	
	# Mensual
	html_title2 = """<h3 style="text-align:center;">Temperatura Promedio Mensual</h3>"""
	st.markdown(html_title2, unsafe_allow_html=True)
	monthly_df = df.groupby(pd.Grouper(freq="M")).mean()
	
	fig1 = px.line(monthly_df["Max. Temperature"],
				   title="Promedio de temperatura máxima mensual:",
				   labels={"value": "Temperatura (°K)", "Date": "Año"})
	st.write(fig1)
	fig2 = px.line(monthly_df["Min. Temperature"],
				   title="Promedio de temperatura mínima mensual:",
				   labels={"value": "Temperatura (°K)", "Date": "Año"})
	st.write(fig2)
	
	# Anual
	html_title3 = """<h3 style="text-align:center;">Temperatura Promedio Anual</h3>"""
	st.markdown(html_title3, unsafe_allow_html=True)
	
	yearly_df = df.groupby(pd.Grouper(freq="Y")).mean()
	fig3 = px.line(yearly_df["Max. Temperature"],
				   title="Promedio de temperatura máxima anual:",
				   labels={"value": "Temperatura (°K)", "Date": "Año"})
	st.write(fig3)
	fig4 = px.line(yearly_df["Min. Temperature"],
				   title="Promedio de temperatura mínima anual:",
				   labels={"value": "Temperatura (°K)", "Date": "Año"})
	st.write(fig4)
	
	# Predicciones
	html_title4 = """<h3 style="text-align:center;">Predicción de Temperatura (
			SARIMAX)</h3>"""
	st.markdown(html_title4, unsafe_allow_html=True)
	st.write("(El entrenamiento del modelo puede tardar unos segundos)")
	
	## tmax
	tmax_model = SARIMAX(monthly_df["Max. Temperature"], order=(1, 2, 10),
						 seasonal_order=(1, 1, 1, 12))
	tmax_model_fit = tmax_model.fit(maxiter=sarimax_iterations, disp=0)
	tmax_residuals = tmax_model_fit.resid
	tmax_res_fig = px.scatter(tmax_residuals,
							  labels={"value": "Temperatura (°K)", "Date": "Año"})
	st.write("Residuales del entreno del modelo de temperatura máxima mensual:")
	st.write(tmax_res_fig)
	
	tmax_yhat = tmax_model_fit.predict()
	tmax_yearly_pred = tmax_yhat.groupby(pd.Grouper(freq="Y")).mean()
	tmax_mae = mean_absolute_error(monthly_df["Max. Temperature"], tmax_yhat)
	st.write("Promedio de error absoluto por mes:", round(tmax_mae, 2))
	
	output = tmax_model_fit.forecast(600)
	errors = pd.Series(index=output.index,
					   data=np.random.normal(loc=0, scale=tmax_mae, size=600))
	output = output + errors
	predictions = pd.concat([tmax_yhat, output], axis=0)
	tmax_yearly_pred = predictions.groupby(pd.Grouper(freq="Y")).mean()
	tmax_pred_df = pd.concat([yearly_df["Max. Temperature"], tmax_yearly_pred], axis=1)
	tmax_pred_df.columns = ["Original", "Predicted"]
	tmax_pred_fig = px.line(tmax_pred_df,
							labels={"value": "Temperatura (°K)", "index": "Año"})
	st.write(tmax_pred_fig)
	
	## tmin
	st.write("(El entrenamiento del modelo puede tardar unos segundos)")
	tmin_model = SARIMAX(monthly_df["Min. Temperature"], order=(1, 2, 10),
						 seasonal_order=(1, 1, 1, 12))
	tmin_model_fit = tmin_model.fit(maxiter=sarimax_iterations, disp=0)
	tmin_residuals = tmin_model_fit.resid
	tmin_res_fig = px.scatter(tmin_residuals,
							  labels={"value": "Temperatura (°K)", "Date": "Año"})
	st.write("Residuales del entreno del modelo de temperatura mínima mensual:")
	st.write(tmin_res_fig)
	
	tmin_yhat = tmin_model_fit.predict()
	tmin_yearly_pred = tmin_yhat.groupby(pd.Grouper(freq="Y")).mean()
	tmin_mae = mean_absolute_error(monthly_df["Min. Temperature"], tmin_yhat)
	st.write("Promedio de error absoluto por mes:", round(tmin_mae, 2))
	
	output = tmin_model_fit.forecast(600)
	errors = pd.Series(index=output.index,
					   data=np.random.normal(loc=0, scale=tmin_mae, size=600))
	output = output + errors
	predictions = pd.concat([tmin_yhat, output], axis=0)
	tmin_yearly_pred = predictions.groupby(pd.Grouper(freq="Y")).mean()
	tmin_pred_df = pd.concat([yearly_df["Min. Temperature"], tmin_yearly_pred], axis=1)
	tmin_pred_df.columns = ["Original", "Predicted"]
	tmin_pred_fig = px.line(tmin_pred_df,
							labels={"value": "Temperatura (°K)", "index": "Año"})
	st.write(tmin_pred_fig)

obtener_btn = st.empty()
ss = SessionState.get(obtener_btn=False)

if obtener_btn.button("Obtener"):
	ss.obtener_btn = True
	
	if data_exists(city, country):
		get_graphics(city, country)
		html_source_code = """
				<p class="source-code">Código Fuente:
				<a href="https://github.com/CrisLeaf/ny_is_burning/blob/master/temperature_analysis.ipynb">
				<i class="fab fa-github"></i></a></p>
				<style>
					.source-code {
						text-align: right;
					}
				</style>
			"""
		st.markdown(html_source_code, unsafe_allow_html=True)
	else:
		st.write("Obteniendo datos...")
		try:
			new_data = download_data(city, country)
			insert_into_psql(city, country, new_data)
			get_graphics(city, country)
		except:
			st.write(f"{city.capitalize()}, {country.capitalize()} no se encuentra disponible.\n"
					 f"Para más información visite")
			st.write(
				"https://www.ncei.noaa.gov/access/search/dataset-search?text=daily%20summaries"
			)