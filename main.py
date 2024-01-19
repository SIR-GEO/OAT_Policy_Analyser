# main.py
import streamlit as st
import pinecone
import os
from embedding_docs import process_documents, ensure_pinecone_index


OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
PINECONE_API_ENVIRONMENT = st.secrets["PINECONE_API_ENVIRONMENT"]
PINECONE_INDEX_NAME = st.secrets["PINECONE_INDEX_NAME"]

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENVIRONMENT)


# Set up the Streamlit interface
st.title('Document Embedding and Indexing')
st.markdown('Drag and drop your files here to index them in the Pinecone database.')

# Ensure Pinecone index exists before processing files
ensure_pinecone_index()

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
    process_documents(pdf_paths)  # Call the function with the list of file paths

    # Clean up the temporary files
    for temp_pdf_path in pdf_paths:
        os.remove(temp_pdf_path)

    st.success('All files have been processed and indexed!')

# Run the Streamlit app with `streamlit run main.py`