import pandas as pd
import io
import streamlit as st

from . import constants as VARS
from . import filepaths as PATHS

def displayAlerts(container, messages):
    with container:
        for message in messages:
            if message["type"] == "success":    st.success(message["content"])
            if message["type"] == "warning":    st.warning(message["content"])
            if message["type"] == "error":      st.error(message["content"])
    return

def cleanCSVtoDF(csv_file):
    """Remove non-UTF-8 characters and convert all cells into string.
    
    Args:
        csv_file (UploadedFile from streamlit.file_uploader): the user's uploaded file

    Returns:
        df (pandas.DataFrame): the cleaned data frame whose columns are of type Object (string)
    """
    
    with csv_file as file:
        csv_text = file.read()
    csv_text_str = str(csv_text, "utf-8", errors="ignore")
    return pd.read_csv(io.StringIO(csv_text_str), low_memory=False)

def setDataTypes(df:pd.DataFrame, dtypes:dict):
    """Set the data type of each column in the passed data frame.

    Args:
        df (pandas.DataFrame): the data frame to be modified
        dtypes (dict): the dictionary mapping column names to their data type codes

    Returns:
        df (pandas.DataFrame): the modified data frame
    """
    
    df = df.astype(str)
    for colname, dtype in dtypes.items():
        if dtype == "string":
            df[colname] = (df[colname]
                .str.upper()
                .str.replace("-", " ")
                .str.replace(" & ", " AND ")
                .str.replace("&", "AND")
                .str.replace(r"\s+", " ", regex=True)
                .str.replace(r"[^\x00-\x7F]+", "", regex=True)
                .str.strip()
            )
        elif dtype == "id":
            df[colname] = (df[colname]
                .str.upper()
                .str.replace(" ", "")
                .str.replace(r"[^\x00-\x7F]+", "", regex=True)
                .str.strip()
            )
        elif dtype == "float":
            df[colname] = pd.to_numeric(df[colname].str.replace(r'[^\d.]', '', regex=True))
        elif dtype == "percentage":
            mask = df[colname].str.contains("%")
            df[colname] = pd.to_numeric(df[colname].str.replace(r'[^\d.]', '', regex=True))
            df.loc[mask, colname] /= 100
        elif dtype == "datetime":
            df[colname] = pd.to_datetime(df[colname], infer_datetime_format=True, errors="coerce")
    return df

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

def getCWMonthSales(salesperson, cw_df, cw_date, msr_masterdf):
    cw_df = cw_df[
        (cw_df["Agent Name"] == salesperson) &
        (cw_df["Opportunity Closed Date"].dt.month == cw_date.month) &
        (cw_df["Opportunity Closed Date"].dt.year == cw_date.year)
    ]
    closed_won = cw_df["Amount"].sum()
    withdrawn = 0
    for i, row in cw_df.iterrows():
        msr = msr_masterdf[
            (msr_masterdf["Student NRIC"] == row["Identity Document Number"]) &
            ((msr_masterdf["Enrollment Status"] == "WITHDRAWN NON SOC") |
             (msr_masterdf["Enrollment Status"] == "WITHDRAWN NON SOC_ATTRITION"))
            # (msr_masterdf["Course Name"] == row["Course Name"])
        ]
        if not msr.empty:
            # withdrawn = withdrawn + msr["Module Fee"].sum()
            withdrawn = withdrawn + row["Amount"]
            # st.table(msr)
        # if not msr.empty:
        #     for j, msr_row in msr.iterrows():
        #         if ((row["Course Name"] in msr_row["Course Name"]) or
        #             (msr_row["Course Name"] in row["Course Name"])):
        #             withdrawn = withdrawn + msr_row["Module Fee"]
        #             st.table(msr_row)
    return closed_won, withdrawn

def getPercentCommission(total_sales, schemacode:str):
    schema_df = pd.read_csv(VARS.SCHEMACODES[schemacode])
    schema_df = setDataTypes(schema_df.astype(str), VARS.DTYPECODES[schemacode])
    percentage = 0.0
    for index, row in schema_df.iterrows():
        if total_sales >= row["Sales Order Required"]:
            percentage = row["% of Commission Payable"]
    return percentage
