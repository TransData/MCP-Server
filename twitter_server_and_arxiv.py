from mcp.server.fastmcp import FastMCP
import requests
import xml.etree.ElementTree as ET
import json
from typing import Tuple, List
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import httpx

mcp = FastMCP("combined_server",port=8080)

@mcp.tool()
async def search_arxiv(topic, max_results=15):
    """
    Search for arXiv papers related to a topic.

    Parameters:
        topic (str): The topic or keywords to search for.
        max_results (int): Number of results to retrieve.

    Returns:
        List of dictionaries with paper details (title, authors, summary, link).
    """
    base_url = "http://export.arxiv.org/api/query?"
    query = f"search_query=all:{topic}&start=0&max_results={max_results}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(base_url + query)

    if response.status_code != 200:
        raise Exception("Failed to fetch results from arXiv API.")

    root = ET.fromstring(response.content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    papers = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip()
        summary = entry.find('atom:summary', ns).text.strip()
        link = entry.find('atom:id', ns).text.strip()
        authors = [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)]
        papers.append({
            'title': title,
            'authors': authors,
            'summary': summary,
            'link': link
        })

    return papers


@mcp.tool()
async def scrap_twitter_for_social_mentions(query: str, token:str,max_results: int = 10) -> List[dict]:
    """
    Scrape Twitter for social mentions based on a query.

    Args:
        query (str): The search query for Twitter.
        max_results (int): Maximum number of tweets to retrieve.

    Returns:
        List[dict]: A list of dictionaries containing tweet data.
    """
    # Mock response object
    """class MockResponse:
        def __init__(self):
            self.status_code = 200

        @property
        def text(self):
            return json.dumps(self.json())

        def json(self):
            return {
                "text": [
                    {"id": "1904628288728768522", "text": "RT @siasatpk: اگر آپ نے سارے راستے بند کردیے ہیں تو یاد رکھیں، عمران خان بہت مضبوط ہیں اور وہ صرف اللہ سے مدد مانگتے ہیں۔ علیمہ خان @Aleema…"},
                    {"id": "1904628237898338684", "text": "RT @siasatpk: اگر آپ نے سارے راستے بند کردیے ہیں تو یاد رکھیں، عمران خان بہت مضبوط ہیں اور وہ صرف اللہ سے مدد مانگتے ہیں۔ علیمہ خان @Aleema…"},
                    {"id": "1904628136467390506", "text": "RT @siasatpk: اگر آپ نے سارے راستے بند کردیے ہیں تو یاد رکھیں، عمران خان بہت مضبوط ہیں اور وہ صرف اللہ سے مدد مانگتے ہیں۔ علیمہ خان @Aleema…"},
                    {"id": "1904628132394787017", "text": "RT @eyeonpakistan_: Imran Khan from Adiala Jail: \"Streets will be heated everywhere, after Eid there will only be protests in Pakistan!\"  #…"},
                    {"id": "1904628012349530127", "text": "RT @newsonepk: آئین کی Flexibilityپر! ایثاررانا نے انور مسعود کی نظم سُنا دی! #ImranKhan #BabarAwan #IsarRana #AdialaJail #PakistanPolitics…"},
                    {"id": "1904627999519252650", "text": "RT @siasatpk: اگر آپ نے سارے راستے بند کردیے ہیں تو یاد رکھیں، عمران خان بہت مضبوط ہیں اور وہ صرف اللہ سے مدد مانگتے ہیں۔ علیمہ خان @Aleema…"},
                    {"id": "1904627959211704530", "text": "RT @rRaomAzamKhan: پاکستان تحریک انصاف ماڈل ٹاؤن کی جانب عمران خان افطار دسترخوان کا اہتمام کیا گیا۔ جس میں پاکستان تحریک انصاف ڈسٹرکٹ ملیر…"},
                    {"id": "1904627938449928573", "text": "RT @siasatpk: اگر آپ نے سارے راستے بند کردیے ہیں تو یاد رکھیں، عمران خان بہت مضبوط ہیں اور وہ صرف اللہ سے مدد مانگتے ہیں۔ علیمہ خان @Aleema…"},
                    {"id": "1904627905633935655", "text": "RT @siasatpk: Video : https://t.co/F6Lah9UDec \"بہت سوں کو یہ امید نہیں تھی، مگر عمران خان بڑی دلیری اور ثابت قدمی سے جیل کاٹ رہے ہیں۔\"جگنو…"},
                    {"id": "1904627890064679212", "text": "RT @eyeonpakistan_: Imran Khan from Adiala Jail: \"Streets will be heated everywhere, after Eid there will only be protests in Pakistan!\"  #…"}
                ]
            }

    response = MockResponse()

    if response.status_code == 200:
        return response.json()["text"]
    else:
        raise Exception("Failed to fetch tweets from Twitter API.")"""
    
    url = "https://plankton-app-ili4n.ondigitalocean.app/scrape_twitter"  # Update if using a different host/port

    payload = {
        "token": token,  # Replace with your Twitter API Bearer token for testing
        "query": query,       # The search query, e.g., 'python'
        "max_res": max_results             # Maximum number of tweets to retrieve
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, json=payload)

    if response.status_code == 200:
        print(response.text)
        return response.text
    else:
        error_msg = f"Error: {response.status_code}"
        return {"error": error_msg, "detail": response.text}


if __name__ == "__main__":
    mcp.run(transport="sse")
