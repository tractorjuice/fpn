# Importing required packages
from streamlit_chat import message
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.callbacks import get_openai_callback
import requests
import openai

API_ENDPOINT = "https://api.onlinewardleymaps.com/v1/maps/fetch?id="
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
#MODEL = "gpt-3"
#MODEL = "gpt-3.5-turbo"
#MODEL = "gpt-3.5-turbo-0613"
#MODEL = "gpt-3.5-turbo-16k"
#MODEL = "gpt-3.5-turbo-16k-0613"
MODEL = "gpt-4"
#MODEL = "gpt-4-0613"
#MODEL = "gpt-4-32k-0613"

st.set_page_config(page_title="Chat with your FPN Wardley Map", layout="wide")
st.sidebar.title("Chat with Map")
st.divider()
st.sidebar.markdown("Developed by Mark Craddock")
st.sidebar.markdown("Current Version: 0.1")
st.sidebar.markdown("Using GPT-4 API")
st.sidebar.markdown("Early release\n\nMinimal testing\n\nMay run out of OpenAI credits")
st.divider()
st.sidebar.markdown("## Enter Map ID")
    
def get_initial_message():
    url = f"https://api.onlinewardleymaps.com/v1/maps/fetch?id={map_id}"
    
    try:
        response = requests.get(url)
        
        # Check if the response status code is 200 (successful)
        if response.status_code == 200:
            map_data = response.json()
            
            # Check if the expected data is present in the response JSON
            if "text" in map_data:
                map_text = map_data["text"]
                st.session_state['map_text'] = map_text
            else:
                st.warning("The response JSON does not contain the expected 'text' key.")
                return []
        else:
            st.warning(f"The API request failed with status code {response.status_code}.")
            return []
    
    except requests.exceptions.RequestException as e:
        st.warning(f"An error occurred while making the API request: {e}")
        return []
    
    messages = [
        {
            "role": "system",
            "content": f"""
             As a chatbot, analyze the provided Wardley Map and offer insights and recommendations based on its components.

             Suggestions:
             Request the Wardley Map for analysis
             Explain the analysis process for a Wardley Map
             Discuss the key insights derived from the map
             Provide recommendations based on the analysis
             Offer guidance for potential improvements or adjustments to the map
             WARDLEY MAP: {map_text}
             """
        },
        {
            "role": "user",
            "content": "{question} Output as markdown"
        },
        {
            "role": "assistant",
            "content": """
            Here is a list of general questions that you could consider asking while examining any Wardley Map:
            1. What is the focus of this map - a specific industry, business process, or company's value chain?
            2. What are the main user needs the map is addressing, and have all relevant user needs been identified?
            3. Are the components correctly placed within the map based on their evolutions (Genesis, Custom Built, Product/Rental, Commodity)?
            4. What linkages exist between the components and how do they interact within the value chain?
             5. Can you identify any market trends or competitor activities that could impact the positioning of the components?
             6. Are there any potential inefficiencies or improvements that could be made in the value chain depicted in the map?
             7. How does your organization take advantage of upcoming opportunities or mitigate risks, considering the layout and components' evolutions on the map?
             8. Are there any areas where innovation or disruption could significantly alter the landscape represented in the map?
             It is essential to provide the actual Wardley Map in question to provide a more accurate, in-depth analysis of specific components or insights tailored to your map.
            """
        }
    ]
    return messages

def get_chatgpt_response(messages, model):

    # Convert messages to corresponding SystemMessage, HumanMessage, and AIMessage objects
    new_messages = []
    for message in messages:
        role = message['role']
        content = message['content']
        
        if role == 'system':
            new_messages.append(SystemMessage(content=content))
        elif role == 'user':
            new_messages.append(HumanMessage(content=content))
        elif role == 'assistant':
            new_messages.append(AIMessage(content=content))
    
    chat = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model_name=model,
        temperature=0.5,
    )
    try:
        with get_openai_callback() as cb:
            response = chat(new_messages)
    except:
        st.error("OpenAI Error")
    if response is not None:
        return response.content, cb
    else:
        st.error("Error")
        return "Error: response not found"
  
def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages

if 'tokens_used' not in st.session_state:
    st.session_state['tokens_used'] = 0
    
if 'total_tokens_used' not in st.session_state:
    st.session_state['total_tokens_used'] = 0

if 'generated' not in st.session_state:
    st.session_state['generated'] = []
    
