"""
This module contains the SpriteScraper class, which is used to download images from the OSRS Wiki.
This utility does not work well with IPv6. If you are having issues, try disabling IPv6 on your machine.
"""

import os
from typing import List
from urllib.parse import urljoin

import cv2
import numpy as np
import requests
from bs4 import BeautifulSoup

if __name__ == "__main__":
    import sys

    sys.path[0] = os.path.dirname(sys.path[0])

import utilities.imagesearch as imsearch

DEFAULT_DESTINATION = imsearch.BOT_IMAGES.joinpath("scraper")


class SpriteScraper:
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
        Example:
            This is an example of using the scraper from a Bot script to download images suitable for searching in the bank:
            >>> scraper = SpriteScraper()
            >>> scraper.search_and_download(
            >>>     search_string = "molten glass, bucket of sand",
            >>>     image_type = 1,
            >>>     destination = imsearch.BOT_IMAGES.joinpath("bank"),
            >>>     notify_callback = self.log_msg,
            >>> )
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
        notify_callback("Beginning search...\n")

        # Iterate through each image name and download the image
        i = -1
        while i < len(img_names) - 1:
            i += 1

            # Locate image on webpage using the alt text
            alt_text = f"File:{img_names[i]}.png"
            url = urljoin(self.base_url, f"w/{alt_text}")
            notify_callback(f"Searching for {img_names[i]}...")
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            img = soup.find("img", alt=alt_text.replace("_", " "))  # Img alt text doesn't seem to include underscores
            if not img:
                capitalized_name = self.capitalize_each_in(img_names[i])
                if capitalized_name not in img_names:
                    img_names.insert(i + 1, capitalized_name)
                    notify_callback(f"No image found for {img_names[i]}. Trying alternative...\n")
                else:
                    notify_callback(f"No image found for: {img_names[i]}.\n")
                continue
            notify_callback("Found image.")

            # Download image
            img_url = urljoin(self.base_url, img["src"])
            notify_callback("Downloading image...")
            try:
                downloaded_img = self.__download_image(img_url)
            except Exception as e:
                notify_callback(f"Error: {e}\n")
                continue

            # Save image according to image_type argument
            filepath = destination.joinpath(img_names[i])
            if image_type in {0, 2}:
                cv2.imwrite(f"{filepath}.png", downloaded_img)
                nl = "\n"
                notify_callback(f"Success: {img_names[i]} sprite saved.{nl if image_type != 2 else ''}")
            if image_type in {1, 2}:
                cropped_img = self.__crop_image(downloaded_img)
                cv2.imwrite(f"{filepath}_bank.png", cropped_img)
                notify_callback(f"Success: {img_names[i]} bank sprite saved.\n")

        notify_callback(f"Search complete. Images saved to:\n{destination}.\n")

    def capitalize_each_in(self, string: str) -> str:
        """
        Capitalizes the first letter of each word in a string of words separated by underscores, retaining the
        underscores.
        """
        exclude = ["from", "of", "to", "in", "with", "on", "at", "by", "for"]
        return "_".join(word if word in exclude else word.capitalize() for word in string.split("_"))

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

    def __crop_image(self, image: cv2.Mat) -> cv2.Mat:
        """
        Makes the top of the image transparent. This is used to crop out stack numbers in bank sprites.
        Args:
            image: The image to crop.
        Returns:
            The cropped image.
        """
        BANK_SLOT_HALF_HEIGHT = 16
        IMG_MAX_HEIGHT = 28
        height, _, _ = image.shape
        # Crop out stack numbers
        crop_amt = int((height - BANK_SLOT_HALF_HEIGHT) / 2) if height > BANK_SLOT_HALF_HEIGHT else 0
        if height >= IMG_MAX_HEIGHT:
            crop_amt += 1  # Crop an additional pixel if the image is very tall
        image[:crop_amt, :] = 0  # Set the top pixels to transparent
        return image

    def __download_image(self, url: str) -> cv2.Mat:
        """
        Downloads an image from a URL.
        Args:
            url: The URL of the image to download.
        Returns:
            The downloaded image as a cv2 Mat.
        """
        response = requests.get(url)
        downloaded_img = np.frombuffer(response.content, dtype="uint8")
        downloaded_img = cv2.imdecode(downloaded_img, cv2.IMREAD_UNCHANGED)
        return downloaded_img


if __name__ == "__main__":
    scraper = SpriteScraper()

    assert scraper.format_args("") == []
    assert scraper.format_args("a, b, c") == ["A", "B", "C"]
    assert scraper.format_args(" shark ") == ["Shark"]
    assert scraper.format_args(" swordfish ,lobster, lobster   pot ") == ["Swordfish", "Lobster", "Lobster_pot"]
    assert scraper.format_args("Swordfish ,lobster, Lobster_Pot ") == ["Swordfish", "Lobster", "Lobster_pot"]

    assert scraper.capitalize_each_in("swordfish") == "Swordfish"
    assert scraper.capitalize_each_in("Lobster_pot") == "Lobster_Pot"
    assert scraper.capitalize_each_in("arceuus_home_teleport") == "Arceuus_Home_Teleport"
    assert scraper.capitalize_each_in("protect_from_magic") == "Protect_from_Magic"
    assert scraper.capitalize_each_in("teleport_to_house") == "Teleport_to_House"
    assert scraper.capitalize_each_in("claws_of_guthix") == "Claws_of_Guthix"

    scraper.search_and_download(
        search_string=" lobster , lobster  Pot",
        image_type=1,
    )

    scraper.search_and_download(
        search_string="protect from magic, arceuus home teleport, nonexitent_sprite",
        image_type=0,
    )

    print("Test cleared.")
