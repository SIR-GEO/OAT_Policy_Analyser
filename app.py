import streamlit as st
from github import Github
import openai
import time
import logging
import pandas as pd
import json
import os
from embedding_docs import process_document
from streamlit.components.v1 import html
from datetime import datetime
from openai import OpenAI
client = OpenAI()

password = st.text_input("Enter the password", type="password")

if password == st.secrets["general"]["password"]:
           
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # At the top of your Streamlit app, after imports
    if 'ai_responses_df' not in st.session_state:
        st.session_state.ai_responses_df = pd.DataFrame(columns=["Query", "AI Response"])

    # Initialize the cumulative cost in session state if it doesn't exist
    if 'cumulative_cost' not in st.session_state:
        st.session_state.cumulative_cost = 0.0

    # Initialize the total tokens in session state if it doesn't exist
    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = 0

    # Initialize the total tokens in session state if it doesn't exist
    if 'run_time' not in st.session_state:
        st.session_state.run_time = 0
        
    # At the top of your Streamlit app, after imports
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    #st.write("Initialized conversation_history:", st.session_state.conversation_history)
    # At the top of your Streamlit app, after imports
    if 'message_time' not in st.session_state:
        st.session_state.message_time = {}

    # At the top of your Streamlit app, after imports and before creating widgets
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""

    # At the top of your Streamlit app, after imports and before creating widgets
    if 'selected_files' not in st.session_state:
        st.session_state.selected_files = {}



    # Create three columns with equal width to center the middle column content
    col1, col2, col3 = st.columns([1,1,1])

    # Use the middle column to display the image
    with col2:
        st.image('images/oat-logo-2.png')

    # Set up the Streamlit interface
    st.markdown("<h1 style='text-align: center;'>OAT Policy Analyser</h1>", unsafe_allow_html=True)

    # Add a slider for the temperature

    temperature = st.slider('Creativity Slider | 0.0 = Highly Predictable | 1.0 = Super Creative', min_value=0.0, max_value=1.0, value=0.5, step=0.1, format='%.1f')


    with st.form(key='query_form'):
        # Create the text input widget inside the form
        search_query = st.text_input("Your Query", value=st.session_state.search_query, key="search_query")
        # Create the submit button
        submitted = st.form_submit_button("Submit")










    # Initialize OpenAI and GitHub clients with your tokens
    g = Github(st.secrets["GITHUB_TOKEN"])
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    repo_name = "OAT_Policies"

    # Initialize a list to store the responses as dictionaries
    ai_responses = []

    # Initialize a DataFrame to store the full responses
    ai_responses_df = pd.DataFrame(columns=["Response"])







    # At the end of Streamlit app, custom css to display the footer stuff
    def render_footer(total_tokens, run_time, cumulative_cost):
        # Check if any of the values are None and return an empty string if so
        if total_tokens is None or run_time is None or cumulative_cost is None:
            return ""
        
        # Construct the footer HTML
        footer_html = f"""
        <style>
        .reportview-container .main footer {{
            display: none;
        }}
        .footer {{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #111;
            color: white;
            text-align: center;
            padding: 10px;
            z-index: 9999;
        }}
        </style>
        <footer class="footer">
            <span>Total tokens: {total_tokens}</span>
            <span style="margin-left: 30px;">Total run time: {run_time:.2f} seconds</span>
            <span style="margin-left: 30px;">Predicted cost: ${cumulative_cost:.6f}</span>
        </footer>
        """
        return footer_html

    def get_current_date_and_time():
        try:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Returns date and time in 'YYYY-MM-DD HH:MM:SS' format
        except Exception as e:
            logging.error(f"Failed to get current date and time: {e}")
            return ""  # Return an empty string in case of failure

    # Define a function to display temporary messages in the sidebar
    def show_temporary_message(message_type, message, key):
        if message_type == 'success':
            message_container = st.sidebar.success(message, key=key)
        elif message_type == 'warning':
            message_container = st.sidebar.warning(message, key=key)
        elif message_type == 'error':
            message_container = st.sidebar.error(message, key=key)
        
        # Set a timer for the message
        if key not in st.session_state:
            st.session_state[key] = time.time()

        # Check if 5 seconds have passed
        if time.time() - st.session_state[key] > 5:
            # Clear the specific message after 5 seconds
            message_container.empty()
            # Remove the timer from the session state
            del st.session_state[key]



    def upload_file_to_github(repo_name, file_path, file_content, commit_message):
        repo = g.get_user().get_repo(repo_name)
        try:
            # Check if the file already exists
            contents = repo.get_contents("")
            existing_files = [content_file.name for content_file in contents if content_file.type == "file"]
            
            if file_path in existing_files:
                st.sidebar.warning(f'File "{file_path}" already exists. No action taken to avoid duplication.')
                return  # Skip the upload to prevent duplication

            # Convert file_content to string if necessary
            if not isinstance(file_content, str):
                file_content = str(file_content)

            # Since the file does not exist, create it
            repo.create_file(file_path, commit_message, file_content)
            st.sidebar.success(f'File "{file_path}" uploaded successfully!')

            # Calculate the number of tokens in the file
            token_count = len(file_content.split())

            # Store the token count in the session state
            if 'file_tokens' not in st.session_state:
                st.session_state.file_tokens = {}
            st.session_state.file_tokens[file_path] = token_count

            # Update the token counts file in the GitHub repository
            update_token_counts(repo, file_path, token_count)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            st.sidebar.error(f'An error occurred while uploading the file "{file_path}".')
            raise e

    # Make sure to define the update_token_counts function as well
    def update_token_counts(repo, file_path, token_count):
        token_counts_file = 'token_counts.json'
        token_counts_content = None  # Initialize the variable outside of the try-except block

        try:
            # Try to get the existing token counts file
            token_counts_content = repo.get_contents(token_counts_file)
            token_counts = json.loads(token_counts_content.decoded_content)
        except:
            # If it doesn't exist, start with an empty dictionary
            token_counts = {}

        # Update the token count for the file
        token_counts[file_path] = token_count

        # Convert the dictionary back to a JSON string
        token_counts_str = json.dumps(token_counts, indent=2)

        # Update or create the token counts file in the repository
        if token_counts_content:
            repo.update_file(token_counts_file, "Update token counts", token_counts_str, token_counts_content.sha)
        else:
            repo.create_file(token_counts_file, "Create token counts", token_counts_str)

        return token_counts
        
    def load_token_counts(repo_name):
        repo = g.get_user().get_repo(repo_name)
        token_counts_file = 'token_counts.json'
        try:
            token_counts_content = repo.get_contents(token_counts_file)
            return json.loads(token_counts_content.decoded_content)
        except:
            # If the file doesn't exist, return an empty dictionary
            return {}

    # At the start of your app, after initializing the GitHub client:
    st.session_state.file_tokens = load_token_counts(repo_name)

    def delete_file_from_github(repo_name, file_path, commit_message):
        repo = g.get_user().get_repo(repo_name)
        try:
            contents = repo.get_contents(file_path)
            repo.delete_file(contents.path, commit_message, contents.sha)
            st.sidebar.success(f'File "{file_path}" deleted successfully!')
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            st.sidebar.error(f'An error occurred while deleting the file "{file_path}".')
            raise e
        




    def get_all_file_contents_from_repo(repo_name):
        try:
            repo = g.get_user().get_repo(repo_name)
            contents = repo.get_contents("")
            all_file_contents = []
            for content_file in contents:
                if content_file.type == "file":
                    file_content = repo.get_contents(content_file.path).decoded_content.decode().strip()
                    # Include the filename as metadata
                    document_with_metadata = f"### Document Source: {content_file.name}\n{file_content}\n"
                    all_file_contents.append(document_with_metadata)
            return "\n".join(all_file_contents)
        except Exception as e:
            logging.error(f"Failed to get file contents from repo: {e}")
            return ""  # Return an empty string in case of failure


    # Initialize metrics
    start_time = None
    total_tokens = 0
    run_time = 0  # Initialize run_time here
    conversation_history_str = ""

    # Streamlit file uploader in the sidebar
    uploaded_files = st.sidebar.file_uploader("", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)

    # Button to trigger the file processing in the sidebar
    if st.sidebar.button('Process and Upload Files'):
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Check if the file already exists to avoid duplicates
                text_file_name = os.path.splitext(uploaded_file.name)[0] + '.txt'
                if text_file_name in st.session_state.selected_files:
                    st.sidebar.warning(f'File "{text_file_name}" already exists. No action taken to avoid duplication.')
                    st.session_state.message_time[text_file_name] = time.time()
                
                else:
                    # Read the file content into memory
                    file_content = uploaded_file.read()

                    # Check the file extension and process accordingly
                    _, file_extension = os.path.splitext(uploaded_file.name)
                    if file_extension.lower() == '.txt':
                        # For .txt files, upload the content directly
                        upload_file_to_github(repo_name, text_file_name, file_content.decode('utf-8'), "Upload .txt file")
                        st.session_state.message_time[text_file_name] = time.time()

                    else:
                        # For other file types, convert to text and then upload
                        text_content = process_document(uploaded_file.name, file_content)
                        if text_content:
                            upload_file_to_github(repo_name, text_file_name, text_content, "Upload processed text file")
                        else:
                            st.sidebar.error(f'Failed to process the file: {uploaded_file.name}')
                    
                    # Add the uploaded file to the selected_files dictionary
                    st.session_state.selected_files[text_file_name] = False

            # Clear the file uploader widget after processing
            uploaded_files = None
        # Outside of the button click event, check if 5 seconds have passed for each message
        for file_name, timestamp in list(st.session_state.message_time.items()):
            if time.time() - timestamp > 5:
                # 5 seconds have passed, clear the message
                st.sidebar.empty()
                # Remove the timestamp from the session state
                del st.session_state.message_time[file_name]


    def get_selected_file_contents_from_repo(repo_name, selected_files):
        try:
            repo = g.get_user().get_repo(repo_name)
            all_file_contents = []
            for file_name in selected_files:
                content_file = repo.get_contents(file_name)
                if content_file.type == "file":
                    file_content = content_file.decoded_content.decode().strip()
                    # Include the filename as metadata
                    document_with_metadata = f"### Document Source: {file_name}\n{file_content}\n"
                    all_file_contents.append(document_with_metadata)
            return "\n".join(all_file_contents)
        except Exception as e:
            logging.error(f"Failed to get selected file contents from repo: {e}")
            return ""  # Return an empty string in case of failure

    def get_all_files_from_repo(repo_name):
        try:
            repo = g.get_user().get_repo(repo_name)
            contents = repo.get_contents("")
            all_files = [content_file.name for content_file in contents if content_file.type == "file"]
            return all_files
        except Exception as e:
            logging.error(f"Failed to get file list from repo: {e}")
            return []  # Return an empty list in case of failure


    # Fetch all files from the repo
    all_files = get_all_files_from_repo(repo_name)

    # Create a dictionary in the session state to store the selection status of each file
    if 'selected_files' not in st.session_state:
        st.session_state.selected_files = {file: False for file in all_files}

    # Initialize file_tokens in session state if it doesn't exist
    if 'file_tokens' not in st.session_state:
        st.session_state.file_tokens = {}



    # Create a checkbox for each file in the sidebar
    MAX_TOKENS = 110000  # Maximum allowed tokens

    for file in all_files:
        # Skip the token_counts.json file
        if file == 'token_counts.json':
            continue

        col1, col2, col3 = st.sidebar.columns([3,1,1])
        # Initialize the value for the file in the session state if it doesn't exist
        if file not in st.session_state.selected_files:
            st.session_state.selected_files[file] = False

        # Check if selecting this file would exceed the maximum tokens
        if st.session_state.selected_files[file] and file in st.session_state.file_tokens and sum(st.session_state.file_tokens.values()) > MAX_TOKENS:
            st.sidebar.warning(f'Selecting "{file}" would exceed the maximum allowed tokens ({MAX_TOKENS}).')
            st.session_state.selected_files[file] = False
        else:
            # Now you can safely create the checkbox with the value from the session state
            st.session_state.selected_files[file] = col1.checkbox(f'{file}', value=st.session_state.selected_files[file])

        if file in st.session_state.file_tokens:
            col2.write(f'Tokens: {st.session_state.file_tokens[file]}')

        if col3.button("🗑️", key=f'delete_{file}'):
            delete_file_from_github(repo_name, file, "Delete file")
            # Remove the file from the selected_files dictionary
            del st.session_state.selected_files[file]
            # Refresh the list of all files
            all_files = get_all_files_from_repo(repo_name)



            
    # Get the list of selected files
    selected_files = [file for file, selected in st.session_state.selected_files.items() if selected]

    # Fetch the contents of the selected files
    all_file_contents = get_selected_file_contents_from_repo(repo_name, selected_files)




    # Create a placeholder for the footer
    footer_placeholder = st.empty()
    footer_placeholder.markdown("") 

    # Reserve space for the metrics at the bottom of the app
    footer_tokens = st.empty()
    footer_run_time = st.empty()

    current_date_and_time = get_current_date_and_time()


    full_response_str = ""
    # Define the function to process the query
    def process_query(query):
        total_tokens = 0  # Define total_tokens at the start of the function
        if search_query:

            current_date_and_time = get_current_date_and_time()
            if current_date_and_time is None:
                current_date_and_time = ""  # Ensure it's a string even if the function fails

            # Start time when the search begins
            start_time = time.time()
            
            # Ensure conversation_history is stored in session state
            if 'conversation_history' not in st.session_state:
                st.session_state.conversation_history = []


            try:
                
                # Add the user's question to the conversation history
                if 'conversation_history' not in st.session_state:
                    st.session_state.conversation_history = []
                st.session_state.conversation_history.append({"role": "user", "content": search_query})
                #st.write("After adding user query:", st.session_state.conversation_history)


                # Separate AI API call for handling user follow up questions, reduces massive user of tokens.
                search_response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    temperature=temperature,
                    stream = True,
                    messages= [
                    {"role": "system", "content": """You are a UK based professional analyst called OAT Docs Analyser assistant.
                    You always respond using UK spelling and grammar. You will be given extensive details on OAT Policies and 
                    OAT documents and will be able to cross-reference entire contents or analyse specific sections in order to answer any question given.
                    You must say if the information does not have enough detail, you must NOT make up facts or lie. 
                    At the end of any response, you must always source every single document source information you used in your response, 
                    each document source will be given in the format **Document Source: (insert content filename here)**. 
                    You must always answer the user's questions using all the information in documents given:""" + all_file_contents + """Today's date and time will given next,
                    use that information to relate contextually relevant user questions """ + current_date_and_time},
                    {"role": "user", "content": search_query}
                    ] + st.session_state.conversation_history
                )

                # Placeholder for streaming responses
                response_placeholder = st.empty()


                # Initialize an empty string to hold the response
                full_response = ""

                # Start time when the search begins
                start_time = time.time()
                

                for chunk in search_response:
                    if chunk.choices[0].delta.content is not None:
                        # Append new content to the full response
                        full_response += chunk.choices[0].delta.content

                        # Update the placeholder with the full response so far
                        response_placeholder.write(full_response)
                        
                        # Calculate and update tokens and run time
                        total_tokens += len(chunk.choices[0].delta.content.split())
                        run_time = time.time() - start_time



                
                # Calculate the cost and tokens for the current response
                input_cost_per_token = 0.01 / 1000  # Cost per token for input
                output_cost_per_token = 0.03 / 1000  # Cost per token for output
                current_cost = (total_tokens * (input_cost_per_token + output_cost_per_token))
                current_total_tokens = total_tokens  # Store the total tokens for the current response

                # Update the cumulative cost and total tokens in session state
                st.session_state.cumulative_cost += current_cost
                st.session_state.total_tokens += current_total_tokens
                st.session_state.run_time += run_time

                # Update the footer
                footer_html_content = render_footer(
                    st.session_state.total_tokens,
                    st.session_state.run_time,
                    st.session_state.cumulative_cost
                )
                footer_placeholder.markdown(footer_html_content, unsafe_allow_html=True)



                # Update full_response_str with the content of full_response
                full_response_str = full_response

                # Create a new row with the AI response
                new_response = {"Response": full_response_str}

                        # Where you have the new response in full_response_str and the user's query in search_query
                new_response_df = pd.DataFrame({
                    'Query': [search_query],  # Add the user's query
                    'AI Response': [full_response_str]
                })

        
                # Concatenate the new DataFrame with the existing one in the session state
                st.session_state.ai_responses_df = pd.concat([st.session_state.ai_responses_df, new_response_df], ignore_index=True)

                # Reverse the DataFrame order to display the most recent messages at the top
                reversed_df = st.session_state.ai_responses_df.iloc[::-1]

                # Display the reversed DataFrame as a static table
                st.table(reversed_df)

                # Add the model's response to the conversation history
                st.session_state.conversation_history.append({"role": "assistant", "content": full_response})
                #st.write("After adding AI response:", st.session_state.conversation_history)


                # Convert conversation_history to a string
                #conversation_history_str = str(st.session_state.conversation_history)
                #st.write("conversation_history_str :    " + conversation_history_str)



                # After the AI response has been fully sent, clear the user's query
                if 'last_query' not in st.session_state or st.session_state.search_query != st.session_state.last_query:
                    st.session_state.last_query = st.session_state.search_query

            except Exception as e:
                st.error(f"An error occurred: {e}")
        # If this is a follow-up question, only include the conversation history


    # Check if the form has been submitted
    if submitted:
        # Process the query only when the form is submitted
        process_query(search_query)
        # Clear the input field by resetting the session state variable
        #st.write("Conversation history after form submission:", st.session_state.conversation_history)












    # Ensure that the footer is rendered after all other components
    if __name__ == "__main__":
        # ... (rest of your Streamlit app logic) ...

        # At the end of your Streamlit app, update the footer in the placeholder
        footer_html_content = render_footer(st.session_state.total_tokens, st.session_state.run_time, st.session_state.cumulative_cost)
        if footer_html_content:
            footer_placeholder = st.empty()
            footer_placeholder.markdown(footer_html_content, unsafe_allow_html=True)
            st.components.v1.html(footer_html_content, height=0, scrolling=False)
        else:
            footer_placeholder.empty()  # Clear the placeholder if footer_html_content is empty



    # Outside of the button click event, check if 5 seconds have passed for each message
    for key in list(st.session_state.keys()):
        if key.startswith('success_') or key.startswith('warning_'):
            show_temporary_message(None, None, key)  
        
else:
    st.write("Access denied.")
