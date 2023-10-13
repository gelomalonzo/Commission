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
master_msr_df, msr_df, cw_df, modules_df, rsp_scheme_df = None, None, None, None, None
wd_nonsoc_msr_df = None
total_runs = 0
rsp_sales = {} # store the previously calculated CW and withdrawn sales

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
    global master_msr_df, cw_df, rsp_sales
    
    # check the previously calculated CW and withdrawn sales first
    df_code = str(salesperson) + "-" + str(cw_date.month) + "-" + str(cw_date.year)
    if df_code in rsp_sales:
        return rsp_sales[df_code][0], rsp_sales[df_code][1] # index 0 for CW sales, index 1 for withdrawn sales
    
    # CW and withdrawn sales are not yet calculated for the salesperson on the indicated CW date
    withdrawn_msr_df = master_msr_df[
        (master_msr_df["Enrollment Status"] == "WITHDRAWN SOC")
    ]
    
    filtered_cw_df = cw_df[
        (cw_df["Agent Name"] == salesperson) &
        (cw_df["Opportunity Closed Date"].dt.month == cw_date.month) &
        (cw_df["Opportunity Closed Date"].dt.year == cw_date.year)
    ]
    
    cw_sales = 0
    withdrawn_sales = 0
    for i, row in filtered_cw_df.iterrows():
        if row["Identity Document Number"] in master_msr_df["Student NRIC"].values: cw_sales = cw_sales + row["Amount"]
        if row["Identity Document Number"] in withdrawn_msr_df["Student NRIC"].values: withdrawn_sales = withdrawn_sales + row["Amount"]
    
    # global cw_df, wd_nonsoc_msr_df, rsp_sales, total_runs
    # closed_won = 0
    # withdrawn = 0
    # df_code = str(salesperson) + "-" + str(cw_date.month) + "-" + str(cw_date.year)
    # if df_code in rsp_sales:
    #     return rsp_sales[df_code][0], rsp_sales[df_code][1]
    # filtered_cw_df = cw_df[
    #     (cw_df["Agent Name"] == salesperson) &
    #     (cw_df["Opportunity Closed Date"].dt.month == cw_date.month) &
    #     (cw_df["Opportunity Closed Date"].dt.year == cw_date.year)
    # ]
    # closed_won = filtered_cw_df["Amount"].sum()
    # for i, row in filtered_cw_df.iterrows():
    #     if row["Identity Document Number"] in wd_nonsoc_msr_df: withdrawn = withdrawn + row["Amount"]
    #     total_runs += 1
    
    rsp_sales[df_code] = [cw_sales, withdrawn_sales]
    return cw_sales, withdrawn_sales

def getRSPPercentCommission(total_sales, cw_date):
    global rsp_scheme_df, total_runs
    cw_date = pd.to_datetime(cw_date)
    rsp_scheme = rsp_scheme_df[
        (rsp_scheme_df["Effective Start Date"] <= cw_date) &
        (rsp_scheme_df["Effective End Date"] >= cw_date)
    ]
    percentage = 0.0
    for index, row in rsp_scheme.iterrows():
        if total_sales >= row["Sales Order Required"]:
            percentage = row["% of Commission Payable"]
        total_runs += 1
    return percentage

# ===== PAGE CONTENT ===== #
st.title("Online Commission Calculator")
st.write("Welcome to the Online Commission Calculator :wave:! You might also want to visit these links for more project info: [Project Plan](https://github.com/gelomalonzo/Commission/wiki/Project-Plan) | [Calculation Processes](https://github.com/gelomalonzo/Commission/wiki/Calculation-Processes)")
st.write("---")

left_col, input_col, right_col = st.columns((0.25, 0.50, 0.25))
with input_col:
    st.subheader("Input Form")
    with st.form("data_input_form"):
        year = st.selectbox("Fiscal Year", VARS.YEARS, format_func=lambda x: x["label"])
        quarter = st.selectbox("Quarter", VARS.QUARTERS, format_func=lambda x: x["label"])
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

