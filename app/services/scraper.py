import re, requests
from bs4 import BeautifulSoup
from flask import current_app as app

class WebScraper:
    @staticmethod
    def fetch_job_description(url: str) -> str:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, timeout=15, headers=headers)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            selectors = [
                "article", "main", "[role=main]",
                ".job-description", ".jobsearch-JobComponent",
                ".content", "#job-description", ".job-detail"
            ]
            for sel in selectors:
                el = soup.select_one(sel)
                if el:
                    text = el.get_text(" ", strip=True)
                    if len(text) > 500:
                        return re.sub(r"\s+", " ", text)
            return re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
        except Exception as e:
            app.logger.error("Web scraping error: %s", e)
            raise Exception(f"İş ilanı alınamadı: {e}")
