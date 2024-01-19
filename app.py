import streamlit as st
from github import Github
from langchain_openai import ChatOpenAI
from embedding_docs import process_documents, process_pdf, process_docx, process_txt
from PyPDF2 import PdfReader
from docx import Document
import tempfile
import os
import openai
from openai import OpenAI
import logging


# Set up logging
logging.basicConfig(level=logging.DEBUG)

client = OpenAI()

repo_name = "OAT_Policies"

# Initialise GitHub client with your token
g = Github(st.secrets["GITHUB_TOKEN"])
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]



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

# Process each uploaded file and upload the text content to GitHub
if uploaded_files:
    repo_name = "OAT_Policies"  
    with tempfile.TemporaryDirectory() as temp_dir:
        for uploaded_file in uploaded_files:
            # Save the uploaded file to a temporary directory
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            # Convert the file to text
            text_content = convert_to_text(uploaded_file.getbuffer(), uploaded_file.name)

            # Create a text file name by replacing the original extension with .txt
            text_file_name = os.path.splitext(uploaded_file.name)[0] + '.txt'

            # Upload text content to GitHub
            if text_content:
                upload_file_to_github(repo_name, text_file_name, text_content, "Upload processed text file")
            else:
                st.error(f'Failed to process the file: {uploaded_file.name}')


# Function to fetch all file contents from the GitHub repo
def get_all_file_contents_from_repo(repo_name):
    repo = g.get_user().get_repo(repo_name)
    contents = repo.get_contents("")
    all_file_contents = ""
    for content_file in contents:
        print(f"Found file in repo: {content_file.path}")  # Debug print
        if content_file.path.endswith(('.pdf', '.docx')):
            file_content = repo.get_contents(content_file.path).decoded_content
            text_content = convert_to_text(file_content, content_file.path)
            if text_content is not None:
                all_file_contents += text_content + "\n\n"
    return all_file_contents



def convert_to_text(file_buffer, file_name):
    _, file_extension = os.path.splitext(file_name)
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(file_buffer)
        tmp_file_path = tmp_file.name
        logging.debug(f"Temporary file created at {tmp_file_path}")

    if not os.path.exists(tmp_file_path):
        logging.error(f"Temporary file {tmp_file_path} does not exist.")
        raise FileNotFoundError(f"The temporary file {tmp_file_path} was not found.")

    try:
        if file_extension.lower() == '.pdf':
            return process_pdf(tmp_file_path)
        elif file_extension.lower() == '.docx':
            logging.debug(f"Processing DOCX file at {tmp_file_path}")
            content = process_docx(tmp_file_path)
            logging.debug(f"DOCX file processed. Content length: {len(content)}")
            return content
        elif file_extension.lower() == '.txt':
            with open(tmp_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    finally:
        # Clean up the temporary file after processing
        os.remove(tmp_file_path)
        logging.debug(f"Temporary file {tmp_file_path} deleted.")




st.markdown('## Search Documents')
search_query = st.text_input("Enter your search query:")


if search_query:
    # Fetch all file contents from the repo
    all_file_contents = get_all_file_contents_from_repo(repo_name)

        # Print the all_file_contents for debugging purposes
    print("All file contents:", all_file_contents)  # Debug print
  
    try:
        search_response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            stream = False,
            messages=[
                {"role": "system", "content": "You are a professional analysis called OAT Docs Analyser assistant. You must say if you the information does not have enough detail, you must not make up facts or lie. You always answer the user's answers using the context given:" + all_file_contents},
                {"role": "user", "content": search_query}
            ]
        )
        
        if search_response.choices:
            response_content = search_response.choices[0].message.content  # Access using dot notation
            st.text_area("Search Results:", value=response_content, height=200, disabled=True)
        else:
            st.error("No response received from the model.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
