import streamlit as st
import requests
import json
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")
from streamlit_extras.switch_page_button import switch_page


FASTAPI_SERVER_URL = st.secrets['FASTAPI_SERVER_URL']


st.set_page_config(page_title='Q&A : Home', page_icon='🍥', initial_sidebar_state='collapsed')

# st.write(FASTAPI_SERVER_URL)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state.messages = []
    st.session_state['access_token'] = ''
    st.session_state['email'] = ''
    st.session_state['start_chatbot'] = False
    st.session_state['get_forms_api_called'] = False
    st.session_state['chatbot_section'] = False

if st.session_state['logged_in'] == False:
    switch_page('Login')
else:
    switch_page('Chatbot')




