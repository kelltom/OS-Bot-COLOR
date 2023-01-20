import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class OSRSWikiScraper:
    def __init__(self):
        self.base_url = "https://oldschool.runescape.wiki"
        self.logs = []
    
    def download_file(self, url, search_param):
        response = requests.get(url)
        path = f"sprites/{search_param}"
        if not os.path.exists(path):
            os.makedirs(path)
        filename = url.split("/")[-1].split("?")[0]
        open(f"src/images/bot/sprites/{filename}", "wb").write(response.content)

    def search_and_download(self, search_param):
        try:
            if ',' in search_param:
                search_params = search_param.split(',')
            else:
                search_params = [search_param]
            for param in search_params:
                search_param = param.strip()
                search_param_query = f"w/File:{search_param.capitalize()}.png"
                search_url = urljoin(self.base_url, search_param_query)
                response = requests.get(search_url)
                soup = BeautifulSoup(response.content, "html.parser")
                img = soup.find("img", alt=lambda x: search_param.lower() in x.lower())
                if img:
                    img_url = urljoin(self.base_url, img["src"])
                    self.download_file(img_url, search_param)
                    # search_feedback_label.set_text(text=f"Success: {search_param} saved.")
                    self.logs.append(f"Success: {search_param} saved.")
                else:
                    # search_feedback_label.set_text(text=f"No image found with the search parameter: {search_param}.")
                    self.logs.append(f"No image found for: {search_param}.")
        except Exception as e:
            self.logs.append(f"An error occured: \n {e}")