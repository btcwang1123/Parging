import streamlit as st
import requests
from datetime import datetime
import folium
from streamlit_folium import folium_static
import time

# 網頁 URL
url = "https://hispark.hccg.gov.tw/OpenData/GetParkInfo"

def fetch_data():
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("無法獲取數據")
        return []

def is_open_now(business_hours):
    return True

def parse_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def parse_float(value):
    try:
        return float(value.replace("元", ""))
    except (ValueError, TypeError):
        return 0

def main():
    global current_time
    current_time = datetime.now().strftime("%H:%M")

    search_query = st.text_input("搜索停車場名稱或地址")

    field_options = [
        "停車場編號", "停車場名稱", "地址", "營業時間", "平日收費", 
        "假日收費", "大車剩餘車位數", "小車剩餘車位數", "摩托車剩餘車位數", 
        "殘障車位剩餘數", "充電車位剩餘數", "更新時間"
    ]

    field_choice = st.multiselect("選擇顯示字段", field_options, 
                                  default=["停車場名稱", "地址", "小車剩餘車位數", "平日收費", "假日收費"])

    sort_by = st.selectbox("選擇排序依據", ["小車剩餘車位數", "平日收費", "假日收費"])

    st.markdown("""
        <style>
        .main {
            max-width: 350px;
            margin: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    while True:
        data = fetch_data()
        update_time = data[0]['UPDATETIME'] if data else "無法獲取更新時間"
        st.write(f"數據更新時間: {update_time}")

        filtered_data = [park for park in data if is_open_now(park['BUSINESSHOURS'])]

        if search_query:
            filtered_data = [park for park in filtered_data if search_query in park['PARKINGNAME'] or search_query in park['ADDRESS']]

        if sort_by == "停車場名稱":
            filtered_data.sort(key=lambda x: x['PARKINGNAME'])
        elif sort_by == "小車剩餘車位數":
            filtered_data.sort(key=lambda x: parse_int(x['FREEQUANTITY']), reverse=True)
        elif sort_by == "平日收費":
            filtered_data.sort(key=lambda x: parse_float(x['WEEKDAYS']))
        elif sort_by == "假日收費":
            filtered_data.sort(key=lambda x: parse_float(x['HOLIDAY']))

        if filtered_data:
            map_center = [float(filtered_data[0]['LATITUDE']), float(filtered_data[0]['LONGITUDE'])]
            folium_map = folium.Map(location=map_center, zoom_start=14, width=350)

            for park in filtered_data:
                folium.Marker(
                    location=[float(park['LATITUDE']), float(park['LONGITUDE'])],
                    popup=folium.Popup(f"""
                        停車場名稱: {park['PARKINGNAME']}<br>
                        地址: {park['ADDRESS']}<br>
                        小車剩餘車位數: {park['FREEQUANTITY']}/{park['TOTALQUANTITY']}<br>
                        平日收費: {park['WEEKDAYS']}<br>
                        假日收費: {park['HOLIDAY']}<br>
                        更新時間: {park['UPDATETIME']}
                    """, max_width=300),
                    icon=folium.Icon(icon="info-sign")
                ).add_to(folium_map)

            folium_static(folium_map, width=350)

        cols = st.columns(1)

        for i, park in enumerate(filtered_data):
            with cols[i % 1]:
                if "停車場編號" in field_choice:
                    st.write(f"停車場編號: {park['PARKNO']}")
                if "停車場名稱" in field_choice:
                    st.write(f"## {park['PARKINGNAME']}")
                if "地址" in field_choice:
                    st.write(f"地址: {park['ADDRESS']}")
                if "營業時間" in field_choice:
                    st.write(f"營業時間: {park['BUSINESSHOURS']}")
                if "平日收費" in field_choice:
                    st.write(f"平日收費: {park['WEEKDAYS']}")
                if "假日收費" in field_choice:
                    st.write(f"假日收費: {park['HOLIDAY']}")
                if "大車剩餘車位數" in field_choice:
                    st.write(f"大車剩餘車位數: {park['FREEQUANTITYBIG']}/{park['TOTALQUANTITYBIG']}")
                if "小車剩餘車位數" in field_choice:
                    st.write(f"小車剩餘車位數: {park['FREEQUANTITY']}/{park['TOTALQUANTITY']}")
                if "摩托車剩餘車位數" in field_choice:
                    st.write(f"摩托車剩餘車位數: {park['FREEQUANTITYMOT']}/{park['TOTALQUANTITYMOT']}")
                if "殘障車位剩餘數" in field_choice:
                    st.write(f"殘障車位剩餘數: {park['FREEQUANTITYDIS']}/{park['TOTALQUANTITYDIS']}")
                if "充電車位剩餘數" in field_choice:
                    st.write(f"充電車位剩餘數: {park['FREEQUANTITYECAR']}/{park['TOTALQUANTITYECAR']}")
                if "更新時間" in field_choice:
                    st.write(f"更新時間: {park['UPDATETIME']}")
                st.write("-" * 40)

        time.sleep(60)

if __name__ == "__main__":
    main()
