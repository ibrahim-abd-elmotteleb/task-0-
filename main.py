import os
import requests
from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv
import google.generativeai as genai
import re
import json
from prompts import PROMPT_TEMPLATE
from fastapi import HTTPException

load_dotenv()

app = FastAPI()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))

# ServiceNow credentials from the .env vault
SN_URL = os.getenv("SERVICENOW_INSTANCE_URL")
SN_USER = os.getenv("SERVICENOW_USERNAME")
SN_PASS = os.getenv("SERVICENOW_PASSWORD")
print(f"DEBUG CHECK -> URL: {SN_URL} | USER: {SN_USER} | PASS: {SN_PASS}")
# In-memory guard to prevent double-processing (FR5)
processed_tickets = set()

def process_ticket_background(ticket_data: dict):
    incident_sys_id = ticket_data.get("incident_sys_id")

    if incident_sys_id in processed_tickets:
        return
    processed_tickets.add(incident_sys_id)

    short_desc = ticket_data.get("short_description", "")
    desc = ticket_data.get("description", "")

    prompt = PROMPT_TEMPLATE.format(short_desc=short_desc, desc=desc)

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        cleaned = re.sub(r"^```json\s*|^```\s*|```$", "", raw_text, flags=re.MULTILINE).strip()

        try:
            parsed = json.loads(cleaned)
            decision = parsed.get("decision", "ask")
            message = parsed.get("message", "Could not parse AI response.")
        except json.JSONDecodeError:
            print(f"Could not parse Gemini's JSON: {raw_text}")
            decision = "ask"
            message = "Automated triage could not parse a decision - please review manually."

        print(f"Parsed decision: {decision} | message: {message}")

        patch_url = f"{SN_URL}/api/now/table/incident/{incident_sys_id}"
        headers = {"Content-Type": "application/json"}

        if decision == "respond":
            payload = {
                "work_notes": message,
                "state": 6,
                "close_notes": message,
                "close_code": "Solution provided"
            }
        elif decision == "ask":
            payload = {"comments": message}
        else:
            payload = {"work_notes": f"Escalated: {message}"}

        resp = requests.patch(patch_url, auth=(SN_USER, SN_PASS), headers=headers, json=payload)
        print(f"ServiceNow responded with status: {resp.status_code}")
        print(f"ServiceNow said: {resp.text}")

    except Exception as e:
        print(f"Error processing background task: {e}")

@app.post("/webhook", status_code=202)
@app.post("/webhook", status_code=202)
async def receive_ticket(request: Request, background_tasks: BackgroundTasks):
    try:
        ticket_data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if "incident_sys_id" not in ticket_data:
        raise HTTPException(status_code=400, detail="Missing required field: incident_sys_id")

    background_tasks.add_task(process_ticket_background, ticket_data)
    return {"status": "Accepted"}