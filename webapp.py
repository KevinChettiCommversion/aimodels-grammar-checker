import streamlit as st
import requests
st.title("Commversion's Grammar Checker Tool")

text = st.text_input("Enter the text: ")

responseFromAIApp = requests.post("http://localhost:9092/grammar_check",
                                      json={"text_message": text,})
responseCode = responseFromAIApp.status_code

response = responseFromAIApp.json()
print(responseFromAIApp.json())
print(response["display_message"])

st.write(response["display_message"])
if response["status"] == 201:
    st.write("This is what the AI model recommends: ",response["output"])