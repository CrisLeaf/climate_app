import streamlit as st
from get_daily_summaries import download_data, data_exists, insert_into_psql


header = st.container()
content = st.container()

with header:
	html_header = """
		<head>
		<link rel="stylesheet"href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"integrity="sha512-Fo3rlrZj/k7ujTnHg4CGR2D7kSs0v4LLanw2qksYuRlEzO+tcaEPQogQ0KaoGN26/zrn20ImR1DfuLWnOo7aBA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
		</head>
		<a href="https://crisleaf.github.io/apps.html">
			<i class="fas fa-arrow-left"></i>
		</a>
		<h2 style="text-align:center;">Simulador de Temperaturas</h2>
		<style>
            i {
                font-size: 30px;
                color: #222;
            }
            i:hover {
            	color: cornflowerblue;
            	transition: color 0.3s ease;
            }
        </style>
		"""
	st.markdown(html_header, unsafe_allow_html=True)

with content:
	city = st.text_input("Ciudad:", placeholder="Ingrese la ciudad... (ex: New York)")
	country = st.text_input("País:", placeholder="Ingrese el país... (ex: United States)")
	
	if st.button("Obtener"):
		if data_exists(city, country):
			st.write("Ya Existe")
		else:
			st.write(f"{city.capitalize()}, {country.capitalize()} no se encuentra en la base de "
					 f"datos.")
			if st.button("Descargar Datos"):
				st.write(":smile:")
		
		
		