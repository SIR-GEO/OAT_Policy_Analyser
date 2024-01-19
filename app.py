# main.py
import streamlit as st
from github import Github
from langchain_openai import ChatOpenAI
from embedding_docs import process_documents
import tempfile
import shutil
import os

# Initialize GitHub client with your token
g = Github(st.secrets["GITHUB_TOKEN"])
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Set OpenAI LLM with the API key
llm_chat = ChatOpenAI(temperature=0.9, model='gpt-4-1106-preview', client=OPENAI_API_KEY)

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

def get_file_from_github(repo_name, file_path):
    repo = g.get_user().get_repo(repo_name)
    contents = repo.get_contents(file_path)
    return contents.decoded_content.decode("utf-8")

# Set up the Streamlit interface
st.title('OAT Policy Analyser')
st.markdown('Upload your policy documents here:')

# Streamlit file uploader
uploaded_files = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)

# Process each uploaded file
if uploaded_files:
    repo_name = "OAT_Policies"  
    with tempfile.TemporaryDirectory() as temp_dir:
        document_paths = []
        for uploaded_file in uploaded_files:
            # Save the uploaded file to a temporary directory
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            document_paths.append(temp_file_path)

        # Process documents
        documents_content = process_documents(document_paths)

        # Upload processed content to GitHub
        for document_path, file_content in documents_content.items():
            file_name = os.path.basename(document_path)
            # Ensure the file content is a string
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8')
            upload_file_to_github(repo_name, file_name, file_content, "Upload new file")