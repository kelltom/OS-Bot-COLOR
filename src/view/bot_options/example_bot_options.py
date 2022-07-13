import customtkinter


class ExampleBotOptions(customtkinter.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.options = {}

        # Grid layout
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(9, weight=1)  # Spacing between Save btn and options
        self.rowconfigure(10, weight=0)  # Save btn
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # Title
        self.lbl_example_bot_options = customtkinter.CTkLabel(master=self,
                                                              text="Example Bot Options",
                                                              text_font=("Roboto Medium", 14))
        self.lbl_example_bot_options.grid(row=0, column=0, padx=10, pady=20)

        # All options should have 10px of spacing between them, and 10px to either side

        # ------------- Iterations -------------
        self.lbl_iterations = customtkinter.CTkLabel(master=self,
                                                     text="Iterations")
        self.lbl_iterations.grid(row=1, column=0, sticky='nsew', padx=(10, 0), pady=20)  # <-- PADDING ON LEFT
        # -- Frame for slider and value indicator
        self.frame_iterations = customtkinter.CTkFrame(master=self)
        self.frame_iterations.columnconfigure(0, weight=1)
        self.frame_iterations.columnconfigure(1, weight=0)
        self.frame_iterations.grid(row=1, column=1, sticky="ew", padx=(0, 10))  # <-- PADDING ON RIGHT
        # -- Slider
        self.slider_iterations = customtkinter.CTkSlider(master=self.frame_iterations,
                                                         command=self.change_iterations)
        self.slider_iterations.grid(row=0, column=0, sticky="ew")
        self.slider_iterations.set(0)
        # -- Value indicator
        self.lbl_iterations_value = customtkinter.CTkLabel(master=self.frame_iterations,
                                                           text="0")
        self.lbl_iterations_value.grid(row=0, column=1)

        # ------------- Multi Select Example -------------
        self.lbl_multi_select_example = customtkinter.CTkLabel(master=self,
                                                               text="Multi Select Example")
        self.lbl_multi_select_example.grid(row=2, column=0, sticky='nsew', padx=(10, 0), pady=20)  # <-- PADDING ON LEFT
        # -- Frame for checkboxes
        self.frame_multi_select_example = customtkinter.CTkFrame(master=self)
        self.frame_multi_select_example.columnconfigure(0, weight=1)
        self.frame_multi_select_example.columnconfigure(1, weight=1)
        self.frame_multi_select_example.columnconfigure(2, weight=1)
        self.frame_multi_select_example.grid(row=2, column=1, sticky="ew", padx=(0, 10))  # <-- PADDING ON RIGHT
        # -- Checkboxes
        self.chk_multi_select_example_1 = customtkinter.CTkCheckBox(master=self.frame_multi_select_example,
                                                                    text="Option 1")
        self.chk_multi_select_example_1.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.chk_multi_select_example_2 = customtkinter.CTkCheckBox(master=self.frame_multi_select_example,
                                                                    text="Option 2")
        self.chk_multi_select_example_2.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.chk_multi_select_example_3 = customtkinter.CTkCheckBox(master=self.frame_multi_select_example,
                                                                    text="Option 3")
        self.chk_multi_select_example_3.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

        # ------------- Menu Example -------------
        self.lbl_menu_example = customtkinter.CTkLabel(master=self,
                                                       text="Menu Example")
        self.lbl_menu_example.grid(row=3, column=0, sticky='nsew', padx=(10, 0), pady=20)
        self.menu = customtkinter.CTkOptionMenu(master=self,
                                                values=["Option 1", "Option 2", "Option 3"])
        self.menu.grid(row=3, column=1, sticky="ew", padx=(0, 10))

        # Save button
        self.btn_save = customtkinter.CTkButton(master=self,
                                                text="Save",
                                                command=lambda: self.save(window=parent))
        self.btn_save.grid(row=10, column=0, columnspan=2, pady=20, padx=20)

    def change_iterations(self, value):
        self.lbl_iterations_value.config(text=str(int(value * 100)))

    def save(self, window):
        '''
        Gives controller a dictionary of options to save to the model. Destroys the window.
        '''
        # Get iterations
        self.options["iterations"] = int(self.slider_iterations.get() * 100)
        # Get checkboxes
        self.options["multi_select_example"] = []
        if self.chk_multi_select_example_1.get():
            self.options["multi_select_example"].append(1)
        if self.chk_multi_select_example_2.get():
            self.options["multi_select_example"].append(2)
        if self.chk_multi_select_example_3.get():
            self.options["multi_select_example"].append(3)
        # Get menu
        self.options["menu_example"] = self.menu.get()

        # Send to controller
        self.controller.save_options(self.options)
        window.destroy()
