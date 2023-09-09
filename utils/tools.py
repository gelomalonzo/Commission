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
    
    try:
        with csv_file as file:
            csv_text = file.read()
    except:
        csv_text = csv_file.read()
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
