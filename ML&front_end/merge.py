# import pandas as pd

# # === 1. 读取两个数据集 ===
# df_places = pd.read_csv("orange_county_places_by_zip.csv")
# df_summary = pd.read_csv("community_summary.csv")

# # === 2. 把 region 字段设为主键，转成字典 ===
# region_dict = df_summary.set_index('region').T.to_dict()

# # === 3. 把 zip_code 转成字符串以便匹配 ===
# df_places['zip_code'] = df_places['zip_code'].astype(str)
# region_dict = {str(k): v for k, v in region_dict.items()}  # 确保 key 也是 str

# # === 4. 定义函数：找到匹配的 region 并添加其属性 ===
# def append_region_info(row):
#     zip_code = row['zip_code']
#     return pd.Series(region_dict.get(zip_code, {}))

# # === 5. 对每一行追加信息 ===
# df_combined = df_places.join(df_places.apply(append_region_info, axis=1))

# # === 6. 保存结果 ===
# df_combined.to_csv("places_with_region_data.csv", index=False)
# print("✅ 合并完成，结果保存为 places_with_region_data.csv")


import pandas as pd

# === 1. 读取两个数据集 ===
df_places = pd.read_csv("places_with_region_data.csv")
df_summary = pd.read_csv("ZHVI_updated_inserted.csv")

# === 2. 明确要追加的字段 ===
columns_to_add = [
    'start_price', 'end_price', 'growth_rate', 'zhvi_mean',
    'zhvi_median', 'zhvi_growth_pct', 'zhvi_std', 'zhvi_avg_annual_pct'
]

# === 3. 创建 region → 特征字典 ===
region_dict = df_summary.set_index('RegionName')[columns_to_add].T.to_dict()

# === 4. 确保 zip_code 是字符串（与 RegionName 匹配）
df_places['zip_code'] = df_places['zip_code'].astype(str)
region_dict = {str(k): v for k, v in region_dict.items()}

# === 5. 按行查找并添加字段
def append_region_info(row):
    zip_code = row['zip_code']
    region_data = region_dict.get(zip_code, {})
    return pd.Series({col: region_data.get(col) for col in columns_to_add})

df_combined = df_places.join(df_places.apply(append_region_info, axis=1))

# === 6. 保存合并结果 ===
df_combined.to_csv("places_with_zhvi_metrics.csv", index=False)
print("✅ 合并完成，结果已保存为 places_with_zhvi_metrics.csv")
