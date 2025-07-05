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
            citations_data = []
            for chunk in chunks:
                if hasattr(chunk, 'web'):
                    title = getattr(chunk.web, 'title', 'Unknown')
                    uri = chunk.web.uri
                    citations_data.append((title, uri))
            
            if citations_data:
                unique_citations = []
                seen = set()
                for title, uri in citations_data:
                    if uri not in seen:
                        unique_citations.append((title, uri))
                        seen.add(uri)
                
                citations = "\n".join(f"[{i+1}] {title} - {uri}" for i, (title, uri) in enumerate(unique_citations))
                text += f"\n\nSources:\n{citations}"
        except (AttributeError, IndexError, TypeError):
            pass
        return text
