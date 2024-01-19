# Document Answering with Langchain, Pinecone and OpenAI

Langchain provides an easy-to-use integration for processing and querying documents with Pinecone and OpenAI's embeddings. With this repository, you can load a PDF, split its contents, generate embeddings, and create a question-answering system using the aforementioned tools.

## Repository Structure:

- `embbeding_doc.py`: The primary script for loading a PDF, splitting its content, generating embeddings using OpenAI, and saving them with Pinecone.
- `constants.py`: Holds the constants used across the repository.
- `app.py`: A Streamlit application that allows you to query the embedded documents using a question-answering chain.

## Requirements:

1. Python 3+
2. Pinecone API key
3. OpenAI API key
4. Streamlit
5. The required modules as seen in the code (e.g., langchain, pinecone)

## Quick Start:

1. **Set Up Configuration**:

   - You must create a `config.py` file that defines the following:

     ```python
     OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'
     PINECONE_API_KEY = 'YOUR_PINECONE_API_KEY'
     PINECONE_API_ENVIRONMENT = 'YOUR_PINECONE_ENVIRONMENT'
     ```

2. **Run `embbeding_doc.py`**:

   - This will load the provided PDF, split its content, generate embeddings, and save them to Pinecone.

     ```bash
     $ python embbeding_doc.py
     ```

3. **Start the Streamlit Application**:

   - Use Streamlit to run the `app.py` script.

     ```bash
     $ streamlit run app.py
     ```

   - Once the application is running, you can enter questions related to the PDF content, and it will provide relevant answers using the created embeddings and the question-answering chain.

## Important Notes:

- This is a sample setup. Depending on your requirements, you might want to modify the document loading, splitting, and embedding strategies.
- Ensure your OpenAI API key and Pinecone API key are kept confidential and are not pushed to public repositories.
