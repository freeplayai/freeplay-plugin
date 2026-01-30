---
name: freeplay-api
description: Use when writing code that interacts with the Freeplay API or SDK, or when trying to perform an action in Freeplay that isn't available via MCP.
---



You can use the Freeplay API like this:

```python
import requests

freeplay_api_key = os.environ["FREEPLAY_API_KEY"]
freeplay_api_base = os.environ["FREEPLAY_API_BASE"]

# Many but not all operations require a project_id
project_id = os.environ["FREEPLAY_PROJECT_ID"]

def freplay_request(method, endpoint, data):
    headers = {
        "Authorization": f"Bearer {freeplay_api_key}",
        "Content-Type": "application/json"
    }
    response = requests.request(method, endpoint, headers=headers, json=data)
    return response.json()

response = freplay_request(
  "POST",
  f"{freeplay_api_base}/v2/projects/{project_id}/search/completions",
  data={
    "filters": {
      "field": "completion_inputs.question",
      "op": "contains",
      "value": "What is freeplay?"
    }
  }
)
print(response)
```

See the API summary (./api_summary.md) for more information on the available endpoints and their usage.
See the OpenAPI specification (./openapi.json) for the extremely detailed OpenAPI specification.
Also see the LLMs.txt (./llms.txt) for the available LLMs and their usage.
