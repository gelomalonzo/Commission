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
def loadModulesDF(container, modules_df_editor):
    modules_df = pd.read_csv(PATHS.MODULES_DB)
    modules_df = TOOLS.setDataTypes(modules_df, VARS.MODULES_DTYPES)
    
    with container:
        container.empty()
        modules_df_editor = modules_df.copy()
    return

def isValidModulesCSV(modules_files):
    # check if there is at least one file in the file upload field
    if len(modules_files) == 0:
        context = {
            "status":False,
            "messages":[
                {"content":"Please add at least one file to upload.", "type":"warning"}
            ]
        }
        return context
    
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
            "content":('Successfully imported modules from "' + new_module_filename + '". Please refresh the page to reflect changes.'),
            "type":"success"
        })

    return context

# ===== PAGE CONTENT ===== #
st.header("Modules List")
st.write("Listed below are the modules and their corresponding module fee.")

st.write("---")
df_col, notes_col = st.columns([1, 0.5])
with df_col:
    ctrl_row = st.container()
    modules_df_editor = st.data_editor(modules_df, num_rows="dynamic", use_container_width=True)
    with ctrl_row:
        ctrl_btn_row = st.container()
        ctrl_msg_row = st.container()
        with ctrl_btn_row:
            if st.button("Save changes"):
                modules_df = modules_df_editor
                modules_df.to_csv(PATHS.MODULES_DB, index=False)
                TOOLS.displayAlerts(ctrl_msg_row, [{"content":"Changes saved successfully.", "type":"success"}])
            
with notes_col:
    st.subheader("Notes and Instructions")
    with st.expander("Editing a row"):
        st.write("To edit a module's details, you can double click on a cell, then type in the updated information for that particular module.")
        st.write('Do not forget to click on the "Save changes" button found on the upper right of the table to save your changes on the data.')
    with st.expander("Adding a new row"):
        st.write("To add a new row, scroll through the bottom-most of the table. Click on the empty last row, then type in the new data.")
        st.write("Make sure to fill in the two fields (Module Name and Fee) to avoid errors.")
        st.write('Do not forget to click on the "Save changes" button found on the upper right of the table to save your changes on the data.')
    with st.expander("Deleting a row"):
        st.write("To delete a row, tick the checkbox corresponding to that row, then press on the keyboard's delete button.")
        st.write("You can select multiple rows and press on the keyboard's delete button to delete multiple rows at once.")
        st.write("You can also select all rows by clicking on the checkboxes' column header and pressing on the keyboard's delete button.")
        st.write('Do not forget to click on the "Save changes" button found on the upper right of the table to save your changes on the data.')