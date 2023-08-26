# ===== IMPORTS ===== #
from io import StringIO
import streamlit as st
import pandas as pd

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
with open(PATHS.MODULES_CSS) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
# ===== VARIABLES ===== #
modules_df = pd.read_csv(PATHS.MODULES_DB)
modules_df = TOOLS.setDataTypes(modules_df, VARS.MODULES_DTYPES)

# ===== FUNCTIONS ===== #
def isValidModulesCSV(modules_files):
    # check if there is at least one file in the file upload field
    if len(modules_files) == 0:
        context = {
            "status":False,
            "messages":[
                {"content":"Please add at least one file to upload.", "type":"warning"}
            ]
        }
        return [], context
    
    context = {
        "status":True,
        "messages":[]
    }
    
    # verify that each file contains the columns Module Name and Module Fee
    valid_dfs = []
    for file in modules_files:
        filename = file.name
        content = file.read()
        is_valid = True
        try:
            content_str = str(content, "utf-8", errors="ignore")
            df = pd.read_csv(StringIO(content_str))
            columns = ""
            for column in df.columns:
                if len(columns) == 0: columns = '"' + column + '"'
                else: columns = columns + ', "' + column + '"'
            if "Module Name" not in df.columns:
                message = {
                    "content":('Column "Module Name" not found in file "' + filename + '". Found the following columns: ' + columns),
                    "type":"error"
                }
                context["messages"].append(message)
                is_valid = False
            if "Module Fee" not in df.columns:
                context["messages"].append({
                    "content":('Column "Module Fee" not found in file "' + filename + '". Found the following columns: {' + columns + "}."),
                    "type":"error"
                })
                is_valid = False
        except pd.errors.EmptyDataError:
            # context["status"] = False
            # context["messages"].append({
            #     "content":('The file "' + filename + '" is empty.'),
            #     "type":"warning"
            # })
            is_valid = False
        except pd.errors.ParserError:
            context["messages"].append({
                "content":('The file "' + filename + '" has an invalid CSV format.'),
                "type":"error"
            })
            is_valid = False
        if is_valid: valid_dfs.append({"filename":filename, "df":df})
    
    # default: the uploaded file is valid
    if len(valid_dfs) == 0:
        context["status"] = False
    return valid_dfs, context

def importModulesFromCSV(new_modules_dfs, modules_df):
    context = {"status":True, "messages":[]}
    
    for new_module in new_modules_dfs:
        new_module_filename = new_module["filename"]
        new_module_df = new_module["df"]
        new_module_df = TOOLS.setDataTypes(new_module_df, VARS.MODULES_DTYPES)
        modules_df = pd.concat([modules_df, new_module_df], ignore_index=True, copy=False, verify_integrity=True)
        modules_df.to_csv(PATHS.MODULES_DB, index=False)
        context["messages"].append({
            "content":('Successfully imported modules from "' + new_module_filename + '".'),
            "type":"success"
        })

    return context

# ===== PAGE CONTENT ===== #
st.header("Import Modules")
st.write("This page is designated for importing module list/s from uploaded CSV files.")

st.write("---")
msg_row = st.empty()
upload_col, instructions_col = st.columns((1.5, 2))
df_row = st.container()
with upload_col:
    with st.form("upload_modules_from_csv"):
        modules_files = st.file_uploader("Add Modules Files", accept_multiple_files=True, type=VARS.FILETYPES)
        upload_modules_btn = st.form_submit_button("Upload")
        if upload_modules_btn:
            msg_row.empty()
            valid_dfs, valid_context = isValidModulesCSV(modules_files)
            TOOLS.displayAlerts(msg_row, valid_context["messages"])
            if valid_context["status"] == True:
                imported = importModulesFromCSV(valid_dfs, modules_df)
                TOOLS.displayAlerts(msg_row, imported["messages"])
                with df_row:
                    st.write("---")
                    st.subheader("Updated list of modules:")
                    st.dataframe(modules_df, use_container_width=True)

with instructions_col:
    st.subheader("Notes and Instructions")
    with st.expander("Uploading from CSV"):
        st.write("")
    with st.expander("File Format"):
        st.write("")