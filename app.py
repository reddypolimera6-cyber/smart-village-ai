import streamlit as st

st.title("🌾 SmartVillage AI")

menu = st.sidebar.selectbox("Menu", ["Home", "AI Crop Advisory", "Equipment Booking", "Weather", "Community"])

if menu == "Home":
    st.write("Welcome to SmartVillage AI")

elif menu == "AI Crop Advisory":
    st.header("Upload Crop Image")
    file = st.file_uploader("Choose image")
    if file:
        st.image(file)
        st.success("AI Suggestion: Crop looks healthy")

elif menu == "Equipment Booking":
    st.header("Book Equipment")
    st.write("🚁 Drone - Available")
    st.write("🚜 Tractor - Available")
    if st.button("Book Now"):
        st.success("Booked successfully!")

elif menu == "Weather":
    st.header("Weather Info")
    st.write("🌦 32°C, Chance of rain")
    st.write("Advice: Delay irrigation")

elif menu == "Community":
    st.header("Community Chat")
    msg = st.text_input("Write message")
    if st.button("Send"):
        st.write("Message sent:", msg)
