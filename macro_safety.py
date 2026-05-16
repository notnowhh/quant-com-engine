import asyncio
import feedparser
import erniebot
import os
from dotenv import load_dotenv

load_dotenv()
erniebot.api_type = 'aistudio'
erniebot.access_token = os.getenv("BAIDU_ACCESS_TOKEN")

async def verify_macro_volatility(latest_news_text):
    """Evaluates text logic to determine if auto-execution should be blocked."""
    if not latest_news_text:
        return False, "No data"

    print(f"\n🛡️ Macro Gatekeeper evaluating context: '{latest_news_text[:60]}...'")
    
    # Strict instruction formatting to isolate volatility risks
    prompt = (
        f"Analyze this news: '{latest_news_text}'. "
        "If it introduces extreme macro volatility (Trump policies, Fed meetings, SEC news), "
        "reply in this EXACT format: VOLATILE | [Short Reason]. "
        "Example: VOLATILE | Trump Tariff Announcement. "
        "If safe, reply: CLEAR | SAFE."
    )
    
    for attempt in range(3):
        try:
            response = await asyncio.to_thread(
                erniebot.ChatCompletion.create,
                model='ernie-3.5',
                messages=[{'role': 'user', 'content': prompt}]
            )
            result = response.get_result().strip()
            
            if "VOLATILE" in result:
                return True, result
            else:
                return False, result
        except Exception as e:
            if attempt == 2:
                print(f"❌ Gatekeeper API Timeout: {e}")
                return True, "API_FAILURE_DEFAULT_VOLATILE" # Fail-safe: assume dangerous if API drops
            await asyncio.sleep(2)