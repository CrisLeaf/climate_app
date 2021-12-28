import psycopg2
from psql_config import psql_params


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

print("Base de datos inicializada!")

conn.commit()
curr.close()
conn.close()
