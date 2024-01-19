# main.py
import streamlit as st
from github import Github
from langchain_openai import ChatOpenAI
from embedding_docs import process_documents

# Initialize GitHub client with your token
g = Github(st.secrets["GITHUB_TOKEN"])
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Set OpenAI LLM with the API key
llm_chat = ChatOpenAI(temperature=0.9, model='gpt-4-1106-preview', client=OPENAI_API_KEY)

def upload_file_to_github(repo_name, file_path, file_content, commit_message):
    repo = g.get_user().get_repo(repo_name)
    try:
        # This will try to update the file if it already exists
        contents = repo.get_contents(file_path)
        repo.update_file(contents.path, commit_message, file_content, contents.sha)
        st.success('File updated successfully!')
    except Exception as e:
        # If the file does not exist, it will create a new one
        if e.status == 404:  # File not found
            repo.create_file(file_path, commit_message, file_content)
            st.success('File created successfully!')
        else:
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
    repo_name = "OAT_Policy_Analyser"  # Replace with your actual GitHub repository name
    document_paths = [uploaded_file.name for uploaded_file in uploaded_files]
    documents_content = process_documents(document_paths)
    
    for uploaded_file in uploaded_files:
        # Get the content from the processed documents
        file_content = documents_content[uploaded_file.name]
        # Call the function to upload the file to GitHub
        upload_file_to_github(repo_name, uploaded_file.name, file_content, "Upload new file")