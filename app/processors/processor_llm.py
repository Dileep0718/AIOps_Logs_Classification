"""

processor_llm.py

----------------

Classifies logs using Groq LLM (DeepSeek model).
 
Used for:

  - LegacyCRM logs (unstructured, no training data)

  - Any log that falls through regex and BERT
 
The LLM is prompted to return one of the known labels.

"""
 
import re

from groq import Groq

from app.config import settings
 
# initialize Groq client once

_client = Groq(api_key=settings.GROQ_API_KEY)
 
# all possible labels the LLM can return

VALID_LABELS = [

    "HTTP Status",

    "User Action",

    "System Notification",

    "Resource Usage",

    "Error",

    "Critical Error",

    "Security Alert",

    "Workflow Error",

    "Deprecation Warning",

    "Unclassified",

]
 
SYSTEM_PROMPT = f"""

You are a log classification expert for an enterprise AIOps system.

Classify the given log message into exactly one of these categories:
 
{chr(10).join(f'- {label}' for label in VALID_LABELS)}
 
Rules:

- Return ONLY the category name inside <category> tags

- Example: <category>Critical Error</category>

- Do not explain, do not add any other text

- If unsure, return <category>Unclassified</category>

"""
 
 
def classify_with_llm(log_message: str) -> str:

    """

    Classify a log message using the Groq LLM.
 
    Returns:

        label (str) — one of VALID_LABELS

    """

    try:

        response = _client.chat.completions.create(

            model="deepseek-r1-distill-llama-70b",

            messages=[

                {"role": "system", "content": SYSTEM_PROMPT},

                {"role": "user",   "content": f"Classify this log: {log_message}"}

            ],

            temperature=0,      # deterministic output

            max_tokens=50,      # we only need a short answer

        )
 
        raw_response = response.choices[0].message.content.strip()
 
        # extract label from <category> tags

        match = re.search(r"<category>(.*?)</category>", raw_response, re.IGNORECASE)
 
        if match:

            label = match.group(1).strip()

            # validate it's one of our known labels

            if label in VALID_LABELS:

                return label
 
        # if parsing fails, return Unclassified

        return "Unclassified"
 
    except Exception as e:

        print(f"LLM classification error: {e}")

        return "Unclassified"
 