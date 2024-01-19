# embedding_docs.py
import os
import pinecone
import streamlit as st
import tempfile
from langchain_community.document_loaders import UnstructuredPDFLoader, TextLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings


OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
PINECONE_API_ENVIRONMENT = st.secrets["PINECONE_API_ENVIRONMENT"]
PINECONE_INDEX_NAME = st.secrets["PINECONE_INDEX_NAME"]

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENVIRONMENT)


# Ensure the Pinecone index exists
def ensure_pinecone_index():
    print('Checking if index exists...')
    if PINECONE_INDEX_NAME not in pinecone.list_indexes():
        print('Index does not exist, creating index...')
        pinecone.create_index(
            name=PINECONE_INDEX_NAME,
            metric='cosine',
            dimension=1536  # The OpenAI embedding model `text-embedding-ada-002` uses 1536 dimensions
        )


# embedding_docs.py
# ... (other import statements and code)

# Process a single document file
def process_document(document_path, update_callback=None):
    print(f'Loading document: {document_path}')
    file_extension = os.path.splitext(document_path)[1].lower()
    
    # Determine the loader based on the file extension
    if file_extension == '.pdf':
        loader = UnstructuredPDFLoader(document_path)
    elif file_extension == '.docx':
        loader = Docx2txtLoader(document_path)
    elif file_extension == '.txt':
        loader = TextLoader(document_path)
    else:
        raise ValueError(f'Unsupported file type: {file_extension}')
    
    data = loader.load()

    # Assuming all loaders return data in a similar structure
    if update_callback:
        update_callback(f'You have loaded a document with {len(data)} pages/sections')
        update_callback(f'There are {len(data[0].page_content)} characters in your document')

    # Chunk data into smaller documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(data)
    
    if update_callback:
        update_callback(f'You have split your document into {len(texts)} smaller documents')

    # Create embeddings and index from your documents
    print('Creating embeddings and index...')
    embeddings = OpenAIEmbeddings(client='')
    docsearch = Pinecone.from_texts(
        [t.page_content for t in texts], embeddings, index_name=PINECONE_INDEX_NAME)

    if update_callback:
        update_callback('Done!')

# Process multiple document files
def process_documents(document_paths, update_callback=None):
    for document_path in document_paths:
        process_document(document_path, update_callback)  # Pass the callback function

# ... (rest of your code)