import streamlit as st
from llama_index.llms.gemini import Gemini
from utils.config import get_model_config

#from transformers import OpenAIGPTTokenizerFast

@st.cache_resource
def get_llm():
    model_config = get_model_config()
    if 'gemini' in model_config['model']:
        return Gemini(model=model_config['model'], 
                      temperature=model_config['temperature'], 
                      api_key=model_config['api_key'])
    else:
        from llama_index.llms.openai import OpenAI
        return OpenAI(model=model_config['model'], 
                      temperature=model_config['temperature'], 
                      api_key=model_config['api_key'])

@st.cache_resource
def get_embed(model_name):
    from llama_index.embeddings.openai import OpenAIEmbedding
    return OpenAIEmbedding(model=model_name)

#@st.cache_resource
#def get_tokenizer(hf_token):
#    return OpenAIGPTTokenizerFast.from_pretrained("openai-community/openai-gpt", token=hf_token)