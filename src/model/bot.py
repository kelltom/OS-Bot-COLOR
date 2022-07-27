'''
A Bot is a base class for bot script models. It is abstract and cannot be instantiated. Many of the methods in this base class are
pre-implemented and can be used by subclasses, or called by the controller. Code in this class should not be modified.
'''
from abc import ABC, abstractmethod
from enum import Enum
import keyboard
from threading import Thread
import time
import cv2
from easyocr import Reader
from PIL import Image, ImageGrab
from pyclick import HumanClicker
from python_imagesearch.imagesearch import imagesearcharea, region_grabber
from typing import NamedTuple
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


class BotStatus(Enum):
    """
    BotStatus enum.
    """
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3
    CONFIGURING = 4


# --- Custom Named Tuples ---
# Simplifies accessing points and areas on the screen by name.
Point = NamedTuple("Point", x=int, y=int)
Rectangle = NamedTuple('Rectangle', start=Point, end=Point)


class Bot(ABC):
    status = BotStatus.STOPPED
    iterations: int = 0
    current_iter: int = 0
    options_set: bool = False
    thread: Thread = None
    hc = HumanClicker()

    # --- Paths to Image folders ---
    TEMP_IMAGES = "./src/images/temp"
    BOT_IMAGES = "./src/images/bot"

    # ---- Abstract Functions ----
    @abstractmethod
    def __init__(self, title, description):
        self.title = title
        self.description = description

    @abstractmethod
    def main_loop(self):
        '''
        Main logic of the bot. This function is called in a separate thread.
        '''
        pass

    @abstractmethod
    def save_options(self, options: dict):
        '''
        Saves a dictionary of options as properties of the bot.
        Args:
            options: dict - dictionary of options to save
        '''
        pass

    def play_pause(self):  # sourcery skip: extract-method
        '''
        Depending on the bot status, this function either starts a bot's main_loop() on a new thread, or pauses it.
        '''
        if self.status == BotStatus.STOPPED:
            self.clear_log()
            if not self.options_set:
                self.log_msg("Options not set. Please set options before starting.")
                return
            self.log_msg("Starting bot...")
            self.reset_iter()
            self.set_status(BotStatus.RUNNING)
            self.thread = Thread(target=self.main_loop)
            self.thread.setDaemon(True)
            self.thread.start()
        elif self.status == BotStatus.RUNNING:
            self.log_msg("Pausing bot...")
            self.set_status(BotStatus.PAUSED)
        elif self.status == BotStatus.PAUSED:
            self.log_msg("Resuming bot...")
            self.set_status(BotStatus.RUNNING)

    def stop(self):
        '''
        Fired when the user stops the bot manually.
        '''
        self.log_msg("Manual stop requested. Attempting to stop...")
        if self.status != BotStatus.STOPPED:
            self.set_status(BotStatus.STOPPED)
            self.reset_iter()
        else:
            self.log_msg("Bot is already stopped.")

    def __check_interrupt(self):
        '''
        Checks for keyboard interrupts.
        '''
        if keyboard.is_pressed("F1"):
            if self.status != BotStatus.PAUSED:
                self.log_msg("Pausing bot...")
                self.set_status(BotStatus.PAUSED)
        elif keyboard.is_pressed("ESC"):
            self.stop()

    def status_check_passed(self, timeout: int = 10) -> bool:
        '''
        Does routine check for:
            - Bot status (stops/pauses)
            - Keyboard interrupts
        This function enters a pause loop for the given timeout. This function also handles sending
        messages to controller. Best used in main_loop() inner loops while bot is waiting for a
        condition to be met.
        Args:
            timeout: int - number of seconds to wait for condition to be met
        Returns:
            True if the bot is safe to continue, False if the bot should terminate.
        '''
        # Check for keypress interrupts
        self.__check_interrupt()
        # Check status
        if self.status == BotStatus.STOPPED:
            self.log_msg("Bot has been stopped.")
            return False
        # If paused, enter loop until status is not paused
        elif self.status == BotStatus.PAUSED:
            self.log_msg("Bot is paused.\n")
            while self.status == BotStatus.PAUSED:
                self.__check_interrupt()
                time.sleep(1)
                if self.status == BotStatus.STOPPED:
                    self.log_msg("Bot has been stopped.")
                    return False
                timeout -= 1
                if timeout == 0:
                    self.log_msg("Timeout reached, stopping...")
                    self.set_status(BotStatus.STOPPED)
                    return False
                if self.status == BotStatus.PAUSED:
                    self.log_msg(msg=f"Terminating in {timeout}.", overwrite=True)
                    continue
        return True

    # ---- Controller Setter ----
    def set_controller(self, controller):
        self.controller = controller

    # ---- Functions that notify the controller of changes ----
    def reset_iter(self):
        '''
        Resets the current iteration property to 0 and notifies the controller to update UI.
        '''
        self.current_iter = 0
        self.controller.update_progress()

    def increment_iter(self, by: int = 1):
        '''
        Increments the current iteration property and notifies the controller to update UI.
        Args:
            by: int - number of iterations to increment by
        '''
        self.current_iter += by
        self.controller.update_progress()

    def set_status(self, status: BotStatus):
        '''
        Sets the status property of the bot and notifies the controller to update UI accordingly.
        Args:
            status: BotStatus - status to set the bot to
        '''
        self.status = status
        self.controller.update_status()

    def log_msg(self, msg: str, overwrite=False):
        '''
        Sends a message to the controller to be displayed in the log for the user.
        Args:
            msg: str - message to log
            overwrite: bool - if True, overwrites the current log message. If False, appends to the log.
        '''
        self.controller.update_log(msg, overwrite)

    def clear_log(self):
        '''
        Requests the controller to tell the UI to clear the log.
        '''
        self.controller.clear_log()

    # ---- Bot Utilities ----
    def capture_screen(self, rect: Rectangle) -> str:
        '''
        Captures a given Rectangle and saves it to a file.
        Args:
            rect: The Rectangle area to capture.
        Returns:
            The path to the saved image.
        '''
        im = ImageGrab.grab(bbox=(rect.start.x, rect.start.y, rect.end.x, rect.end.y))
        return self.__save_image('/screenshot.png', im)

    # --- Image Search ---
    def search_img_in_rect(self, img_path: str, rect: Rectangle, conf: float = 0.8) -> Point:
        '''
        Searches for an image in a rectangle.
        Args:
            img_path: The path to the image to search for.
            rect: The rectangle to search in.
            conf: The confidence level of the search.
        Returns:
            The coordinates of the center of the image if found (as a Point) relative to display,
            otherwise None.
        '''
        width, height = Image.open(img_path).size
        im = region_grabber((rect.start.x, rect.start.y, rect.end.x, rect.end.y))
        pos = imagesearcharea(img_path, rect.start.x, rect.start.y, rect.end.x, rect.end.y, conf, im)
        if pos == [-1, -1]:
            return None
        return self.Point(x=pos[0] + rect.start.x + width/2,
                          y=pos[1] + rect.start.y + height/2)

    # --- OCR ---
    def get_text_in_rect(self, rect: Rectangle, is_low_res=False) -> str:
        # sourcery skip: class-extract-method
        '''
        Fetches text in a Rectangle.
        Args:
            rect: The rectangle to search in.
            is_low_res: Whether the text within the rectangle is low resolution/pixelated.
        Returns:
            The text found in the rectangle, space delimited.
        '''
        # Screenshot the rectangle and load the image
        path = self.capture_screen(rect)

        if is_low_res:
            path = self.__preprocess_low_res_text_at(path)

        image = cv2.imread(path)

        # OCR the input image using EasyOCR
        reader = Reader(['en'], gpu=-1)
        res = reader.readtext(image)

        return "".join(f"{_text} " for _, _text, _ in res)

    def search_text_in_rect(self, rect: Rectangle, expected: list, blacklist: list = None) -> bool:
        '''
        Searches for text in a Rectangle.
        Args:
            rect: The rectangle to search in.
            expected: List of strings that are expected within the rectangle area.
            blacklist: List of strings that, if found, will cause the function to return False.
        Returns:
            False if ANY blacklist words are found, else True if ANY expected text exists,
            and None if the text is irrelevant.
        '''
        # Screenshot the rectangle and load the image
        path = self.capture_screen(rect)
        image = cv2.imread(path)

        # OCR the input image using EasyOCR
        reader = Reader(['en'], gpu=-1)
        res = reader.readtext(image)

        # Loop through results
        word_found = False
        for (_, text, _) in res:
            if text is None or text == "":
                return None
            text = text.lower()
            print(f"OCR Result: {text}")
            # If any strings in blacklist are found in text, return false
            if blacklist is not None:
                _result, _word = self.__any_in_str(blacklist, text)
                if _result:
                    print(f"Blacklist word found: {_word}")
                    return False
            # If any strings in expected are found in text, set flag true
            if not word_found:
                _result, _word = self.__any_in_str(expected, text)
                if _result:
                    word_found = True
                    print(f"Expected word found: {_word}")
        if word_found:
            return True
        return None

    def __any_in_str(self, words: list, str: str) -> bool:
        '''
        Checks if any of the words in the list are found in the string.
        Args:
            words: The list of words to search for.
            str: The string to search in.
        Returns:
            True if any of the words are found (also returns the word found), else False.
        '''
        return next(((True, word) for word in words if word.lower() in str), (False, None))

    def __preprocess_low_res_text_at(self, path: str) -> str:
        '''
        Preprocesses an image at a given path and saves it back to the same path.
        This function improves text clarity for OCR by upscaling, antialiasing, and isolating text.
        Note:
            Only use for low-resolution images with pixelated text and a solid background.
        Args:
            path: The path to the image to preprocess.
        Returns:
            The path to the processed image.
        Reference: https://stackoverflow.com/questions/50862125/how-to-get-better-accurate-results-with-ocr-from-low-resolution-images
        '''
        im = Image.open(path)
        width, height = im.size
        new_size = width*6, height*6
        im = im.resize(new_size, Image.Resampling.LANCZOS)
        im = im.convert('L')  # Convert to grayscale
        intensity = 120  # Between 0 and 255, every pixel less than this value will be set to 0
        im = im.point(lambda x: 0 if x < intensity else 255, '1')
        return self.__save_image('/low_res_text_processed.png', im)

    def __save_image(self, filename, im):
        '''
        Saves an image to the temporary image directory.
        Args:
            filename: The filename to save the image as.
            im: The image to save.
        Returns:
            The path to the saved image.
        Example:
            path = __save_image('/screenshot.png', im)
        '''
        path = f"{self.TEMP_IMAGES}{filename}"
        im.save(path)
        return path
