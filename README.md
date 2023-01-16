### ⚠️ This project is in Alpha stage ⚠️

# ![](documentation/media/logo.png)
OSRS Bot COLOR (OSBC) is a desktop client for controlling and monitoring automation scripts (bots) for Old School RuneScape and private server alternatives. This application is paired with a custom library of tools for streamlining the development of new bots. Unlike most botting frameworks that employ code injection into the game client, OSBC uses a combination of color manipulation, image recognition, and optical character recognition to navigate the game. The goal of OSBC is to emulate human eyes and hands, and wrap that complex logic in an easy-to-use framework.

💬 [Join the Discord](https://discord.gg/Znks7Smya4) to discuss the project, ask questions, and follow development

📹 Subscribe to [Kell's Code](https://www.youtube.com/@KellsCode/featured) on YouTube for updates and tutorials

⭐ If you like this project, please leave a Star :)

<p>
  <a href="https://www.buymeacoffee.com/kelltom" target="_blank">
    <img src="https://i.imgur.com/5X29MVY.png" alt="Buy Me A Coffee" height="60dp">
  </a>
  &nbsp;&nbsp;&nbsp;
  <a href="https://www.paypal.com/paypalme/kelltom" target="_blank">
    <img src="https://i.imgur.com/6EFKj2m.png" alt="PayPal" height="60dp">
  </a>
</p>

# Table of Contents
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
  - [Lightning Fast Optical Character Recognition](#lightning-fast-optical-character-recognition)

# Developer Setup <img height=20 src="documentation/media/windows_logo.png"/>
1. Install [Python 3.10](https://www.python.org/downloads/release/python-3109/) *(newer versions are not compatible)*
2. Clone/download this repository
3. Open the project folder in your IDE (VS Code preferred)
4. Open the repository folder in a terminal window
   1. Create a virtual environment ```python -m venv env``` or ```py -m venv env``` if you have multiple versions of Python installed
   2. Activate the newly created virtual environment ```.\env\Scripts\activate```
   3. Install the depedencies ```pip install -r requirements.txt```
5. Run `./src/*OSBC.py*` *(may need to restart IDE for it to recognize installed dependencies)*

# Documentation

See the [Wiki](https://github.com/kelltom/OSRS-Bot-COLOR/wiki) for tutorials, and software design information.

# Features
## User Interface
OSBC offers a clean interface for configuring, running, and monitoring your Python bots. For developers, this means that all you need to do is write a bot's logic loop, and *the UI is already built for you*.

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

![options_menu](https://user-images.githubusercontent.com/44652363/206808756-aac29140-e41d-4b6c-9f26-dc08ce0662b9.png)

## RuneLite Launcher
In one click, you can launch RuneLite with pre-configured, *legal* plugins that allow OSBC to work its magic. This works completely separate from your normal RuneLite installation, so your personal configuration is not affected.

![rl launcher](https://user-images.githubusercontent.com/44652363/206948553-608d0337-862c-41ca-b2e1-7cd473838060.gif)

## Any Client Size, Anywhere
Your scripts will work no matter the size or position of the game client. OSBC locates important UI elements and allows you to access them by name.

![resize support](https://user-images.githubusercontent.com/44652363/206949051-16e1bf57-a189-4eda-bbb2-1864e2849c45.gif)

## Human-like Mouse Movement
OSBC uses Bezier curves to create smooth, human-like mouse movements.

![mouse movements](https://user-images.githubusercontent.com/44652363/206948347-88e6296c-a5bf-43d4-a491-4680467ada31.gif)

## RuneLite Leverage
### Object Detection
Official RuneLite plugins exist to add quality of life to players. Many plugins offer highlighting/outlining of in-game objects with solid colors, making them easier for players to see them. Using color isolation, OSBC can quickly locate these outlined objects and extract their properties into simple data structures.

![RL object](https://user-images.githubusercontent.com/44652363/206809467-8cdefa01-235d-441f-b563-69773a2badb8.png)

### API
There are some RuneLite plugins that expose game data to a localhost API endpoint. You can leverage this data to provide a more robust botting experience without the risks associated with modifying the game client's code. See the [API utility folder](src/utilities/api/) for more.

## Random Click Distribution
With the help of the OSBC community, we've created a randomization algorithm that distributes clicks in a way that is more human-like. We followed the same principles used by individuals who've beat the system and achieved max levels without lifting a finger.

![click dist](https://user-images.githubusercontent.com/44652363/206948686-89cb0c30-8626-4aa2-9415-f2f985c80cbc.gif)

## Efficient Image Searching
Sometimes, your bot might need to find a specific image on screen. We've modified OpenCV's template matching algorithm to be more efficient and reliable with RuneScape UI elements and sprites - even supporting images with transparency. That means you can search images directly from the OSRS Wiki.

![shark](https://user-images.githubusercontent.com/44652363/206808973-8bea1717-c227-43cf-b8af-6825316eb95d.png)

## Lightning Fast Optical Character Recognition
We've ditched machine learned OCR in favor of a much faster and more reliable custom implementation. OSBC can locate text on screen in as little as **2 milliseconds**. That's **0.002 seconds**.

![ocr](https://user-images.githubusercontent.com/44652363/206808982-16f58a50-4709-4c27-9fc2-94b0c4edab21.png)
