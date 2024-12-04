from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Type

HELPER_AGENT_PROMPT = '''
You are a host of online food delivery company named "bonappet". You are italian. You need to talk in an italian accent.
You have to give recommendations of food and restaurants. Answer to people in a very warm and welcoming way. You have
to only answer about food and restaurants only. Don't answer anything that is out of scope of your specific domain. Just politely
refuse to tell them about other stuff. Your knowledge about food and restaurants only comes from the context given to you. Don't
answer the question without the given content. You have tell about which Restuarant the food is from and explain its description to
the user. If a question about food and restaurent is asked and the content didn't have the detail to answer it. Just say the user that
nothing related to that is available.

Current conversation:
{history}

User Input: {query}

Context: {context}

'''


class BonBot:
    def __init__(self, api_key: str, max_output_tokens: int=1200, model="gemini-1.5-pro"):
        self.llm = ChatGoogleGenerativeAI(
                api_key=api_key,
                model=model,
                temperature=0.7,
                max_output_tokens=max_output_tokens,
            )
        self.prompt = PromptTemplate(
                template=HELPER_AGENT_PROMPT,
                input_variables=["query", "context", "history"],
            )
        
        self.chat_history = []
    
    def clear_chat_history(self):
        self.chat_history = []

    def get_llm_chain(self):
       return self.prompt | self.llm | StrOutputParser()