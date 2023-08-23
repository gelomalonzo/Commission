# ===== IMPORTS ===== #
import streamlit as st
from datetime import datetime
import pandas as pd
import io

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
    # extract dates
    start_year = year["start"]
    start_month, start_day = quarter["start"]
    start_date = datetime(start_year, start_month, start_day)
    end_year = start_year if start_month > 6 else start_year + 1
    end_month, end_day = quarter["end"]
    end_date = datetime(end_year, end_month, end_day)
    
    # extract and process MSR file
    msr_df = TOOLS.cleanCSVtoDF(msr_file) # remove non UTF-8 characters and convert all cells to string
    msr_df = msr_df[VARS.MSR_COLS_RAW] # get only the defined columns
    # msr_df["Module Fee"] = 0
    msr_df["Salesperson"] = ""
    msr_df["Closed Won Date"] = ""
    msr_df["% Commission"] = 0
    msr_df["Total Sales on CW Month"] = 0
    msr_df["Payable Commission"] = 0
    msr_df = TOOLS.setDataTypes(msr_df, "MSR_RAW")
    msr_df = msr_df.dropna(subset=["Module Completion Date"]) # drop rows with blank Module Completion Date
    msr_df = msr_df[ # drop rows whose Module Completion Date is not within the indicated quarter
        (msr_df["Module Completion Date"] >= start_date) & 
        (msr_df["Module Completion Date"] <= end_date)
    ]
    msr_df = msr_df[msr_df["Module Status"] == "PASSED"] # drop rows whose Module Status is not Passed
    
    # to do: extract rows whose Module Status is "Withdrawn" and is "SOC" into a data frame
    
    # extract and process CW file
    cw_df = TOOLS.cleanCSVtoDF(cw_file) # remove non UTF-8 characters and convert all cells to string
    
    cw_df = cw_df[VARS.CW_COLS_RAW] # get only the defined columns
    cw_df = cw_df.dropna(subset=["Opportunity Closed Date"]) # drop rows with blank Opportunity Closed Date
    cw_df = TOOLS.setDataTypes(cw_df, "CW_RAW")
    
    # identify module fee for each MSR
    module_fees_df = pd.read_csv(PATHS.MODULES_DB)
    module_fees_df = TOOLS.setDataTypes(module_fees_df.astype(str), "MODULES")
    msr_df = pd.merge(msr_df, module_fees_df, on="Module Name", how="left") # join msr_df and module_fees_df on Module Name column
    
    # identify closed won date and salesperson for each MSR
    msr_df = pd.merge(msr_df, cw_df[["Identity Document Number", "Opportunity Closed Date", "Agent Name"]], left_on="Student NRIC", right_on="Identity Document Number", how="left")
             # join msr_df and cw_df on msr_df["Student NRIC"] and cw_df["Identity Document Number"],
             # appending columns cw_df[["Identity Document Number", "Opportunity Closed Date", "Agent Name"]] into msr_df
    msr_df["Closed Won Date"] = msr_df["Opportunity Closed Date"]
    msr_df["Salesperson"] = msr_df["Agent Name"]
    msr_df = msr_df.drop(columns=["Identity Document Number", "Opportunity Closed Date", "Agent Name"])
    
    inc_msr_df = msr_df.dropna().copy() # get all the rows with blank cells
    msr_df = msr_df.dropna() # remove all raws with blank cells from the main dataframe
    
    # calculate payable commission
    totals, percent_commission, payable_commission = [], [], []
    for index, row in msr_df.iterrows():
        salesperson = row["Salesperson"]
        cw_date = row["Closed Won Date"]
        total = TOOLS.getCWMonthTotal(salesperson, cw_df, cw_date)
        totals.append(total)
        percentage = TOOLS.getPercentCommission(total, "RSP_SCHEMA")
        percent_commission.append(percentage)
        module_fee = row["Module Fee"]
        payable_commission.append(module_fee * percentage / 100)
    msr_df["Total Sales on CW Month"] = totals
    msr_df["% Commission"] = percent_commission
    msr_df["Payable Commission"] = payable_commission
        
    st.dataframe(msr_df[VARS.MSR_COLS]
                 .apply(lambda x: x.dt.date if x.name in ["Module Completion Date", "Closed Won Date"] else x), 
                 hide_index=True, use_container_width=True)