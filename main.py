# main.py
import streamlit as st
import os
from embedding_docs import process_documents, ensure_pinecone_index
from github import Github

# Initialize GitHub client with your token
g = Github("your_github_token")

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]



# Set up the Streamlit interface
st.title('Document Embedding and Indexing')
st.markdown('Drag and drop your files here to index them in the Pinecone database.')

# Ensure Pinecone index exists before processing files
ensure_pinecone_index()
def streamlit_update(message):
    st.write(message)  # This will display the message on the Streamlit page

# File uploader allows user to add their own PDF
# main.py
uploaded_files = st.file_uploader("Upload PDF, DOCX, TXT files. Use this link to chat with those documents: https://oat-policy-analyser.streamlit.app/", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)

if uploaded_files:
    # Save the PDFs to temporary files and collect their paths
    pdf_paths = []
    for uploaded_file in uploaded_files:
        # To read file as bytes:
        bytes_data = uploaded_file.read()
        # Save the PDF to a temporary file
        temp_pdf_path = f'temp_{uploaded_file.name}'
        with open(temp_pdf_path, "wb") as f:
            f.write(bytes_data)
        pdf_paths.append(temp_pdf_path)

    # Process the PDFs and upload to Pinecone
    process_documents(pdf_paths, update_callback=streamlit_update)  # Pass the update function

    # Clean up the temporary files
    for temp_pdf_path in pdf_paths:
        os.remove(temp_pdf_path)

    st.success('All files have been processed and indexed!')


def upload_file_to_github(repo_name, file_path, file_content, commit_message):
    repo = g.get_user().get_repo(repo_name)
    repo.create_file(file_path, commit_message, file_content)

def get_file_from_github(repo_name, file_path):
    repo = g.get_user().get_repo(repo_name)
    contents = repo.get_contents(file_path)
    return contents.decoded_content.decode("utf-8")
# Run the Streamlit app with `streamlit run main.py`