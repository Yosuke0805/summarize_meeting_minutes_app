''' coding: utf-8 '''
# ------------------------------------------------------------
# Content : Creating a tool for automcatically creating a meeting meniute using gpt-api
# Author : Yosuke Kawazoe
# Data Updated：
# Update Details：
# ------------------------------------------------------------

# Import
import os
import streamlit as st
import traceback
import tempfile
# Used to securely store your API key
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# Config
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# ------------------------------------------------------------
# ★★★★★★  main part ★★★★★★
# ------------------------------------------------------------
def main():

    try:
        # Set the title and description
        st.title("Creating Meeting Minutes from Audio")

        # set Gemini API
        GOOGLE_API_KEY = st.sidebar.text_input("Input your Google AI Studio API", type="password")

        genai.configure(api_key=GOOGLE_API_KEY)

        # File uploader widget
        uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3", "ogg", "m4a"])

        # wait until file is uploaded
        if uploaded_file:
            if uploaded_file is not None:
                st.subheader('Uploaded file detail')
                file_details = {'FileName': uploaded_file.name, 'FileType': uploaded_file.type, 'FileSize': uploaded_file.size}
                st.write(file_details)
            else:
                st.error("There is no uploaded file!!", icon="🚨")

        with st.form("summary_form", clear_on_submit=False):
            submitted = st.form_submit_button('Start creating summary')

            if submitted:
                # save uploaded audio file as tmp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_file:
                    temp_file.write(uploaded_file.read())
                    temp_file_path = temp_file.name
                    # print('temp path:', temp_file_path)
                    # print('temp file type:',type(temp_file_path))

                try:
                    summary, transcription = summarize_from_audio_file(temp_file_path)
                    # Deleting tmp file
                    os.remove(temp_file_path)
                    # Display the summary
                    st.title("Summary:")
                    st.markdown(summary)
                    st.markdown(f"## Meeting minutes \n {transcription}")
                except ResourceExhausted as e:
                    st.error("Resource Exhausted: The request exceeded the available resources. Please try again later.", icon="🚨")
                    st.error(f"Details: {str(e)}")
                except Exception as e:
                    st.error("An unexpected error occurred.", icon="🚨")
                    st.error(f"Details: {str(e)}")
                    traceback.print_exc()
    except Exception:
        traceback.print_exc()


# ------------------------------------------------------------
# ★★★★★★  functions ★★★★★★
# ------------------------------------------------------------
def transcribe_audio_file(audio_file):
    # upload audio file by using File API
    audio_file = genai.upload_file(audio_file)
    prompt =  """
  You are a professional transcriber.
  I would you like to transcrbe this file which recoreded a meeting by following format as a markdown.

  ### caution
  - If a spaker change, please intend next sentece.
  - There are several topic can be discussed. If a topic change, please write topic before next sentese.

  ### format example
  ## topic1
  Today, we are going to talk about...

  ## topic2
  Moving on to next topic, ...

  """
    response = model.generate_content(
        [
            prompt,
            audio_file
        ]
    )
    transcription = response.text

    return transcription

def summary_prompt_response(transcription):
    chat = model.start_chat(enable_automatic_function_calling=True)
    prompt = f"""
    ### request
    Based on the meeting minutes below, please do the two things and return as markdown by following format:
    1. Create a bulleted summary for the minutes. The summary should include important points.
    2. Create a TODO list. If there are none, do not create a TODO list.

    ### format example
    ## Meeting summary
　　・
    ## TO-DO list
　　・
　　
    ### meeting menutes
    {transcription}
    """
    response = chat.send_message(prompt)
    summary = response.text

    return summary

def summarize_from_audio_file(audio_file):
  transcription = transcribe_audio_file(audio_file)
  summary = summary_prompt_response(transcription)

  return summary, transcription


# ------------------------------------------------------------
# ★★★★★★  execution part  ★★★★★★
# ------------------------------------------------------------
if __name__ == '__main__':

    # execute
    main()
