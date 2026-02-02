import os

# Handle SSL for local development (self-signed certs)
# This must be done before importing libraries that use requests/urllib3
if os.environ.get("FREEPLAY_VERIFY_SSL", "true").lower() == "false":
    import ssl
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Monkey-patch requests to disable SSL verification
    import requests
    _original_request = requests.Session.request
    def _patched_request(self, *args, **kwargs):
        kwargs.setdefault('verify', False)
        return _original_request(self, *args, **kwargs)
    requests.Session.request = _patched_request

from openai import OpenAI

client = OpenAI()


def summarize(text: str) -> str:
    """Summarize the given text using GPT-4o-mini."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes text.",
            },
            {"role": "user", "content": f"Summarize this: {text}"},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    text = """
    The quick brown fox jumps over the lazy dog. This is a sample text for testing.
    It contains multiple sentences to give the summarizer something to work with.
    The goal is to see if the LLM can condense this into a shorter form while
    preserving the key information about foxes and dogs.
    """
    result = summarize(text)
    print("Summary:", result)
