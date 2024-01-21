import os
import tempfile
import traceback
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders.word_document import Docx2txtLoader

def process_pdf(file_content):
    # Write the PDF content to a temporary file and then process it
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='wb') as tmp_file:
        tmp_file.write(file_content)
        tmp_file.flush()
        try:
            loader = UnstructuredPDFLoader(tmp_file.name)
            text = loader.load()
            return text
        except Exception as e:
            print(f"An error occurred while processing PDF: {e}")
            return None
        finally:
            tmp_file.close()  # Ensure the file is closed before attempting to delete it
            os.remove(tmp_file.name)

def process_docx(file_content):
    # Write the DOCX content to a temporary file and then process it
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx', mode='wb') as tmp_file:
        tmp_file.write(file_content)
        tmp_file.flush()
        try:
            loader = Docx2txtLoader(tmp_file.name)
            text = loader.load()
            return text
        except Exception as e:
            error_message = f"An error occurred while processing DOCX: {e}\nError type: {type(e)}\nTraceback: {traceback.format_exc()}"
            return error_message
        finally:
            tmp_file.close()  # Ensure the file is closed before attempting to delete it
            os.remove(tmp_file.name)


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