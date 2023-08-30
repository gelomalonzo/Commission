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
def removeDuplicates(df:pd.DataFrame):
    unique_modules = df["Module Name"].unique()
    dup_indices = []
    for module_name in unique_modules:
        temp_df = df[df["Module Name"] == module_name]
        for i, row_i in temp_df.iterrows():
            for j, row_j in temp_df.iterrows():
                if j > i: dup_indices.append(i)
    return df.drop(dup_indices).sort_values(by=["Module Name"], ignore_index=True).reset_index(drop=True)

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

def appendModulesFromCSV(new_modules_dfs, modules_df):
    context = {"status":True, "messages":[]}
    for new_module in new_modules_dfs:
        new_module_filename = new_module["filename"]
        new_module_df = new_module["df"]
        new_module_df = TOOLS.setDataTypes(new_module_df, VARS.MODULES_DTYPES)
        modules_df = pd.concat([modules_df, new_module_df], ignore_index=True, copy=False, verify_integrity=True)
        modules_df = removeDuplicates(modules_df)
        modules_df.to_csv(PATHS.MODULES_DB, index=False)
        context["messages"].append({
            "content":('Successfully imported modules from "' + new_module_filename + '".'),
            "type":"success"
        })
    return modules_df, context

def updateModulesFromCSV(new_modules_dfs, modules_df:pd.DataFrame):
    context = {"status":True, "messages":[]}
    for new_module in new_modules_dfs:
        new_module_filename = new_module["filename"]
        new_module_df = new_module["df"]
        new_module_df = TOOLS.setDataTypes(new_module_df, VARS.MODULES_DTYPES)
        modules_df = pd.merge(modules_df, new_module_df, on="Module Name", how="outer", suffixes=("_old", "_new"))
        modules_df["Module Fee"] = modules_df["Module Fee_new"].fillna(modules_df["Module Fee_old"])
        modules_df = modules_df.drop(columns=["Module Fee_old", "Module Fee_new"])
        modules_df = removeDuplicates(modules_df)
        modules_df.to_csv(PATHS.MODULES_DB, index=False)
        context["messages"].append({
            "content":('Successfully imported modules from "' + new_module_filename + '".'),
            "type":"success"
        })
    return modules_df, context

# ===== PAGE CONTENT ===== #
st.header("Import Modules")
st.write("This page is designated for importing module list/s from uploaded CSV files. You may also view the list of modules at the bottom of this page.")
st.write("---")

main_alert_row = st.container()
main_row = st.container()
df_row = st.empty()

with df_row.container():
    st.write("---")
    st.subheader("List of Modules")
    st.dataframe(modules_df, use_container_width=True)

with main_row:
    import_col, mid_col, instructions_col = st.columns((1.25, 0.10, 1.65))
    with import_col:
        st.subheader("Import Form")
        with st.form("import-modules-form"):
            command = st.selectbox("Command to Perform", ["Append", "Update", "Replace"])
            modules_files = st.file_uploader("Upload Modules Files", accept_multiple_files=True, type=VARS.FILETYPES)
            input_alert_row = st.container()
            if st.form_submit_button("Import"):
                main_alert_row.empty()
                valid_dfs, valid_context = isValidModulesCSV(modules_files)
                if valid_context["status"] == False:
                    TOOLS.displayAlerts(input_alert_row, valid_context["messages"])
                elif valid_context["status"] == True:
                    df_row.empty()
                    if command == "Append":
                        modules_df, imported = appendModulesFromCSV(valid_dfs, modules_df)
                        modules_df = modules_df
                        TOOLS.displayAlerts(main_alert_row, imported["messages"])
                    elif command == "Update":
                        # messages = [{"content":"Updating rows not yet available.", "type":"warning"}]
                        # TOOLS.displayAlerts(input_alert_row, messages)
                        modules_df, imported = updateModulesFromCSV(valid_dfs, modules_df)
                        modules_df = modules_df
                        TOOLS.displayAlerts(main_alert_row, imported["messages"])
                    elif command == "Replace":
                        messages = [{"content":"Replacing the entire modules data not yet available.", "type":"warning"}]
                        TOOLS.displayAlerts(input_alert_row, messages)
                    with df_row.container():
                        st.write("---")
                        st.subheader("Updated List of Modules")
                        st.dataframe(modules_df, use_container_width=True)
                        
    with instructions_col:
        st.subheader("Notes and Instructions")
        with st.expander("Appending Modules Data"):
            st.write("")
        with st.expander("Updating Module Fees"):
            st.write("")
        with st.expander("Replacing Entire Modules Data"):
            st.write("")
        with st.expander("Deleting Modules"):
            st.write("")
        with st.expander("File Format"):
            st.write("")
