from google import genai
from google.genai import types
import os
from pathlib import Path
from search import google_search

class Gemini:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        script_dir = Path(__file__).parent
        self.url_prompt = self._load_file(script_dir / "url_instruction.txt", "Generate search terms for: ")
        system_instruction = self._load_file(script_dir / "system_instruction.txt", "You are a helpful assistant.")
        
        self.config = types.GenerateContentConfig(
            tools=[types.Tool(url_context=types.UrlContext())], 
            system_instruction=system_instruction
        )
        self.search_config = types.GenerateContentConfig(system_instruction="Generate search terms as requested.")

    def _load_file(self, file_path, default_content):
        try:
            return open(file_path, "r", encoding="utf-8").read().strip()
        except FileNotFoundError:
            return default_content

    def get_reddit_urls(self, prompt):
        search_terms = self.client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=self.url_prompt + prompt, 
            config=self.search_config
        )
        search_lines = [line.strip() for line in (search_terms.text or "").split('\n') if line.strip()]
        
        all_urls = []
        for search_term in search_lines:
            results = google_search(search_term).get("organic_results", [])
            all_urls.extend([r["link"] for r in results if "reddit.com" in r.get("link", "")])
        
        unique_urls = list(dict.fromkeys(all_urls))
        return unique_urls[:19] if len(unique_urls) > 19 else unique_urls

    def generate_response_from_urls(self, prompt, urls):
        if not urls:
            return "No URLs provided for analysis."
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=f"{prompt}\n\nPlease summarize the following URLs: {', '.join(urls)}", 
                config=self.config
            )
            return response.text or ""
        except Exception:
            return self.generate_response_from_urls(prompt, urls[:5]) if len(urls) > 5 else "Sorry, I couldn't analyze the URLs."

    def generate(self, prompt):
        urls = self.get_reddit_urls(prompt)
        response = self.generate_response_from_urls(prompt, urls) or "Sorry, I couldn't generate a response."
        return f"{response}\n\nSources:\n" + "\n".join(urls)