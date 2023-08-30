# ===== IMPORTS ===== #
import streamlit as st
from datetime import datetime
import pandas as pd
import time

from utils import constants as VARS
from utils import filepaths as PATHS
from utils import tools as TOOLS

# ===== PAGE CONFIGURATIONS ===== #
st.set_page_config(
    page_title=VARS.SITE_TITLE,
    page_icon=VARS.LOGO,
    layout=VARS.LAYOUT,
    initial_sidebar_state=VARS.SIDEBAR_STATE
)
with open(PATHS.INDEX_CSS) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
with open(PATHS.HOME_CSS) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ===== FUNCTIONS ===== #
def removeDuplicates(df:pd.DataFrame):
    unique_nrics = df["Identity Document Number"].unique()
    dup_indices = []
    for nric in unique_nrics:
        temp_df = df[df["Identity Document Number"] == nric]
        for i, row_i in temp_df.iterrows():
            for j, row_j in temp_df.iterrows():
                if j > i:
                    course_name_i = row_i["Course Name"]
                    course_name_j = row_j["Course Name"]
                    if ((course_name_i.find(course_name_j) != -1) or
                        (course_name_j.find(course_name_i) != -1)):
                        dup_indices.append(i)

    return df.drop(dup_indices)

# ===== PAGE CONTENT ===== #
st.title("Online Commission Calculator")
st.write("---")

show_results = False
with st.form("data_input_form"):
    st.subheader("Data Input")
    form_col1, form_col2, form_col3 = st.columns((1.5, 2, 2))
    with form_col1:
        quarter = st.selectbox("Quarter", VARS.QUARTERS, format_func=lambda x: x["label"])
        year = st.selectbox("Academic Year", VARS.YEARS, format_func=lambda x: x["label"])
    with form_col2:
        cw_file = st.file_uploader("Upload Closed Won Data", type=VARS.FILETYPES)
    with form_col3:
        msr_file = st.file_uploader("Upload MSR Data", type=VARS.FILETYPES)
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
    start_time = time.time()
    # EXTRACT START AND END DATES
    start_year = year["start"]
    start_month, start_day = quarter["start"]
    start_date = datetime(start_year, start_month, start_day)
    end_year = start_year if start_month > 6 else start_year + 1
    end_month, end_day = quarter["end"]
    end_date = datetime(end_year, end_month, end_day)
    
    # STORE AND INITIALIZE MSR DATA TO DATA FRAME
    msr_df = TOOLS.cleanCSVtoDF(msr_file)[VARS.MSR_COLS_RAW]
    msr_df = TOOLS.setDataTypes(msr_df, VARS.MSR_DTYPES_RAW)
    msr_df = msr_df.rename(columns={"Course name":"Course Name"})
    msr_df = msr_df.dropna(subset=["Module Completion Date"])
    wd_nonsoc_msr_df = msr_df[
        (msr_df["Enrollment Status"] == "WITHDRAWN NON SOC") |
        (msr_df["Enrollment Status"] == "WITHDRAWN NON SOC_ATTRITION")
    ]
    
    # INITIALIZE MAIN MSR DATA FRAME
    msr_df = msr_df[
        (msr_df["Module Completion Date"] >= start_date) &
        (msr_df["Module Completion Date"] <= end_date)
    ]
    msr_df = msr_df[msr_df["Module Status"] == "PASSED"]
    
    # STORE AND INITIALIZE CLOSED WON DATA TO DATA FRAME
    cw_df = TOOLS.cleanCSVtoDF(cw_file)[VARS.CW_COLS_RAW]
    cw_df = TOOLS.setDataTypes(cw_df, VARS.CW_DTYPES_RAW)
    cw_df = cw_df.rename(columns={"Course name":"Course Name"})
    cw_df = cw_df[(cw_df["Course Name"] != "NAN")]
    # cw_df = cw_df.dropna(axis=0)
    cw_df = cw_df.sort_values(by="Opportunity Closed Date", ascending=True)
    cw_df = cw_df.drop_duplicates(subset=["Identity Document Number", "Course Name"])
    cw_df = removeDuplicates(cw_df)
    
    st.write("Closed Won Data")
    st.dataframe(cw_df)
    
    # POPULATE MSR'S MODULE FEE COLUMN
    modules_df = pd.read_csv(PATHS.MODULES_DB)
    modules_df = TOOLS.setDataTypes(modules_df, VARS.MODULES_DTYPES)
    msr_df = pd.merge(msr_df, modules_df, how="left", on="Module Name")
    msr_df["Module Fee"] = msr_df["Module Fee"].fillna(0)
    wd_nonsoc_msr_df = pd.merge(wd_nonsoc_msr_df, modules_df, how="left", on="Module Name")
    
    # POPULATE MSR'S CLOSED WON DATE AND SALESPERSON COLUMNS
    msr_df = pd.merge(
        how="left",
        left=msr_df,
        left_on="Student NRIC",
        right=cw_df[["Identity Document Number", "Opportunity Closed Date", "Agent Name"]],
        right_on="Identity Document Number"
    )
    msr_df["Closed Won Date"] = msr_df["Opportunity Closed Date"]
    msr_df["Salesperson"] = msr_df["Agent Name"]
    msr_df = msr_df.drop(columns=["Identity Document Number", "Opportunity Closed Date", "Agent Name"])
    
    # CALCULATE PAYABLE COMMISSION
    closed_wons, withdrawns, totals, percents, payables = [], [], [], [], []
    for i, row in msr_df.iterrows():
        closed_won, withdrawn = TOOLS.getCWMonthSales(row["Salesperson"], cw_df, row["Closed Won Date"], wd_nonsoc_msr_df["Student NRIC"].unique())
        total = closed_won - withdrawn
        percent = TOOLS.getPercentCommission(total, "RSP_SCHEMA")
        payable = row["Module Fee"] * percent / 100
        closed_wons.append(closed_won)
        withdrawns.append(withdrawn)
        totals.append(total)
        percents.append(percent)
        payables.append(payable)
    msr_df["Closed Won Sales"] = closed_wons
    msr_df["Withdrawn Sales"] = withdrawns
    msr_df["Total Sales Less Withdrawn"] = totals
    msr_df["Commission %"] = percents
    msr_df["Payable Commission"] = payables
    
    end_time = time.time()
    
    st.write("Results")
    st.dataframe(msr_df[VARS.MSR_COLS]
                 .apply(lambda x: x.dt.date if x.name in ["Module Completion Date", "Closed Won Date"] else x), 
                 hide_index=True, use_container_width=True)
    
    st.write("Total runtime: " + str(end_time - start_time))
    
    # msr_df.to_csv("results.csv")