import psycopg2
from psql_config import psql_params
import streamlit as st


@st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})
def create_tables():
	commands = (
		"""
		CREATE TABLE IF NOT EXISTS cities (
			city_id SERIAL PRIMARY KEY ,
			city TEXT NOT NULL,
			country TEXT NOT NULL,
			UNIQUE (city, country)
		)
		""",
		"""
		CREATE TABLE IF NOT EXISTS temperatures (
			temp_id SERIAL PRIMARY KEY,
			city_id INT,
			station text,
			date DATE,
			tmax REAL,
			tmin REAL,
			CONSTRAINT fk_city FOREIGN KEY (city_id) REFERENCES cities(city_id),
			UNIQUE (station, date)
		)
		"""
	)
	
	conn = psycopg2.connect(**psql_params)
	# conn = psycopg2.connect(**st.secrets["postgres"])
	curr = conn.cursor()
	
	
	for command in commands:
		curr.execute(command)
	
	print("Base de datos creada!")
	
	conn.commit()
	curr.close()
	conn.close()
	
def reset_tables():
	commands = (
		"""
		DROP TABLE IF EXISTS temperatures
		""",
		"""
		DROP TABLE IF EXISTS cities
		""",
		"""
		CREATE TABLE cities (
			city_id SERIAL PRIMARY KEY ,
			city TEXT NOT NULL,
			country TEXT NOT NULL,
			UNIQUE (city, country)
		)
		""",
		"""
		CREATE TABLE temperatures (
			temp_id SERIAL PRIMARY KEY,
			city_id INT,
			station text,
			date DATE,
			tmax REAL,
			tmin REAL,
			CONSTRAINT fk_city FOREIGN KEY (city_id) REFERENCES cities(city_id),
			UNIQUE (station, date)
		)
		"""
	)
	
	conn = psycopg2.connect(**psql_params)
	curr = conn.cursor()
	
	for command in commands:
		curr.execute(command)
	
	print("Base de datos creada!")
	
	conn.commit()
	curr.close()
	conn.close()
	

if __name__ == "__main__":
    reset_tables()