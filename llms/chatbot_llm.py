from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from utils.knowledge_files import load_file_to_temp
import streamlit as st
import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from transformers import OpenAIGPTTokenizerFast

from pinecone import Pinecone, ServerlessSpec
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.pinecone import PineconeVectorStore
from s3fs import S3FileSystem

def load_text_file(file_path):
    return open(file_path, 'r').read()

@st.cache_resource
def get_embed(model_name):
    return OpenAIEmbedding(model=model_name)

@st.cache_resource
def get_tokenizer(hf_token):
    return OpenAIGPTTokenizerFast.from_pretrained("openai-community/openai-gpt", token=hf_token)

@st.cache_resource
def get_chat_engine_old(openai_api_key, knowledge_file_paths):
    # Transfer data from remote directory to local temporary directory
    tmp_paths = [load_file_to_temp(file_path) for file_path in knowledge_file_paths]
    
    # Embed files
    documents = SimpleDirectoryReader(input_files=tmp_paths).load_data()

    # Initialize the OpenAI embedding model
    embedding_model = get_embed()
    embedding_model.api_key = openai_api_key

    # Tokenizer for OpenAI's GPT models using HuggingFace API Key
    #hf_token = os.environ["HF_API_KEY"]
    #tokenizer = get_tokenizer(hf_token)

    # Index the knowledge files using the embedding model
    index = VectorStoreIndex.from_documents(documents, 
                                            embed_model=embedding_model)#,
                                            #tokenizer=tokenizer)
    
    # Set up the chat engine
    return index


def get_chat_engine(tool_name, openai_api_key, knowledge_file_paths):
    # Connect to Pinecone index
    index_name = tool_name.lower().replace(' ','-')#'-'.join(knowledge_file_paths)[:42]
    pc_api_key = os.environ["PC_API_KEY"]
    pc = Pinecone(api_key=pc_api_key)

    # Pinecone and Embedding params
    embedding_params = {'name': 'text-embedding-3-small',
                        'dimension': 1536,
                        'metric': 'cosine'}
    
    # Initialize the OpenAI embedding model
    embedding_model = get_embed(embedding_params['name'])
    embedding_model.api_key = openai_api_key

    # Create index if it doesn't already exist
    if index_name not in pc.list_indexes().names():

        # Load data from remote directory        
        s3_fs = S3FileSystem(anon=False, 
                             key=os.getenv('AWS_ACCESS_KEY_ID'), 
                             secret=os.getenv('AWS_SECRET_ACCESS_KEY'))
        documents = SimpleDirectoryReader(input_files=knowledge_file_paths,
                                  fs=s3_fs,
                                  recursive=True).load_data()
        try:
            # Create index
            pc.create_index(
                index_name,
                dimension=embedding_params['dimension'],
                metric=embedding_params['metric'],
                spec=ServerlessSpec(cloud="aws", region="us-east-1"))
        
            # Initialize your index 
            pinecone_index = pc.Index(index_name)

            # Initialize VectorStore
            vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

            # Create the embedding pipeline with transformations and vector storing
            pipeline = IngestionPipeline(
                transformations=[
                    SentenceSplitter(),
                    embedding_model,
                ],
                vector_store=vector_store
            )

            # Run the pipeline
            pipeline.run(documents=documents)
        except:
            # Initialize your index 
            pinecone_index = pc.Index(index_name)

            # Initialize VectorStore
            vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    else:
        # Initialize your index 
        pinecone_index = pc.Index(index_name)

        # Initialize VectorStore
        vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

    # Set up the chat engine
    return VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embedding_model)


class AITutor:
    """
    A class that facilitates a back-and-forth conversation between a student and an AI tutor.
    It uses an LLM (Large Language Model) to guide students through questions, provide feedback, 
    and help them understand science concepts without directly giving them the answers.

    This class is designed to work with any LLM that has a chat function.

    Attributes:
        llm (Any LLM with a chat function): The LLM model used to interact with the student.
        message_history (list): A history of messages exchanged between the student and the tutor.
    
    Methods:
        initiate_conversation(grade, topic): Initiates the tutoring session by asking the student for more details.
        get_response(student_input): Handles student input and provides a response using the LLM.
        get_message_history(): Returns the history of messages in the conversation.
    """

    def __init__(self, llm_model, tool_name, instructions, introduction, knowledge_file_paths, openai_api_key=None, display_system=False):
        self.llm = llm_model
        self.message_history = []
        self.introduction = introduction

        # Add these as a "system prompt"
        system_prompt = "# AI Tutor Instructions\n\n"
        system_prompt += "Below are the guidelines for the tutor's interactions with the user:\n\n"
        system_prompt += f"{instructions}\n\n"
        system_prompt += """
**Math Formatting:**
   - Importantly, **NEVER USE `\(`, `\)` OR `\[`, `\]` FORMATTING FOR MATH IN ANY OF MY COMMUNICATION OR CONTENT. STRICTLY USE `$`,`$` OR `$$`,`$$` FORMATTING.**
   - This is extremely important because the `\(\)` and `\[\]` formatting will not work when displayed to the user.
        """
        system_prompt += "\n\n## Your Task\n\n"
        system_prompt += "You are a helpful AI tutor/assistant. "
        system_prompt += "Following the instructions above, provide supportive assistance to the student user."
        if display_system:
            print(system_prompt)

        if len(knowledge_file_paths)>0:
            
            index = get_chat_engine(tool_name, openai_api_key, knowledge_file_paths)

            self.chat_engine = index.as_chat_engine(chat_mode="best", 
                                                    llm=self.llm)#, 
                                                    #system_prompt=system_prompt)
            self.index_routine = True
        else:
            self.chat_engine = None
            self.index_routine = False
        
        # Initialize the conversation with the system prompt
        self.message_history.append(ChatMessage(role="system", content=system_prompt))
        
        # Append initial request from AI tutor
        self.initiate_conversation()

    def initiate_conversation(self):
        """
        Initiates the conversation with the student, asking for the grade level and topic they are working on.
        """

        self.message_history.append(ChatMessage(role="assistant", content=self.introduction))

    def get_response(self, student_input):
        """
        Handles student input and provides a response.
        The LLM will respond based on the system instructions, conversation history, and the input provided by the student.
        """
        # Add the student's message to the history
        self.message_history.append(ChatMessage(role="user", content=student_input))
        
        # Get the response from the LLM
        if self.index_routine:
            response = self.chat_engine.chat(student_input, self.message_history[:-1]).response
        else:
            response = self.llm.chat(self.message_history).message.content
        
        # Add the AI's response to the history
        self.message_history.append(ChatMessage(role="assistant", content=response))
        
        return response