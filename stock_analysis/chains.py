import os
from dotenv import load_dotenv
load_dotenv(".env")
from langchain_core.output_parsers import StrOutputParser  
from langchain_core.prompts import ChatPromptTemplate  
from langchain_core.runnables import RunnablePassthrough  
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from .retrieval import StockDataRetriever
from datetime import datetime

def format_docs(docs):
    return " ".join(doc.page_content for doc in docs)

def init():
    groq_api_key = os.getenv("UMAIS")
    os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY")
    open_api_key = os.getenv("OPENAI")
    llm = ChatOpenAI(api_key=open_api_key, model="gpt-4o", temperature=0.2)
    return llm

llm = init()

class BaseAnalysisChain:
    def __init__(self, ticker, q=3, etf=True, year=2024):
        self.llm = init()
        self.ticker = ticker
        self.stock_data_retriever = StockDataRetriever(self.ticker, q=q, year=year, etf=etf)  # Initialize StockDataRetriever here
        self.name = self.stock_data_retriever.name 
        self.transcript_link = self.stock_data_retriever.transcript_link if not etf else ""
        self.press_release_link = self.stock_data_retriever.press_release_link if not etf else ""
        
        self.retriever, self.prompt = self._get_retriever_and_prompt()
        # print(self.prompt)
        self.chain = self.make_chain()

    def _get_retriever_and_prompt(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def make_chain(self):
        return (
            {"context": self.retriever | format_docs, "ticker": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def execute_chain(self) -> str:
        try:
            return self.chain.invoke({"ticker": self.ticker})
        except Exception as e:
            print(f"Error faced:{e}")
            return ""
# Subclasses only specify which retriever and prompt to use

class TechnicalAnalysisChain(BaseAnalysisChain):
    def _get_retriever_and_prompt(self):
        retriever = self.stock_data_retriever.get_stats_retriever()
        prompt = ChatPromptTemplate.from_template(
            """
            Using the context given, generate a concise technical analysis summary for a one-page report on {ticker}, focusing on key insights from the following financial indicators. Aim for a balance of brevity and relevance, providing interpretations of recent trends and signals based on these indicators:
            
            Relative Strength Index (RSI): Describe its current level, noting any significant movement towards overbought (above 70) or oversold (below 30) conditions.

            Moving Average Convergence Divergence (MACD): Summarize recent crossovers of the MACD line with the signal line, indicating either bullish or bearish momentum. Mention any notable divergence or convergence patterns.

            50-day and 200-day Moving Averages: Indicate whether the current price of {ticker} is above or below these averages, which could signal potential upward or downward momentum.

            Bollinger Bands: Describe the current price position of {ticker} relative to the bands (e.g., nearing the upper band for possible overbought conditions or the lower band for possible oversold conditions).

            Combine these insights into a coherent analysis, offering a high-level overview of the market sentiment for {ticker}. Avoid using raw data, and instead interpret these indicators to help investors make informed entry and exit decisions.
            Context: {context}
            """
        )
        return retriever, prompt

class FundamentalAnalysisChain(BaseAnalysisChain):
    def _get_retriever_and_prompt(self):
        retriever = self.stock_data_retriever.get_stats_retriever()
        prompt = ChatPromptTemplate.from_template(
            """
            Using the context, provide a report of the financial fundamentals for ticker {ticker}.
            Context: {context}  
            Question: "
            Fundamental Analysis 500-1000 words using the context.
            start with the h1 heading: "# Fundamental Analysis:"

            If the ticker is a mutual fund, only show metrics related to it.

            If a metric is not available, do not mention it in the report.
            Examples of metrics are :
            P/E ratio:
            Quarterly Revenue:
            Yearly Revenue:
            Ex dividend date:
            Yield %:
            Profit/ Loss per Qtr:
            Profit/ Loss per Year:
            Market Cap:
            Also mention other metrics in the context that are used in fundamental analysis.

            If the mutual fund or ETF contains holdings, generate a single markdown section titled Holdings and Sector Allocation using an H1 heading (#) like "# Holdings and Sector Allocation". Ensure this section appears only once and is placed after the main content without duplication.
            """
        )
        return retriever, prompt

    def execute_chain(self) -> str:
        try:
            output = self.chain.invoke({"ticker": self.ticker})
            return output.replace("## Holdings and Sector Allocation", "# Holdings and Sector Allocation")
        except Exception as e:
            print(f"Error faced:{e}")
            return ""
    

class CompanyOverviewChain(BaseAnalysisChain):
    def _get_retriever_and_prompt(self):
        retriever = self.stock_data_retriever.get_profile_retriever()
        prompt = ChatPromptTemplate.from_template(
            """
            Using the context, provide a 1000-1500 words report of the symbol {ticker}.
            Context: {context}[END OF CONTEXT]

            Describe {ticker}, in these headings:
            Ticker : (ticker)

            Exchange Traded On:
            Specify the exchange (e.g., NYSE, NASDAQ).

            Ticker Price:
            Provide the most recent stock price as of the current market date and time (e.g., March 12, 2024, 2:45 PM EST).
            Display the stock price in bold and include the currency symbol (e.g., $237.38).

            Summary:
                Make an extensive report 1000 words, using context.
                Key findings, Overall Performance, and Insights.

            About (ticker):
            Brief description of the company or mutual fund/ETF.

            Management Team:
            Key executives and their roles.

            Products/Services:
            Overview of main products or services offered.
            """.format(context="{context}", ticker='{ticker}')
        )
        return retriever, prompt
    

class AnalystCoverageChain(BaseAnalysisChain):
    def _get_retriever_and_prompt(self):
        retriever = self.stock_data_retriever.get_analyst_retriever()
        prompt = ChatPromptTemplate.from_template(
            """
Context: {context}

Task: Summarize the latest analyst coverage for {ticker}, using the provided context. Include insights into how analysts and the industry view the stock, along with the latest ratings. If available, provide the following details in a structured format:

Price Target $: [Value]
Analyst Name: [Name]
Rating: [e.g., Buy, Sell, Neutral, Overweight, etc.]
List up to 10 entries, with a minimum of 5 if possible, and format each entry as follows:

Example Output:

Price Target $: 300 | Analyst: Jane Doe | Rating: Buy
Price Target $: 280 | Analyst: John Smith | Rating: Neutral
If analyst ratings are unavailable, explain why they may not be present. For example, {ticker} could be a mutual fund, ETF, or an index that typically does not receive individual analyst ratings.
            """.format(context="{context}", ticker="{ticker}")
        )
        return retriever, prompt

class NotableFactsChain(BaseAnalysisChain):
    def _get_retriever_and_prompt(self):
        retriever = self.stock_data_retriever.get_news_retriever()
        prompt = ChatPromptTemplate.from_template(
            """
            Using the provided context, identify and summarize the 5 most notable recent facts, trends, or
            developments about {ticker}. Focus on recent updates, competitive landscape changes, market
            trends, or other impactful events. For each fact, provide a brief explanation and its significance.
            Give a recommendation and then end with a conclusion based on these insights.
            Context: {context}
            """
        )
        return retriever, prompt
    
    def execute_chain(self) -> str:
        try:
            output = super().execute_chain()
            # output.replace("## ")
            return output.replace("### Recommendations", "# Recommendations")
        except Exception as e:
            print(f"Error faced:{e}")
            return ""
        
class ReferencesChain(BaseAnalysisChain):
    def __init__(self, ticker, q=3, etf=False, year=2024):
        super().__init__(ticker, q, etf, year)

    def _get_retriever_and_prompt(self):
        self.name = self.stock_data_retriever.name
        self.context = self.stock_data_retriever.get_references_quality_retriever()
        prompt_string =     """
Here’s an optimized version of your prompt to ensure it focuses on retrieving around **10-15 articles** and providing concise summaries:

---

**Context:**  
{context}  

**Task:**  
From the context, identify and summarize all **12-15 articles**. Prioritize the most recent or impactful articles. For each, provide a extensive summary along with its title and URL.  

---

**Output Format:**  

#### 1. [Article Title](Article URL)  
   **Summary**: [Concise summary of the article content]  

#### 2. [Article Title](Article URL)  
   **Summary**: [Concise summary of the article content]  

#### 3. [Article Title](Article URL)  
   **Summary**: [Concise summary of the article content]  

…and so on for up to **15 articles**. Ensure all information is accurate and focused on key takeaways. Do not include headings or labels such as "Article List:"


After listing all articles, create a **References** section that includes only the links in the following format:  

- Ensure **the first one or two references** are listed **exactly as provided** in Markdown format in the prompt:
  - `https://www.finance.yahoo.com/quote/{symbol}/`
  - `{transcript_link}` (insert a link here if this is a placeholder)
- For the remaining links, list them in Markdown format, ensuring no duplicates.  

**References Format:**

## References:
1. [https://www.finance.yahoo.com/quote/{symbol}/](https://www.finance.yahoo.com/quote/{symbol}/)  
2. [{transcript_link}]({transcript_link})  
3. [Source URL]  
4. [Source URL]  
...up to 10+ unique links


**Instructions for Output:**  
1. Retain the exact text of the link of the first two references.  
2. Include all links used in the article list in the **References** section.  
3. Ensure proper Markdown formatting, with links listed sequentially and without additional text or duplicates.
""".format(context="{context}", ticker="{ticker}", transcript_link=self.transcript_link if self.transcript_link else f"https://seekingalpha.com/symbol/{self.ticker}/holdings", symbol=self.ticker)

        # print(prompt_string)
        prompt = ChatPromptTemplate.from_template(prompt_string
        )
        return self.context, prompt
    
    def make_chain(self):
        # Build chain without a retriever, using `self.context` as direct input
        return (
            {"context": RunnablePassthrough(), "ticker": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def execute_chain(self) -> str:
        try:
            return self.chain.invoke({"context":self.context, "ticker": self.name})
        except Exception as e:
            print(f"Error faced:{e}")
            return ""
    
class PressReleaseChain(BaseAnalysisChain):
    def __init__(self, ticker, q, etf=False, year=2024):
        # Initialize BaseAnalysisChain and set up the LLM and prompt
        super().__init__(ticker, q,etf=False, year=year)
        self.context = self.stock_data_retriever.get_press_release_content()  # Direct context string

    def _get_retriever_and_prompt(self):
        # No retriever needed, so we return None for retriever
        prompt = ChatPromptTemplate.from_template(
            """
            Context: {context}
The following is all available context about recent press releases for {ticker}.

Please summarize the articles as one cohesive report in the following format:

Title:
Date: [date of the most recent article]
Press Release Link: {press_release_link}

Summary:
Write a comprehensive 700-word summary that consolidates the main points from all articles, addressing the central themes and key takeaways across all sources.
            """.format(context="{context}", ticker="{ticker}", press_release_link=self.press_release_link)
        )
        return None, prompt

    def make_chain(self):
        # Build chain without a retriever, using `self.context` as direct input
        return (
            {"context": RunnablePassthrough(), "ticker": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def execute_chain(self):
        # Execute chain with ticker and pre-fetched context string
        try:
            return self.chain.invoke({"context":self.context, "ticker": self.name})
        except Exception as e:
            print(f"Error faced:{e}")
            return ""


class CallTranscriptChain(BaseAnalysisChain):
    def __init__(self, ticker, q, year):
        # Initialize BaseAnalysisChain and set up the LLM and prompt
        super().__init__(ticker,q, year=year, etf=False)
        self.context = self.stock_data_retriever.get_call_transcript_content()  # Fetch call transcript content as a string

    def _get_retriever_and_prompt(self):
        # No retriever needed, so return None for retriever
        prompt = ChatPromptTemplate.from_template(
            """
            Context: {context}
            The following is a summary of the latest earnings call for {ticker}:
            Please provide the summary in the following format:
            **Quarter number and Date**: The quarter which the summary is for, and the date of release.
            Transcript Link: [{transcript_link}]({transcript_link})
            **Present Company Representatives**: List of key company personnel (e.g., CEO, CFO).
            **Main Discussion Topics**: Brief overview of the primary topics covered in the call.
            **Overall Tone and Future Outlook**: Summarize the tone of the call, any forward-looking statements, and major takeaways.
            Write 1000-1500 words.
            Note: Links should be in markdown format
            """.format(context="{context}", ticker="{ticker}", transcript_link=self.transcript_link)
        )
        return None, prompt

    def make_chain(self):
        # Build chain without a retriever, using `self.context` as direct input
        return (
            {"context": RunnablePassthrough(), "ticker": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def execute_chain(self):
        # Execute chain with ticker and pre-fetched context string
        try:
            if self.context == "":
                raise Exception("No transcript found")
            else:
                return self.chain.invoke({"context":self.context, "ticker": self.name})
        except Exception as e:
            print(f"Error doing call transcripts: {e}")
            return ""
    
class QnATranscriptsCallChain(BaseAnalysisChain):
    def __init__(self, ticker, q, year):
        # Initialize the base chain and retrieve the Q&A transcript content directly
        super().__init__(ticker, q, year=year, etf=False)
        self.context = self.stock_data_retriever.get_call_transcript_content()  # Fetch Q&A content as a string

    def _get_retriever_and_prompt(self):
        # No retriever needed, so return None for retriever
        prompt = ChatPromptTemplate.from_template(
            """
            The context is a summary of the transcript from the latest earnings call for {ticker}:
            
            Please provide the summary in the following format:
            **Investor Questions and Responses**:
            
            - **Question 1**: Brief summary of the question.\n
              **Response**: Summary of the response from the company.
            
            - **Question 2**: Brief summary of the question.\n
              **Response**: Summary of the response from the company.
            
            Continue in this format, summarizing the key questions and answers. Focus on the most insightful or critical responses.
            Make sure to include the name of the person which asked or answered a question, if mentioned. There should be at least 8 questions and responses.
            
            Context: {context}
            """
        )
        return None, prompt

    def make_chain(self):
        # Build chain without a retriever, using `self.context` directly
        return (
            {"context": RunnablePassthrough(), "ticker": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def execute_chain(self):
        # Execute chain with ticker and the pre-fetched context
        try:
            if self.context == "":
                raise Exception("No transcript found for this ticker")
            else:
                return self.chain.invoke({"context":self.context, "ticker": self.name})
        except Exception as e:
            print(f"Error doing Q&A for call transcripts: {e}")
            return ""
    

if __name__ == "__main__":
    ticker = "QYLD"
    etf=False
    # etf = False
    # note= AnalystCoverageChain(ticker=ticker).execute_chain()
    note= CompanyOverviewChain(ticker).execute_chain()
    # note = FundamentalAnalysisChain(ticker).execute_chain()
    # note = ReferencesChain(ticker, etf=etf).execute_chain()
    # with open("test.txt","w") as t:
    #     t.write(note)
    # response = fund.execute_chain()
    # print(overview)
    # note = PressReleaseChain(ticker, q=4, year=2025).execute_chain()
    # print(note)
    # print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    # note = NotableFactsChain(ticker).execute_chain()
    # note= QnATranscriptsCallChain(ticker=ticker, q=4, year=2024).execute_chain()
    # print(note)
    # note = CallTranscriptChain(ticker=ticker, q=4, year=2024).execute_chain()
    print(note)
    # import markdown2
    # print(note.replace("## Holdings and Sdector Allocation", "# Holdings and Sector Allocation"))
    # print(markdown2.markdown(note))
    # # print(ac)