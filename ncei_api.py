import requests


class NCEIData:
	"""
	References:
	https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation
	"""
	
	def __init__(self, dataset_name, data_types, stations, start_date_time, end_date_time,
				 location):
		self._base_api_url = "https://www.ncei.noaa.gov/access/services/data/v1/?"
		self._dataset_name = self.call_api(dataset_name, data_types, stations, start_date_time,
										   end_date_time, location)
	
	def call_api(self, dataset_name, data_types, stations, start_date_time, end_date_time,
				 location):
		full_url = self._base_api_url + "dataset=" + dataset_name + "&dataTypes=" + data_types + \
				   "&stations=" + stations + "&startDate=" + start_date_time + "&endDate=" + \
				   end_date_time + "&boundingBox=" + location + "&units=standard"
		response = requests.get(full_url)
		return response.text
	
	def get_data(self):
		return self._dataset_name
	
	def write_data_file(self, file_name):
		with open(file_name, "w") as file:
			file.write(self._dataset_name)