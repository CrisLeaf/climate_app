import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("TkAgg") # <- for IntelliJ inline plotting
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("darkgrid")
from sklearn.linear_model import LinearRegression
from psql_config import psql_params
import psycopg2

city = "new york"
country = "united states"

conn = psycopg2.connect(**psql_params)
curr = conn.cursor()
curr.execute("SELECT city_id FROM cities WHERE city = %s AND country = %s", (city, country))
city_id = curr.fetchall()[0][0]
curr.execute("SELECT * FROM temperatures where city_id = %s", (city_id, ))
df = pd.DataFrame(curr.fetchall())[[3, 4, 5]]
df.columns = ["Date", "Max. Temperature", "Min. Temperature"]
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df.set_index("Date", inplace=True)
df["Max. Temperature"] = df["Max. Temperature"].apply(lambda x: int(x))
df["Min. Temperature"] = df["Min. Temperature"].apply(lambda x: int(x))
conn.commit()
curr.close()
conn.close()


print(df.head())
