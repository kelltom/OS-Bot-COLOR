### ⚠️ This project is in Alpha *v0.2.0* ⚠️

# ![](documentation/media/logo.png)
OSRS Bot COLOR (OSBC) is a desktop client for controlling and monitoring automation scripts (bots) for OSRS and private server alternatives. This project is paired with a custom library of tools for streamlining the development of new bots, even for inexperienced developers. Unlike most botting frameworks that employ code injection into the game client, OSBC uses a combination of color manipulation, image recognition, and optical character recognition to navigate the game. The goal of OSBC is to emulate human eyes and hands, and wrap that complex logic in a simple, easy-to-use framework.

💬 [Join the Discord](https://discord.gg/Znks7Smya4) to discuss the project, ask questions, and follow development

📹 Subscribe to [Kell's Code](https://www.youtube.com/@KellsCode/featured) on YouTube for updates and tutorials

⭐ If you like this project, please leave a Star :)

# Table of Contents
- [](#)
- [Table of Contents](#table-of-contents)
- [Developer Setup ](#developer-setup-)
- [Documentation](#documentation)
- [Features](#features)
  - [User Interface](#user-interface)
    - [Script Log](#script-log)
    - [Simple Option Menus](#simple-option-menus)
  - [RuneLite Launcher](#runelite-launcher)
  - [Any Client Size, Anywhere](#any-client-size-anywhere)
  - [Human-like Mouse Movement](#human-like-mouse-movement)
  - [RuneLite Leverage](#runelite-leverage)
    - [Object Detection](#object-detection)
    - [API](#api)
  - [Random Click Distribution](#random-click-distribution)
  - [Efficient Image Searching](#efficient-image-searching)
  - [Lightning Fast OCR](#lightning-fast-ocr)
- [Packaging an Executable](#packaging-an-executable)
- [Support](#support)

# Developer Setup <img height=20 src="documentation/media/windows_logo.png"/>
1. Install [Python 3.10](https://www.python.org/downloads/release/python-3109/) *(newer versions are not compatible)*
2. Clone/download this repository
3. Open the project folder in your IDE (VS Code preferred)
4. Open the repository folder in a terminal window
   1. Create a virtual environment ```python -m venv env```
   2. Activate the newly created virtual environment ```.\env\Scripts\activate```
   3. Install the depedencies ```pip install -r requirements.txt```
5. Run `./src/*OSBC.py*`

# Documentation

See the [Wiki](https://github.com/kelltom/OSRS-Bot-COLOR/wiki) for tutorials, and software design information.

# Features
## User Interface
Gone are the days of manually running your bot scripts from an IDE. OSBC offers a clean interface for configuring, running, and monitoring your Python bots. For developers, this means that all you need to do is write a bot's logic loop, and *the UI is already built for you*.

![intro_demo](https://user-images.githubusercontent.com/44652363/197059102-27a9a942-25b6-4012-b83b-90ae8399b4e8.gif)

### Script Log
The Script Log provides a clean and simple way to track your bot's progress. No more command line clutter!

```python
self.log_msg("The bot has started.")
```

### Simple Option Menus
OSBC allows developers to create option menus and parse user selections with ease.

```python
def create_options(self):
  ''' Declare what should appear when the user opens the Options menu '''
  self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 180) 
  self.options_builder.add_text_edit_option("text_edit_example", "Text Edit Example", "Placeholder text here")
  self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
  self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])
```

PUT OPTIONS MENU PNG HERE

## RuneLite Launcher
Color bots rely on very specific in-game settings. In one click, you can launch RuneLite with pre-configured, *legal* plugins that allow OSBC to work its magic. This works completely separate from your normal RuneLite installation, so your personal configuration is not affected.

ADD RUNELITE LAUNCHER GIF HERE

## Any Client Size, Anywhere
New in *v0.2.0*, your scripts will work no matter what size your client is, or where it is on your primary monitor. OSBC locates important UI elements and allows you to access them by name.

ADD RESIZEABLE GIF HERE

## Human-like Mouse Movement
OSBC uses Bezier curves to create smooth, human-like mouse movements.

ADD MOUSE MOVEMENT GIF HERE

## RuneLite Leverage
### Object Detection
Official RuneLite plugins exist to add quality of life to players. Many plugins offer highlighting/outlining of in-game objects with solid colors, making them easier to see. This inadvertedly makes them easier to detect for bots as well. Using color isolation, OSBC can quickly detect these outlined objects and extract its properties into a simple data structure.

ADD OBJECT DETECTION PNG HERE

### API
There are some RuneLite plugins that expose game data to a localhost API endpoint. OSBC can leverage this data to provide a more robust botting experience without the need to modify the game client. See the [API utility folder](src/utilities/api/) for more.

## Random Click Distribution
With the help of the OSBC community, we've created a randomization algorithm that distributes clicks in a way that is more human-like. We followed the same principles used by individuals who've beat the system and achieved max levels without lifting a finger. This feature is a work in progress.

ADD RANDOM CLICK GIF HERE

## Efficient Image Searching
Sometimes, your bot might need to find a specific image on screen. This can be done with the help of OpenCV's template matching algorithm. We've modified it to be more efficient and reliable with RuneScape UI elements and sprites - even supporting images with transparency.

ADD IMAGE SEARCH PNG HERE

## Lightning Fast OCR
In *v0.2.0*, we've ditched machine learned OCR in favor of a much faster and more reliable custom implementation. OSBC can locate text on screen in as little as **2 milliseconds**. That's **0.002 seconds**.

Add OCR PNG HERE

# Packaging an Executable
Due to some issues with dependencies, it's not possible to build this project into a *single file* executable, however, a directory-based executable can be made.

1. In the terminal/cmd, navigate to the directory containing the project.
2. Ensure the venv is activated: ```.\env\Scripts\activate```
3. Run AutoPyToEXE via the terminal command: ```auto-py-to-exe```
   1. You may need to install it first. ```pip install auto-py-to-exe```
4. Configure the window similarly to the figure below (or import the [auto-py-to-exe_settings.json](auto-py-to-exe_settings.json) file included in the root of this repository to speed up the process).
   1. Ensure the *Additional Files* paths are correct for *your system*.
   2. Under the *Icon* tab, you may point it to the [icon](documentation/media/icon.ico) file included, or use your own.
5. Click the *Convert* button.
6. Navigate to the generated `./output/OSBC` folder, and within that folder you can run the `OSBC.exe` file. You may move this folder to wherever you'd like.

![](documentation/media/auto-py-to-exe-settings.png)

*Note: CustomTkinter need to be pointed to in the Additional Files section.

```{path to repo}/env/Lib/site-packages/customtkinter;customtkinter```

# Support
<p align="center">
  <a href="https://www.buymeacoffee.com/kelltom" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="60px">
  </a>  
</p> 
