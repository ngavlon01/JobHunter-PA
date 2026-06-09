import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])

def search_jobs(role, location):
    jobs = []
    try:
        query = f"{role} {location}"
        url = f"https://www.indeed.com/jobs?q={query.replace(' ','+')}&l=South+Africa"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.find_all("h2", class_="jobTitle", limit=5)
        for card in cards:
            title = card.get_text(strip=True)
            if title:
                jobs.append(title)
    except Exception as e:
        print(f"Scraping error: {e}")
    return jobs

@app.command("/findjobs")
def handle_findjobs(ack, body, client):
    ack()
    query = body["text"]
    channel = body["channel_id"]
    user_id = body["user_id"]

    parts = query.strip().split()
    role = parts[0] if len(parts) > 0 else "general"
    location = parts[1] if len(parts) > 1 else "South Africa"

    client.chat_postMessage(
        channel=channel,
        text=f"🔍 Searching for *{role}* jobs in *{location}*... hang tight Your Majesty! 👑"
    )

    jobs = search_jobs(role, location)

    if jobs:
        job_list = "\n".join([f"✅ {job}" for job in jobs])
        message = (
            f"*Here are fresh {role} jobs in {location}:*\n\n"
            f"{job_list}\n\n"
            f"🌍 View more: https://www.indeed.com/jobs?q={role}&l=South+Africa\n\n"
            f"💪 Keep pushing Your Majesty — your next job is out there!"
        )
    else:
        message = (
            f"😔 No jobs found for *{role}* in *{location}* right now.\n\n"
            f"💡 Try a broader search like:\n"
            f"`/findjobs driver Johannesburg`\n"
            f"`/findjobs accountant Pretoria`\n\n"
            f"💪 Don't give up Your Majesty!"
        )

    client.chat_postMessage(
        channel=channel,
        text=message
    )

if __name__ == "__main__":
    handler = SocketModeHandler(
        app,
        os.environ["SLACK_APP_TOKEN"]
    )
    handler.start()