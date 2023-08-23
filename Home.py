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
msr_display_columns = [
    "Student NRIC",
    "Module Completion Date",
    "Closed Won Date",
    "Salesperson",
    "Total Sales on CW Month",
    "% Commission",
    "Module Fee",
    "Payable Commission",
    "Module Name",
    "Student Name"
]
cw_columns = [
    "Identity Document Number",
    "Opportunity Closed Date",
    "Student Name",
    "Agent Name",
    "Amount"
]

# ===== GLOBAL FUNCTIONS ===== #
def clean_csv(csv_file):
    with csv_file as file:
        csv_text = file.read()
    csv_text_str = str(csv_text, "utf-8", errors="ignore")
    # cleaned_csv_text = csv_text_str.replace("\xa0", "")
    return pd.read_csv(io.StringIO(csv_text_str), low_memory=False)

def getCWMonthTotal(salesperson, cw_df, cw_date):
    cw_df = cw_df[
        (cw_df["Agent Name"] == salesperson) & 
        (cw_df["Opportunity Closed Date"].dt.month == cw_date.month) &
        (cw_df["Opportunity Closed Date"].dt.year == cw_date.year)
    ]
    cw_df["Amount"] = pd.to_numeric(cw_df["Amount"], errors="coerce")
    return cw_df["Amount"].sum()

def getPercentCommission(total_sales, sales_type):
    filepath = st.secrets["paths"]["RSP_SCHEMA_DB"] if sales_type=="RSP" else st.secrets["paths"]["RTL_SCHEMA_DB"]
    schema_df = pd.read_csv(filepath)
    percentage = "0%"
    for index, row in schema_df.iterrows():
        if total_sales >= row["BAU Sales Order Required"]: percentage = row["% of Commission Payable"]
    return percentage

# ===== PAGE CONTENT ===== #
st.title("Online Commission Calculator")
st.write("---")

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
    start_date = datetime(start_year, start_month, start_day)
    end_year = start_year if start_month > 6 else start_year + 1
    end_month, end_day = quarter["end"]
    end_date = datetime(end_year, end_month, end_day)
    
    # extract and process MSR file
    msr_df = clean_csv(msr_file)
    msr_df = msr_df[msr_columns] # get only the defined columns
    msr_df = msr_df.dropna(subset=["Module Completion Date"]) # drop rows with blank Module Completion Date
    msr_df["Module Completion Date"] = pd.to_datetime(msr_df["Module Completion Date"], infer_datetime_format=True, errors="coerce") # convert Module Completion Date to date objects
    msr_df = msr_df[(msr_df["Module Completion Date"] >= start_date) & (msr_df["Module Completion Date"] <= end_date)] # drop rows whose Module Completion Date is not within the indicated quarter
    msr_df = msr_df[msr_df["Module Status"] == "Passed"] # drop rows whose Module Status is not Passed
    msr_df["Module Name"] = (
        msr_df["Module Name"]
        .str.upper() # set module names to uppercase
        .str.replace("-", " ") # replace hyphens with spaces
        .str.replace(" & ", " AND ") # elongate ampersands
        .str.replace("&", "AND") # elongate ampersands
        .str.replace(r"\s+", " ") # replace multiple spaces with single space
        .str.strip() # remove trailing spaces
    )
    msr_df["Module Fee"] = 0
    msr_df["Salesperson"] = ""
    msr_df["Closed Won Date"] = ""
    msr_df["% Commission"] = 0
    msr_df["Total Sales on CW Month"] = 0
    msr_df["Payable Commission"] = 0
    
    # extract and process CW file
    cw_df = clean_csv(cw_file)
    cw_df = cw_df[cw_columns] # get only the defined columns
    cw_df = cw_df.dropna(subset=["Opportunity Closed Date"]) # drop rows with blank Opportunity Closed Date
    cw_df["Opportunity Closed Date"] = pd.to_datetime(cw_df["Opportunity Closed Date"], infer_datetime_format=True, errors="coerce") # convert Opportunity Closed Date to date objects
    cw_df["Amount"] = pd.to_numeric(cw_df["Amount"].str.replace(",", "").str.replace(" ", ""), errors="coerce") # convert Amount column to numeric
    
    # identify module fee for each MSR
    module_fees_df = pd.read_csv(st.secrets["paths"]["MODULES_DB"])
    module_fees_df["Module Name"] = (
        module_fees_df["Module Name"]
        .str.upper() # set module names to uppercase
        .str.replace("-", " ") # replace hyphens with spaces
        .str.replace(" & ", " AND ") # elongate ampersands
        .str.replace("&", "AND") # elongate ampersands
        .str.replace(r"\s+", " ") # replace multiple spaces with single space
        .str.strip() # remove trailing spaces
    )
    msr_df = pd.merge(msr_df, module_fees_df, on="Module Name", how="left") # join msr_df and module_fees_df on Module Name column
    msr_df["Module Fee"] = msr_df["Course fee"] # transfer the new column to the Module Fee column
    msr_df = msr_df.drop(columns=["Course fee"]) # drop the created column (from the join)
    
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
        total = getCWMonthTotal(salesperson, cw_df, cw_date)
        totals.append(total)
        percentage = getPercentCommission(total, "RSP")
        percent_commission.append(percentage)
        module_fee = row["Module Fee"]
        payable = module_fee * float(percentage.strip("%")) / 100
        payable_commission.append(payable)
    msr_df["Total Sales on CW Month"] = totals
    msr_df["% Commission"] = percent_commission
    msr_df["Payable Commission"] = payable_commission
        
    st.dataframe(msr_df[msr_display_columns]
                 .apply(lambda x: x.dt.date if x.name in ["Module Completion Date", "Closed Won Date"] else x), 
                 hide_index=True, use_container_width=True)