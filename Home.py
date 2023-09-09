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

# ===== VARIABLES ===== #
if "show_results" not in st.session_state:
    st.session_state.show_results = False
msr_df, cw_df, modules_df, rsp_schema_df = None, None, None, None
wd_nonsoc_msr_df = None
total_runs = 0
rsp_sales = {}

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
                global total_runs
                total_runs += 1
    return df.drop(dup_indices)

def getCWMonthSales(salesperson, cw_date):
    global cw_df, wd_nonsoc_msr_df, rsp_sales, total_runs
    closed_won = 0
    withdrawn = 0
    df_code = str(salesperson) + "-" + str(cw_date.month) + "-" + str(cw_date.year)
    if df_code in rsp_sales:
        return rsp_sales[df_code][0], rsp_sales[df_code][1]
    filtered_cw_df = cw_df[
        (cw_df["Agent Name"] == salesperson) &
        (cw_df["Opportunity Closed Date"].dt.month == cw_date.month) &
        (cw_df["Opportunity Closed Date"].dt.year == cw_date.year)
    ]
    closed_won = filtered_cw_df["Amount"].sum()
    for i, row in filtered_cw_df.iterrows():
        if row["Identity Document Number"] in wd_nonsoc_msr_df: withdrawn = withdrawn + row["Amount"]
        total_runs += 1
    rsp_sales[df_code] = [closed_won, withdrawn]
    return closed_won, withdrawn

def getRSPPercentCommission(total_sales):
    global rsp_schema_df, total_runs
    percentage = 0.0
    for index, row in rsp_schema_df.iterrows():
        if total_sales >= row["Sales Order Required"]:
            percentage = row["% of Commission Payable"]
        total_runs += 1
    return percentage

# ===== PAGE CONTENT ===== #
st.title("Online Commission Calculator")
st.write("Welcome to the Online Commission Calculator :wave:! You might also want to visit these links for more project info: [Project Plan](https://github.com/gelomalonzo/Commission/wiki/Project-Plan) | [Calculation Processes](https://github.com/gelomalonzo/Commission/wiki/Calculation-Processes)")
st.write("---")

input_col, mid_col, notes_col = st.columns((1.25, 0.10, 1.65))
with input_col:
    st.subheader(":clipboard: Input Form")
    with st.form("data_input_form"):
        quarter = st.selectbox("Quarter", VARS.QUARTERS, format_func=lambda x: x["label"])
        year = st.selectbox("Fiscal Year", VARS.YEARS, format_func=lambda x: x["label"])
        cw_file = st.file_uploader("Upload Closed Won Data", type=VARS.FILETYPES)
        msr_file = st.file_uploader("Upload MSR Data", type=VARS.FILETYPES)
        msg = st.container()
        calculate_btn = st.form_submit_button("Calculate")
        if calculate_btn:
            if quarter and year and cw_file and msr_file:
                with msg:
                    msg.empty()
                    st.session_state.show_results = True
            else:
                with msg:
                    st.error("Please fill in all fields from the data input form.")
                    st.session_state.show_results = False

with notes_col:
    st.subheader(":round_pushpin: Notes and Instructions")

