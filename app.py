import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
import pinecone


OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
PINECONE_API_ENVIRONMENT = st.secrets["PINECONE_API_ENVIRONMENT"]
PINECONE_INDEX_NAME = st.secrets["PINECONE_INDEX_NAME"]

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENVIRONMENT)

# Setting streamlit
st.title('OAT Policy Analyser')
usr_input = st.text_input('Ask any question about any OAT Policies. Use this link to upload PDFs, WORD DOCS, TXT to the database: https://documents-to-database.streamlit.app/')

# Set OpenAI LLM and embeddings
llm_chat = ChatOpenAI(temperature=0.9,
                      model='gpt-4-1106-preview', client='')

embeddings = OpenAIEmbeddings(client='')

# Set Pinecone index
docsearch = Pinecone.from_existing_index(
    index_name=PINECONE_INDEX_NAME, embedding=embeddings)

# Create chain
chain = load_qa_chain(llm_chat)

# conversation_state.py
class ConversationState:
    def __init__(self):
        self.history = []

    def update(self, user_input, ai_response, documents):
        self.history.append({
            "user_input": user_input,
            "ai_response": ai_response,
            "documents": documents
        })

    def get_full_context(self):
        # Implement logic to combine the conversation history into a single context string
        # For simplicity, we concatenate user inputs and AI responses
        context = ""
        for entry in self.history:
            context += f"User: {entry['user_input']} \nAI: {entry['ai_response']}\n"
        return context

# Check Streamlit input
if usr_input:
    # Generate LLM response
    try:
        search = docsearch.similarity_search(usr_input)
        response = chain.run(input_documents=search, question=usr_input)
        print('Response:', response)
        st.write(response)
    except Exception as e:
        st.write('It looks like you entered an invalid prompt. Please try again.')
        print(e)

    with st.expander('Document Similarity Search'):

        # Display results
        search = docsearch.similarity_search(usr_input)
        print('Search results:', search)
        st.write(search)
