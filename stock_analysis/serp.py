from serpapi import Client
from dotenv import load_dotenv
import os
load_dotenv()

def get_transcript_link(name,q=3, year=2024):
  params = {
    "engine": "google",
    "q": f"{name} latest earning call transcripts",
    "location": "Austin, Texas, United States",

  }

  client = Client(api_key=os.getenv("SERP"))
  results = client.search(params=params)
  # print(results['organic_results'].as_dict())
  link = results["organic_results"][0]['link']
  return link

def get_press_release_link(name,q, year):
  params = {
    "engine": "google",
    "q": f"{name} press release financial results for this Q{q} {year}",
    "location": "Austin, Texas, United States",
  }
  client = Client(api_key=os.getenv("SERP"))
  results = client.search(params=params)
  # print(results['organic_results'].as_dict())
  link = results["organic_results"][0]['link']
  # print("Press release link", link)
  return link

 
import requests

def get_call_transcript(ticker, year, quarter):
    # print(ticker, year, quarter)
    api_url = 'https://api.api-ninjas.com/v1/earningstranscript?ticker={}&year={}&quarter={}'.format(ticker, year, quarter)
    response = requests.get(api_url, headers={'X-Api-Key': os.getenv("TRANSCRIPTS")})
    if response.json():
      # print(response.json())
      transcript = response.json().get("transcript")
      if transcript:
          # print(transcript)
          return transcript
    # print("Error or no transcript found fot:", response.status_code)
    return None

def get_latest_transcript(ticker, year, quarter):
    init_year = year
    init_quarter = quarter
    while year > 0:  # Ensure the loop runs until valid years
        transcript = get_call_transcript(ticker, year, quarter)
        if transcript:
            return {'transcript':transcript, "quarter": quarter,"year":year}
        # Adjust the quarter and year
        quarter -= 1
        if quarter == 0:
            quarter = 4
            year -= 1
        # print(quarter, year)
        if year <= init_year-3:  # Break condition to avoid infinite loop
            break
    print("No transcript found for any valid quarters or years.")
    return {"quarter": init_quarter,"year":init_year-1}



if __name__ == "__main__":
  ticker = 'QMMM'
  year = 2025
  quarter = 3
  get_latest_transcript(ticker, year, quarter)
  # print(get_transcript_link(ticker, q=quarter, year=year))
  # print(get_press_release_link("AAPL", 4, 2024))