st.write("---")
st.subheader(":abacus: Results")
if st.session_state.show_results and msr_file and cw_file:
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
    msr_df.rename(columns={"Course name":"Course Name"}, inplace=True)
    msr_df.dropna(subset=["Module Completion Date"], inplace=True)
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
    cw_df.rename(columns={"Course name":"Course Name"}, inplace=True)
    cw_df = cw_df[(cw_df["Course Name"] != "NAN")]
    cw_df.sort_values(by="Opportunity Closed Date", ascending=True, inplace=True)
    cw_df.drop_duplicates(subset=["Identity Document Number", "Course Name"], keep="last", inplace=True)
    # cw_df = removeDuplicates(cw_df)
    
    # POPULATE MSR'S MODULE FEE COLUMN
    modules_df = pd.read_csv(PATHS.MODULES_DB)
    modules_df = TOOLS.setDataTypes(modules_df, VARS.MODULES_DTYPES)
    msr_df = pd.merge(msr_df, modules_df, how="left", on="Module Name")
    msr_df["Module Fee"].fillna(0, inplace=True)
    wd_nonsoc_msr_df = pd.merge(wd_nonsoc_msr_df, modules_df, how="left", on="Module Name")["Student NRIC"].unique()
    
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
    msr_df.drop(columns=["Identity Document Number", "Opportunity Closed Date", "Agent Name"], inplace=True)
    msr_df.dropna(subset=["Closed Won Date"], inplace=True)
    
    # INITIALIZE RSP SCHEMA
    rsp_schema_df = pd.read_csv(VARS.SCHEMACODES["RSP_SCHEMA"])
    rsp_schema_df = TOOLS.setDataTypes(rsp_schema_df.astype(str), VARS.DTYPECODES["RSP_SCHEMA"])
    
    # CALCULATE PAYABLE COMMISSION
    closed_wons, withdrawns, totals, percents, payables = [], [], [], [], []
    for i, row in msr_df.iterrows():
        closed_won, withdrawn = getCWMonthSales(row["Salesperson"], row["Closed Won Date"])
        total = closed_won - withdrawn
        percent = getRSPPercentCommission(total)
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
    
    missing_modules_df = pd.DataFrame(msr_df[msr_df["Module Fee"] == 0]["Module Name"].unique())
    
    # SET UP FILTERS
    filters_col, commands_col = st.columns([0.75, 0.25])
    with filters_col:
        sp_filter = st.multiselect(
            label="Filter by Salespersons",
            options=msr_df["Salesperson"].unique(),
        )
        percent_filter = st.multiselect(
            label="Filter by Commission %",
            options=msr_df["Commission %"].unique()
        )
    
    if sp_filter and percent_filter:
        msr_df_filtered = msr_df[
            msr_df["Salesperson"].isin(sp_filter) &
            msr_df["Commission %"].isin(percent_filter)
        ]
    elif sp_filter and not percent_filter:
        msr_df_filtered = msr_df[
            msr_df["Salesperson"].isin(sp_filter)
        ]
    elif not sp_filter and percent_filter:
        msr_df_filtered = msr_df[
            msr_df["Commission %"].isin(percent_filter)
        ]
    else: msr_df_filtered = msr_df.copy()
    
    sp_payables_df = msr_df.groupby(by=["Salesperson"], as_index=False)["Payable Commission"].sum()
    sp_payables_df_filtered = msr_df_filtered.groupby(by=["Salesperson"], as_index=False)["Payable Commission"].sum()
    
    # SET UP COMMANDS
    with commands_col:
        st.download_button(
            "Download Passed MSR as CSV", 
            use_container_width=True, 
            data=msr_df.to_csv(index=False), 
            file_name="msr -passed.csv",
            mime="csv"
        )
        # st.download_button(
        #     "Download Passed MSR as CSV", 
        #     use_container_width=True, 
        #     data=pd.concat([msr_df, wd_nonsoc_msr_df]).to_csv(index=False), 
        #     file_name="msr -passed,wd.csv",
        #     mime="csv"
        # )
        st.download_button(
            "Download filtered MSR as CSV", 
            use_container_width=True, 
            data=msr_df_filtered.to_csv(index=False), 
            file_name="msr -filtered.csv",
            mime="csv"
        )
        st.download_button(
            "Download payable commissions of salespersons as CSV", 
            use_container_width=True, 
            data=sp_payables_df.to_csv(index=False), 
            file_name="msr -filtered.csv",
            mime="csv"
        )
        st.download_button(
            "Download list of missing modules as CSV", 
            use_container_width=True, 
            data=missing_modules_df.to_csv(index=False), 
            file_name="missing modules.csv",
            mime="csv"
        )
    
    # DATA TABLES AND VISUALIZATIONS
    st.write("")
    st.write("")
    col_1, col_2, col_3, col_4, col_5 = st.columns([2, 1, 2, 2, 2])
    with col_1: st.metric("Total Payable Commissions", value=f"SGD {sp_payables_df_filtered['Payable Commission'].sum()}")
    with col_2: st.metric("No. of MSRs", value=len(msr_df))
    with col_3: st.metric("No. of Payable Salespersons", value=len(sp_payables_df_filtered[sp_payables_df_filtered["Payable Commission"] > 0]))
    with col_4: st.metric("No. of Missing Modules", value=len(missing_modules_df))
    
    st.write("")
    st.write("")
    sp_col, tl_col = st.columns(2)
    with sp_col:
        st.write("Payable Commissions of Salespersons")
        st.dataframe(data=sp_payables_df_filtered, use_container_width=True)
        
    with tl_col:
        st.write("Payable Commissions of Teams")
        st.write("No data yet")
    
    st.write("")
    st.write("")
    st.write("MSR Table")
    st.dataframe(msr_df_filtered[VARS.MSR_COLS]
                 .apply(lambda x: x.dt.date if x.name in ["Module Completion Date", "Closed Won Date"] else x), 
                 hide_index=True, use_container_width=True)
    