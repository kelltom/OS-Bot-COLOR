"""
This module contains the SpriteScraper class, which is used to download images from the wiki API.
If you are having issues, try disabling IPv6 on your machine.
"""

import os
import re
from enum import IntEnum
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
import requests

if __name__ == "__main__":
    import sys

    sys.path[0] = os.path.dirname(sys.path[0])

import utilities.imagesearch as imsearch


class ImageType(IntEnum):
    NORMAL = 0
    BANK = 1
    ALL = 2


class SpriteScraper:
    def __init__(self):
        self.BASE_URL = "https://oldschool.runescape.wiki/"
        self.DEFAULT_DESTINATION = imsearch.BOT_IMAGES.joinpath("scraper")

    def search_and_download(self, search_string: str, **kwargs) -> Path:
        """
        Searches for and downloads the image(s) specified by the search_string argument.
        Args:
            search_string (str): The search string to use.
            **kwargs: Keyword arguments.
        Keyword Args:
            image_type (ImageType): The type of image to save. Defaults to ImageType.NORMAL.
            destination (str or Path): The destination folder to save the image. Defaults to DEFAULT_DESTINATION.
            notify_callback (function): Callback function to notify the user. Defaults to print.
        Returns:
            Path: The destination folder where the images were saved.
        """
        # Extract and validate keyword arguments
        image_type, destination, notify_callback = self.__extract_kwargs(kwargs)
        img_names = self._format_args(search_string)

        if not img_names:
            notify_callback("No search terms entered.")
            return

        notify_callback("Beginning search...\n")

        completed_with_errors = False

        # Search for each image and attempt to download it
        for img_name in img_names:
            notify_callback(f"Searching for {img_name}...")
            img_url = self.__find_image_url(img_name, notify_callback)

            if img_url is None:
                notify_callback(f"No image found for {img_name}.\n")
                completed_with_errors = True
                continue

            did_succeed = self.__download_and_save_image(img_name, img_url, image_type, destination, notify_callback)
            if not did_succeed:
                completed_with_errors = True

        if completed_with_errors:
            notify_callback(f"Search completed with errors. Some images may not have been saved. See:\n{destination}.\n")
        else:
            notify_callback(f"Search complete. Images saved to:\n{destination}.\n")

        return Path(destination)

    # -------------------
    # Region: Protected Methods
    # -------------------
    def _bankify_image(self, image: cv2.Mat) -> cv2.Mat:
        """
        Converts a sprite into an image that is suitable for image searching within a bank interface.
        This function centers the image in a 36x32 frame, and deletes some pixels at the top of the image to
        remove the stack number.
        Args:
            image: The image to crop.
        Returns:
            The bankified image.
        """
        height, width = image.shape[:2]
        max_height, max_width = 32, 36

        if height > max_height or width > max_width:
            print("Warning: Image is already larger than bank slot. This sprite is unlikely to be relevant for bank functions.")
            return image

        height_diff = max_height - height
        width_diff = max_width - width
        image = cv2.copyMakeBorder(image, height_diff // 2, height_diff // 2, width_diff // 2, width_diff // 2, cv2.BORDER_CONSTANT, value=0)
        image[:9, :] = 0
        return image

    def _capitalize_each_word(self, string: str) -> str:
        """
        Capitalizes the first letter of each word in a string of words separated by underscores, retaining the
        underscores.
        """
        exclude = ["from", "of", "to", "in", "with", "on", "at", "by", "for"]
        return "_".join(word if word in exclude else word.capitalize() for word in string.split("_"))

    def __insert_underscores(self, string: str) -> str:
        """
        If the item has spaces it will replace them with underscores.
        Args:
            string: String you want to input underscores to.
        Return:
            Returns the string with underscores within it.
        """
        return string.replace(" ", "_") if " " in string else string

    def _format_args(self, string: str) -> List[str]:
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

    # -------------------
    # Region: Private Methods
    # -------------------
    def __extract_kwargs(self, kwargs):
        """
        Extracts and validates keyword arguments from the input dictionary.
        Args:
            kwargs (dict): Keyword arguments dictionary.
        Returns:
            tuple: A tuple containing image_type, destination, and notify_callback.
        """
        image_type = kwargs.get("image_type", ImageType.NORMAL)
        destination = kwargs.get("destination", self.DEFAULT_DESTINATION)
        notify_callback = kwargs.get("notify_callback", print)

        if image_type not in iter(ImageType):
            notify_callback("Invalid image type argument. Assigning default value.\n")
            image_type = ImageType.NORMAL

        return image_type, str(destination), notify_callback

    # -------------------
    # Subregion: API-Specific Methods
    # -------------------
    def __get_item_infobox_data(self, item: str) -> Optional[str]:
        """
        Returns a string of data from the info box for a specific item from the Wiki.
        Args:
            item: The item name.
        Returns:
            String of json data of the info box or None if the item does not exist or if an error occurred.
        """
        params = {"action": "query", "prop": "revisions", "rvprop": "content", "format": "json", "titles": item}

        try:
            response = requests.get(url=f"{self.BASE_URL}/api.php", params=params)
            data = response.json()
            pages = data["query"]["pages"]
            page_id = list(pages.keys())[0]
            return None if int(page_id) < 0 else pages[page_id]["revisions"][0]["*"]
        except requests.exceptions.ConnectionError as e:
            print("Network error:", e)
            return None
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            return None

    def __sprite_url(self, item: str) -> str:
        """
        Returns the sprite URL of the item provided.
        Args:
            item: The item name.
        Returns:
            URL of the sprite image (string)
        """
        info_box = self.__get_item_infobox_data(item)
        if info_box is None:
            print(f"{item}: Page doesn't exist")
            return None

        pattern = r"\[\[File:(.*?)\]\]"
        if match := re.search(pattern, info_box):
            filename = match[1]
            filename = self.__insert_underscores(filename)
            return f"{self.BASE_URL}images/{filename}"
        else:
            print(f"{item}: Sprite couldn't be found in the info box.")
            return None

    def __find_image_url(self, img_name: str, notify_callback) -> Optional[str]:
        """
        Finds the image URL with two attempts. Handles capitalization of each word on the second attempt.
        Args:
            img_name (str): The name of the image to search for.
            notify_callback (function): Callback function to notify the user.
        Returns:
            Optional[str]: The image URL, or None if not found.
        """
        for attempt in range(2):
            if attempt == 1:
                img_name = self._capitalize_each_word(img_name)

            img_url = self.__sprite_url(img_name)

            if img_url is not None:
                notify_callback("Found image.")
                return img_url
        return None

    # -------------------
    # Subregion: Download/Saving Methods
    # -------------------
    def __download_and_save_image(self, img_name: str, img_url: str, image_type: ImageType, destination: str, notify_callback) -> bool:
        """
        Downloads the image and saves it according to the image_type argument.

        Args:
            img_name (str): The name of the image to save.
            img_url (str): The URL of the image to download.
            image_type (ImageType): The type of image to save.
            destination (str): The destination folder to save the image.
            notify_callback (function): Callback function to notify the user.
        Returns:
            bool: True if the image was saved successfully, False otherwise.
        """
        notify_callback("Downloading image...")
        try:
            response = requests.get(img_url)
            downloaded_img = np.frombuffer(response.content, dtype="uint8")
            downloaded_img = cv2.imdecode(downloaded_img, cv2.IMREAD_UNCHANGED)
        except requests.exceptions.RequestException as e:
            notify_callback(f"Network error: {e}\n")
            return False
        except cv2.error as e:
            notify_callback(f"Image decoding error: {e}\n")
            return False
        self.__save_image(img_name, downloaded_img, image_type, destination, notify_callback)
        return True

    def __save_image(self, img_name: str, downloaded_img: np.ndarray, image_type: ImageType, destination: str, notify_callback) -> bool:
        """
        Saves the image according to the image_type argument.
        Args:
            img_name (str): The name of the image to save.
            downloaded_img (np.ndarray): The image to save.
            image_type (ImageType): The type of image to save.
            destination (str): The destination folder to save the image.
            notify_callback (function): Callback function to notify the user.
        Returns:
            bool: True if the image saving succeeded, False otherwise.
        """
        # Create the destination folder if it doesn't already exist
        destination: Path = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        filepath = destination.joinpath(img_name)

        try:
            if image_type in {ImageType.NORMAL, ImageType.ALL}:
                cv2.imwrite(f"{filepath}.png", downloaded_img)
                nl = "\n"
                notify_callback(f"Success: {img_name} sprite saved.{nl if image_type != 2 else ''}")
            if image_type in {ImageType.BANK, ImageType.ALL}:
                cropped_img = self._bankify_image(downloaded_img)
                cv2.imwrite(f"{filepath}_bank.png", cropped_img)
                notify_callback(f"Success: {img_name} bank sprite saved.\n")
            return True
        except Exception as e:
            notify_callback(f"Error saving image: {e}\n")
            return False


if __name__ == "__main__":
    scraper = SpriteScraper()

    assert scraper._format_args("") == []
    assert scraper._format_args("a, b, c") == ["A", "B", "C"]
    assert scraper._format_args(" shark ") == ["Shark"]
    assert scraper._format_args(" swordfish ,lobster, lobster   pot ") == ["Swordfish", "Lobster", "Lobster_pot"]
    assert scraper._format_args("Swordfish ,lobster, Lobster_Pot ") == ["Swordfish", "Lobster", "Lobster_pot"]

    assert scraper._capitalize_each_word("swordfish") == "Swordfish"
    assert scraper._capitalize_each_word("Lobster_pot") == "Lobster_Pot"
    assert scraper._capitalize_each_word("arceuus_home_teleport") == "Arceuus_Home_Teleport"
    assert scraper._capitalize_each_word("protect_from_magic") == "Protect_from_Magic"
    assert scraper._capitalize_each_word("teleport_to_house") == "Teleport_to_House"
    assert scraper._capitalize_each_word("claws_of_guthix") == "Claws_of_Guthix"

    # Test saving to non-existent directory in string format
    new_destination = str(scraper.DEFAULT_DESTINATION.joinpath("lobster_stuff"))
    scraper.search_and_download(
        search_string=" lobster , lobster  Pot",
        image_type=ImageType.BANK,
        destination=new_destination,
    )

    # Test saving without using Enum, and with a non-existent item query
    scraper.search_and_download(
        search_string="protect from magic, arceuus home teleport, nonexitent_sprite",
        image_type=0,
    )

    print("Test cleared.")
