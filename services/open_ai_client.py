from openai import OpenAI
from datetime import datetime, UTC
import os
from dotenv import load_dotenv
import json
from tools import tools

load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

def call_openai_function_call(note, retry=False):
    now_iso = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    prompt = (
        "You are an assistant that extracts a structured behavior record for each student "
        "mentioned in a teacher's note. Use the provided function schema. "
        f"Use this timestamp for recording: {now_iso}"
    ) if not retry else (
        "Previous extraction failed validation. Re-extract accurately, ensuring all required fields "
        "are complete and match the schema."
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        temperature=0,
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": note}],
        tools=tools,
        tool_choice="auto"
    )

    return [
        json.loads(tool_call.function.arguments)
        for tool_call in response.choices[0].message.tool_calls
    ]