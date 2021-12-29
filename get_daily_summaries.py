import pandas as pd
from ncei_api import NCEIData
from selenium import webdriver
import re
import time
import psycopg2
from psql_config import psql_params


def download_data(city, country):
	cities_df = pd.read_csv("worldcities.csv")[["city", "country", "lat", "lng"]]
	cities_df["city"] = cities_df["city"].apply(lambda x: x.lower())
	cities_df["country"] = cities_df["country"].apply(lambda x: x.lower())
	cities_df2 = cities_df[cities_df["country"] == country]
	coordinates = cities_df2[cities_df2["city"] == city][["city", "country", "lat", "lng"]]
	
	try:
		north = round(coordinates["lat"].values[0] + 0.5, 3)
		south = round(coordinates["lat"].values[0] - 0.5, 3)
		east = round(coordinates["lng"].values[0] + 0.5, 3)
		west = round(coordinates["lng"].values[0] - 0.5, 3)
		query_url = "https://www.ncei.noaa.gov/access/search/data-search/daily-summaries?bbox=" + \
					str(north) + "," + str(west) + "," + str(south) + "," + str(east)
	except:
		return
	
	browser = webdriver.Firefox()
	browser.get(query_url)
	time.sleep(2)
	html = browser.page_source
	browser.close()
	station = re.findall(r"[A-Z]*[0-9]*.csv", html)[0]
	station = re.findall(r"[A-Z]*[0-9]*", station)[0]
	params = {
		"dataset_name": "daily-summaries",
		"data_types": "TMAX, TMIN",
		"stations": station,
		"start_date_time": "1800-12-20",
		"end_date_time": "2022-12-31",
		"location": "90,-180,-90,180"
	}
	ncei_data = NCEIData(**params)
	data = ncei_data.get_data()
	data_splited = data.split("\n")

	return data_splited

def data_exists(city, country):
	conn = psycopg2.connect(**psql_params)
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
	conn = psycopg2.connect(**psql_params)
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