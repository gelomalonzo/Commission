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
st.header("Modules List")
modules_df = pd.read_csv(st.secrets["paths"]["MODULES_DB"])

row1 = st.container()
row2 = st.container()
row3 = st.container()
row4 = st.container()

with row3:
    modules_df = st.data_editor(modules_df, num_rows="dynamic", use_container_width=True)

with row2:
    col1, col2 = st.columns((2, 0.5))
    with col1:
        st.write("Listed below are the modules and their corresponding module fee. Scroll through the bottom of the page for instructions.")
            
    with col2:
        if st.button("Save changes"):
            modules_df.to_csv("./assets/references/Modules.csv", index=False)
            with row1:
                st.success("Changes saved successfully.")

with row4:
    st.write("---")
    st.subheader("Instructions")
    
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