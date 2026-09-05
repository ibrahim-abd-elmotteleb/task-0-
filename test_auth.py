import os
from dotenv import load_dotenv
import requests

load_dotenv()

SN_URL = os.getenv("SERVICENOW_INSTANCE_URL")
SN_USER = os.getenv("SERVICENOW_USERNAME")
SN_PASS = os.getenv("SERVICENOW_PASSWORD")

print(f"URL loaded as: {SN_URL}")
print(f"USER loaded as: {SN_USER}")
print(f"PASSWORD loaded, length: {len(SN_PASS) if SN_PASS else 'MISSING'}")

resp = requests.get(f"{SN_URL}/api/now/table/incident?sysparm_limit=1", auth=(SN_USER, SN_PASS))
print(f"Status code: {resp.status_code}")
print(resp.text[:300])