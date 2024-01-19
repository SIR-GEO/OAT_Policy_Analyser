import streamlit as st
from github import Github
import openai
import time
import logging
import os
from embedding_docs import process_document
from streamlit.components.v1 import html
from datetime import datetime
from openai import OpenAI
client = OpenAI()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize OpenAI and GitHub clients with your tokens
g = Github(st.secrets["GITHUB_TOKEN"])
openai.api_key = st.secrets["OPENAI_API_KEY"]

repo_name = "OAT_Policies"

def get_current_date_and_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Returns date and time in 'YYYY-MM-DD HH:MM:SS' format


def upload_file_to_github(repo_name, file_path, file_content, commit_message):
    repo = g.get_user().get_repo(repo_name)
    try:
        # Check if the file already exists
        contents = repo.get_contents("")
        existing_files = [content_file.name for content_file in contents if content_file.type == "file"]
        
        if file_path in existing_files:
            st.warning(f'File "{file_path}" already exists. No action taken to avoid duplication.')
            return  # Skip the upload to prevent duplication

        # Convert file_content to string if necessary
        if not isinstance(file_content, str):
            file_content = str(file_content)

        # Since the file does not exist, create it
        repo.create_file(file_path, commit_message, file_content)
        st.success(f'File "{file_path}" created successfully!')
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        st.error(f'An error occurred while uploading the file "{file_path}".')
        raise e

def get_all_file_contents_from_repo(repo_name):
    repo = g.get_user().get_repo(repo_name)
    contents = repo.get_contents("")
    all_file_contents = []
    for content_file in contents:
        if content_file.type == "file":
            file_content = repo.get_contents(content_file.path).decoded_content.decode().strip()
            # Include the filename as metadata
            document_with_metadata = f"### Document Source: {content_file.name}\n{file_content}\n"
            all_file_contents.append(document_with_metadata)
    return "\n".join(all_file_contents)

# Set up the Streamlit interface
st.title('OAT Policy Analyser')
st.markdown('Upload your policy documents here:')

# Initialize metrics
start_time = None
total_tokens = 0
tokens_per_sec = 0
footer_tokens_per_sec = 0  # Initialize tokens_per_sec here
run_time = 0  # Initialize run_time here



footer_placeholder = st.empty()
# Streamlit file uploader
uploaded_files = st.file_uploader("Upload Documents", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)

# Button to trigger the file processing
if st.button('Process and Upload Files'):
    if uploaded_files:
         # Store the current time in session state when the files are uploaded
        st.session_state.upload_time = time.time()

        for uploaded_file in uploaded_files:
            # Read the file content into memory
            file_content = uploaded_file.read()

            # Check the file extension and process accordingly
            _, file_extension = os.path.splitext(uploaded_file.name)
            if file_extension.lower() == '.txt':
                # For .txt files, upload the content directly
                text_file_name = uploaded_file.name
                upload_file_to_github(repo_name, text_file_name, file_content.decode('utf-8'), "Upload .txt file")
            else:
                # For other file types, convert to text and then upload
                text_content = process_document(uploaded_file.name, file_content)
                if text_content:
                    # Create a text file name by replacing the original extension with .txt
                    text_file_name = os.path.splitext(uploaded_file.name)[0] + '.txt'
                    upload_file_to_github(repo_name, text_file_name, text_content, "Upload processed text file")
                else:
                    st.error(f'Failed to process the file: {uploaded_file.name}')

        # Clear the file uploader widget after processing
        uploaded_files = None
# Check if 'upload_time' is set in session_state and 4 seconds have passed
if 'upload_time' in st.session_state and time.time() - st.session_state.upload_time > 4:
    # Clear the uploaded files after 4 seconds
    uploaded_files = None
    # Remove 'upload_time' from session_state
    del st.session_state.upload_time
    # Rerun the app to clear the file uploader widget
    st.experimental_rerun()


# Initialize a list to hold the conversation history
conversation_history = []

