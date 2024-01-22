from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import streamlit as st
import anthropic
# Replace 'your_api_key_here' with your actual API key
# Ensure you have the correct API key set in your environment or secrets file
api_key = st.secrets["ANTHROPIC_API_KEY"]
anthropic = Anthropic(api_key=api_key)
client = anthropic

def chat_with_claude(prompt):
    with client.beta.messages.stream(
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        model="claude-2.1",
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

# Simple CLI for chatting with Claude with streaming enabled
print("Welcome to the simple Claude 2.1 chatbot interface with streaming!")
print("Type 'quit' to exit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        break
    chat_with_claude(user_input)