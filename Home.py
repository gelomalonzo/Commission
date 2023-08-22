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
with open(st.secrets["paths"]["HOME_CSS"]) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ===== GLOBAL VARIABLES ===== #
current_date = datetime.now()
current_month = current_date.month
current_year = current_date.year
max_year = current_year
if current_month > 6: max_year += 1
years = [
    {"label":f"{y} - {y+1}", "start":y, "end":y+1}
    for y in reversed(range(max_year - 5, max_year))
]
quarters = [
    {"label":"Quarter 1 (July - September)", "start":(7,1), "end":(9,30)},
    {"label":"Quarter 2 (October - December)", "start":(10,1), "end":(12,31)},
    {"label":"Quarter 3 (January - March)", "start":(1,1), "end":(3,31)},
    {"label":"Quarter 4 (April - June)", "start":(4,1), "end":(6,30)}
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
        quarter = st.selectbox("Quarter", quarters, format_func=lambda x: x["label"])
        year = st.selectbox("Academic Year", years, format_func=lambda x: x["label"])
        msr_file = st.file_uploader("Upload MSR Data", type=["csv"])
        cw_file = st.file_uploader("Upload Closed Won Data", type=["csv"])
        msg = st.container()
        calculate_btn = st.form_submit_button("Calculate")
        
        if calculate_btn:
            if quarter and year and cw_file and msr_file:
                with col3:
                    msg = st.empty()
                    start_year = year["start"]
                    start_month, start_day = quarter["start"]
                    start_date = datetime(start_year, start_month, start_day)
                    end_year = start_year if start_month > 6 else start_year + 1
                    end_month, end_day = quarter["end"]
                    end_date = datetime(end_year, end_month, end_day)
                    
            else:
                with msg:
                    st.warning("Please fill in all fields from the data input form.")