from langchain_mistralai import ChatMistralAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from dotenv import load_dotenv
import os

class KnowledgeGraphGenerator:
    """
    A class that initializes the LLM, processes queries and responses to generate a knowledge graph as a string.

    Attributes:
        model_name (str): The model name to be used (e.g., "mistral-large-latest").
        llm (ChatMistralAI): The instance of the LLM model.
        chat_history (InMemoryChatMessageHistory): Stores the conversation history.

    Methods:
        initialize_llm():
            Initializes the LLM with the given model and API key.
        
        prompt(user_query, llm_response):
            Constructs the prompt for knowledge graph extraction.

        generate_knowledge_graph(user_query, llm_response):
            Uses the LLM to generate a knowledge graph from the conversation.
    """

    def __init__(self, model_name: str = "mistral-large-latest"):
        load_dotenv()
        self.api_key = os.getenv("MISTRALAI_API")
        self.model_name = model_name
        self.llm = None
        self.chat_history = InMemoryChatMessageHistory()

    def initialize_llm(self):
        """Initializes the LLM model with the provided API key and model name."""
        self.llm = ChatMistralAI(
            model_name=self.model_name, 
            api_key=self.api_key, 
            temperature=0.5
        )

    def prompt(self, user_query: str, llm_response: str) -> str:
        prompt = f""" 
        Construct a concise knowledge graph from the conversation below.
         **Context**:
         - Focus on key entities, relationships, and attributes.
         - The graph should capture no more than 5-7 nodes, formatted like:
            [ ('Entity 1', 'Relationship', 'Entity 2'), ('Entity 3', 'Attribute', 'Value'), ... ]
         - Only include relevant details from the current conversation, avoiding outdated context.
         **Input**:
         Query: "{user_query}"
         LLM Response: "{llm_response}"
         **Output**: A concise knowledge graph in the format:
         [ ('Entity 1', 'Relationship', 'Entity 2'), ('Entity 3', 'Attribute', 'Value'), ... ]
         """
        return prompt
        
    def generate_knowledge_graph(self, user_query: str, llm_response: str) -> str:
        prompt_text = self.prompt(user_query, llm_response)
        if self.llm is None:
            self.initialize_llm()
        Knowledge_graph = self.llm.predict(prompt_text)
        return Knowledge_graph
    




