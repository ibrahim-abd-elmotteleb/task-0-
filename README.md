DEMO
https://drive.google.com/drive/folders/1DiJZmoPNCzCqLBVV-XG8ryvy4cmkIgzc?usp=sharing

# Task 0 — Agentic Incident Flow on ServiceNow PDI

Automatically triages new ServiceNow incidents using Gemini AI and a fixed set of
knowledge-base articles. When someone opens a ticket, this service reads it, decides
whether to **respond** (auto-resolve), **ask** (request more info), or **escalate**
(hand off to a human) — and writes that decision straight back onto the same ticket,
with no manual steps.

## How it works

1. A ServiceNow Business Rule fires whenever a new Incident is created and POSTs the
   ticket data to this service's `/webhook` endpoint.
2. FastAPI immediately accepts it (`202`) and processes the rest in the background.
3. The background task sends the ticket text plus the 5 knowledge-base articles to
   Gemini, asking for a JSON decision.
4. The service writes that decision back to the same incident via ServiceNow's REST
   Table API.

## Technologies

- Python 3.11+, FastAPI, Uvicorn
- Gemini API (`google-generativeai`)
- ServiceNow PDI (REST Table API, Basic Auth)
- ngrok (public tunnel to your local machine)

## Prerequisites

- Python 3.11+
- A free ServiceNow PDI (developer.servicenow.com)
- A free Gemini API key (aistudio.google.com)
- ngrok installed

## Setup

### 1. Clone this repository

```bash
git clone <your-repo-url>
cd task0
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn google-generativeai python-dotenv requests
```

### 3. Create your `.env` file

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Fill in the values:

```
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com
SERVICENOW_USERNAME=admin
SERVICENOW_PASSWORD=your_admin_password
```

### 4. Grant your ServiceNow user API access

As of mid-2026, new ServiceNow PDIs block plain Basic Auth on the REST API by
default. Give your admin user the extra role:

1. In ServiceNow, go to **User Administration > Users** and open the `admin` user.
2. Open the **Roles** tab, click **Edit**, search for `snc_basic_auth_api_access`,
   add it, and save.

### 5. Start the FastAPI service

```bash
uvicorn main:app --port 8080 --reload
```

### 6. Expose it with ngrok

In a separate terminal:

```bash
ngrok http 8080
```

Copy the `https://....ngrok-free.dev` URL it gives you.

### 7. Create the ServiceNow Business Rule

1. In ServiceNow, go to **System Definition > Business Rules > New**.
2. Name: `Task0 - Send Incident to Agent`, Table: `Incident [incident]`, check
   **Advanced**.
3. **When to run** tab: When = `after`, check **Insert**.
4. **Advanced** tab: paste the script from `business_rule.js`, replacing
   `YOUR_ENDPOINT` with your ngrok URL (keep `/webhook` at the end).
5. Click **Submit**.

### 8. Test it

Create a new Incident in ServiceNow with a short description like "Printer not
printing after office move". Within a few seconds, refresh the ticket — you should
see a decision written back (Resolution notes, Comments, or Work notes, depending on
the decision).

## Notes

- Every time you restart ngrok, its URL changes — update the Business Rule script
  with the new URL each time.
- The Gemini prompt used by this service lives in `prompts.py`, committed exactly as
  sent to the API.
- `.env` is git-ignored; never commit real credentials. Use `.env.example` as the
  template.
