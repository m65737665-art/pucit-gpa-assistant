from dotenv import load_dotenv
import os
from langchain.chat_models import init_chat_model
load_dotenv()
groq_api_key=os.getenv("GROQ_API_KEY")
llm=init_chat_model("groq:openai/gpt-oss-20b",api_key=groq_api_key) 
