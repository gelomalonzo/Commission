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
# modules_df = pd.read_csv(PATHS.MODULES_DB)
# modules_df = TOOLS.setDataTypes(modules_df, VARS.MODULES_DTYPES)

if "modules_df" not in st.session_state:
    modules_df = pd.read_csv(PATHS.MODULES_DB)
    st.session_state.modules_df = TOOLS.setDataTypes(modules_df, VARS.MODULES_DTYPES)

if "editor_key" not in st.session_state:
    st.session_state.editor_key = 0
    
print(st.session_state.modules_df)
print("\nKEY=" + str(st.session_state.editor_key))


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

def redisplayDFEditor(container):
    st.session_state.editor_key += 1
    with container:
        modules_df_editor = st.data_editor(
            data=st.session_state.modules_df, 
            num_rows="dynamic", 
            use_container_width=True, 
            hide_index=False, 
            column_config=VARS.MODULES_COLCONFIG,
            key=f"editor-{st.session_state.editor_key}"
        )
    return

# ===== PAGE CONTENT ===== #
st.header("Modules List")
st.write("Listed below are the modules and their corresponding module fee. The module names are listed in alphabetical order.")
st.write("---")

main_alert_row = st.container()
df_row = st.empty()
control_row = st.container()

with df_row:
    modules_df_editor = st.data_editor(
        data=st.session_state.modules_df, 
        num_rows="dynamic", 
        use_container_width=True, 
        hide_index=False, 
        column_config=VARS.MODULES_COLCONFIG,
        key=f"editor-{st.session_state.editor_key}"
    )

with control_row:
    save_col, col_2, revert_col, col_4, download_col = st.columns([0.3, 0.05, 0.3, 0.05, 0.3])
    with save_col:
        if st.button("Save changes", use_container_width=True):
            st.session_state.modules_df = TOOLS.setDataTypes(removeDuplicates(modules_df_editor), VARS.MODULES_DTYPES)
            st.session_state.modules_df.to_csv(PATHS.MODULES_DB, index=False)
            redisplayDFEditor(df_row)
            TOOLS.displayAlerts(main_alert_row, [{"content":"Successfully saved all changes.", "type":"success"}])
    with revert_col:
        if st.button("Revert unsaved changes", use_container_width=True):
            redisplayDFEditor(df_row)
            TOOLS.displayAlerts(main_alert_row, [{"content":"Successfully reverted all unsaved changes.", "type":"warning"}])
    with download_col:
        st.download_button(
            "Download as CSV", 
            use_container_width=True, 
            data=st.session_state.modules_df.to_csv(index=False), 
            file_name="modules-list.csv",
            mime="csv"
        )

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