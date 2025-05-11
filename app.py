import streamlit as st
import folium
import requests
import time
import streamlit.components.v1 as components

# --- PAGE SETUP ---
st.set_page_config(layout="centered", page_title="ISS Tracker", page_icon="🛰️")
st.title("🛰️ Live ISS Tracker")

# Initialize a list to store the previous positions of the ISS
if "trajectory" not in st.session_state:
    st.session_state["trajectory"] = []

def fetch_iss_data():
    url = "https://api.wheretheiss.at/v1/satellites/25544"
    try:
        resp = requests.get(url, timeout=2)
        data = resp.json()
        lat, lon, alt = data["latitude"], data["longitude"], data["altitude"]

        # Store the position (latitude, longitude) in the trajectory list
        st.session_state["trajectory"].append([lat, lon])

        return lat, lon, alt

    except Exception as e:
        st.warning(f"Failed to fetch ISS data: {e}")
        return None

# auto refresh loop
refresh_interval = 5 # seconds

while True:
    lat, lon, alt = fetch_iss_data()

    if lat and lon and alt:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric("Latitude", f"{lat:.2f}°", border=True)
        with col2:    
            st.metric("Longitude", f"{lon:.2f}°", border=True)
        with col3:
            st.metric("Altitude", f"{alt:.2f} km", border=True)

        # Create folium map centered on ISS
        m = folium.Map(location=[lat, lon], zoom_start=2)

        # Add the trajectory as a polyline (line connecting past positions)
        trajectory = st.session_state["trajectory"]

        if len(trajectory) > 1:
            folium.PolyLine(trajectory, color="blue", weight=2.5, opacity=1).add_to(m)
        
        folium.Marker([lat, lon], tooltip="ISS Location").add_to(m)
        # Render the map in Streamlit
        map_html = m._repr_html_()
        components.html(map_html, height=800)
    
    # Wait for the next refresh
    time.sleep(refresh_interval)
    st.rerun()
