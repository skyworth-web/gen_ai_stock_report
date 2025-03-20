import requests
from tavily import TavilyClient
import os
from langchain_community.retrievers import TavilySearchAPIRetriever
# Step 1. Instantiating your TavilyClient


def fetch_news_articles_with(ticker):
    api_key = "9ff80b4d37744fe889be1e43213974b9"  # Your actual API key
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        json_data = response.json()
        print(json_data)
        print("tr")

        if json_data['status'] == "ok":
            articles = json_data['articles']
            analysts = []
            research_articles = []
            references = []

            for article in articles:
                if article.get('author'):
                    analysts.append({'name': article['author'], 'title': article['title'], 'url': article['url']})
                research_articles.append({'title': article['title'], 'url': article['url']})
                references.append(f"{article['source']['name']}: {article['url']}")
                print(references)

            return {
                'references': references[:10] , # Return only the first 10
                'researchArticles': research_articles[:10],  # Return only the first 10
            }
        else:
            print("Error fetching news:", json_data.get('message', 'Unknown error'))
            return {'analysts': [], 'researchArticles': [], 'references': []}

    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return {'analysts': [], 'researchArticles': [], 'references': []}


def fetch_news_articles_with_tavily(ticker):
    # Step 1: Instantiate the Tavily client with your API key
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY"))  # Replace with your actual API key

    # Step 2: Execute a search query for news about the ticker
    response = tavily_client.search(query=f"{ticker} stock news")

    if response['status'] == "ok" and response['articles']:
        articles = response['articles']
        analysts = []
        research_articles = []
        references = []

        for article in articles:
            # Add author details for analyst section if available
            if article.get('author'):
                analysts.append({
                    'name': article['author'],
                    'title': article['title'],
                    'url': article['url']
                })

            # Add article information for research articles
            research_articles.append({
                'title': article['title'],
                'url': article['url']
            })

            # Add source and URL for references
            references.append(f"{article['source']['name']}: {article['url']}")

        # Limit the lists to the first 10 items
        return {
            'analysts': analysts[:10],
            'researchArticles': research_articles[:10],
            'references': references[:10]
        }
    else:
        print("No relevant articles found or an error occurred.")
        return {'analysts': [], 'researchArticles': [], 'references': []}

def get_latest_news(name):
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY"))  # Replace with your actual API key

        response = tavily_client.get_search_context(
            query=f"What are the latest news, trends and developments for ticker {name}", 
                                                    max_results=15, 
                                                    topic='news',
                                                    days=30)
        # response = [{"source":res['url'], "content":res['content'], "title":res['title'], 'date':res['published_date']} for res in response['results']]
        print(response)

def get_press_release(name, q):
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY"))  # Replace with your actual API key

    response = tavily_client.get_search_context(
        query=f" {name} financial press release results for Q{q} .", 
                                                max_results=10, 
                                                )
    
def get_call_transcript():
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY"))  # Replace with your actual API key

    response = tavily_client.search(
        query=f"() earnings call transcripts summary", 
                                                max_results=10, 
                                                )
    


    
# Example usage
if __name__ == "__main__":
    ticker = "Nvidia"
    # news_data = fetch_news_articles_with_tavily(ticker)
    # print("Analysts:", news_data['analysts'])
    # print("Research Articles:", news_data['researchArticles'])
    # print("References:", news_data['references'])

    get_latest_news(ticker)
    # fetch_news_articles_with(ticker)