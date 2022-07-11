import customtkinter


class ExampleBotOptions(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.rowconfigure(0, weight=1)

        self.lbl_example_bot_options = customtkinter.CTkLabel(master=self,
                                                              text="Example Bot Options", 
                                                              text_font=("Roboto Medium", 14))
        self.lbl_example_bot_options.grid(row=0, column=0, pady=10, padx=10)
