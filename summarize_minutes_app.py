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
# Used to securely store your API key
import google.generativeai as genai

# Config
model = genai.GenerativeModel(model_name="gemini-1.0-pro")

# ------------------------------------------------------------
# ★★★★★★  main part ★★★★★★
# ------------------------------------------------------------
def main():

    try:
        # Set the title and description
        st.title("Creating Meeting Minutes from Audio")
        st.write("Input an audio file and get a summary")

        # set Gemini API
        GOOGLE_API_KEY = st.text_input("Input your Google AI Studio API", type="password")

        genai.configure(api_key=GOOGLE_API_KEY)

        # File uploader widget
        uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3", "ogg", "m4a"])
        print(uploaded_file.name)

        if uploaded_file is not None:
            # Save the uploaded file to a temporary location
            temp_file_path = os.path.join("\tmp", uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            # Call the summarization function
            summary = summarize_from_audio_file(temp_file_path)

            # Display the summary
            st.write("Summary:")
            st.text(summary)
        else:
            print("There is no uploaded file!!")
    except Exception:
        traceback.print_exc()


# ------------------------------------------------------------
# ★★★★★★  functions ★★★★★★
# ------------------------------------------------------------
def transcribe_audio_file(audio_file):
    prompt = "Can you transcribe the following audio file?"
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
    Can you summarize this meeting menutes by following format?

    ### format
    - meeting summary

    - TO-DO list

    ### meeting menutes
    {transcription}
    """
    response = chat.send_message(prompt)
    summary = response.text

    return summary

def summarize_from_audio_file(audio_file):
  transcription = transcribe_audio_file(audio_file)
  summary = summary_prompt_response(transcription)

  return summary


# ------------------------------------------------------------
# ★★★★★★  execution part  ★★★★★★
# ------------------------------------------------------------
if __name__ == '__main__':

    # execute
    main()
