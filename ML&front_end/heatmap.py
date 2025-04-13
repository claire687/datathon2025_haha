import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# === 1. 加载 ZHVI 数据 ===
df = pd.read_csv("ZHVI.csv")
df['start_price'] = df['2000-01-31']
df['end_price'] = df['2025-02-28']
df['growth_rate'] = (df['end_price'] - df['start_price']) / df['start_price'] * 100
growth_df = df[['RegionName', 'growth_rate']].copy()
growth_df['RegionName'] = growth_df['RegionName'].astype(str)

# === 2. 加载 ZIP Code 地理数据 ===
# 如果你有 geojson 文件：gpd.read_file("your_zip.geojson")
zip_shapes = gpd.read_file("ca_zip.geojson")  # 替换为你自己的路径
zip_shapes['ZCTA5CE10'] = zip_shapes['ZCTA5CE10'].astype(str)

# === 3. 合并房价数据和地图数据 ===
merged = zip_shapes.merge(growth_df, left_on='ZCTA5CE10', right_on='RegionName')

# === 4. 画热力图 ===
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
merged.plot(column='growth_rate',
            cmap='OrRd',
            linewidth=0.8,
            ax=ax,
            edgecolor='0.8',
            legend=True)

plt.title("ZHVI Growth Rate by ZIP Code (2000–2025)", fontsize=16)
plt.axis('off')
plt.show()
