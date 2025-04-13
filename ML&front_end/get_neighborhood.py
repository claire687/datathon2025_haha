import requests
import pandas as pd
import time

api_key = "ae1618f0bd9c54f6d45e71b8c54a5cb5"
headers = {"apikey": api_key}
base_url = "https://api.gateway.attomdata.com/v4/neighborhood/community"


df_geo = pd.read_csv("zip_to_geo_id.csv") 
geo_ids = df_geo['geo_id_v4'].dropna().unique()

results = []

for geo_id in geo_ids:
    if geo_id in ["REQUEST_FAILED", ""]:  # skip failed or blank
        continue

    params = {"geoIdv4": geo_id}
    try:
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"❌ 请求失败: {geo_id} 状态码: {response.status_code}")
            continue

        data = response.json()
        demo = data['community']['demographics']
        crime = data['community']['crime']
        climate = data['community']['climate']
        disaster = data['community']['naturalDisasters']
        geo = data['community']['geography']

        summary = {
            "geoIdV4": geo.get('geoIdV4'),
            "region": geo.get('geographyName'),
            "population": demo.get('population'),
            "median_age": demo.get('median_Age'),
            "avg_income": demo.get('avg_Household_Income'),
            "white_collar_pct": demo.get('occupation_White_Collar_Pct'),
            "edu_bachelor_plus_pct": sum([
                demo.get('education_Bach_Degree_Pct', 0),
                demo.get('education_Mast_Degree_Pct', 0),
                demo.get('education_Prof_Degree_Pct', 0),
                demo.get('education_Doct_Degree_Pct', 0)
            ]),
            "crime_index": crime.get('crime_Index'),
            "robbery_index": crime.get('forcible_Robbery_Index'),
            "assault_index": crime.get('aggravated_Assault_Index'),
            "avg_temp": climate.get('annual_Avg_Temp'),
            "sunshine_pct": climate.get('possible_Sunshine_Pct'),
            "annual_rainfall_in": climate.get('annual_Precip_In'),
            "earthquake_risk": disaster.get('earthquake_Index'),
            "hurricane_risk": disaster.get('hurricane_Index'),
            "tornado_risk": disaster.get('tornado_Index'),
        }

        results.append(summary)
        print(f"✅ 成功处理 geoId: {geo_id}")
        time.sleep(0.5)  # Optional: avoid rate limiting

    except Exception as e:
        print(f"⚠️ 发生异常 geoId: {geo_id}, 错误: {e}")
        continue

# === Step 3: Save all to CSV ===
df_result = pd.DataFrame(results)
df_result.to_csv("community_summary.csv", index=False)
print("📁 所有数据已保存至 community_summary.csv")