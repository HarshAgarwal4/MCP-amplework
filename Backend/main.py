from fastapi import FastAPI
# from fastapi.middleware import CORSMiddleware
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage,ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from dotenv import load_dotenv
from pydantic import BaseModel , Field
from rich import print
from langchain_mcp_adapters.client import MultiServerMCPClient
import os

class Need_Tool(BaseModel):
    tool_required: bool = Field(
        default=False,
        description="Whether any tool is required to answer the user's query."
    )

load_dotenv()

app = FastAPI()
# app.add_middleware(CORSMiddleware)
llm = ChatGroq(model='openai/gpt-oss-120b' , api_key=os.getenv('GROQ_API_KEY')) 

@app.get("/")
def home():
    return {"message": "API is running"}

@app.post("/chat")
async def chat(data: dict):
    print(f"Data = {data}")
    try:
        message = data.get("message", "")

        if (message is None or message.strip() == ''):
            return {'reply' : 'Invalid user query'}

        need_tool = llm.with_structured_output(Need_Tool).invoke(
    f"""
    Decide whether any tool is required to answer the user's query.

    User Query: {message}

    Return only the structured output:
    - tool_required=True if a tool is needed.
    - tool_required=False if the query can be answered without tools.
    """
)      
        print(need_tool) 
        production = os.getenv('production') == 'true'
        tools=[]
        print(need_tool.tool_required)
        if need_tool.tool_required:
            client = MultiServerMCPClient({
                'my_mcp':{
                    'transport':'http',
                    'url':os.getenv('MCP_BACKEND_URL') if production else 'http://127.0.0.1:8000/mcp'
                }
            })
            tools = await client.get_tools()

        agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt="""
    You are Ample Agent, a helpful AI employee for AmpleWork.

    Rules:
    - For current weather questions, ALWAYS call get_weather.
    - For latest news questions, ALWAYS call get_news.
    - Pass the city mentioned by the user to the appropriate tool.
    - Never invent live weather or news information.
    - Use the tool's result to formulate your answer.
    - For general knowledge questions, answer directly without tools.
    """
        )

        response = await agent.ainvoke({
                "messages": [
                    {"role": "user", "content": message}
                ]
            })

        a = response['messages'][-1].content
        print(response)
        
        return {"reply": a}
    except Exception as e:
        print(e)
        return {'reply' : 'error caught'}