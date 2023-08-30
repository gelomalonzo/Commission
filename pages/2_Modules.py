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
df_col, notes_col = st.columns([1, 0.5])
with df_col:
    ctrl_row = st.container()
    modules_df_editor = st.data_editor(modules_df, num_rows="dynamic", use_container_width=True, hide_index=False)
    with ctrl_row:
        ctrl_btn_row = st.container()
        ctrl_msg_row = st.container()
        with ctrl_btn_row:
            if st.button("Save changes"):
                modules_df = removeDuplicates(modules_df_editor)
                modules_df.to_csv(PATHS.MODULES_DB, index=False)
                modules_df_editor = modules_df
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