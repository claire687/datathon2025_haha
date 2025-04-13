import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder


category_options = sorted([
    'bakery', 'book_store', 'clothing_store', 'convenience_store', 'department_store',
    'drugstore', 'electronics_store', 'finance', 'furniture_store',
    'grocery_or_supermarket', 'hardware_store', 'home_goods_store',
    'liquor_store', 'point_of_interest', 'shoe_store', 'store', 'supermarket'
])


st.title("📍 Best ZIP Code Recommender by Business Category")

selected_category = st.selectbox("Choose or type a business category:", options=category_options, index=category_options.index("grocery_or_supermarket"))
top_n = st.slider("Number of top ZIP codes to display", 3, 20, 10)


@st.cache_data
def load_data():
    df = pd.read_csv("final_dataset.csv")
    df['zip_code'] = df['zip_code'].astype(str)
    df['primary_category'] = df['primary_category'].astype(str)

    feature_cols = [
        'zip_code', 'primary_category',
        'zhvi_mean', 'avg_income', 'white_collar_pct',
        'edu_bachelor_plus_pct', 'crime_index', 'zhvi_growth_pct'
    ]
    df = df.dropna(subset=feature_cols + ['rating'])

    for col in feature_cols[2:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=feature_cols[2:])
    return df

df = load_data()

# === Train Model ===
ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
X_cat = ohe.fit_transform(df[['zip_code', 'primary_category']])
X_cat_df = pd.DataFrame(X_cat, columns=ohe.get_feature_names_out(['zip_code', 'primary_category']))

X_num = df[[
    'zhvi_mean', 'avg_income', 'white_collar_pct',
    'edu_bachelor_plus_pct', 'crime_index', 'zhvi_growth_pct'
]].reset_index(drop=True)

X = pd.concat([X_cat_df, X_num], axis=1)
y = df['rating'].reset_index(drop=True)

model = RandomForestRegressor(random_state=42)
model.fit(X, y)

# === Make Predictions ===
zip_group = df.groupby('zip_code').first()
results = []

for zip_code, row in zip_group.iterrows():
    try:
        input_df = pd.DataFrame([{
            'zip_code': zip_code,
            'primary_category': selected_category,
            'zhvi_mean': float(row['zhvi_mean']),
            'avg_income': float(row['avg_income']),
            'white_collar_pct': float(row['white_collar_pct']),
            'edu_bachelor_plus_pct': float(row['edu_bachelor_plus_pct']),
            'crime_index': float(row['crime_index']),
            'zhvi_growth_pct': float(row['zhvi_growth_pct'])
        }])

        X_cat_input = ohe.transform(input_df[['zip_code', 'primary_category']])
        X_cat_input_df = pd.DataFrame(X_cat_input, columns=ohe.get_feature_names_out(['zip_code', 'primary_category']))

        X_num_input = input_df.drop(columns=['zip_code', 'primary_category']).reset_index(drop=True)
        X_input_final = pd.concat([X_cat_input_df, X_num_input], axis=1)

        pred_rating = model.predict(X_input_final)[0]
        results.append((zip_code, round(pred_rating, 2)))

    except Exception as e:
        st.warning(f"❌ Failed for ZIP {zip_code}: {e}")

# === Display Results ===
top_zipcodes = sorted(results, key=lambda x: x[1], reverse=True)[:top_n]
st.subheader(f"🔍 Top {top_n} ZIP Codes for `{selected_category}`")
st.table(pd.DataFrame(top_zipcodes, columns=["ZIP Code", "Predicted Rating"]))


import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json

# ✅ Step 1: Define Orange County ZIP codes
orange_county_zips = [
    '90620', '90621', '90623', '92602', '92603', '92604', '92606', '92610', '92612',
    '92614', '92617', '92618', '92620', '92624', '92625', '92626', '92627', '92629',
    '92630', '92637', '92646', '92647', '92648', '92649', '92651', '92653', '92655',
    '92656', '92657', '92660', '92661', '92662', '92663', '92672', '92673', '92675',
    '92676', '92677', '92679', '92683', '92688', '92691', '92692', '92694', '92701',
    '92703', '92704', '92705', '92706', '92707', '92708', '92780', '92782', '92801',
    '92802', '92804', '92805', '92806', '92807', '92808', '92821', '92823', '92831',
    '92832', '92833', '92835', '92840', '92841', '92843', '92844', '92845', '92861',
    '92865', '92866', '92867', '92868', '92869', '92870', '92886', '92887'
]

@st.cache_data
def load_filtered_geojson():
    with open("ca_zip.geojson", "r") as f:
        data = json.load(f)

    filtered_features = [
        feature for feature in data["features"]
        if feature["properties"]["ZCTA5CE10"] in orange_county_zips
    ]

    data["features"] = filtered_features
    return data

geojson_data = load_filtered_geojson()


example_data = [
    ("92626", 4.57), ("92660", 4.43), ("90720", 4.38),
    ("92627", 4.36), ("92618", 4.35), ("90680", 4.34),
    ("92707", 4.34), ("92703", 4.33), ("92625", 4.31),
    ("92683", 4.31)
]

rating_map_df = pd.DataFrame(example_data, columns=["zip_code", "predicted_rating"])
rating_map_df["zip_code"] = rating_map_df["zip_code"].astype(str)


rating_map_df = rating_map_df[rating_map_df["zip_code"].isin(orange_county_zips)]


m = folium.Map(location=[33.7, -117.8], zoom_start=9)


folium.Choropleth(
    geo_data=geojson_data,
    name="choropleth",
    data=rating_map_df,
    columns=["zip_code", "predicted_rating"],
    key_on="feature.properties.ZCTA5CE10",
    fill_color="Reds",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Predicted Rating",
).add_to(m)


st.subheader("🗺️ Orange County ZIP Code Suitability Heatmap")
st_folium(m, width=750, height=500)
