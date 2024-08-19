import streamlit as st
import requests
from datetime import datetime
import folium
from streamlit_folium import folium_static

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
    global current_time, search_query
    current_time = datetime.now().strftime("%H:%M")

    st.markdown("""
        <style>
        .main {
            max-width: 350px;
            margin: auto;
        }
        .stTextInput, .stButton {
            display: inline-block;
            vertical-align: middle;
        }
        .stTextInput {
            width: 70%;
        }
        .stButton {
            width: 25%;
        }
        </style>
    """, unsafe_allow_html=True)

    search_query = st.text_input("搜索停車場名稱或地址", key="search_input")
    search_button = st.button("搜尋")

    sort_by = st.selectbox("選擇排序依據", ["小車剩餘車位數", "平日收費", "假日收費"])

    def filter_and_display_data():
        data = fetch_data()
        update_time = data[0]['UPDATETIME'] if data else "無法獲取更新時間"
        st.write(f"數據更新時間: {update_time}")

        filtered_data = [park for park in data if is_open_now(park['BUSINESSHOURS'])]

        if search_query:
            filtered_data = [park for park in filtered_data if search_query in park['PARKINGNAME'] or search_query in park['ADDRESS']]
        else:
            filtered_data = data

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
                st.write(f"## {park['PARKINGNAME']}")
                st.write(f"地址: {park['ADDRESS']}")
                st.write(f"平日收費: {park['WEEKDAYS']}")
                st.write(f"假日收費: {park['HOLIDAY']}")
                st.write(f"小車剩餘車位數: {park['FREEQUANTITY']}/{park['TOTALQUANTITY']}")
                st.write(f"更新時間: {park['UPDATETIME']}")
                st.write("-" * 40)

    filter_and_display_data()

    # 如果搜索按鈕被按下，重新篩選和顯示數據
    if search_button:
        filter_and_display_data()

if __name__ == "__main__":
    main()
