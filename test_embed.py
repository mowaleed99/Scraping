import modal

app = modal.App("test-embed")
image = modal.Image.debian_slim().pip_install("google-genai")

@app.function(image=image, secrets=[modal.Secret.from_name("lost-found-secrets")])
def try_embed():
    import os
    import google.genai as genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    for model_name in ["text-embedding-004", "gemini-embedding-exp-03-07", "gemini-embedding-001"]:
        try:
            res = client.models.embed_content(model=model_name, contents="hello world")
            print(f"SUCCESS with {model_name}: {len(res.embeddings[0].values)}")
        except Exception as e:
            print(f"FAILED with {model_name}: {e}")
