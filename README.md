# osrs-bot
 A program that can execute a variety of automation tools for Old School RS.
 This project is a work in progress and is not yet complete.

# Project Setup
1. Clone/download the repository.
2. Open the repository folder in a terminal window.
   1. Create a virtual environment. ```python -m venv env```
   2. Activate the newly created virtual environment. ```.\env\Scripts\activate```
   3. Install the depedencies. ```pip install -r requirements.txt```
3. Open the project folder in your IDE (VS Code preferred).
4. Run main.py (./src/main.py)

# Instructions for adding new bots
These instructions are only valid as of **July 5th 2022**.

Much of the boilerplate code is already in place. You just need to add and modify a few files to add a new bot. Before jumping the gun, make sure you have a good understanding of the codebase and have finished reading this guide.

## Building the UI
Much of the UI code is already written for you. However, since each bot is different, you must implement the *options panel* for the UI manually.

You'll need to add the following:
- Add a new button to the left panel in [main.py](src/main.py).
- Add a new [BotView](src/views/bot_view.py) to the right panel in [main.py](src/main.py).
- Create a reference to your custom bot model in [src/model](src/model/).
- Create a reference to a new [BotController](src/controller/bot_controller.py), passing it the newly created BotView and Bot Model.
- Lastly, call the setup() method on the BotView passing it the required arguments.

### Step 1: Create the button in main.py
Find the section where all the other script buttons exist and add a new button. The command of this button should call the existing *show_frame()* function with a name matching the name of your bot. We are using "Woodcutting" in this example.

```python
self.btn_wc = customtkinter.CTkButton(master=self.frame_left,
                                      text="Woodcutting",
                                      fg_color=("gray75", "gray30"),
                                      command=lambda: self.toggle_frame_by_name("Woodcutting", self.btn_wc))
# Set row argument according to position of button in left panel
self.btn_wc.grid(row=3, column=0, pady=10, padx=20)
```

### Step 2: Create the BotView in main.py
Navigate main.py to find the section where all the other BotViews exist and add a new BotView. You should instantiate this new view as a member of the views dictionary. The key that you assign this object to should be the name of your bot. The parent argument should always be *self.frame_right*.

```python
self.views["Woodcutting"] = BotView(parent=self.frame_right)
```
**At this point, you can run the app to see the base UI and functionality that this creates. The buttons on the right-side view should not work at this stage.**

### Step 3: Create an instance of your bot's model in main.py
Directly below the BotView you created in main.py, create a new instance of your bot's model. For instructions on how to create a model, see the [Bot logic section](#bot-logic). If you have not yet implemented a bot model, you can use the [ExampleBot](src/model/example.py) class as a substitute.

```python
self.wc_model = Woodcutting()
```

### Step 4: Create an instance of BotController in main.py
The bot controller is entirely prewritten. You just need to create an instance of it and pass it to the BotView you created in main.py. The controller handles interaction between the bot/model and the view.

```python
self.wc_controller = BotController(model=self.wc_model,
                                   view=self.views["Woodcutting"])
```

### Step 5: Call the setup() method on the BotView in main.py
To finalize the BotView UI, you must call the setup() method. This will establish the connection between the model and the view via the controller, and update the name/description in the information panel.

```python
self.views["Woodcutting"].setup(controller=self.wc_controller,
                                title=self.wc_model.title,
                                description=self.wc_model.description)
```

If you used the [ExampleBot](src/model/example_bot.py) model as a substitute, your UI should be fairly functional. Otherwise, see the next section for how to implement a custom bot model.

### Here's what it should look like when you're done:
```python
# --- Buttons ---
self.btn_wc = customtkinter.CTkButton(master=self.frame_left,
                                      text="Woodcutting",
                                      fg_color=("gray75", "gray30"),
                                      command=lambda: self.toggle_frame_by_name("Woodcutting", self.btn_wc))
self.btn_wc.grid(row=?, column=0, pady=10, padx=20)
# --- Views ---
self.views = {}
self.views["Woodcutting"] = BotView(parent=self.frame_right)
self.wc_model = Woodcutting()
self.wc_controller = BotController(model=self.wc_model,
                                   view=self.views["Woodcutting"])
self.views["Woodcutting"].setup(controller=self.wc_controller,
                                title=self.wc_model.title,
                                description=self.wc_model.description)
```

## Bot logic
To create a new bot model and script, begin by creating a new model file in [src/model](src/model/). For instance, if you are making a bot for woodcutting, call it *woodcutting.py*. Create a class of matching name that extends [Bot](src/model/bot.py). The majority of the logic for controlling your bot is already implemented in the base class. You need only implement the three required functions below.

```python
from model.bot import Bot, BotStatus

class Woodcutting(Bot):
    def __init__(self):
        title = "Woodcutting"
        description = ("Some " + "description")
        super().__init__(title=title, description=description)
    
    def main_loop(self):
        '''
        Main logic of the bot. This function is called in a separate thread. The main loop should frequently
        check the status of the bot and terminate when the status is STOPPED.
        '''
        pass

    def set_options_gui(self):
        '''
        Runs PyAutoGUI message boxes to set the options for the bot. This function is called on a separate thread.
        Collect all necessary information from the user and set the bot's options. This function should log messages
        to the controller upon failure or success, and set the options_set flag to True if successful.
        '''
        pass
```

The *init()* function requires you to specify a bot title and description and pass them along to the base class. You can also declare any other attributes/options you want to use in your bot (E.g., for a Woodcutting bot, you may want to have a reference to the type of log to burn).

The *main_loop()* function is where your bot's logic will go. It will run on a separate thread. Be sure to have many spots in your loop that will check for the [status](src/model/bot.py) of your bot such that you can decide what should happen when it is paused or stopped. When the status of the bot is set to *BotStatus.STOPPED*, your main loop should do its best to reach the end of the code block or return so the thread can terminate. See [ExampleBot](src/model/example_bot.py) for an example of how to do this.

```python
if self.status == BotStatus.STOPPED:
    self.log_msg("Bot stopped. Breaking...")
    return
```

The *set_options_gui()* function is where you will need to implement the logic for setting the bot's configuration based on user input. The best way to do this is to use PyAutoGUI message boxes. Collect user input for things like how many iterations they want the bot to run (or how many logs to burn), whether or not to take random breaks, etc., and then assign that input to the bot's properties. The *main_loop()* should make use of these properties to operate.

### Bot Commands
**TODO: A library will be created for the bot to use. This library will simplify basic bot commands, such as moving a character around, teleporting, and interacting with objects.**

### Updating the UI throughout the bot loop
Throughout your *main_loop()* function, you should make use of functions that relay information back to the UI. For instance, when an iteration of the bot loop has finished, you should call the [increment_iter()](src/model/bot.py#increment_iter) function, which will update the progress bar on the UI as well as updating the bot's current iterations counter property. [log_msg()](src/model/bot.py#log_msg) is a function that will log a message to the UI, and should be used frequently to keep the user informed of the bot's progress.

**TODO: Add full list of built-in functions users should use.**
