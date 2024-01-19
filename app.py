import streamlit as st
from github import Github
import openai
import time
import logging
import os
from embedding_docs import process_document
from openai import OpenAI
client = OpenAI()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize OpenAI and GitHub clients with your tokens
g = Github(st.secrets["GITHUB_TOKEN"])
openai.api_key = st.secrets["OPENAI_API_KEY"]

repo_name = "OAT_Policies"

def upload_file_to_github(repo_name, file_path, file_content, commit_message):
    repo = g.get_user().get_repo(repo_name)
    try:
        # Before calling repo.create_file or repo.update_file
        if not isinstance(file_content, str):
            file_content = str(file_content)

        contents = repo.get_contents(file_path)
        # Log the type of file_content for debugging
        logging.debug(f"Type of file_content: {type(file_content)}")
        repo.update_file(contents.path, commit_message, file_content, contents.sha)
        st.success(f'File "{file_path}" updated successfully!')
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if getattr(e, 'status', None) == 404:  # File not found
            # Ensure file_content is a string
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8')

            repo.create_file(file_path, commit_message, file_content)
            st.success(f'File "{file_path}" created successfully!')
        else:
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
st.markdown('## Upload your policy documents here:')

# At the beginning of your Streamlit app, after initializing Streamlit
footer_tokens_per_sec = st.empty()
footer_tokens = st.empty()
footer_run_time = st.empty()

# Initialize metrics
start_time = None
total_tokens = 0

# Reserve space for the metrics at the bottom of the app
footer_placeholder = st.empty()
# Streamlit file uploader
uploaded_files = st.file_uploader("Upload Documents", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)

# Process each uploaded file and upload the text content to GitHub
if uploaded_files:
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

st.title('Search Documents')
search_query = st.text_input('Enter your search query:')



if search_query:
    # Fetch all file contents from the repo
    all_file_contents = get_all_file_contents_from_repo(repo_name)

    try:
        search_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            temperature=0.5,
            stream = True,
            messages=[
                {"role": "system", "content": """You are a UK based professional analyst called OAT Docs Analyser assistant.
                You always respond using UK spelling and grammar. 
                 You must say if the information does not have enough detail, you must NOT make up facts or lie. 
                 At the end of any response, you must always source every single document source information you used in your response, 
                 each document source will be given in the format **Document Source: (insert content filename here)**. 
                 You must always answer the user's questions using all the information in documents given:""" + all_file_contents},
                {"role": "user", "content": search_query}
            ]
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

                footer_tokens_per_sec.markdown(f"Tokens / sec: {tokens_per_sec:.2f}")
                footer_tokens.markdown(f"Tokens: {total_tokens}")
                footer_run_time.markdown(f"Run time: {run_time:.2f}")

    except Exception as e:
        st.error(f"An error occurred: {e}")

with footer_placeholder.container():
    st.markdown("---")  # Optional: insert a horizontal line for visual separation
    st.markdown(f"Tokens / sec: {tokens_per_sec:.2f}")
    st.markdown(f"Tokens: {total_tokens}")
    st.markdown(f"Run time: {run_time:.2f}")