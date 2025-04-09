import os
import requests
from dotenv import load_dotenv
import json
import re

load_dotenv()

API_KEY = "sk-317a77a7add641f8b36a6850cff659fb"
API_URL = "https://api.deepseek.com/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def analyze_comment(comment):
    prompt = f"""
Analyze the following customer comment and extract:
1. Sentiment: Positive, Neutral, or Negative.
2. Category: Broad category (e.g., Delivery, Product Quality, Customer Service).
3. Key Themes: Key points in brief phrases.

Comment: "{comment}"

Return JSON like this (only pure JSON inside triple backticks please):
```json
{{
  "sentiment": "...",
  "category": "...",
  "themes": ["...", "..."]
}}
```
"""

    try:
        response = requests.post(API_URL, headers=headers, json={
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        })

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # 提取 JSON 内容
        match = re.search(r'```json\n(.*?)```', content, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return content

    except Exception as e:
        return f"ERROR: {e}"
