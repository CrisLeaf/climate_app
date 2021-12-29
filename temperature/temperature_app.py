import streamlit as st
import pandas as pd
import streamlit.components.v1 as components


def main():
	html_temp = """
	<h1 style="text-align: center;">Título</h1>
	"""

	go_back_link = "[< Go Back](https://crisleaf.github.io/simulations.html)"
	st.markdown(go_back_link, unsafe_allow_html=True)

	st.markdown(html_temp, unsafe_allow_html=True)

	city = st.text_input("Ciudad")
	country = st.text_input("País")

	if st.button("Obtener"):
		cities_df = pd.read_csv("worldcities.csv")[["city", "country", "lat", "lng"]]
		cities_df["city"] = cities_df["city"].apply(lambda x: x.lower())
		cities_df["country"] = cities_df["country"].apply(lambda x: x.lower())
		cities_df2 = cities_df[cities_df["country"] == country]
		if cities_df2.shape[0] == 0:
			st.success(f"{city.capitalize()}, {country.capitalize()} "
					   f"no se encuentra en la base de datos.")
		else:
			try:
				coordinates = cities_df2[cities_df2["city"] == city][[
					"city", "country", "lat", "lng"
				]]
				st.write(f"{city.capitalize()}, {country.capitalize()} "
						 f"Latitud: {coordinates.lat.values[0]}")
				st.write(f"{city.capitalize()}, {country.capitalize()} "
						 f"Longitud: {coordinates.lng.values[0]}")
			except:
				st.success(f"{city.capitalize()}, {country.capitalize()} "
						   f"no se encuentra en la base de datos.")


if __name__ == "__main__":
	main()
