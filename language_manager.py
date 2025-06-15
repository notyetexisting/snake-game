import os
import json
import requests

class LanguageManager:
    def __init__(self, cache_file="translations.json", source_lang="en"):
        self.source_lang = source_lang
        self.target_lang = source_lang
        self.cache_file = cache_file
        self.cache = {}
        self.load_cache()

    def set_language(self, lang_code):
        self.target_lang = lang_code

    def _cache_key(self, text):
        # Key format: "en:fr:Text Here"
        return f"{self.source_lang}:{self.target_lang}:{text}"

    def smart_translate(self, text):
        if self.target_lang == self.source_lang:
            return text
        key = self._cache_key(text)
        if key in self.cache:
            return self.cache[key]
        try:
            resp = requests.post(
                "https://libretranslate.com/translate",
                data={
                    "q": text,
                    "source": self.source_lang,
                    "target": self.target_lang,
                    "format": "text"
                },
                timeout=5
            )
            if resp.status_code == 200:
                translated = resp.json().get("translatedText", text)
                self.cache[key] = translated
                return translated
            else:
                return text
        except Exception as e:
            print(f"Translation error: {e}")
            return text

    def load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception as e:
                print(f"Failed to load translation cache: {e}")

    def save_cache(self):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save translation cache: {e}")