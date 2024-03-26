## Streamlit Chabot

Chatbot that answers queries about members of the Build Club, a community of passionate AI builders! 
Members provide general information about their current projects and start-up when they join, 
and also regular build updates that details the progress of their projects.

## How to use

This chatbot is deployed on [buildclub.streamlit.app](https://buildclub.streamlit.app/)
You just need to provide your OpenAI api key to use it.

## Airtable Chat Application Setup in localhost

Follow these instructions to set up the Airtable Chat application.

### Prerequisites

- Python installed on your system.
- Git installed on your system.
- (Alternatively use a dev container, check [Setup dev environment with DevContainers](https://isabelle.hashnode.dev/setup-a-development-environment-to-experiment-with-langchain) for instructions)
- Access to [Supabase](https://supabase.com/) for database services. Create a project. (Refer to [Chatbot With LlamInde](https://isabelle.hashnode.dev/streamlit-chatbot-with-llamaindex-i))

## Setup Instructions

### 1. Clone the Repository

First, clone the repository to your local machine using the following command:

```bash
git clone https://github.com/IsisChameleon/airtable-chat.git
```

Then, navigate into the directory:

```bash
cd airtable-chat
```

### 2. Install Dependencies

Install the required Python libraries specified in requirements.txt:

```bash
pip install -r requirements.txt
```

### 3. Create a Supabase project

Refer to [Chatbot With LlamInde](https://isabelle.hashnode.dev/streamlit-chatbot-with-llamaindex-i)

### 4. Setup env file

Open file .env.example and replace with correct tokens as per instructions.

```
OPENAI_API_KEY='' ## <<<<< Your API key here for OpenAI (https://platform.openai.com/)
AIRTABLE_TOKEN='' 
AIRTABLE_BASE_ID='app...'
AIRTABLE_TABLE_ID='tbl...'
AIRTABLE_BUILDBOUNTY_TOKEN=''
AIRTABLE_BUILDBOUNTY_BASE_ID='app...'
AIRTABLE_BUILDBOUNTY_MEMBERS_TABLE_ID='tbl...'
AIRTABLE_BUILDBOUNTY_MEMBERSGENAIVERSION_TABLE_ID='tbl...'
AIRTABLE_BUILDBOUNTY_BUILDUPDATES_TABLE_ID='tbl...' #'viwWFmmmFL9SxnAX4'
SUPABASE_CONNECTION_STRING='postgresql://postgres.....'
```
Supabase & Airtable:
Refer to Refer to [Chatbot With LlamInde](https://isabelle.hashnode.dev/streamlit-chatbot-with-llamaindex-i)

OpenAI: 
#### Obtaining an OpenAI API Key

To use OpenAI's services, including GPT models, you need an API key from OpenAI. Follow these steps to obtain your API key:

##### Step 1: Create an OpenAI Account

- Visit the OpenAI website at [https://openai.com/](https://openai.com/).
- Click on the `Sign Up` button to create a new account or `Log In` if you already have an account.

##### Step 2: Access the API Key Section

- Once logged in, navigate to the API section by clicking on `API` in the top navigation bar or go directly to [https://platform.openai.com/](https://platform.openai.com/)

### 5. Run app

```streamlit run app_st.py```
