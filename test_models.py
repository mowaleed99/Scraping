import modal

app = modal.App("test-models")
image = modal.Image.debian_slim().pip_install("google-genai", "pydantic-settings")

@app.function(image=image, secrets=[modal.Secret.from_name("lost-found-secrets")])
def list_models():
    import os
    import google.genai as genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    for m in client.models.list():
        if "embed" in m.name.lower():
            print(m.name, m.supported_actions)
