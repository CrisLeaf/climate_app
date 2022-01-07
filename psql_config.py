import os
import streamlit as st

# psql_params = {
# 	"host": os.environ["CLIMATE_DATABASE_HOST"],
# 	"port": os.environ["CLIMATE_DATABASE_PORT"],
# 	"user": os.environ["CLIMATE_DATABASE_USER"],
# 	"password": os.environ["CLIMATE_DATABASE_PASSWORD"],
# 	"database": os.environ["CLIMATE_DATABASE"]
# }

psql_params = {
	"host": st.secrets("db_host"),
	"port": st.secrets("db_port"),
	"user": st.secrets("db_user"),
	"password": st.secrets("db_pass"),
	"database": st.secrets("db_name"),
}