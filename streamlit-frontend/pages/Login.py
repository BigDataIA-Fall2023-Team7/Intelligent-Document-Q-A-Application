import streamlit as st
import requests
import json
import time
from streamlit_extras.switch_page_button import switch_page


FASTAPI_SERVER_URL = st.secrets['FASTAPI_SERVER_URL']

st.set_page_config(page_title='Login', page_icon='🍥', initial_sidebar_state='collapsed')

# st.write(FASTAPI_SERVER_URL)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state.messages = []
    st.session_state['access_token'] = ''
    st.session_state['email'] = ''
    st.session_state['start_chatbot'] = False
    st.session_state['get_forms_api_called'] = False
    st.session_state['chatbot_section'] = False


st.title("Q&A ChatBot")
st.header("Login Page")

email = st.text_input("Email",key= 'email')
password = st.text_input("Password", type="password")

col1,col2,col3,col4 = st.columns([1.5,2,2,5])

with col1:
    login_button = st.button('Log In')

with col2:    
    # register_button = st.button("Create New", on_click=onClickNewAccount, type="primary")
    register_button = st.button("Create New", type="primary")

if login_button:
    if email == "" and password == "":
        st.warning("Please enter email and password")
    elif email == "":
        st.warning("Please enter email")
    elif password == "":
        st.warning("Please enter password")
    else:
        with st.spinner("Wait for it..."):
            login_user_api = f"{FASTAPI_SERVER_URL}/login"
            # user_info = ('{"email":"%s", "password":"%s"}'%(str(username),str(password)))
            user_info = {"username":email, "password":password}
            try:
                create_user_response = requests.post(login_user_api,
                                                     headers={'Content-Type': 'application/x-www-form-urlencoded', 'accept': 'application/json'},
                                                     data = user_info)
            except:
                st.error("Service is unavailable at the moment !!")
                st.error("Please try again later")
                st.stop()
            # st.write(create_user_response)
        if create_user_response.status_code == 200:
            st.toast("Login Successful")
            with st.spinner("Initiating ChatBot..."):
                # if "messages" not in st.session_state:

                response_data = json.loads(create_user_response.text)
                st.session_state['access_token'] = response_data['access_token']
                st.session_state['logged_in'] = True
                st.session_state.messages = []
                get_history_api = f"{FASTAPI_SERVER_URL}/chatAnswer"
                try:
                    response = requests.get(get_history_api,headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                    st.session_state['get_history_api'] = True
                except:
                    st.error("Service is unavailable at the moment !!")
                    st.error("Please try again later")
                    st.stop()
                if response.status_code == 401:
                    st.session_state['logged_in']== False
                    st.stop()
                elif response.status_code == 200:
                    st.session_state["api_response"]=response.text
                    for rows in json.loads(response.text):
                        st.session_state.messages.append({"role": "user", "content": rows["user_question"]})
                        st.session_state.messages.append({"role": "assistant", "content": rows["system_answer"]})
                    
                    # st.write(st.session_state.messages)
                time.sleep(1)
            switch_page('ChatBot')
        elif create_user_response.status_code == 401:
            st.warning("Login failed. Please enter valid email and password")
        elif create_user_response.status_code == 422: 
            st.write(create_user_response.text)
        else:
            st.warning("Something went wrong")
            print(create_user_response.text)
if register_button:
    st.session_state['login_page'] = False
    with st.spinner("Loading...."):
        switch_page('registration')



        

