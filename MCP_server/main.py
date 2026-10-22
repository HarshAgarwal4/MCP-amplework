from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

PRODUCTION = os.getenv('production') == "true"

mcp = FastMCP(
    "my_mcp",
    json_response=True,
    stateless_http=PRODUCTION,
    host='0.0.0.0' if PRODUCTION else '127.0.0.1',
    port=8000
)

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather of a city like city , bhopal"""

    try:    
        api_key = os.getenv("Open_Weather_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
        
        response = requests.get(url)
        data = response.json()

        if str(data.get("cod")) != "200":
            return f"Error: {data.get('message', 'Could not fetch weather')}"
        
        return str(data)
    except Exception as e:
        print(e)
        return "Error: {data.get('message', 'Could not fetch weather')}"

@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for any topic, including current information, latest updates,
    recent news, technical documentation, people, companies, and general research."""

    try:
        tavily_client = TavilyClient(
            api_key=os.getenv("TAVILY_API_KEY")
        )

        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True,
        )

        results = response.get("results", [])

        if not results:
            return f"No relevant web results found for: {query}"

        output = []

        answer = response.get("answer")
        if answer:
            output.append(f"Search summary:\n{answer}")

        for i, result in enumerate(results, start=1):
            title = result.get("title", "Untitled")
            url = result.get("url", "")
            content = result.get("content", "")

            output.append(
                f"{i}. {title}\n"
                f"URL: {url}\n"
                f"Content: {content}"
            )

        return f"Web search results for '{query}':\n\n" + "\n\n".join(output)

    except Exception as e:
        print(f"Web search failed: {e}")
        return "Error: A technical issue prevented the web search."
    
if __name__ == "__main__":
        mcp.run(
            transport="streamable-http",
        )