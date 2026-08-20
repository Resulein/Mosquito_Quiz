import streamlit as st
import time

st.set_page_config(
    page_title="Test",
    layout="centered"
)

if "page" not in st.session_state:
    st.session_state.page = "start"


if st.session_state.page == "start":

    st.title("START PAGE")

    st.write("This is the start page.")

    if st.button("START QUIZ"):

        st.session_state.page = "quiz"

        st.rerun()


elif st.session_state.page == "quiz":

    st.title("QUIZ PAGE")

    st.write("THIS IS THE QUIZ PAGE.")

    st.write("There should be absolutely nothing from the start page above.")


st.write("---")
st.write("CURRENT STATE:", st.session_state.page)
