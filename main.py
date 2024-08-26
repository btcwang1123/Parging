import streamlit as st
import requests
from datetime import datetime
import folium
from streamlit_folium import folium_static
from streamlit_geolocation import streamlit_geolocation

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
    location = streamlit_geolocation()
    current_time = datetime.now().strftime("%H:%M")

    field_choice = ["停車場名稱", "地址", "小車剩餘車位數", "平日收費", "假日收費"]

    data = fetch_data()
    update_time = data[0]['UPDATETIME'] if data else "無法獲取更新時間"

    filtered_data = [park for park in data if is_open_now(park['BUSINESSHOURS'])]

    if filtered_data:
        if (location['latitude'] and location['longitude']):
            map_center = [float(location['latitude']), float(location['longitude'])]
            folium_map = folium.Map(location=map_center, zoom_start=14, width=350)
            folium.Marker(
                location=[location['latitude'], location['longitude']],
                popup="Your Location",
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(folium_map)
        else:
            map_center = [float(filtered_data[0]['LATITUDE']), float(filtered_data[0]['LONGITUDE'])]
            folium_map = folium.Map(location=map_center, zoom_start=14, width=350)

        for park in filtered_data:
            folium.Marker(
                location=[float(park['LATITUDE']), float(park['LONGITUDE'])],
                popup=folium.Popup(f"""
                    <div style="font-size: 16px;">
                    {park['PARKINGNAME']}<br>
                    剩餘車位數: {park['FREEQUANTITY']}/{park['TOTALQUANTITY']}<br>
                    地址: {park['ADDRESS']}<br>
                    平日收費: {park['WEEKDAYS']}<br>
                    假日收費: {park['HOLIDAY']}<br>
                    <a href="https://www.google.com/maps/dir/?api=1&destination={park['LATITUDE']},{park['LONGITUDE']}" target="_blank">
                        <img src="https://png.pngtree.com/png-vector/20230822/ourlarge/pngtree-vw-beetle-in-the-sunset-vw-car-tattoo-illustration-clipart-vector-png-image_7026644.png" alt="導航" style="width:20px;height:20px;">
                    </a>
                    </div>
                """, max_width=220),
                icon=folium.Icon(icon="info-sign")
            ).add_to(folium_map)

        folium_static(folium_map, width=350)
        st.write(f"數據更新時間: {update_time}")

if __name__ == "__main__":
    main()
