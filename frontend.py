import streamlit as st
import requests
import pandas as pd
import altair as alt

API_URL = "http://localhost:8000"

def get_auth_headers():
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}

def load_covid():
    resp = requests.get(f"{API_URL}/covid", headers=get_auth_headers())
    if resp.status_code == 200:
        return resp.json()
    st.error(f"Error fetching COVID data: {resp.text}")
    return []

def load_kpis():
    resp = requests.get(f"{API_URL}/covid/kpis", headers=get_auth_headers())
    if resp.status_code == 200:
        return resp.json()
    st.error(f"Error fetching KPIs: {resp.text}")
    return {}

def main():
    st.title("Hospital BI Dashboard")
    if "token" not in st.session_state:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
            if response.status_code == 200:
                st.session_state["token"] = response.json()["access_token"]
                st.rerun()
            else:
                st.error("Login failed")
        return

    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

    kpis = load_kpis()
    st.subheader("Key Performance Indicators (KPIs)")
    if kpis:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total COVID Patients", kpis.get("total_covid_patients", 0))
        col2.metric("Avg ICU Occupancy", f"{kpis.get('avg_icu_occupancy', 0):.2f}")
        col3.metric("Staffing Shortage (Yes)", kpis.get("staffing_shortage_today_yes", 0))

        st.markdown("""
        Interpretation:
        - **Total COVID Patients** represents current hospital burden.
        - **Average ICU Occupancy** reflects strain on critical care capacity.
        - **Staffing Shortage Today** indicates workforce constraints.
        """)

    covid_data = load_covid()
    if covid_data:
        df = pd.DataFrame(covid_data)
        st.subheader("COVID Hospital Data")
        st.dataframe(df)

        if 'state' in df.columns and 'critical_staffing_shortage_today_yes' in df.columns:
            chart = alt.Chart(df).mark_bar().encode(
                x='state',
                y='critical_staffing_shortage_today_yes'
            ).properties(title='Staffing Shortage Today (Yes)')
            st.altair_chart(chart, use_container_width=True)
    else:
        st.write("No COVID data available.")

if __name__ == "__main__":
    main()
