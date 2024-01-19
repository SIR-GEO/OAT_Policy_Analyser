# app.py
import streamlit as st
from github import Github
import openai
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
        contents = repo.get_contents(file_path)
        repo.update_file(contents.path, commit_message, file_content, contents.sha)
        st.success('File updated successfully!')
    except Exception as e:
        if getattr(e, 'status', None) == 404:  # File not found
            repo.create_file(file_path, commit_message, file_content)
            st.success('File created successfully!')
        else:
            st.error('An error occurred while uploading the file.')
            raise e

def get_all_file_contents_from_repo(repo_name):
    repo = g.get_user().get_repo(repo_name)
    contents = repo.get_contents("")
    all_file_contents = []
    for content_file in contents:
        if content_file.type == "file":
            file_content = repo.get_contents(content_file.path).decoded_content.decode().strip()
            all_file_contents.append(file_content)
    return "\n".join(all_file_contents)

# Set up the Streamlit interface
st.title('OAT Policy Analyser')
st.markdown('Upload your policy documents here:')

# Streamlit file uploader
uploaded_files = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)

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

st.markdown('## Search Documents')
search_query = st.text_input("Enter your search query:")



if search_query:
    # Fetch all file contents from the repo
    all_file_contents = get_all_file_contents_from_repo(repo_name)

    try:
        search_response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": "You are a professional analyst called OAT Docs Analyser assistant. You must say if the information does not have enough detail, you must NOT make up facts or lie. You always answer the user's questions using the context given:" + all_file_contents},
                {"role": "user", "content": search_query}
            ]
        )
        
        if search_response.choices:
            # Assuming that the 'content' attribute exists within the 'message' object
            response_content = search_response.choices[0].message.content  # Direct attribute access
            st.write(response_content)
        else:
            st.error("No response received from the model.")
    except Exception as e:
        st.error(f"An error occurred: {e}")