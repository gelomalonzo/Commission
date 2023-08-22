# ===== IMPORTS ===== #
import streamlit as st
from datetime import datetime
import pandas as pd
import io

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
show_results = False
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
msr_columns = [
    "Student Name",
    "Student NRIC",
    "Module Name",
    "Module Status",
    "Module Completion Date"
]
cw_columns = [
    "Identity Document Number",
    "Opportunity Closed Date",
    "Student Name",
    "Agent Name"
]

# ===== GLOBAL FUNCTIONS ===== #
def clean_csv(csv_file):
    with csv_file as file:
        csv_text = file.read()
    csv_text_str = str(csv_text, "utf-8", errors="ignore")
    # cleaned_csv_text = csv_text_str.replace("\xa0", "")
    return pd.read_csv(io.StringIO(csv_text_str), low_memory=False)

# ===== PAGE CONTENT ===== #
st.title("Online Commission Calculator")
st.write("---")
# col1, col2, col3 = st.columns((1, 0.1, 1.9))

with st.form("data_input_form"):
    st.subheader("Data Input")
    form_col1, form_col2, form_col3 = st.columns((1.5, 2, 2))
    with form_col1:
        quarter = st.selectbox("Quarter", quarters, format_func=lambda x: x["label"])
        year = st.selectbox("Academic Year", years, format_func=lambda x: x["label"])
    with form_col2:
        cw_file = st.file_uploader("Upload Closed Won Data", type=["csv"])
    with form_col3:
        msr_file = st.file_uploader("Upload MSR Data", type=["csv"])
    msg = st.container()
    calculate_btn = st.form_submit_button("Calculate")
    
    if calculate_btn:
        if quarter and year and cw_file and msr_file:
            with msg:
                msg.empty()
                show_results = True
        else:
            with msg:
                st.error("Please fill in all fields from the data input form.")
                show_results = False

st.write("---")
st.subheader("Results")
if show_results:
    # extract dates
    start_year = year["start"]
    start_month, start_day = quarter["start"]
    start_date = datetime(start_year, start_month, start_day).date()
    end_year = start_year if start_month > 6 else start_year + 1
    end_month, end_day = quarter["end"]
    end_date = datetime(end_year, end_month, end_day).date()
    
    # extract and process MSR file
    msr_df = clean_csv(msr_file)
    msr_df = msr_df[msr_columns] # get only the defined columns
    msr_df = msr_df.dropna(subset=["Module Completion Date"]) # drop rows with blank Module Completion Date
    msr_df["Module Completion Date"] = pd.to_datetime(msr_df["Module Completion Date"]).dt.date # convert Module Completion Date to date objects
    msr_df = msr_df[(msr_df["Module Completion Date"] >= start_date) & (msr_df["Module Completion Date"] <= end_date)] # drop rows whose Module Completion Date is not within the indicated quarter
    msr_df = msr_df[msr_df["Module Status"] == "Passed"] # drop rows whose Module Status is not Passed
    msr_df["Module Fee"] = 0
    msr_df["Salesperson"] = ""
    msr_df["Closed Won Date"] = ""
    msr_df["% Commission"] = 0
    
    st.dataframe(msr_df, hide_index=True, use_container_width=True)
    
    # extract and process CW file
    cw_df = clean_csv(cw_file)
    cw_df = cw_df[cw_columns] # get only the defined columns
    cw_df = cw_df.dropna(subset=["Opportunity Closed Date"]) # drop rows with blank Opportunity Closed Date
    cw_df["Opportunity Closed Date"] = pd.to_datetime(cw_df["Opportunity Closed Date"]).dt.date # convert Opportunity Closed Date to date objects
    
    st.dataframe(cw_df, hide_index=True, use_container_width=True)