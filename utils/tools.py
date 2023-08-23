import pandas as pd
import io

from . import constants as VARS
from . import filepaths as PATHS

def cleanCSVtoDF(csv_file):
    with csv_file as file:
        csv_text = file.read()
    csv_text_str = str(csv_text, "utf-8", errors="ignore")
    return pd.read_csv(io.StringIO(csv_text_str), low_memory=False)

def setDataTypes(df:pd.DataFrame, dtypecode:str):
    df = df.astype(str)
    dtypes = VARS.DTYPECODES[dtypecode]
    for colname, dtype in dtypes.items():
        if dtype == "string":
            df[colname] = (df[colname]
                .str.upper()
                .str.replace("-", " ")
                .str.replace(" & ", " AND ")
                .str.replace("&", "AND")
                .str.replace(r"\s+", " ")
                .str.strip()
            )
        elif dtype == "id":
            df[colname] = (df[colname]
                .str.upper()
                .str.replace(" ", "")
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

def getCWMonthTotal(salesperson, cw_df, cw_date):
    cw_df = cw_df[
        (cw_df["Agent Name"] == salesperson) &
        (cw_df["Opportunity Closed Date"].dt.month == cw_date.month) &
        (cw_df["Opportunity Closed Date"].dt.year == cw_date.year)
    ]
    return cw_df["Amount"].sum() # to do: subtract withdrawn sales amounts

def getPercentCommission(total_sales, dtypecode:str):
    schema_df = pd.read_csv(VARS.SCHEMACODES[dtypecode])
    schema_df = setDataTypes(schema_df.astype(str), dtypecode)
    percentage = 0.0
    for index, row in schema_df.iterrows():
        if total_sales >= row["Sales Order Required"]:
            percentage = row["% of Commission Payable"]
    return percentage