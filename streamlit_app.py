from openai import OpenAI
import os
import streamlit as st

import PyPDF2

def process_file(upload_file):
    #st.sidebar.image(upload_file)
    #return
    pdfReader = PyPDF2.PdfReader(uploaded_file)
    count = len(pdfReader.pages)
    text=""
    for i in range(count):
        page = pdfReader.pages[i]
        text=text+page.extract_text()
    # Save text to file
    #with open('data/pdf_file.txt','w') as f:
    #    f.write(text)
    #f.close()
    with st.sidebar.expander("File contents"):
        st.write(text)
    return text


OPENAI_MODEL_NAME=st.secrets['OPENAI_MODEL_NAME']
OPENAI_API_KEY=st.secrets['OPENAI_API_KEY']

avatars={"system":"💻🧠","user":"🧑‍💼","assistant":"🎓"}
client=OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_MESSAGE={"role": "system", 
                "content": "Ignore all previous commands. You are a helpful and patient guide based in Silicon Valley."
                }

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(SYSTEM_MESSAGE)

st.title("Chat Bot")

for message in st.session_state.messages:
    if message["role"] != "system":
        avatar=avatars[message["role"]]
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

prompt=st.chat_input("Say something, or upload a PDF", accept_file=True,
                     file_type=["pdf","jpg","jpeg","png"])

if prompt and prompt["files"]:
    uploaded_file=prompt["files"][0]
    process_file(uploaded_file)

if prompt and prompt.text:
    print("Inside CHAT")
    st.session_state.messages.append({"role": "user", "content": prompt.text})
    with st.chat_message("user"):
        st.markdown(prompt.text)
    with st.chat_message("assistant", avatar=avatars["assistant"]):
        print("Inside WITH loop")
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[{"role": m["role"], "content": m["content"]}
                      for m in st.session_state.messages], stream=True):
            delta_response=response.choices[0].delta
            #print(f"Basic CHat Delta response: {delta_response}")
            if delta_response.content:
                full_response += delta_response.content
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
