from datetime import datetime
import streamlit as st

from . import filepaths as PATHS

SITE_TITLE = "Online Commission Calculator"
LOGO = ":coin:"
LAYOUT = "wide"
SIDEBAR_STATE = "auto"

CURR_DATE = datetime.now()
CURR_MONTH = CURR_DATE.month
CURR_YEAR = CURR_DATE.year
MAX_YEAR = CURR_YEAR if CURR_MONTH <= 6 else CURR_YEAR + 1

# for listing selectbox options in data input form
YEARS = [
    {"label":f"{y} - {y+1}", "start":y, "end":y+1}
    for y in reversed(range(MAX_YEAR - 5, MAX_YEAR))
]

# for listing selectbox options in data input form, and
# extracting the start and end dates
QUARTERS = [
    {"label":"Quarter 1 (July - September)", "start":(7,1), "end":(9,30)},
    {"label":"Quarter 2 (October - December)", "start":(10,1), "end":(12,31)},
    {"label":"Quarter 3 (January - March)", "start":(1,1), "end":(3,31)},
    {"label":"Quarter 4 (April - June)", "start":(4,1), "end":(6,30)}
]

# for specifying accepted file types in data input form
FILETYPES = [
    "csv",
]

# these will be the retained columns from the raw MSR CSV file
MSR_COLS_RAW = [
    "Student Name",
    "Student NRIC",
    "Course Name",
    "Enrollment Status",
    "Module Name",
    "Module Status",
    "Module Completion Date"
]

# these should be the data types of the raw MSR CSV file
MSR_DTYPES_RAW = {
    "Student Name"              :   "string",
    "Student NRIC"              :   "id",
    "Course Name"               :   "string",
    "Enrollment Status"         :   "string",
    "Module Name"               :   "string",
    "Module Status"             :   "string",
    "Module Completion Date"    :   "datetime"
}

# these will be the columns after calculating the payable commission
MSR_COLS = [
    "Student NRIC",
    "Module Completion Date",
    "Closed Won Date",
    "Salesperson",
    "Closed Won Sales",
    "Withdrawn Sales",
    "Total Sales Less Withdrawn",
    "Commission %",
    "Module Fee",
    "Payable Commission",
    "Course Name",
    "Module Name",
    "Student Name"
]

# these should be the data types of the MSR data frame post-calculation of payable commission
MSR_DTYPES = {
    "Student NRIC"              :   "id",
    "Module Completion Date"    :   "datetime",
    "Closed Won Date"           :   "datetime",
    "Salesperson"               :   "string",
    "Withdrawn Sales"           :   "float",
    "Closed Won Sales"          :   "float",
    "Total Sales Less Withdrawn":   "float",
    "Commission %"              :   "float",
    "Module Fee"                :   "float",
    "Payable Commission"        :   "float",
    "Course Name"               :   "string",
    "Module Name"               :   "string",
    "Student Name"              :   "string"
}

# these will be the retained columns from the raw CW CSV file
CW_COLS_RAW = [
    "Identity Document Number",
    "Opportunity Closed Date",
    "Course name",
    "Student Name",
    "Agent Name",
    "Amount"
]

# these should be the data types of the raw CW CSV file
CW_DTYPES_RAW = {
    "Identity Document Number"  :   "id",
    "Opportunity Closed Date"   :   "datetime",
    "Course name"               :   "string",
    "Student Name"              :   "string",
    "Agent Name"                :   "string",
    "Amount"                    :   "float"
}

CWSALES_COLS = [
    "Salesperson",
    "Closed Won Date",
    "Closed Won Sales",
    "Withdrawn Sales",
    "Total Sales"
]

CWSALES_DTYPES = {
    "Salesperson"               :   "string",
    "Closed Won Date"           :   "datetime",
    "Closed Won Sales"          :   "float",
    "Withdrawn Sales"           :   "float",
    "Total Sales"               :   "float"
}

MODULES_DTYPES = {
    "Module Name"               :   "string",
    "Module Fee"                :   "float"
}

MODULES_COLCONFIG = {
    "":st.column_config.Column(
        disabled=True
    ),
    "Module Name":st.column_config.TextColumn(
        label="Module Name",
        help="The name of the module",
        required=True
    ),
    "Module Fee":st.column_config.NumberColumn(
        label="Module Fee",
        help="The price of the module in SGD",
        min_value=0,
        required=True,
        width="small"
    )
}

# these should be the data types of the CSV file of the commission schema for retail (salespersons)
RSP_SCHEMA_DTYPES = {
    "Tier"                      :   "string",
    "Sales Order Required"      :   "float",
    "% of Commission Payable"   :   "float"
}

# these should be the data types of the CSV file of the commission schema for retail (team leaders)
RTL_SCHEMA_DTYPES = {
    "Tier"                      :   "string",
    "Sales Order Required"      :   "float",
    "% of Commission Payable"   :   "float"
}

# these should be the data types of the CSV file of the commission schema for enterprise
ENT_SCHEMA_DTYPES = {
    
}

# map the data type codes with the corresponding dictionary of data types
# NOTE: make sure the dtypecodes for schemas are the same as their corresponding schemacodes
DTYPECODES = {
    "MSR_RAW":MSR_DTYPES_RAW,
    "CW_RAW":CW_DTYPES_RAW,
    "MODULES":MODULES_DTYPES,
    "RSP_SCHEMA":RSP_SCHEMA_DTYPES,
    "RTL_SCHEMA":RTL_SCHEMA_DTYPES,
    "ENT_SCHEMA":ENT_SCHEMA_DTYPES
}

# map the schema codes with the corresponding file directory of the schema
SCHEMACODES = {
    "RSP_SCHEMA":PATHS.RSP_SCHEMA_DB,
    "RTL_SCHEMA":PATHS.RTL_SCHEMA_DB,
    "ENT_SCHEMA":PATHS.ENT_SCHEMA_DB
}