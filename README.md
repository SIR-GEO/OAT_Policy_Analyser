# OAT Policy Analyser

## Introduction
"Ormiston Academies Trust (OAT) is one of the largest not-for-profit multi-academy trusts in England. Our aim as a charity, alongside our schools, is to help provide local children with a great education. We educate over 30,000 pupils across five OAT regions, in over 40 schools – currently 32 secondary schools, six primary schools, three alternative provision schools and one special school. We are one of the longest-established trusts and have been sponsoring academies since 2009. Our sole purpose is to provide OAT pupils with excellent learning opportunities inside and outside the classroom." 
Source: https://www.ormistonacademiestrust.co.uk/ 

The **OAT Policy Analyser** is a tool designed to facilitate the analysis of policies using advanced language models. It leverages the capabilities of Large Language Models (LLMs) to interpret, summarise, and provide insights into various policy documents. This github repo is designed as an experiment with various Retrieval-augmented generation (RAG) techniques. Specifically for OAT documents. is a technique for enhancing the accuracy and reliability of generative AI models with facts fetched from external sources. In other words, it fills a gap in how LLMs work.

## What makes this different from other RAG
### Background Information
#### AI Models Token Limit Overview
The architecture of each LLM will determine a token limit: the maximum number of tokens that the model can process at once, the maximum length of the prompt and the output of the model.
As of 21/01/24 Here's a summary of some token limits for various AI models:
- **OpenAI GPT-4 Preview**
  - Highest token window of 128,000.
- **Anthropic Claude 2**
  - Highest token window of 200,000.
- **LLaMA-2 70B**
  - Supports up to 4096 tokens, equivalent to around 3000 words, suitable for dialogue, logical reasoning, and coding tasks.
- **Google PaLM 2 "Text Bison" Model**
  - Input token limit of 8196 and an output token limit of 1024.
- **Google Gemini Models**
  - **"Gemini Pro"**: Input token limit of 30720 and output token limit of 2048.
  - **"Gemini Pro Vision"**: Input token limit of 12288 and output token limit of 4096 (handles text and images).
  - **"Gemini Nano"**: Token limit details not specified; designed for efficiency on resource-constrained devices.
  - **Google Gemini Ultra**: Token limit details not available; it's Google's largest and most capable model, optimized for complex, multimodal tasks.
- **Falcon AI Falcon-40B Model**
  - Prompt token limit of 2048.
- **Mistral AI Mistral-7B Model**
  - Trained with a context length of 8000 tokens and a theoretical attention span of 128K tokens. Platform rate limits are 2 requests per second and up to 200 million tokens per month.

#### OAT use case with 100 documents
For OAT use cases lets say theres 100 documents that people want to ask questions on and generate new content with. This amount exceeds most LLMs token context window, so only really OpenAI or Anthropic models can answer it, by the user uploading each document manually and then asking questions, however these companys only hosted chatbots have file limits on the uploads, so uploading 100 documents is not possible, they would have to be consolidated into the same document which takes further effort. 
So you have options for giving LLMs data to work with.

## Approaches for Integrating PDFs with Large Language Models (LLMs)

### RAG through an Index - **received unsatisfactory responses, missing too much context**
- **Method**: Index the PDFs' contents and use RAG where the LLM fetches relevant information from this index before answering.
- **Advantages**:
  - Answers are based on actual document contents.
  - Handles large data volumes efficiently.
- **Challenges**:
  - Requires setup for indexing and retrieval systems.
  - Answers limited to indexed information.

### RAG by Uploading Documents into the System Prompt - **Current setup**
- **Method**: Input relevant PDF sections into the LLM's prompt with your question.
- **Advantages**:
  - Direct and specific to the PDFs' content for each query.
- **Challenges**:
  - Limited by the LLM's token limit.
  - Impractical for large text volumes.

### Fine-Tuning the AI with the Contents of the PDFs - **Yet to experiment with**
- **Method**: Train or fine-tune the LLM on the extracted text from the PDFs.
- **Advantages**:
  - Tailors the model to your data, potentially improving accuracy and relevance.
- **Challenges**:
  - Requires resources for fine-tuning.
  - Risk of overfitting on a limited dataset.

### Best Approach
- **Fine-Tuning**: Best for highly specific questions and detailed answers, especially if you have the resources and expertise.
- **RAG with Indexed Database**: Suitable for general queries; balances efficiency with the ability to use specific data without retraining the model.
- **Uploading to System Prompt**: Less practical due to token limits and effort required; feasible for very targeted queries.

**Note**: The optimal approach depends on factors like the specificity of your questions, frequency of queries, and available resources. Additionally, for fine-tuning, you need to format your data appropriately, often creating pairs of prompts and expected responses, and periodically update the model with new data from the PDFs.

**For this system as of 21/01/24 it only explores the 'RAG by Uploading Documents into the System Prompt'. Due to our testing finding limitations with document indexing - the system still seemed to miss out key data from the docuements and not provide enough data to be more analytical in terms of data manipulation. Need to explore fine-tuning or training an AI model next**



## Features
- **Policy Analysis**: Utilises language models to analyse entire documents (not indexed) policy documents, offering summaries and key insights.
- **Document Embedding**: Converts documents into a numerical form that can be processed by machine learning models.
- **User-Friendly Interface**: Built with Streamlit, the tool provides an intuitive web interface for easy interaction.
- **GitHub Integration**: Integrates with GitHub, allowing users to fetch policy documents directly from repositories.

## Requirements
- Python 3.11 or later
- Dependencies are listed in `requirements.txt`, including `openai`, `streamlit`, `PyGithub`, `unstructured`, `langchain`, and their respective versions.

## Installation
1. Clone the repository: `git clone https://github.com/SIR-GEO/OAT_Policy_Analyser.git`
2. Navigate to the project directory.
3. Install the required packages: `pip install -r requirements.txt`

## Usage
- Run `app.py` to start the Streamlit web application.
- Access the application via a web browser at `localhost:8501` (default Streamlit port).

## Files and Directories
- `app.py`: The main application file for the Streamlit interface.
- `embedding_docs.py`: Contains functions for document embedding.
- `.gitignore`: Lists files and directories to be ignored by Git.
- `README.md`: This file, providing documentation for the project.
- `requirements.txt`: Lists the Python dependencies for the project.

## Contributing
Contributions to the OAT Policy Analyser are welcome. Please follow the standard procedures for contributing to open-source projects on GitHub:
1. Fork the repository.
2. Create a new branch for your feature.
3. Commit your changes.
4. Push to the branch.
5. Submit a pull request.

## Licence
The project is not yet licenced.

## Contact
For any queries or support, please contact git owner
