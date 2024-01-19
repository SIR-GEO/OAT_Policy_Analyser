# embedding_docs.py
import os
import tempfile
from PyPDF2 import PdfReader
from docx import Document

def process_pdf(file_content):
    # Write the PDF content to a temporary file and then process it
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(file_content)
        tmp_file.flush()
        try:
            reader = PdfReader(tmp_file.name)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            print(f"An error occurred while processing PDF: {e}")
            return None
        finally:
            os.remove(tmp_file.name)

def process_docx(file_content):
    # Write the DOCX content to a temporary file and then process it
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx', mode='wb') as tmp_file:  # Add 'mode=wb' to open the file in binary mode
        tmp_file.write(file_content)
        tmp_file.flush()
        try:
            doc = Document(tmp_file.name)
            text = "\n".join(para.text for para in doc.paragraphs)
            return text
        except Exception as e:
            print(f"An error occurred while processing DOCX: {e}")
            return None
        finally:
            os.remove(tmp_file.name)

# The rest of the embedding_docs.py file remains unchanged

def process_txt(document_path):
    # Implement TXT processing here
    try:
        with open(document_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        print(f"An error occurred while processing TXT: {e}")
        return None

def process_document(document_path, file_content):
    _, file_extension = os.path.splitext(document_path)
    if file_extension.lower() == '.pdf':
        return process_pdf(file_content)  # Pass file_content instead of document_path
    elif file_extension.lower() == '.docx':
        return process_docx(file_content)  # Pass file_content instead of document_path
    elif file_extension.lower() == '.txt':
        return process_txt(document_path)  # Here document_path is correct because it's a text file
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