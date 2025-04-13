# import requests
# api_key = "ae1618f0bd9c54f6d45e71b8c54a5cb5"
# zip_code = "92617"
# geo_type = "ZI"
# url = "https://api.gateway.attomdata.com/v4/location/lookup"
# params = {
#     "name": zip_code,
#     "geographyTypeAbbreviation": geo_type
# }
# headers = {
#     "apikey": api_key
# }

# # 发送请求
# response = requests.get(url, headers=headers, params=params)

# # 打印结果
# if response.status_code == 200:
#     data = response.json()
#     geo_id_v4 = data['geographies'][0]['geoIdV4']
#     print("✅ 请求成功，返回数据如下：")
#     print(data)
# else:
#     print(f"❌ 请求失败，状态码：{response.status_code}")
#     print(response.text)

import requests
import pandas as pd

# API setup
api_key = "ae1618f0bd9c54f6d45e71b8c54a5cb5"
url = "https://api.gateway.attomdata.com/v4/location/lookup"
headers = {"apikey": api_key}

# List of target zip codes
target_zips = [
    90630, 90680, 90720, 92603, 92604, 92606, 92612, 92614, 92618,
    92625, 92626, 92627, 92660, 92662, 92683, 92701, 92703, 92704,
    92705, 92706, 92707, 92782, 92801, 92802, 92804, 92805, 92806,
    92831, 92832, 92833, 92840, 92841, 92866, 92868, 92869, 92870
]

# Collect results
results = []

for zip_code in target_zips:
    params = {
        "name": str(zip_code),
        "geographyTypeAbbreviation": "ZI"
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            geo_id_v4 = data['geographies'][0]['geoIdV4']
            results.append({"zip_code": zip_code, "geo_id_v4": geo_id_v4})
        else:
            results.append({"zip_code": zip_code, "geo_id_v4": "REQUEST_FAILED"})
    except Exception as e:
        results.append({"zip_code": zip_code, "geo_id_v4": str(e)})

# Save results to CSV
df_geo = pd.DataFrame(results)
df_geo.to_csv("zip_to_geo_id.csv", index=False)
