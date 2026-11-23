# bank-alert-extractor
Extract structured data from Nigerian bank alerts using an LLM
# Bank Alert Extractor

Turns messy Nigerian bank alert SMS messages into clean structured data (CSV)
using a Gemini model.

## What it does
- Reads bank alerts as plain text
- Extracts type, amount, currency, merchant/sender, date, balance and reference
- Retries on server errors and falls back to other models
- Scores itself against hand-written correct answers (`truth.json`)

## How to run
1. `pip install google-genai`
2. Get a free API key from aistudio.google.com
3. Set it as an environment variable: `setx GEMINI_API_KEY "your-key"`
4. Run `python test3.py`

## Results
| Test set | Accuracy |
|----------|----------|
| 10 alerts (varied formats) | 50/50 fields (100%) |

## Problems I ran into
- DNS failure (`getaddrinfo failed`): fixed by changing DNS servers
- Model not available / overloaded (404, 503): added a fallback list of models
- Dropped connections: added retries with exponential backoff
- Low score caused by misaligned test files: added a length check

## What I learned
[Write 2 or 3 sentences in your own words.]

## Next steps
- Test on more real, messy alerts
- Add few-shot examples and compare accuracy
- Wrap in a FastAPI web service
