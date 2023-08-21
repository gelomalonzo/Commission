# ===== IMPORTS ===== #
import streamlit as st
from datetime import datetime

# ===== PAGE CONFIGURATIONS ===== #
st.set_page_config(
    page_title=st.secrets["env"]["TITLE"],
    page_icon=st.secrets["env"]["LOGO"],
    layout=st.secrets["env"]["LAYOUT"],
    initial_sidebar_state=st.secrets["env"]["SIDEBAR_STATE"]
)
with open(st.secrets["paths"]["INDEX_CSS"]) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
with open(st.secrets["paths"]["DASHBOARD_CSS"]) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ===== GLOBAL VARIABLES ===== #
current_date = datetime.now()
current_month = current_date.month
current_year = current_date.year
quarters = [
    "Quarter 1 (July - September)",
    "Quarter 2 (October - December)",
    "Quarter 3 (January - March)",
    "Quarter 4 (April - June)"
]

# ===== PAGE CONTENT ===== #
st.title("Online Commission Calculator")
st.write("---")
col1, col2, col3 = st.columns((1, 0.1, 1.9))

with col3:
    st.subheader("Results")

with col1:
    with st.form("data_input_form"):
        st.subheader("Data Input")
        quarter = st.selectbox("Quarter", quarters)
        year = st.number_input("Year", min_value=1000, max_value=current_year, step=1, format="%d", value=current_year)
        cw_file = st.file_uploader("Upload Closed Won Data", type=["csv"])
        msr_file = st.file_uploader("Upload MSR Data", type=["csv"])
        calculate_btn = st.form_submit_button("Calculate")
        if calculate_btn:
            with col3:
                st.write("Okay")