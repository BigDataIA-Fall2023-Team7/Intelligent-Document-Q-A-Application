import streamlit as st
import requests
import time
from streamlit_extras.switch_page_button import switch_page
import re

st.set_page_config(page_title='New User', page_icon='🍥', initial_sidebar_state='collapsed')

FASTAPI_SERVER_URL = st.secrets['FASTAPI_SERVER_URL']

# st.write(FASTAPI_SERVER_URL)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['login_page'] = False
    st.session_state['access_token'] = ''
    st.session_state['email'] = ''

st.title("Q&A ChatBot")
st.header("Create New User")

email = st.text_input("Email",key= 'email')
password = st.text_input("Password", type="password")
confirm_password = st.text_input("Confirm Password", type="password")


buf1,col,buf2 = st.columns([3,2,3])
with col:
    create_button = st.button("Register", type="primary")

if create_button:
        regExEmail = r'.+@.+\.(com)$'
        regExPassword = r'^(?=.*[!@#$%^&*])\S{5,}$'
        email_match = re.match(regExEmail, email)
        password_match = re.match(regExPassword, password)
        if email == "" and password == "":
            st.warning("Please enter email and password")
        elif email == "":
            st.warning("Please enter email")
        elif not email_match:
            st.warning("Please enter valid email")
        elif password == "":
            st.warning("Please enter password")
        elif not password_match:
            st.warning("Enter Valid Password (Minimum length 5 and must have at least 1 special character)!")
        elif confirm_password == "":
            st.warning("Please enter confirm password")
        elif password != confirm_password:
            st.warning("Passwords does not match")
        else:
            with st.spinner("Wait for it..."):
                create_user_api = f"{FASTAPI_SERVER_URL}/register"
                user_info = {"user_email":email, "user_password":password}
                try:
                    create_user_response = requests.post(create_user_api, json = user_info)
                except Exception as e:
                    print(e)
                    st.error("Service is unavailable at the moment !!")
                    st.error("Please try again later")
                    st.stop()
            if create_user_response.status_code == 200:
                st.toast("User Created")
                switch_page('Login')
            elif create_user_response.status_code == 422:
                st.error("")
            elif create_user_response.status_code == 400:
                st.error("User already registered")
            else:
                st.error(create_user_response.text)

buf1,col,buf2 = st.columns([2,2,2])
with col:
    if st.button('Go back to Login'):
        switch_page('Login')
