import streamlit as st
import requests
import pandas as pd
import altair as alt

API_URL = "http://localhost:8000"


def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state["token"] = token  # Store token in session_state
            st.success("Login successful")
            st.rerun()  # Refresh to load main content
        else:
            st.error("Login failed")


def get_auth_headers():
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def load_visits():
    headers = get_auth_headers()
    response = requests.get(f"{API_URL}/visits", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error getting visits data")
        return []


def load_cases():
    headers = get_auth_headers()
    response = requests.get(f"{API_URL}/cases", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error getting cases data")
        return []


def main():
    st.title("Hospital BI Dashboard")

    if "token" not in st.session_state:
        login()
    else:
        # Display logout button
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

        visits = load_visits()
        cases = load_cases()

        st.subheader("Hospital Visits")
        if visits:
            df_visits = pd.DataFrame(visits)
            chart = alt.Chart(df_visits).mark_bar().encode(
                x="nama_kabupaten_kota",
                y="jumlah_kunjungan",
                color="kategori_kunjungan"
            )
            st.altair_chart(chart, use_container_width=True)

        st.subheader("Disease Cases")
        if cases:
            df_cases = pd.DataFrame(cases)
            chart = alt.Chart(df_cases).mark_bar().encode(
                x="jenis_penyakit",
                y="jumlah_kasus",
                color="jenis_penyakit"
            )
            st.altair_chart(chart, use_container_width=True)


if __name__ == "__main__":
    main()
