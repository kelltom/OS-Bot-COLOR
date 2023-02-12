import os
from pathlib import Path
from typing import Callable, List
from urllib.parse import urljoin

import cv2
import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    import sys

    sys.path[0] = os.path.dirname(sys.path[0])

import utilities.imagesearch as imsearch

DEFAULT_DESTINATION = imsearch.BOT_IMAGES.joinpath("scraper")


class OSRSWikiSpriteScraper:
    def __init__(self):
        self.base_url = "https://oldschool.runescape.wiki"

    def search_and_download(self, search_string: str, **kwargs):
        """
        Searches the OSRS Wiki for the given search parameter and downloads the image(s) to the appropriate folder.
        Args:
            search_string: A comma-separated list of wiki keywords to locate images for.
        Keyword Args:
            image_type: 0 = Normal, 1 = Bank, 2 = Both. Normal sprites are full-size, and bank sprites are cropped at the top
                        to improve image search performance within the bank interface (crops out stack numbers). Default is 0.
            destination: The folder to save the downloaded images to. Default is defined in the global `DEFAULT_DESTINATION`.
            notify_callback: A function (usually defined in the view) that takes a string as a parameter. This function is
                             called with search results and errors. Default is print().
        Notes:
            Images are downloaded to the folder defined in the class property `destination_folder`.
        """
        image_type = kwargs.get("image_type", 0)
        destination = kwargs.get("destination", DEFAULT_DESTINATION)
        notify_callback = kwargs.get("notify_callback", print)

        # Ensure the iamge_type is valid
        if image_type not in (0, 1, 2):
            notify_callback("Invalid image type argument.")
            return
        # Format search args into a list of strings
        img_names = self.format_args(search_string)
        if not img_names:
            notify_callback("No search terms entered.")
            return
        notify_callback("Beginning search...")
        # Iterate through each image name and download the image
        i = -1
        while i < len(img_names) - 1:
            notify_callback("")
            i += 1
            alt_text = f"File:{img_names[i]}.png"
            url = urljoin(self.base_url, f"w/{alt_text}")
            notify_callback(f"Searching for {img_names[i]}...")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            img = soup.find("img", alt=alt_text.replace("_", " "))  # Img alt text doesn't seem to include underscores
            if not img:
                notify_callback(f"No image found for: {img_names[i]}.")
                capitalized_name = self.capitalize_each_in(img_names[i])
                if capitalized_name not in img_names:
                    img_names.insert(i + 1, capitalized_name)
                    notify_callback(f"Failed to find {img_names[i]}. Trying alternative...")
                    continue
            notify_callback("Found image.")
            img_url = urljoin(self.base_url, img["src"])
            try:
                notify_callback("Downloading...")
                filepath = self.__download_file(img_url, destination)
            except Exception as e:
                notify_callback(f"Error: {e}")
                return
            if image_type in {0, 2}:
                notify_callback(f"Success: {img_names[i]} sprite saved to filepath.")
            if image_type in {1, 2}:
                img = cv2.imread(f"{filepath}.png", cv2.IMREAD_UNCHANGED)
                height, _, _ = img.shape
                crop_amt = int((height - 16) / 2) if height > 16 else 0  # Crop out stack numbers, 16 is half the height of a bank slot
                if height >= 28:
                    crop_amt += 1  # Crop an additional pixel if the image is very tall
                img[:crop_amt, :] = 0  # Set the top pixels to transparent
                cv2.imwrite(f"{filepath}_bank.png", img)
                notify_callback(f"Success: {img_names[i]} bank sprite saved to filepath.")
                if image_type == 1:
                    os.remove(f"{filepath}.png")
        notify_callback(f"\nSearch complete. Images saved to:\n{destination}.")

    def __download_file(self, url: str, destination: Path):
        """
        Downloads a file from the given URL and saves it to the scraped images folder.
        Args:
            url: The URL of the file to download.
        Returns:
            The full path of the downloaded file.
        """
        response = requests.get(url)
        filename = url.split("/")[-1].split("?")[0]
        print(f"Downloading {filename}...")
        full_path = destination.joinpath(filename.lower())
        with open(f"{full_path}", "wb") as f:
            f.write(response.content)
        return full_path.with_suffix("")

    def format_args(self, string: str) -> List[str]:
        """
        Formats a comma-separated list of strings into a list of strings where each string is capitalized and
        underscores are used instead of spaces.
        """
        # If the string is empty, return an empty list
        if not string.strip():
            return []
        # Reduce multiple spaces to a single space
        string = " ".join(string.split())
        # Strip whitespace and replace spaces with underscores
        return [word.strip().replace(" ", "_").capitalize() for word in string.split(",")]

    def capitalize_each_in(self, string: str) -> str:
        """
        Capitalizes the first letter of each word in a string of words separated by underscores, retaining the
        underscores.
        """
        return "_".join(word.capitalize() for word in string.split("_"))


if __name__ == "__main__":
    scraper = OSRSWikiSpriteScraper()

    assert scraper.format_args("") == []
    assert scraper.format_args("a, b, c") == ["A", "B", "C"]
    assert scraper.format_args(" shark ") == ["Shark"]
    assert scraper.format_args(" swordfish ,lobster, lobster   pot ") == ["Swordfish", "Lobster", "Lobster_pot"]
    assert scraper.format_args("Swordfish ,lobster, Lobster_Pot ") == ["Swordfish", "Lobster", "Lobster_pot"]

    assert scraper.capitalize_each_in("swordfish") == "Swordfish"
    assert scraper.capitalize_each_in("Lobster_pot") == "Lobster_Pot"
    assert scraper.capitalize_each_in("arceuus_home_teleport") == "Arceuus_Home_Teleport"

    print("Test cleared.")
