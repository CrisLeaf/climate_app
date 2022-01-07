import os
import streamlit as st

# psql_params = {
# 	"host": os.environ["db_host"],
# 	"port": os.environ["db_port"],
# 	"user": os.environ["db_user"],
# 	"password": os.environ["db_pass"],
# 	"database": os.environ["db_name"]
# }

psql_params = {
	"host": st.secrets["db_host"],
	"port": st.secrets["db_port"],
	"user": st.secrets["db_user"],
	"password": st.secrets["db_pass"],
	"database": st.secrets["db_name"]
}