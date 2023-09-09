# ===== IMPORTS ===== #
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
if "rsp_df" not in st.session_state:
    rsp_df = pd.read_csv(PATHS.RSP_SCHEME_DB)
    st.session_state.rsp_df = TOOLS.setDataTypes(rsp_df, VARS.RSP_SCHEME_DTYPES)
if "rsp_key" not in st.session_state:
    st.session_state.rsp_key = 0
if "rtl_df" not in st.session_state:
    rtl_df = pd.read_csv(PATHS.RTL_SCHEME_DB)
    st.session_state.rtl_df = TOOLS.setDataTypes(rtl_df, VARS.RTL_SCHEME_DTYPES)
if "rtl_key" not in st.session_state:
    st.session_state.rtl_key = 0
# if "ent_df" not in st.session_state:
#     ent_df = pd.read_csv(PATHS.ENT_SCHEME_DB)
#     st.session_state.ent_df = TOOLS.setDataTypes(ent_df, VARS.ENT_SCHEME_DTYPES)
# if "ent_key" not in st.session_state:
#     st.session_state.ent_key = 0

# ===== FUNCTIONS ===== #
def redisplayDFEditor(container, code:str):
    container.empty()
    if code == "RSP":
        st.session_state.rsp_key += 1
        with container:
            rsp_df_editor = st.data_editor(
                data=st.session_state.rsp_df, 
                num_rows="dynamic", 
                use_container_width=True, 
                hide_index=True, 
                key=f"rsp-editor-{st.session_state.rsp_key}"
            )
    if code == "RTL":
        st.session_state.rtl_key += 1
        with container:
            rtl_df_editor = st.data_editor(
                data=st.session_state.rtl_df, 
                num_rows="dynamic", 
                use_container_width=True, 
                hide_index=True, 
                key=f"rtl-editor-{st.session_state.rtl_key}"
            )
    if code == "ENT":
        st.session_state.ent_key += 1
        with container:
            ent_df_editor = st.data_editor(
                data=st.session_state.ent_df, 
                num_rows="dynamic", 
                use_container_width=True, 
                hide_index=True, 
                key=f"rtl-editor-{st.session_state.ent_key}"
            )
    return

# ===== PAGE CONTENT ===== #
st.header("Schemes")
st.write("Listed below are the SCHEME tables for retail and enterprise. Scroll through the bottom of the page for instructions.")
st.write("---")
ret_col, mid_col, ent_col = st.columns((1, 0.1, 1))

with ret_col:
    st.subheader(":bust_in_silhouette: Retail")
    
    st.write("For Salespersons")
    rsp_df_row = st.empty()
    rsp_alert_row = st.container()
    with rsp_df_row:
        rsp_df_editor = st.data_editor(
            data=st.session_state.rsp_df, 
            num_rows="dynamic", 
            use_container_width=True, 
            hide_index=True, 
            key=f"rsp-editor-{st.session_state.rsp_key}"
        )
    rsp_revert_col, rsp_save_col = st.columns([0.5, 0.5])
    with rsp_revert_col:
        if st.button("Revert unsaved changes", key="rsp-revert", use_container_width=True):
            redisplayDFEditor(rsp_df_row, "RSP")
            TOOLS.displayAlerts(rsp_alert_row, [{"content":"Successfully reverted all unsaved changes.", "type":"warning"}])
    with rsp_save_col:
        if st.button("Save changes", key="rsp-save", use_container_width=True):
            st.session_state.rsp_df = TOOLS.setDataTypes(rsp_df_editor, VARS.RSP_SCHEME_DTYPES)
            st.session_state.rsp_df.to_csv(PATHS.RSP_SCHEME_DB, index=False)
            redisplayDFEditor(rsp_df_row, "RSP")
            TOOLS.displayAlerts(rsp_alert_row, [{"content":"Successfully saved changes.", "type":"success"}])
    
    st.divider()
    st.write("For Team Leaders")
    rtl_df_row = st.empty()
    rtl_alert_row = st.container()
    with rtl_df_row:
        rtl_df_editor = st.data_editor(
            data=st.session_state.rtl_df, 
            num_rows="dynamic", 
            use_container_width=True, 
            hide_index=True, 
            key=f"rtl-editor-{st.session_state.rtl_key}"
        )
    rtl_revert_col, rtl_save_col = st.columns([0.5, 0.5])
    with rtl_revert_col:
        if st.button("Revert unsaved changes", key="rtl-revert", use_container_width=True):
            redisplayDFEditor(rtl_df_row, "RTL")
            TOOLS.displayAlerts(rtl_alert_row, [{"content":"Successfully reverted all unsaved changes.", "type":"warning"}])
    with rtl_save_col:
        if st.button("Save changes", key="rtl-save", use_container_width=True):
            st.session_state.rtl_df = TOOLS.setDataTypes(rtl_df_editor, VARS.RSP_SCHEME_DTYPES)
            st.session_state.rtl_df.to_csv(PATHS.RTL_SCHEME_DB, index=False)
            redisplayDFEditor(rtl_df_row, "RTL")
            TOOLS.displayAlerts(rtl_alert_row, [{"content":"Successfully saved changes.", "type":"success"}])

with ent_col:
    st.subheader(":busts_in_silhouette: Enterprise")

st.write("---")
st.subheader(":round_pushpin: Notes and Instructions")

with st.expander(":pencil: Editing a row"):
    st.write("To edit a row's details, you can double click on a cell, then type in the updated information for that particular row.")
    st.write('Do not forget to click on the "Save changes" button found on the upper right of the table to save your changes on the data.')

with st.expander(":heavy_plus_sign: Adding a new row"):
    st.write("To add a new row, scroll through the bottom-most of the table. Click on the empty last row, then type in the new data.")
    st.write("Make sure to fill in all its fields.")
    st.write('Do not forget to click on the "Save changes" button found on the upper right of the table to save your changes on the data.')

with st.expander(":wastebasket: Deleting a row"):
    st.write("To delete a row, tick the checkbox corresponding to that row, then press on the keyboard's delete button.")
    st.write("You can select multiple rows and press on the keyboard's delete button to delete multiple rows at once.")
    st.write("You can also select all rows by clicking on the checkboxes' column header and pressing on the keyboard's delete button.")
    st.write('Do not forget to click on the "Save changes" button found on the upper right of the table to save your changes on the data.')

with st.expander(":leftwards_arrow_with_hook: Reverting unsaved changes"):
    st.write('To revert unsaved changes, just click on the "Revert unsaved changes" button.')
    st.write('Note that this does not undo the changes that have already been saved to the modules list of the website.')