st.title('Search Documents')
search_query = st.text_input('Enter your search query:')

# Reserve space for the metrics at the bottom of the app
footer_tokens_per_sec = st.empty()
footer_tokens = st.empty()
footer_run_time = st.empty()

current_date_and_time = get_current_date_and_time()

if search_query:
    # Fetch all file contents from the repo
    all_file_contents = get_all_file_contents_from_repo(repo_name)

    # Start time when the search begins
    start_time = time.time()

    try:
        
        # Add the user's question to the conversation history
        conversation_history.append({"role": "user", "content": search_query})

        # If this is the first question, include the system message
        if len(conversation_history) == 1:
            messages=[
                {"role": "system", "content": """You are a UK based professional analyst called OAT Docs Analyser assistant.
                You always respond using UK spelling and grammar. You will be given extensive details on OAT Policies and 
                OAT documents and will be able to cross-reference entire contents or analyse specific sections in order to answer any question given.
                You must say if the information does not have enough detail, you must NOT make up facts or lie. 
                At the end of any response, you must always source every single document source information you used in your response, 
                each document source will be given in the format **Document Source: (insert content filename here)**. 
                You must always answer the user's questions using all the information in documents given:""" + all_file_contents + "Today's date and time will given next, use that information to relate contextually relevant user questions " + current_date_and_time},
                {"role": "user", "content": search_query}
            ] + conversation_history  # Include the conversation history in the messages
        else:
            # If this is a follow-up question, only include the conversation history
            messages = conversation_history

        # Separate AI API call for handling user follow up questions, reduces massive user of tokens.
        search_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            temperature=0.5,
            stream = True,
            messages= ["You must answer the query:" + search_query + "using the information provided in a previous question and answer:" + messages]
        )

        # Placeholder for streaming responses
        response_placeholder = st.empty()

        # Initialize an empty string to hold the response
        full_response = ""

        # Start time when the search begins
        start_time = time.time()

        # Iterate over the stream and update the placeholder
        for chunk in search_response:
            if chunk.choices[0].delta.content is not None:

                # Append new content to the full response
                full_response += chunk.choices[0].delta.content

                # Update the placeholder with the full response so far
                response_placeholder.write(full_response)

                # Calculate and update tokens and run time
                total_tokens += len(chunk.choices[0].delta.content.split())
                run_time = time.time() - start_time
                tokens_per_sec = total_tokens / run_time if run_time > 0 else 0

        # Add the model's response to the conversation history
        conversation_history.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"An error occurred: {e}")



# At the end of Streamlit app, custom css to display the footer stuff
def render_footer(tokens_per_sec, total_tokens, run_time, predicted_cost):
    footer_html = f"""
    <style>
    .reportview-container .main footer {{
        display: none;
    }}
    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #111;
        color: white;
        text-align: center;
        padding: 10px;
        z-index: 9999;
    }}
    </style>
    <footer class="footer">
        <span>Tokens / sec: {tokens_per_sec:.2f}</span>
        <span style="margin-left: 30px;">Tokens: {total_tokens}</span>
        <span style="margin-left: 30px;">Run time: {run_time:.2f} seconds</span>
        <span style="margin-left: 30px;">Predicted cost: ${predicted_cost:.6f}</span>
    </footer>
    """
    st.markdown(footer_html, unsafe_allow_html=True)
    # Use the `html` function to render the custom HTML for the sticky footer
    st.components.v1.html(footer_html, height=0, scrolling=False)

# Ensure that the footer is rendered after all other components
if __name__ == "__main__":
    # ... (rest of your Streamlit app logic) ...

    # Calculate the predicted cost
    input_cost_per_token = 0.01 / 1000  # Cost per token for input
    output_cost_per_token = 0.03 / 1000  # Cost per token for output
    predicted_cost = (total_tokens * (input_cost_per_token + output_cost_per_token))

    # Call the function to render the footer with the updated metrics
    render_footer(tokens_per_sec, total_tokens, run_time, predicted_cost)