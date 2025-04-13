# import requests
# import pandas as pd
# import time
# import re

# API_KEY = 'AIzaSyDgpTNlmFWMPj3fm5uCnNLLb2PYX3PBmU8'  # Replace this with your real key

# def search_places(query, location, radius, next_page_token=None):
#     url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
#     params = {
#         'query': query,
#         'location': location,
#         'radius': radius,
#         'key': API_KEY
#     }
#     if next_page_token:
#         params['pagetoken'] = next_page_token
#         time.sleep(2)
#     response = requests.get(url, params=params)
#     return response.json()

# def get_place_details(place_id):
#     url = 'https://maps.googleapis.com/maps/api/place/details/json'
#     fields = 'name,rating,user_ratings_total,price_level,types,business_status,geometry,reviews,formatted_address'
#     params = {
#         'place_id': place_id,
#         'fields': fields,
#         'key': API_KEY
#     }
#     response = requests.get(url, params=params)
#     return response.json()

# def extract_zip_code(address):
#     match = re.search(r'\b\d{5}\b', address)
#     return match.group() if match else None


# def get_oc_places_sorted_by_zip(query='store', location='33.7175,-117.8311', radius=50000, max_results=60):
#     all_data = []
#     next_page_token = None
#     total_fetched = 0

#     while total_fetched < max_results:
#         results = search_places(query, location, radius, next_page_token)
#         places = results.get('results', [])
#         for place in places:
#             if total_fetched >= max_results:
#                 break
#             place_id = place['place_id']
#             detail = get_place_details(place_id).get('result', {})
#             address = detail.get('formatted_address', '')
#             zip_code = extract_zip_code(address)
#             if not zip_code:
#                 continue  # skip if no zip

#             data = {
#                 'name': detail.get('name'),
#                 'rating': detail.get('rating'),
#                 'price_level': detail.get('price_level'),
#                 'types': detail.get('types'),
#                 'business_status': detail.get('business_status'),
#                 'zip_code': zip_code,
#                 'reviews': [r.get('text') for r in detail.get('reviews', [])[:3]]
#             }
#             all_data.append(data)
#             total_fetched += 1
#         next_page_token = results.get('next_page_token')
#         if not next_page_token:
#             break

#     df = pd.DataFrame(all_data)
#     df_sorted = df.sort_values(by='zip_code').reset_index(drop=True)
#     return df_sorted


# # df = get_oc_places_sorted_by_zip(max_results=60)
# # print(df.head())


import requests
import pandas as pd
import time
import re

API_KEY = 'AIzaSyDgpTNlmFWMPj3fm5uCnNLLb2PYX3PBmU8'  # Replace this with your real Google Maps API key

# Step 1: Define multiple locations across Orange County
locations = [
    (33.6846, -117.8265),  # Irvine
    (33.8353, -117.9145),  # Anaheim
    (33.6405, -117.8443),  # Newport Beach
    (33.7460, -117.8677),  # Santa Ana
    (33.7805, -117.9897),  # Garden Grove
]


def extract_zip_code(address):
    match = re.search(r'\b\d{5}\b', address)
    return match.group() if match else None


def search_places_nearby(location, radius=5000, keyword='store'):
    lat, lng = location
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': f'{lat},{lng}',
        'radius': radius,
        'keyword': keyword,
        'key': API_KEY
    }
    all_places = []
    next_page_token = None

    for _ in range(3):  # Up to 3 pages per location
        if next_page_token:
            params['pagetoken'] = next_page_token
            time.sleep(2)
        response = requests.get(url, params=params)
        data = response.json()
        all_places.extend(data.get('results', []))
        next_page_token = data.get('next_page_token')
        if not next_page_token:
            break
    return all_places


def get_place_details(place_id):
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    fields = 'name,rating,user_ratings_total,price_level,types,business_status,geometry,reviews,formatted_address'
    params = {
        'place_id': place_id,
        'fields': fields,
        'key': API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

def collect_data_from_grid(locations, keyword='store'):
    all_data = []
    seen_place_ids = set()

    for loc in locations:
        print(f"Searching at location: {loc}")
        places = search_places_nearby(loc, keyword=keyword)
        for place in places:
            place_id = place['place_id']
            if place_id in seen_place_ids:
                continue
            seen_place_ids.add(place_id)

            detail_resp = get_place_details(place_id)
            result = detail_resp.get('result', {})
            if not result:
                continue

            address = result.get('formatted_address', '')
            zip_code = extract_zip_code(address)
            if not zip_code:
                continue

            data = {
                'name': result.get('name'),
                'rating': result.get('rating'),
                'price_level': result.get('price_level'),
                'types': result.get('types'),
                'business_status': result.get('business_status'),
                'user_ratings_total': result.get('user_ratings_total'),
                'zip_code': zip_code,
                'reviews': [r.get('text') for r in result.get('reviews', [])[:3]]
            }
            all_data.append(data)

    # Step 4: Create and sort DataFrame by ZIP code
    df = pd.DataFrame(all_data)
    df_sorted = df.sort_values(by='zip_code').reset_index(drop=True)
    return df_sorted

df = collect_data_from_grid(locations)
df.to_csv("orange_county_places_by_zip.csv", index=False)
# print(df.head())