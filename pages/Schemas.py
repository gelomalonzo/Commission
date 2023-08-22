# ===== IMPORTS ===== #
import streamlit as st
import pandas as pd

# ===== PAGE CONFIGURATIONS ===== #
st.set_page_config(
    page_title=st.secrets["env"]["TITLE"],
    page_icon=st.secrets["env"]["LOGO"],
    layout=st.secrets["env"]["LAYOUT"],
    initial_sidebar_state=st.secrets["env"]["SIDEBAR_STATE"]
)
with open(st.secrets["paths"]["INDEX_CSS"]) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
with open(st.secrets["paths"]["MODULES_CSS"]) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ===== GLOBAL VARIABLES ===== #

# ===== PAGE CONTENT ===== #
st.header("Schemas")
st.write("Listed below are the schema tables for retail and enterprise. Scroll through the bottom of the page for instructions.")
st.write("---")
ret_col, mid_col, ent_col = st.columns((1, 0.1, 1))

with ret_col:
    st.subheader("Retail")
    
    row1 = st.container()
    row2 = st.container()
    with row2:
        ret_schema_df = pd.read_csv(st.secrets["paths"]["RSP_SCHEMA_DB"])
        ret_schema_df = st.data_editor(ret_schema_df, num_rows="dynamic", use_container_width=True)
    with row1:
        col1, col2 = st.columns((2, 1))
        with col1:
            st.write("For Salespersons")
        with col2:
            if st.button("Save changes", key="salespersons-schema"):
                ret_schema_df.to_csv(st.secrets["paths"]["RSP_SCHEMA_DB"], index=False)
                with row1:
                    st.success("Changes saved successfully.")
    
    row1 = st.container()
    row2 = st.container()
    with row2:
        ret_schema_df = pd.read_csv(st.secrets["paths"]["RTL_SCHEMA_DB"])
        ret_schema_df = st.data_editor(ret_schema_df, num_rows="dynamic", use_container_width=True)
    with row1:
        col1, col2 = st.columns((2, 1))
        with col1:
            st.write("For Team Leaders")
        with col2:
            if st.button("Save changes", key="team-leaders-schema"):
                ret_schema_df.to_csv(st.secrets["paths"]["RTL_SCHEMA_DB"], index=False)
                with row1:
                    st.success("Changes saved successfully.")

with ent_col:
    st.subheader("Enterprise")

st.write("---")
st.subheader("Instructions")

with st.expander("Editing a row"):
    st.write("To edit a row's details, you can double click on a cell, then type in the updated information for that particular row.")
    st.write('Do not forget to click on the "Save changes" button found on the upper right of the table to save your changes on the data.')

with st.expander("Adding a new row"):
    st.write("To add a new row, scroll through the bottom-most of the table. Click on the empty last row, then type in the new data.")
    st.write("Make sure to fill in all its fields.")
    st.write('Do not forget to click on the "Save changes" button found on the upper right of the table to save your changes on the data.')

with st.expander("Deleting a row"):
    st.write("To delete a row, tick the checkbox corresponding to that row, then press on the keyboard's delete button.")
    st.write("You can select multiple rows and press on the keyboard's delete button to delete multiple rows at once.")
    st.write("You can also select all rows by clicking on the checkboxes' column header and pressing on the keyboard's delete button.")
    st.write('Do not forget to click on the "Save changes" button found on the upper right of the table to save your changes on the data.')