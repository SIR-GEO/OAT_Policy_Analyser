# embedding_docs.py
import os
import pinecone
import streamlit as st
from langchain_community.document_loaders import UnstructuredPDFLoader
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

# Process a single PDF file
def process_pdf(pdf_file):
    print(f'Loading document: {pdf_file}')
    loader = UnstructuredPDFLoader(pdf_file)
    data = loader.load()

    print(f'You have loaded a PDF with {len(data)} pages')
    print(f'There are {len(data[0].page_content)} characters in your document')

    # Chunk data into smaller documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(data)

    print(f'You have split your document into {len(texts)} smaller documents')

    # Create embeddings and index from your documents
    print('Creating embeddings and index...')
    embeddings = OpenAIEmbeddings(client='')
    docsearch = Pinecone.from_texts(
        [t.page_content for t in texts], embeddings, index_name=PINECONE_INDEX_NAME)

    print('Done!')

# Process multiple PDF files
def process_pdfs(pdf_files):
    for pdf_file in pdf_files:
        process_pdf(pdf_file)