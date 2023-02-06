import functools
import os
from typing import Callable, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from PIL import Image

import utilities.imagesearch as imsearch


class OSRSWikiSpriteScraper:
    def __init__(self):
        self.base_url = "https://oldschool.runescape.wiki"
        self.images_folder = imsearch.BOT_IMAGES.joinpath("scraper")

    def search_and_download(self, search_string: str, image_type: int, notify_callback: Callable):
        """
        Searches the OSRS Wiki for the given search parameter and downloads the image(s) to the appropriate folder.
        Args:
            search_string: A comma-separated list of wiki keywords to locate images for.
            image_type: 0 = Normal, 1 = Bank, 2 = Both. Normal sprites are full-size, and bank sprites are cropped at the top
                        to improve image search performance within the bank interface (crops out stack numbers).
            notify_callback: A function (usually defined in the view) that takes a string as a parameter. This function is
                             called with search results and errors.
        """
        notify_callback("Beginning search...")
        # Format search args into a list of strings
        img_names = self.__format_args(search_string)
        # Iterate through each image name and download the image
        for img_name in img_names:
            url = urljoin(self.base_url, f"w/File:{img_name.capitalize()}.png")
            notify_callback(f"Searching: {url}...")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            # TODO: This might fail
            img = soup.find("img", alt=functools.partial(lambda x, name: name.lower() in x.lower(), img_name))
            if not img:
                notify_callback(f"No image found for: {img_name}.")
                return
            notify_callback(f"Found image for: {img_name}.")
            img_url = urljoin(self.base_url, img["src"])
            try:
                notify_callback(f"Downloading: {img_url}...")
                filepath = self.__download_file(img_url)
            except Exception as e:
                notify_callback(f"Error: {e}")
                return
            if image_type in {0, 2}:
                notify_callback(f"Success: {img_name} sprite saved to {filepath}.")
            if image_type in {1, 2}:
                img = Image.open(f"{filepath}.png")
                img_cropped = img.crop((0, 10, img.width, 30))
                img_cropped.save(f"{filepath}_bank.png")
                notify_callback(f"Success: {img_name} bank sprite saved to {filepath}.")
                if image_type == 1:
                    os.remove(f"{filepath}.png")

    def __download_file(self, url: str):
        """
        Downloads a file from the given URL and saves it to the scraped images folder.
        Args:
            url: The URL of the file to download.
        Returns:
            The full path of the downloaded file.
        """
        response = requests.get(url)
        filename = url.split("/")[-1].split("?")[0]
        print(f"__download_file, filename: {filename}")
        full_path = self.images_folder.joinpath(filename.lower())
        with open(f"{full_path}", "wb") as f:
            f.write(response.content)
        return full_path

    def __format_args(self, string: str) -> List[str]:
        return [s.strip() for s in string.split(",")]
