# osnr-bot
 A program that can execute a variety of automation tools for Old School Near Reality.

# Instructions for adding new bots
These instructions are only valid as of July 4th 2022.

Much of the boilerplate code is already in place. You just need to add and modify a few files to add a new bot. Before jumping the gun, make sure you have a good understanding of the codebase and have finished reading this guide.

## Building the UI
Much of the UI code is already written for you. However, since each bot is different, you must implement the *options panel* for the UI manually.

You'll need to add the following:
- Add a new button to the left panel in [main.py](src/main.py).
- Add a new [BotView](src/views/bot_view.py) to the right panel in [main.py](src/main.py).
- Create a reference to your custom bot model in [src/model](src/model/).
- Create a reference to a new [BotController](src/controller/bot_controller.py), passing it the newly created BotView and Bot Model.
- Lastly, call the setup() method on the BotView passing it the required arguments, including an instance of a custom Options frame (more on this later).

### Step 1: Create the button in main.py
Find the section where all the other script buttons exist and add a new button. The command of this button should call the existing *show_frame()* function with a name matching the name of your bot. We are using "Woodcutting" in this example.

```python
self.btn_name = customtkinter.CTkButton(master=self.frame_left,
                                        text="Woodcutting",
                                        fg_color=("gray75", "gray30"),
                                        command=lambda: self.show_frame("Woodcutting", self.btn_name))
self.btn_name.grid(row=3, column=0, pady=10, padx=20)
# Make sure to append the button to the button list
self.button_list.append(self.btn_name)
```

### Step 2: Create the BotView in main.py
Navigate main.py to find the section where all the other BotViews exist and add a new BotView. The name of the BotView should match the name of your bot. The parent should be *self.frame_right*.

```python
self.view_list["Woodcutting"] = BotView(parent=self.frame_right)
```
**At this point, you can run the app to see the base UI and functionality that this creates. The buttons on the right-side view should not work at this stage.**

### Step 3: Create an instance of your bot's model in main.py
Directly below the BotView you created in main.py, add a new instance of your bot's model. The name of the model should match the name of your bot. For instructions on how to create a model, see the [Bot logic section](#bot-logic).

```python
self.wc_model = Woodcutting()
```

### Step 4: Create an instance of BotController in main.py
The bot controller is entirely prewritten. You just need to pass create an instance of it and pass it to the BotView you created in main.py. The controller handles interaction between the bot/model and the view.

```python
self.wc_controller = BotController(model=self.wc_model,
                                   view=self.view_list["Woodcutting"])
```

### Step 5: Create the Options frame in main.py
**TODO: Describe how the options frame is made.**

### Step 6: Call the setup() method on the BotView in main.py
To finalize the BotView UI, you must call the setup() method. This will establish the connection between the model and the view via the controller, update the name/description in the information panel, and set up the options panel.

```python
self.view_list["Woodcutting"].setup(controller=self.wc_controller,
                                    options_view=WoodcuttingOptionsFrame(parent=self.view_list["Woodcutting"]),
                                    title=self.wc_model.title,
                                    description=self.wc_model.description)
```

Now, the UI should be fairly functional. You will need to implement the main_loop() function of your bot's model in order for the control buttons to work.

## Bot logic
To create a new bot script, begin by creating a new model file for your bot in [src/model](src/model/). For instance, if you are making a bot for woodcutting, call it *woodcutting.py*. Create a class that extends [Bot](src/model/bot.py). The majority of the logic for controlling your bot should already be implemented in the base class.

```python
from model.bot import Bot, BotStatus

class Woodcutting(Bot):
    def __init__(self):
        title = "Firemaking"
        description = ("Some " + "description")
        super().__init__(title=title, description=description)
    
    def save_settings(self, settings: dict):
        pass

    def main_loop(self):
        '''
        This is run on another thread.
        '''
        pass
```

The *main_loop()* function is where your bot's logic will go. It will run on a separate thread. Be sure to have many spots in your loop that will check for the [status](src/model/bot.py) of your bot such that you can decide what should happen when it is paused or stopped. When the status of the bot is set to *BotStatus.STOPPED*, your main loop should do its best to break and reach the end of the code block so the thread can terminate.

```python
if self.status == BotStatus.STOPPED:
    self.log_msg("Bot stopped. Breaking...")
    break
```

### Bot Commands
**TODO: A library will be created for the bot to use. This library will simplify basic bot commands, such as moving a character around, teleporting, and interacting with objects.**

This line should go after the line that creates the BotView.
### Updating the UI throughout bot loop
Throughout your *main_loop()* function, you should make use of functions that relay information back to the UI. For instance, when an iteration of the bot loop has finished, you should call the [increment_iter()](src/model/bot.py#increment_iter) function, which will update the progress bar on the UI as well as updating the bot's current iterations counter property. [log_msg()](src/model/bot.py#log_msg) is a function that will log a message to the UI, and should be used frequently to keep the user informed of the bot's progress.

**TODO: Add full list of built-in functions users should use.**
