from openai import OpenAI

client = OpenAI(api_key="sk-PASTE-YOUR-REAL-OPENAI-KEY-HERE")

def chatbot_response(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception:
        return "Chatbot is currently unavailable"
