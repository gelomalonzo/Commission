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

# ===== PAGE CONTENT ===== #
st.header("Modules List")
st.write("Listed below are the modules and their corresponding module fee. The module names are listed in alphabetical order.")
st.write("---")

main_alert_row = st.container()
df_col, ctrl_col = st.columns([0.8, 0.2])
with df_col:
    modules_df_editor = st.data_editor(modules_df, num_rows="dynamic", use_container_width=True, hide_index=False)
with ctrl_col:
    if st.button("Save changes", use_container_width=True):
        modules_df = removeDuplicates(modules_df_editor)
        modules_df.to_csv(PATHS.MODULES_DB, index=False)
        modules_df_editor = modules_df
        TOOLS.displayAlerts(main_alert_row, [{"content":"Changes saved successfully.", "type":"success"}])
    if st.button("Revert unsaved changes", use_container_width=True): st.experimental_rerun()
    st.download_button("Download as CSV", use_container_width=True, data=modules_df.to_csv(index=False), file_name="modules-list.csv",mime="csv")

st.write("---")
st.subheader(":round_pushpin: Notes and Instructions")
with st.expander(":pencil: Editing a row"):
    st.write("To edit a module's details, you can double click on a cell, then type in the updated information for that particular module.")
    st.write('Do not forget to click on the "Save changes" button found on the upper right of the table to save your changes on the data.')
with st.expander(":heavy_plus_sign: Adding a new row"):
    st.write("To add a new row, scroll through the bottom-most of the table. Click on the empty last row, then type in the new data.")
    st.write("Make sure to fill in the two fields (Module Name and Fee) to avoid errors.")
    st.write('Do not forget to click on the "Save changes" button found on the upper right of the table to save your changes on the data.')
with st.expander(":wastebasket: Deleting a row"):
    st.write("To delete a row, tick the checkbox corresponding to that row, then press on the keyboard's delete button.")
    st.write("You can select multiple rows and press on the keyboard's delete button to delete multiple rows at once.")
    st.write("You can also select all rows by clicking on the checkboxes' column header and pressing on the keyboard's delete button.")
    st.write('Do not forget to click on the "Save changes" button found on the upper right of the table to save your changes on the data.')
with st.expander(":leftwards_arrow_with_hook: Reverting unsaved changes"):
    st.write('To revert unsaved changes, just click on the "Revert unsaved changes" button which reloads the page.')
    st.write('Note that this does not undo the changes that have already been saved to the modules list of the website.')
with st.expander(":arrow_down: Download as CSV"):
    st.write('To download the modules list as a CSV file, click on the "Download as CSV" button.')
    st.write('This triggers your browser to download the CSV file with filename "modules-list.csv".')
    st.write('Note that only the saved changes are included in the downloaded file.')