import csv
import json
import time
from google import genai
from google.genai import types, errors

client = genai.Client()
#MODEL = "gemini-4-hydrogen"
MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-4-hydrogen",
]

SYSTEM = """You extract data from Nigerian bank alerts.
Dates are written day/month/year.
Return ONLY a JSON object with these keys:
type ("debit" or "credit"), amount (number), currency (string),
merchant_or_sender (string or null), date (YYYY-MM-DD or null),
balance (number or null), reference (string or null).
If a field is missing, use null. Never guess."""

FIELDS = ["type", "amount", "currency", "merchant_or_sender",
          "date", "balance", "reference"]

alerts = [
  
    "Debit alert: NGN 15,500.00 spent at SHOPRITE IKEJA on 12/11/2026. Bal: NGN 84,320.50. Ref: TRX88213",
    "Credit Alert! You received N50,000 from ADEBAYO TUNDE on 03/11/2026. Avail Bal: N134,320.50",
    "Acct debited NGN2,000 AIRTIME MTN 15-Nov-2026. Balance NGN 82,320.50",
    "DEBIT NGN 120,000.00 POS TRANSFER FOODCO LEKKI. Ref 99120AB",
    "Your account has been credited with 1,250.75 NGN. Thank you for banking with us.",
    "Debit alert: NGN 5,000.00 on 14Nov26 at BOLT RIDE. Bal: NGN 77,320.50",
    "Credit: N 25,000.00 from OLUWASEUN A. Value date 2026-11-10. Avail bal N102,320.50 Ref: NIP240981",
    "DEBIT NGN1500 airtime 12/11/26 Bal NGN75820.50",
    "Acct credited NGN 10,000.00 and charged NGN 50.00 stamp duty. Bal NGN 85,000.00 on 16/11/2026.",
    "Dr: 45,000.00 NGN ATM WDL ZENITH ABUJA 09/11/2026 Ref 7781234 Bal 40,000.00",

]

    

MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-4-hydrogen",
]

def extract(text, retries_per_model=3):
    for model in MODELS:
        for attempt in range(retries_per_model):
            wait = 2 ** attempt
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=text,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM,
                        temperature=0,
                        response_mime_type="application/json",
                    ),
                )
                if response.text:
                    return response.text
                print(f"[{model}] empty response, retrying in {wait}s")
            except errors.ClientError as e:
                if e.code == 429:
                    print(f"[{model}] rate limited, waiting 15s")
                    wait = 15
                elif e.code == 404:
                    print(f"[{model}] not available to you, skipping")
                    break          # go to next model
                else:
                    raise
            except Exception as e:
                print(f"[{model}] {type(e).__name__}, retrying in {wait}s")
            time.sleep(wait)
        print(f"Switching away from {model}...")
    return None

rows, failures = [], []

for alert in alerts:
    raw = extract(alert)
    try:
        data = json.loads(raw)
        rows.append({k: data.get(k) for k in FIELDS})
    except (json.JSONDecodeError, TypeError):
        failures.append(alert)
        print("PARSE FAILED for:", alert)
    time.sleep(1)  # be gentle with the free tier

with open("alerts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)

print(f"Done. {len(rows)} saved, {len(failures)} failed. See alerts.csv")

truth = json.load(open("truth.json", encoding="utf-8"))
check_fields = ["type", "amount", "date", "balance", "reference"]

correct = 0
total = 0
for predicted, expected in zip(rows, truth):
    for field in check_fields:
        total += 1
        if predicted.get(field) == expected[field]:
            correct += 1
        else:
            print(f"WRONG {field}: model said {predicted.get(field)!r}, correct is {expected[field]!r}")

print(f"Score: {correct}/{total} = {correct/total:.0%}")

print(f"Alerts parsed: {len(rows)}, answers in truth.json: {len(truth)}")
if len(rows) != len(truth):
    print("STOP: the two lists have different lengths, so the score would be wrong.")