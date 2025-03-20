import os
os.environ['USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
from langchain_community.document_loaders import WebBaseLoader ,WikipediaLoader
import bs4
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_community.retrievers import TavilySearchAPIRetriever
from dotenv import load_dotenv
load_dotenv()
from tavily import TavilyClient
from langchain_core.retrievers import BaseRetriever
from typing import List
from langchain_community.retrievers import WikipediaRetriever
from warnings import filterwarnings
filterwarnings("ignore")
import yfinance as yahooFinance
from .serp import get_transcript_link, get_press_release_link, get_latest_transcript
from datetime import datetime

def get_date():
    now = datetime.now()
    day_of_week = now.strftime("%A")         # Extensive name of the day, e.g., "Monday"
    date_str = now.strftime("%d/%m/%Y") 
    date = day_of_week + date_str
    return date

def get_data_yfincance(ticker):
    data = yahooFinance.Ticker(ticker)
    return data.info
 
def format_docs(docs):
    return " ".join(doc.page_content for doc in docs)


class SimpleRetriever(BaseRetriever):
    docs: List[Document]
    k: int = 5

    def _get_relevant_documents(self, query: str) -> List[Document]:
        """Return the first k documents from the list of documents"""
        return self.docs
    
# Example usage
class StockDataRetriever:
    def __init__(self, ticker: str, q=3, year=2024, etf=True):
        self.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
        self.etf = etf
        self.ticker = ticker
        self.ticker_data = yahooFinance.Ticker(ticker)
        self.name = self.ticker_data.info.get("longName")
        if not self.etf:
            transcript_dict = get_latest_transcript(ticker=ticker, year=year, quarter=q)
            self.q = transcript_dict['quarter']
            self.year = transcript_dict['year']
            # print("Quarter ", self.q)
            # print("year ", self.year)
            self.transcript_link = get_transcript_link(name=self.name,q=self.q, year=self.year)
            self.press_release_link = get_press_release_link(name=self.name, q=self.q, year=self.year)
    
    def get_data_yfinance(self):
        return self.ticker_data.info
    
    def format_docs(self, docs):
        return " ".join(doc.page_content for doc in docs)

    def get_stats_retriever(self):
        data = self.get_data_yfinance()
        urls = [
            f"https://finance.yahoo.com/quote/{self.ticker}/key-statistics/",
            # f"https://finance.yahoo.com/quote/{self.ticker}/financials/"
        ]
        stats_loader = WebBaseLoader(
            web_path=urls,
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer(attrs={"class": "gridLayout yf-cfn520"})
            ),
            requests_kwargs={"headers":self.headers}
        )
        docs = stats_loader.load() + [Document(page_content=str(data))]
        # print([len(doc.page_content) for doc in docs])
        return SimpleRetriever(docs=docs)
    
    def get_press_release_content(self):
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY"))  # Replace with your actual API key

        response = tavily_client.get_search_context(
                                        query=f"{self.name} announces financial results for Q{self.q} {self.year},", 
                                        max_results=10, 
                                        topic='general',
                                        # days=90,
                                    max_tokens=4000)
        return response
     

    def get_call_transcript_content(self):
        transcript = get_latest_transcript(self.ticker, self.year, self.q).get("transcript", "")
        # print("returning",transcript)
        return transcript

    def get_call_transcript_qna_content(self):
        transcript = get_latest_transcript(self.ticker, self.year, self.q).get("transcript", "")
        return transcript

    def get_analyst_retriever(self):
        urls = [f"https://finance.yahoo.com/quote/{self.ticker}/analysis/"]
        analyst_loader = WebBaseLoader(
            web_path=urls,
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer(attrs={"class": "gridLayout yf-cfn520"})
            )
        )
        docs = analyst_loader.load()
        # print([len(doc.page_content) for doc in docs])
        return SimpleRetriever(docs=docs)

    def get_profile_retriever(self):
        urls = [
            f"https://finance.yahoo.com/quote/{self.ticker}",
            f"https://finance.yahoo.com/quote/{self.ticker}/profile/",
        ]
        profile_loader = WebBaseLoader(
            web_path=urls,
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer("article", attrs={"class": "gridLayout yf-cfn520"})
            )
        )
        wiki_docs = WikipediaRetriever().invoke(self.name)  # Assuming WikipediaRetriever is predefined
        date_doc = [Document(page_content="Latest Date: {}".format(get_date()))]
        docs = date_doc + profile_loader.load() + wiki_docs
        # print(wiki_docs)
        # print([len(doc.page_content) for doc in docs])
        return SimpleRetriever(docs=docs)
    
    def get_news_retriever(self):
        # from news import get_latest_news
        # data = get_latest_news(ticker=self.ticker)
        tavily = TavilySearchAPIRetriever(k=10, 
                                          api_key=os.getenv("TAVILY"),
                                        #   include_raw_content=True
                                          )
        docs = tavily.invoke(f"What are the latest news, trends and developments for {self.ticker}.")
        # print(docs)
        # print([len(doc.page_content) for doc in docs])
        return SimpleRetriever(docs=docs)
    
    def get_references_retriever(self):
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY"))  # Replace with your actual API key
        print(self.name)
        responses = tavily_client.search(
            query=f"What are the latest news, trends and developments for {self.name}", 
                                                    max_results=15,
                                                    topic="general")
        # print(responses)
        responses_list = [{"title":res['title'],"link_url":res['url'], "content":res['content']} for res in responses['results']]
        # [print(res['link_url'],"\n\n",res['content'], end="\n\n")for res in responses_list]
        # docs = [Document(page_content=str(res['content']),metadata={'link_url':res['link_url'], 'title':res['title']} ) for res in responses_list]
        # docs = [Document(page_content=str(res)) for res in responses_list]
        # print(docs)
        # print([len(doc.page_content) for doc in docs])
        # return SimpleRetriever(docs=docs)
        return str(responses_list)
    
    def get_references_quality_retriever(self):
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY"))  # Replace with your actual API key
        query=f"What are the latest news, trends and developments for {self.name}" 
        # print(query)
        query_kwargs = dict(
            query=query,
            max_results=15, 
            topic='news',
            days=100
        )
        # if self.etf:
        #     query_kwargs['include_domains'] = 'seekingalpha.com'

        response = tavily_client.get_search_context(**query_kwargs)        # response = [{"source":res['url'], "content":res['content'], "title":res['title'], 'date':res['published_date']} for res in response['results']]
        # print(response)
        return response
if __name__ == "__main__":
    # resp = wiki_retriever.invoke("TSLA")
    print(str([{'sda':'sfdsd'}]))
    ticker = "VFINX"
    # resp = get_data_yfincance("ASML").get("longName")
    # resp = StockDataRetriever(ticker).get_profile_retriever()
    # resp = StockDataRetriever(ticker=ticker).get_references_with_api_retriever()
    engine = StockDataRetriever(ticker=ticker,year=2025, q=3, etf=False)
    print(engine.name)
    resp = engine.get_profile_retriever()
    # print(resp.get_references_quality_retriever())
    # print(resp.get_news_retriever())
    # loader = WebBaseLoader(web_path="https://seekingalpha.com/article/4668072-viasat-inc-vsat-q3-2024-earnings-call-transcript")
    print(resp)