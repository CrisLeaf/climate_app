import os

psql_params = {
	"host": os.environ["CLIMATE_DATABASE_HOST"],
	"port": os.environ["CLIMATE_DATABASE_PORT"],
	"user": os.environ["CLIMATE_DATABASE_USER"],
	"password": os.environ["CLIMATE_DATABASE_PASSWORD"],
	"database": os.environ["CLIMATE_DATABASE"]
}