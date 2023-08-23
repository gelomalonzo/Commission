from datetime import datetime

from . import filepaths as PATHS

SITE_TITLE = "Online Commission Calculator"
LOGO = ":coin:"
LAYOUT = "wide"
SIDEBAR_STATE = "collapsed"

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
    "Module Name",
    "Module Status",
    "Module Completion Date"
]

# these should be the data types of the raw MSR CSV file
MSR_DTYPES_RAW = {
    "Student Name"              :   "string",
    "Student NRIC"              :   "id",
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
    "Total Sales on CW Month",
    "% Commission",
    "Module Fee",
    "Payable Commission",
    "Module Name",
    "Student Name"
]

# these should be the data types of the MSR data frame post-calculation of payable commission
MSR_DTYPES = {
    "Student NRIC"              :   "id",
    "Module Completion Date"    :   "datetime",
    "Closed Won Date"           :   "datetime",
    "Salesperson"               :   "string",
    "Total Sales on CW Month"   :   "float",
    "% Commission"              :   "float",
    "Module Fee"                :   "float",
    "Payable Commission"        :   "float",
    "Module Name"               :   "string",
    "Student Name"              :   "string"
}

# these will be the retained columns from the raw CW CSV file
CW_COLS_RAW = [
    "Identity Document Number",
    "Opportunity Closed Date",
    "Student Name",
    "Agent Name",
    "Amount"
]

# these should be the data types of the raw CW CSV file
CW_DTYPES_RAW = {
    "Identity Document Number"  :   "id",
    "Opportunity Closed Date"   :   "datetime",
    "Student Name"              :   "string",
    "Agent Name"                :   "string",
    "Amount"                    :   "float"
}

MODULES_DTYPES = {
    "Module Name"               :   "string",
    "Module Fee"                :   "float"
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