from openai import OpenAI, RateLimitError
set_client=OpenAI(
        api_key="your moonshot api_key",
        base_url="https://api.moonshot.cn/v1",
    )

def chat(history):
    client = set_client
    response = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=history,
        temperature=0.3,
        stream=True,
    )
    return response