import json
import urllib.request

req = urllib.request.Request(
    'http://localhost:11434/api/generate',
    data=json.dumps({
        "model": "llama3",
        "prompt": "Hello",
        "stream": False
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