if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = []
    
if 'map_text' not in st.session_state:
    st.session_state['map_text'] = []
    
if 'code_has_run' not in st.session_state:
    st.session_state['code_has_run'] = False
    
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    col1.markdown("## Chat")
    query = st.text_input("Question: ", value="Suggest 5 questions you can answer about this Wardley Map?", key="input")

map_id = st.sidebar.text_input("Enter the ID of the Wardley Map:", value="gTTfD4r2mORudVFKge")    
st.divider()
st.sidebar.write(f"Total Tokens Used: {st.session_state['total_tokens_used']}")
st.sidebar.write(f"Total Cost: ${st.session_state['total_tokens_used'] * 0.06 / 1000}")
st.divider()
    
if st.session_state.get('current_map_id') != map_id:
    del st.session_state['messages']
    st.session_state['total_tokens_used'] = 0
    st.session_state['tokens_used'] = 0
    st.session_state['past'] = []
    st.session_state['generated'] = []
    st.session_state['code_has_run'] = False
    st.session_state['current_map_id'] = map_id
    query = "Suggest 3 questions you can answer about this Wardley Map?"
    st.session_state['messages'] = get_initial_message()

# Display the map in the sidebar
if 'map_text' in st.session_state:
    map_text = st.session_state['map_text']
    for line in map_text.split("\n"):
        if line.startswith("title"):
            title = line.split("title ")[1]
    if title:
        st.sidebar.markdown(f"### {title}")
    st.sidebar.code(st.session_state['map_text'])

with col1:
    query_button = st.button("Ask Question")
    st.divider()
    if query_button and query:
        with st.spinner("Thinking... this can take a while..."):
            messages = st.session_state['messages']
            messages = update_chat(messages, "user", query)
            try:
                content, response = get_chatgpt_response(messages, MODEL)
                st.session_state.tokens_used = response.total_tokens
                st.session_state.total_tokens_used = st.session_state.total_tokens_used + st.session_state.tokens_used
                messages = update_chat(messages, "assistant", content)
                st.session_state.generated.append(content)
                st.session_state.past.append(query)
            except:
                st.error("GPT-4 Error")
                
with col2:
    st.markdown("## Structured Prompts")
    st.divider()
    if st.session_state["generated"]:
        for text in st.session_state["generated"]:
            sentences = text.strip().split("\n")
            for i, sentence in enumerate(sentences):
                stripped_sentence = sentence.strip()
                if stripped_sentence and stripped_sentence[0].isdigit():
                    st.write(stripped_sentence)
                    generated_index = st.session_state["generated"].index(text)
                    unique_key = f"{generated_index}-{i}"
                    if st.button(f"Ask follow up question", key=unique_key):
                        with st.spinner("thinking... this can take a while..."):
                            messages = st.session_state['messages']
                            messages = update_chat(messages, "user", stripped_sentence)
                            try:
                                content, response = get_chatgpt_response(messages, MODEL)
                                st.session_state.tokens_used = response.total_tokens
                                st.session_state.total_tokens_used = st.session_state.total_tokens_used + st.session_state.tokens_used
                                messages = update_chat(messages, "assistant", content)
                                st.session_state.past.append(stripped_sentence)
                                st.session_state.generated.append(content)
                            except:
                                st.error("GPT4 Error")

with col3:
    st.markdown("## Output Document")
    st.divider()
    if st.session_state['generated']:
        download_doc_str = []
        for i in range(len(st.session_state['generated'])):
            st.divider()
            st.write(st.session_state['generated'][i])

        for i in range(len(st.session_state['generated']) - 1, -1, -1):    
            download_doc_str.append(st.session_state["generated"][-(i+1)])

        if download_doc_str:
            download_doc_str = '\n'.join(download_doc_str)
            st.download_button('Download', download_doc_str)
            
with col1:
    if st.session_state['generated']:
        download_chat_str = []
        for i in range(len(st.session_state['generated']) - 1, -1, -1):  # Loop in reverse order
            message(st.session_state['generated'][i], is_user=False, key=str(i) + '_assistant', avatar_style="shapes", seed=25)
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="shapes", seed=20)     
            download_chat_str.append(st.session_state["generated"][i])
            download_chat_str.append(st.session_state["past"][i])

        if download_chat_str:
            download_chat_str = '\n'.join(download_chat_str)
            st.download_button('Download',download_chat_str)
