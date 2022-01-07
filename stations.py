import pandas as pd


def get_stations(city, country):
	cities_df = pd.read_csv("worldcities.csv")[["city", "country", "lat", "lng"]]
	cities_df["city"] = cities_df["city"].apply(lambda x: x.lower())
	cities_df["country"] = cities_df["country"].apply(lambda x: x.lower())
	cities_df2 = cities_df[cities_df["country"] == country]
	coordinates = cities_df2[cities_df2["city"] == city][["city", "country", "lat", "lng"]]
	
	with open("stations.txt", "r") as stations:
		lines = stations.readlines()
	
	stations = []
	for i in range(2, len(lines)):
		try:
			latitude_diff = abs(float(lines[i][57:64]) - coordinates["lat"].values[0])
			longitude_diff = abs(float(lines[i][65:73]) - coordinates["lng"].values[0])
			if latitude_diff < 0.5 and longitude_diff < 0.5:
				print(f"station: {lines[i][:7]}")
				stations.append(lines[i][43:45] + "000" + lines[i][:6])
				stations.append(lines[i][43:45] + "M00" + lines[i][:6])
				stations.append(lines[i][43:45] + "W00" + lines[i][:6])
				stations.append(lines[i][43:45] + "0000" + lines[i][:5])
				stations.append(lines[i][43:45] + "M000" + lines[i][:5])
				stations.append(lines[i][43:45] + "W000" + lines[i][:5])
		except:
			pass
	
	stations = ",".join(stations)
	
	return stations