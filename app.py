import os
import streamlit as st
# from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_API_ENVIRONMENT
from constants import PINECONE_INDEX_NAME
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
usr_input = st.text_input('Ask any question about these OAT Policies: https://www.ormistonacademiestrust.co.uk/who-we-are/docs-and-policies/policies/')

# Set OpenAI LLM and embeddings
llm_chat = ChatOpenAI(temperature=0.9,
                      model='gpt-3.5-turbo-16k', client='')

embeddings = OpenAIEmbeddings(client='')

# Set Pinecone index
docsearch = Pinecone.from_existing_index(
    index_name=PINECONE_INDEX_NAME, embedding=embeddings)

# Create chain
chain = load_qa_chain(llm_chat)

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
