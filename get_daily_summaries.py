import pandas as pd
from ncei_api import NCEIData
import psycopg2
# from psql_config import psql_params
from stations import get_stations
import streamlit as st


def download_data(city, country):
	stations = get_stations(city, country)
	for i in range(int(len(stations) / 50) + 1):
		stations_divided = ",".join(stations[0 + i*50:50 + i*50])
		params = {
			"dataset_name": "daily-summaries",
			"data_types": "TMAX,TMIN",
			"stations": stations_divided,
			"start_date_time": "1800-01-01",
			"end_date_time": "2021-12-31",
			"location": "90,-180,-90,180"
		}
		ncei_data = NCEIData(**params)
		data = ncei_data.get_data()
		data_splited = data.split("\n")
		if len(data_splited) >= 10000:
			break

	return data_splited

def data_exists(city, country):
	# conn = psycopg2.connect(**psql_params)
	conn = psycopg2.connect(st.secrets["postgres"])
	curr = conn.cursor()
	curr.execute("SELECT * FROM cities WHERE city = %s AND country = %s", (city, country))
	result = curr.fetchall()
	curr.close()
	conn.close()
	
	if len(result) == 0:
		return False
	else:
		return True

def insert_into_psql(city, country, data):
	# conn = psycopg2.connect(**psql_params)
	conn = psycopg2.connect(st.secrets["postgres"])
	curr = conn.cursor()
	
	try:
		curr.execute("INSERT INTO cities (city, country) VALUES (%s, %s)", (city, country))
	except:
		conn.rollback()
	
	curr.execute("SELECT city_id FROM cities WHERE city = %s AND country = %s", (city, country))
	city_id = curr.fetchall()[0][0]
	
	def clean_float(value):
		value = value.replace('"', '')
		if value == '':
			return 0.0
		else:
			return float(value)
	
	for i in range(1, len(data)):
		row = data[i]. split(",")
		if len(row) == 4:
			try:
				curr.execute(
					"""INSERT INTO temperatures (city_id, station, date, tmax, tmin)
					VALUES (%s, %s, %s, %s, %s)""",
					(city_id, row[0], row[1], clean_float(row[2]), clean_float(row[3]))
				)
			except:
				conn.rollback()
			
	conn.commit()
	curr.close()
	conn.close()
	

if __name__ == "__main__":
	city = input("Ingrese la ciudad:").lower()
	country = input("Ingrese el país:").lower()
	
	exists = data_exists(city, country)
	if not exists:
		print("Descargando datos...")
		data = download_data(city, country)
		if data == None:
			print(f"{city.capitalize()}, {country.capitalize()} no se ha podido encontrar.")
		else:
			insert_into_psql(city, country, data)
			print(f"Datos de {city.capitalize()}, {country.capitalize()} agregados "
				  f"satisfactoriamente!")
	else:
		print(f"{city.capitalize()}, {country.capitalize()} ya existe en la base de datos.")
		while True:
			redownload = input("Quieres descargar los datos nuevamente?[y/n]:").lower()
			if redownload == "y":
				print("Descargando datos...")
				data = download_data(city, country)
				if data == None:
					print(f"{city.capitalize()}, {country.capitalize()} no se ha podido encontrar.")
				else:
					insert_into_psql(city, country, data)
					print(f"Datos de {city.capitalize()}, {country.capitalize()} agregados "
						  f"satisfactoriamente!")
				break
			elif redownload == "n":
				break