# embedding_docs.py

import os
from PyPDF2 import PdfReader
from docx import Document

def process_pdf(document_path):
    # Implement PDF processing here
    try:
        reader = PdfReader(document_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"An error occurred while processing PDF: {e}")
        return None

def process_docx(document_path):
    # Implement DOCX processing here
    try:
        doc = Document(document_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text
    except Exception as e:
        print(f"An error occurred while processing DOCX: {e}")
        return None

def process_txt(document_path):
    # Implement TXT processing here
    try:
        with open(document_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"An error occurred while processing TXT: {e}")
        return None

def process_document(document_path):
    # Determine the type of document and call the appropriate processing function
    _, file_extension = os.path.splitext(document_path)
    if file_extension.lower() == '.pdf':
        return process_pdf(document_path)
    elif file_extension.lower() == '.docx':
        return process_docx(document_path)
    elif file_extension.lower() == '.txt':
        return process_txt(document_path)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def process_documents(document_paths):
    # Process each document and return their contents
    documents_content = {}
    for document_path in document_paths:
        content = process_document(document_path)
        if content is not None:
            documents_content[document_path] = content
    return documents_content