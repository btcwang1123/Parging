import streamlit as st
import requests
from datetime import datetime
import folium
from streamlit_folium import folium_static
import geocoder

# 網頁 URL
url = "https://hispark.hccg.gov.tw/OpenData/GetParkInfo"

def get_current_gps_coordinates():
    g = geocoder.ip('me')#this function is used to find the current information using our IP Add
    if g.latlng is not None: #g.latlng tells if the coordiates are found or not
        return g.latlng
    else:
        return None

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

    search_query = st.text_input("搜索停車場名稱或地址", key="search_query")

    field_choice = ["停車場名稱", "地址", "小車剩餘車位數", "平日收費", "假日收費"]

    data = fetch_data()
    update_time = data[0]['UPDATETIME'] if data else "無法獲取更新時間"
    st.write(f"數據更新時間: {update_time}")

    filtered_data = [park for park in data if is_open_now(park['BUSINESSHOURS'])]

    if search_query:
        filtered_data = [park for park in filtered_data if search_query in park['PARKINGNAME'] or search_query in park['ADDRESS']]
        if filtered_data == []:
             filtered_data = [park for park in data if is_open_now(park['BUSINESSHOURS'])]

    if filtered_data:
        map_center = [float(filtered_data[0]['LATITUDE']), float(filtered_data[0]['LONGITUDE'])]
        folium_map = folium.Map(location=map_center, zoom_start=14, width=350)

        for park in filtered_data:
            folium.Marker(
                location=[float(park['LATITUDE']), float(park['LONGITUDE'])],
                popup=folium.Popup(f"""
                    <div style="font-size: 16px;">
                    {park['PARKINGNAME']}<br>
                    剩餘車位數: {park['FREEQUANTITY']}/{park['TOTALQUANTITY']}<br>
                    </div>
                    地址: {park['ADDRESS']}<br>
                    平日收費: {park['WEEKDAYS']}<br>
                    假日收費: {park['HOLIDAY']}                  
                """, max_width=220),
                icon=folium.Icon(icon="info-sign")
            ).add_to(folium_map)

        folium_static(folium_map, width=350)

if __name__ == "__main__":
    coordinates = get_current_gps_coordinates()
    if coordinates is not None:
        latitude, longitude = coordinates
      print(f"Your current GPS coordinates are:")
      print(f"Latitude,Longitude: {latitude},{longitude}")
        st.write(f"Your current GPS coordinates are:")
        st.write(f"Latitude,Longitude: {latitude},{longitude}")

    else:
        #print("Unable to retrieve your GPS coordinates.")
        st.write(f"Unable to retrieve your GPS coordinates.")
    main()
