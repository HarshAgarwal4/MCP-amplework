
import requests
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()


def get_weather(city: str) -> str:
    """Get current weather of a city like city, bhopal"""

    try:
        api_key = os.getenv("Open_Weather_API_KEY")
        print(api_key)

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"

        response = requests.get(url)
        data = response.json()

        if str(data.get("cod")) != "200":
            return f"Error: {data.get('message', 'Could not fetch weather')}"

        return str(data)

    except Exception as e:
        print(e)
        return "Error: Could not fetch weather"


def get_news(city: str) -> str:
    """Get latest news about a city"""

    try:
        tavily_client = TavilyClient(
            api_key=os.getenv("TAVILY_API_KEY")
        )

        response = tavily_client.search(
            query=f"latest news in {city}",
            search_depth="basic",
            max_results=3
        )

        results = response.get("results", [])

        if not results:
            return f"No news found for {city}"

        news_list = []

        for r in results:
            title = r.get("title", "No title")
            url = r.get("url", "")
            snippet = r.get("content", "")

            news_list.append(
                f"- {title}\n  🔗 {url}\n  📝 {snippet[:100]}..."
            )

        return f"Latest news in {city}:\n\n" + "\n\n".join(news_list)

    except Exception as e:
        print(e)
        return "Error in fetching news due to some technical reason"


if __name__ == "__main__":
    print("\n--- WEATHER ---")
    print(get_weather("Jaipur"))

    print("\n--- NEWS ---")
    print(get_news("Jaipur"))
