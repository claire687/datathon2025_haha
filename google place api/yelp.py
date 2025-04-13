import requests

url = "https://api.yelp.com/v3/businesses/business_id_or_alias"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)