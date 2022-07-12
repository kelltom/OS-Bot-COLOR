import customtkinter


class ExampleBotOptions(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.options = {}

        # configure grid layout (3x1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.lbl_example_bot_options = customtkinter.CTkLabel(master=self,
                                                              text="Example Bot Options",
                                                              text_font=("Roboto Medium", 14))
        self.lbl_example_bot_options.grid(row=0, column=0, pady=10, padx=10)

        for i in range(1, 4):
            customtkinter.CTkLabel(master=self, text="Hello").grid(row=i, column=0, pady=10, padx=10)

        # Save button
        self.btn_save = customtkinter.CTkButton(master=self,
                                                text="Save",
                                                command=lambda: self.save(window=parent))
        self.btn_save.grid(row=4, column=0, pady=10, padx=20)

    def save(self, window):
        '''
        Gives controller a dictionary of options to save to the model. Destroys the window.
        '''
        self.options["iterations"] = 2
        self.controller.save_options(self.options)
        window.destroy()
