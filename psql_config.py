import os


psql_params = {
	"host": os.environ["db_host"],
	"port": os.environ["db_port"],
	"user": os.environ["db_user"],
	"password": os.environ["db_pass"],
	"database": os.environ["db_name"]
}