st.write("---")
st.subheader("Results")
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
    master_msr_df = TOOLS.cleanCSVtoDF(msr_file)[VARS.MSR_COLS_RAW]
    master_msr_df = TOOLS.setDataTypes(master_msr_df, VARS.MSR_DTYPES_RAW)
    master_msr_df.rename(columns={"Course name":"Course Name"}, inplace=True)
    master_msr_df.dropna(subset=["Module Completion Date"], inplace=True)
    
    # st.dataframe(master_msr_df[
    #     (master_msr_df["Course Category"] == "SGUS") |
    #     (master_msr_df["Course Category"] == "SGUS2")
    # ])
    
    master_msr_df = master_msr_df[
        (master_msr_df["Course Category"] != "SGUS") & 
        (master_msr_df["Course Category"] != "SGUS2")
    ]
    
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
    master_msr_df = pd.merge(master_msr_df, modules_df, how="left", on="Module Name")
    master_msr_df["Module Fee"].fillna(0, inplace=True)
    # wd_nonsoc_msr_df = pd.merge(wd_nonsoc_msr_df, modules_df, how="left", on="Module Name")["Student NRIC"].unique()
    
    # POPULATE MSR'S CLOSED WON DATE AND SALESPERSON COLUMNS
    master_msr_df = pd.merge(
        how="left",
        left=master_msr_df,
        left_on="Student NRIC",
        right=cw_df[["Identity Document Number", "Opportunity Closed Date", "Agent Name"]],
        right_on="Identity Document Number"
    )
    master_msr_df["Closed Won Date"] = master_msr_df["Opportunity Closed Date"]
    master_msr_df["Salesperson"] = master_msr_df["Agent Name"]
    master_msr_df.drop(columns=["Identity Document Number", "Opportunity Closed Date", "Agent Name"], inplace=True)
    master_msr_df.dropna(subset=["Closed Won Date"], inplace=True)
    
    # st.write("MSR MASTERLIST")
    # st.dataframe(master_msr_df)
    
    msr_df = master_msr_df[
        # (master_msr_df["Module Status"] == "PASSED") &
        (master_msr_df["Module Completion Date"] >= start_date) &
        (master_msr_df["Module Completion Date"] <= end_date)
    ]
    
    # INITIALIZE RSP SCHEME
    rsp_scheme_df = pd.read_csv(VARS.SCHEMECODES["RSP_SCHEME"])
    rsp_scheme_df = TOOLS.setDataTypes(rsp_scheme_df.astype(str), VARS.DTYPECODES["RSP_SCHEME"])
    
    st.write("RSP SCHEME")
    st.dataframe(rsp_scheme_df)
    
    # CALCULATE PAYABLE COMMISSION
    closed_wons, withdrawns, totals, percents, payables = [], [], [], [], []
    for i, row in msr_df.iterrows():
        closed_won, withdrawn = getCWMonthSales(row["Salesperson"], row["Closed Won Date"])
        total = closed_won - withdrawn
        closed_wons.append(closed_won)
        withdrawns.append(withdrawn)
        totals.append(total)
        percent = 0
        payable = 0
        if row["Module Status"] == "PASSED":
            percent = getRSPPercentCommission(total, row["Closed Won Date"])
            payable = row["Module Fee"] * percent / 100
        percents.append(percent)
        payables.append(payable)
    msr_df["Closed Won Sales"] = closed_wons
    msr_df["Withdrawn Sales"] = withdrawns
    msr_df["Total Sales Less Withdrawn"] = totals
    msr_df["Commission %"] = percents
    msr_df["Payable Commission"] = payables
    
    msr_df.drop_duplicates(subset=["Student NRIC", "Module Name", "Module Completion Date"], keep="last", inplace=True)
    missing_modules_df = pd.DataFrame(msr_df[msr_df["Module Fee"] == 0]["Module Name"].unique())
    
    # SET UP FILTERS
    filters_col, commands_col = st.columns([0.75, 0.25])
    with filters_col:
        sp_filter = st.multiselect(
            label="Filter by Salespersons",
            options=msr_df["Salesperson"].unique(),
        )
        nric_filter = st.multiselect(
            label="Filter by Student NRIC",
            options=msr_df["Student NRIC"].unique()
        )
        studname_filter = st.multiselect(
            label="Filter by Student Name",
            options=msr_df["Student Name"].unique()
        )
    
    if sp_filter and nric_filter and studname_filter:
        msr_df_filtered = msr_df[
            msr_df["Salesperson"].isin(sp_filter) &
            msr_df["Student NRIC"].isin(nric_filter) &
            msr_df["Student Name"].isin(studname_filter)
        ]
    elif sp_filter and nric_filter and not studname_filter:
        msr_df_filtered = msr_df[
            msr_df["Salesperson"].isin(sp_filter) &
            msr_df["Student NRIC"].isin(nric_filter)
        ]
    elif sp_filter and not nric_filter and studname_filter:
        msr_df_filtered = msr_df[
            msr_df["Salesperson"].isin(sp_filter) &
            msr_df["Student Name"].isin(studname_filter)
        ]
    elif not sp_filter and nric_filter and studname_filter:
        msr_df_filtered = msr_df[
            msr_df["Student NRIC"].isin(nric_filter) &
            msr_df["Student Name"].isin(studname_filter)
        ]
    elif sp_filter and not nric_filter and not studname_filter:
        msr_df_filtered = msr_df[
            msr_df["Salesperson"].isin(sp_filter)
        ]
    elif not sp_filter and nric_filter and not studname_filter:
        msr_df_filtered = msr_df[
            msr_df["Student NRIC"].isin(nric_filter)
        ]
    elif not sp_filter and not nric_filter and studname_filter:
        msr_df_filtered = msr_df[
            msr_df["Student Name"].isin(studname_filter)
        ]
    else: msr_df_filtered = msr_df.copy()
    
    sp_payables_df = msr_df.groupby(by=["Salesperson"], as_index=False)["Payable Commission"].sum()
    sp_payables_df_filtered = msr_df_filtered.groupby(by=["Salesperson"], as_index=False)["Payable Commission"].sum()
    
    # SET UP COMMANDS
    with commands_col:
        st.write("")
        st.write("")
        st.download_button(
            "Download MSR as CSV", 
            use_container_width=True, 
            data=msr_df.to_csv(index=False), 
            file_name="msr -all.csv",
            mime="csv"
        )
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
            file_name="sp payables.csv",
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
    st.dataframe(msr_df_filtered
                 .apply(lambda x: x.dt.date if x.name in ["Module Completion Date", "Closed Won Date"] else x), 
                 hide_index=True, use_container_width=True, column_order=VARS.MSR_COLS)
    