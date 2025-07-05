from google import genai
from google.genai import types
import os

class Gemini:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.search = types.Tool(google_search=types.GoogleSearch())
        self.config = types.GenerateContentConfig(tools=[self.search])

    def generate_response(self, prompt):
        response = self.client.models.generate_content(model="gemini-2.5-flash", contents=prompt, config=self.config)
        return self.add_citations(response)

    def add_citations(self, response):
        text = response.text
        try:
            chunks = response.candidates[0].grounding_metadata.grounding_chunks
            urls = [chunk.web.uri for chunk in chunks if hasattr(chunk, 'web')]
            if urls:
                citations = "\n".join(f"[{i+1}] {url}" for i, url in enumerate(set(urls)))
                text += f"\n\nSources:\n{citations}"
        except (AttributeError, IndexError, TypeError):
            pass
        return text
