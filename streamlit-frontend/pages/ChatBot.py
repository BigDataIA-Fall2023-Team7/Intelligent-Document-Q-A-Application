import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import requests
import json
import time

FASTAPI_SERVER_URL = st.secrets['FASTAPI_SERVER_URL']
st.set_page_config(page_title='ChatBoT', page_icon='🍥', initial_sidebar_state='collapsed')
# print(st.session_state)

def trigger_chatbot():
    st.session_state['start_chatbot'] = True

def logout():
    for key in st.session_state.keys():
        del st.session_state[key]
    switch_page('Login')

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state.messages = []
    st.session_state['access_token'] = ''
    st.session_state['email'] = ''
    st.session_state['start_chatbot'] = False
    st.session_state['get_forms_api_called'] = False
    st.session_state['chatbot_section'] = False


if st.session_state['logged_in']== False:
    switch_page('Login')
else:
    st.title("Q&A ChatBoT")
    # if st.session_state['chatbot_section'] == False:
    get_forms_api = f"{FASTAPI_SERVER_URL}/pineconeForms"
    if st.session_state['get_forms_api_called'] == False:
        st.session_state['start_chatbot'] = False
        try:
            response = requests.get(get_forms_api,headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
            st.session_state['get_forms_api_called'] = True
        except:
            st.error("Service is unavailable at the moment !!")
            st.error("Please try again later")
            st.stop()
        if response.status_code == 401:
            st.session_state['logged_in']== False
            st.stop()
        elif response.status_code == 200:
            st.session_state["api_response"]=response
    if st.session_state['get_forms_api_called'] == True:
        forms_list = []
        response = st.session_state["api_response"]
        for row in json.loads(response.text):
            forms_list.append(row['form_name'])

        options = st.multiselect('Filter by form name (Optional) :', forms_list, placeholder="All available forms")

        col1,col2,col3,col4 = st.columns([1.5,2,2,5])

        with col1:
            st.button("Save", on_click=trigger_chatbot)


        with col2:    
    # register_button = st.button("Create New", on_click=onClickNewAccount, type="primary")
            st.button("Log Out!", type="primary", on_click=logout)    

        if st.session_state['start_chatbot'] :
            st.session_state['chatbot_section'] = True
            st.session_state['form_titles'] = forms_list if options == [] else options
            st.session_state['display_forms'] = ['all'] if options == [] else options 


    
    if st.session_state['chatbot_section'] == True:
        st.subheader("Chat")

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        
        
        # Accept user input
        if prompt := st.chat_input("Ask question here"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt + str(st.session_state['display_forms'])})
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt + str(st.session_state['display_forms']))
                

                # Display assistant response in chat message container
            with st.chat_message("assistant"):
                with st.spinner("loading.."):
                    get_answer_api = f"{FASTAPI_SERVER_URL}/askQuestion"
                    data = {
                        "question": prompt,
                        "form_titles": st.session_state['form_titles']
                    }
                    try:
                        answer = requests.post(get_answer_api,data=data, headers={'Authorization' : f"Bearer {st.session_state['access_token']}"})
                    except:
                        st.error("Service is unavailable at the moment !!")
                        st.error("Please try again later")
                        st.stop()
                    if answer.status_code == 401:
                        st.session_state['logged_in']== False
                        st.stop()
                    elif answer.status_code == 200:
                        st.session_state["api_answer"]=answer

                    res = json.loads(answer.text)
                    system_response =res['system_answer']

                message_placeholder = st.empty()
                full_response = ""
                # Simulate stream of response with milliseconds delay
                for chunk in system_response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})


        back = st.button("Close Chat")
        if back:
            st.session_state['chatbot_section'] = False
            st.session_state['start_chatbot'] = False




    



    
    



