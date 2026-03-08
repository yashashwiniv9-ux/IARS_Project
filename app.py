import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium

# -----------------------------
# Title
# -----------------------------
st.title("🚑 Intelligent Ambulance Routing System (IARS)")
st.header("Emergency Incident Input")

# -----------------------------
# User Inputs
# -----------------------------
incident = st.selectbox(
    "Incident Type",
    ["Accident", "Cardiac Arrest", "Trauma"]
)

injuries = st.slider("Number of Injuries", 0, 10)

traffic = st.selectbox(
    "Traffic Level",
    ["Low", "Medium", "High"]
)

distance = st.slider("Distance to Incident (km)", 1, 20)

# -----------------------------
# Incident Summary
# -----------------------------
st.subheader("Incident Summary")
st.write("Incident:", incident)
st.write("Injuries:", injuries)
st.write("Traffic:", traffic)
st.write("Distance:", distance, "km")

# -----------------------------
# Session State (prevents blinking)
# -----------------------------
if "dispatched" not in st.session_state:
    st.session_state.dispatched = False

if st.button("Dispatch Ambulance"):
    st.session_state.dispatched = True

# -----------------------------
# After Dispatch
# -----------------------------
if st.session_state.dispatched:

    # Priority calculation
    priority = 0

    if incident == "Cardiac Arrest":
        priority += 3
    elif incident == "Trauma":
        priority += 2
    else:
        priority += 1

    priority += injuries

    if traffic == "High":
        priority -= 1

    # Priority output
    if priority >= 5:
        st.error("🚨 High Priority Emergency! Dispatch immediately!")
    elif priority >= 3:
        st.warning("⚠ Medium Priority Emergency")
    else:
        st.success("✅ Low Priority Emergency")

    # Estimated time
    arrival_time = distance * 3
    st.info(f"⏱ Estimated Arrival Time: {arrival_time} minutes")

    st.success("🚑 Ambulance Dispatched Successfully")

    # -----------------------------
    # Graph for Road Network
    # -----------------------------
    G = nx.Graph()

    G.add_edge("Ambulance", "Junction1", weight=4)
    G.add_edge("Junction1", "Junction2", weight=3)
    G.add_edge("Junction2", "Hospital A", weight=2)
    G.add_edge("Junction1", "Hospital B", weight=6)
    G.add_edge("Junction2", "Hospital C", weight=4)

    # -----------------------------
    # Hospital Status
    # -----------------------------
    hospital_status = {
        "Hospital A": "Vacant",
        "Hospital B": "Full",
        "Hospital C": "Vacant"
    }

    st.subheader("🏥 Hospital Availability")

    for hospital, status in hospital_status.items():
        st.write(f"{hospital} : {status}")

    # -----------------------------
    # Find nearest available hospital
    # -----------------------------
    available_hospitals = [
        h for h in hospital_status if hospital_status[h] == "Vacant"
    ]

    shortest_routes = {}

    for hospital in available_hospitals:
        length = nx.shortest_path_length(
            G,
            source="Ambulance",
            target=hospital,
            weight="weight"
        )
        shortest_routes[hospital] = length

    nearest_hospital = min(shortest_routes, key=shortest_routes.get)

    st.subheader("📍 Nearest Available Hospital")
    st.success(f"{nearest_hospital} selected for patient transfer")

    st.write("Shortest Distance:", shortest_routes[nearest_hospital], "km")

    # -----------------------------
    # Map Coordinates
    # -----------------------------
    locations = {
        "Ambulance": [17.3850, 78.4867],
        "Hospital A": [17.3950, 78.4767],
        "Hospital B": [17.4050, 78.4967],
        "Hospital C": [17.3750, 78.4667]
    }

    # -----------------------------
    # Create Map
    # -----------------------------
    st.subheader("🗺 Ambulance Routing Map")

    m = folium.Map(location=[17.3850, 78.4867], zoom_start=12)

    # Ambulance marker
    folium.Marker(
        locations["Ambulance"],
        popup="🚑 Ambulance Location",
        icon=folium.Icon(color="red")
    ).add_to(m)

    # Hospital markers
    for hospital in ["Hospital A", "Hospital B", "Hospital C"]:

        color = "green" if hospital_status[hospital] == "Vacant" else "gray"

        folium.Marker(
            locations[hospital],
            popup=f"{hospital} ({hospital_status[hospital]})",
            icon=folium.Icon(color=color)
        ).add_to(m)

    # Draw route from ambulance to nearest hospital
    route = [
        locations["Ambulance"],
        locations[nearest_hospital]
    ]

    folium.PolyLine(
        route,
        color="blue",
        weight=5,
        tooltip="Ambulance Route"
    ).add_to(m)

    st_folium(m, width=700)