from typing import Dict, List
import customtkinter
import psutil
import platform



class OptionsBuilder:
    """
    The options map is going to hold the option name, and the UI details that will map to it. An instance of this class
    will go to the options UI class to be interpreted and built.
    """

    def __init__(self, title) -> None:
        self.options = {}
        self.title = title

    def add_slider_option(self, key, title, min, max):
        """
        Adds a slider option to the options menu.
        Args:
            key: The key to map the option to (use variable name in your script).
            title: The title of the option.
            min: The minimum value of the slider.
            max: The maximum value of the slider.
        """
        self.options[key] = SliderInfo(title, min, max)

    def add_checkbox_option(self, key, title, values: list):
        """
        Adds a checkbox option to the options menu.
        Args:
            key: The key to map the option to (use variable name in your script).
            title: The title of the option.
            values: A list of values to display for each checkbox.
        """
        self.options[key] = CheckboxInfo(title, values)

    def add_dropdown_option(self, key, title, values: list):
        """
        Adds a dropdown option to the options menu.
        Args:
            key: The key to map the option to (use variable name in your script).
            title: The title of the option.
            values: A list of values to display for each entry in the dropdown.
        """
        self.options[key] = OptionMenuInfo(title, values)
        
    def add_process_selector(self, key):
        """
        Adds a dropdown option to the options menu.
        Args:
            key: The key to map the option to (use variable name in your script).
            title: The title of the option.
        """
        process_selector = self.get_processes()
        self.options[key] = OptionMenuInfo("Select your client", process_selector)

    def add_text_edit_option(self, key, title, placeholder=None):
        """
        Adds a text edit option to the options menu.
        Args:
            key: The key to map the option to (use variable name in your script).
            title: The title of the option.
            placeholder: The placeholder text to display in the text edit box (optional).
        """
        self.options[key] = TextEditInfo(title, placeholder)

    def build_ui(self, parent, controller):
        """
        Returns a UI object that can be added to the parent window.
        """
        return OptionsUI(parent, self.title, self.options, controller)
    
    def get_processes(self):
        def get_window_title(pid):
            """Helper function to get the window title for a given PID."""
            titles = []
            if platform.system() == 'Windows':
                import ctypes
                EnumWindows = ctypes.windll.user32.EnumWindows
                EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
                GetWindowText = ctypes.windll.user32.GetWindowTextW
                GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
                IsWindowVisible = ctypes.windll.user32.IsWindowVisible
                GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
                def foreach_window(hwnd, lParam):
                    if IsWindowVisible(hwnd):
                        length = GetWindowTextLength(hwnd)
                        buff = ctypes.create_unicode_buffer(length + 1)
                        GetWindowText(hwnd, buff, length + 1)
                        window_pid = ctypes.c_ulong()
                        GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
                        if pid == window_pid.value:
                            titles.append(buff.value)
                    return True
                EnumWindows(EnumWindowsProc(foreach_window), 0)
                
            elif platform.system() == 'Darwin' or platform.system() == 'Linux':
                import Xlib.display
                display = Xlib.display.Display()
                root = display.screen().root
                window_ids = root.get_full_property(display.intern_atom("_NET_CLIENT_LIST"), Xlib.X.AnyPropertyType).value
                for window_id in window_ids:
                    try:
                        window = display.create_resource_object('window', window_id)
                        window_pid = window.get_full_property(display.intern_atom("_NET_WM_PID"), Xlib.X.AnyPropertyType).value[0]
                        if pid == window_pid:
                            window_title = window.get_full_property(display.intern_atom("_NET_WM_NAME"), Xlib.X.AnyPropertyType).value
                            if window_title:
                                titles.append(window_title.decode())
                    except:
                        pass
                display.close()
            return titles

        processes = {}
        for proc in psutil.process_iter():
            if 'Rune' in proc.name():
                name = proc.name()
                pid = proc.pid
                window_titles = get_window_title(pid)
                for window_title in window_titles:
                    if name in processes:
                        processes[name].append((pid, window_title))
                    else:
                        processes[name] = [(pid, window_title)]

        process_info = []
        for name, pids in processes.items():
            for pid, window_title in pids:
                process_info.append(f"{window_title} : {pid}")
        return process_info


    

class SliderInfo:
    def __init__(self, title, min, max):
        self.title = title
        self.min = min
        self.max = max


class OptionMenuInfo:
    def __init__(self, title, values: list):
        self.title = title
        self.values = values


class CheckboxInfo:
    def __init__(self, title, values: list):
        self.title = title
        self.values = values


class TextEditInfo:
    def __init__(self, title, placeholder):
        self.title = title
        self.placeholder = placeholder


class OptionsUI(customtkinter.CTkFrame):
    def __init__(self, parent, title: str, option_info: dict, controller):
        # sourcery skip: raise-specific-error
        super().__init__(parent)
        # Contains the widgets for option selection.
        # It will be queried to get the option values selected upon save btn clicked.
        self.widgets: Dict[str, customtkinter.CTkBaseClass] = {}
        # The following dicts exist to hold references to UI elements so they are not destroyed
        # by garbage collector.
        self.labels: Dict[str, customtkinter.CTkLabel] = {}
        self.frames: Dict[str, customtkinter.CTkFrame] = {}
        self.slider_values: Dict[str, customtkinter.CTkLabel] = {}

        self.controller = controller

        # Grid layout
        self.num_of_options = len(option_info.keys())
        self.rowconfigure(0, weight=0)  # Title
        for i in range(self.num_of_options):
            self.rowconfigure(i + 1, weight=0)
        self.rowconfigure(self.num_of_options + 1, weight=1)  # Spacing between Save btn and options
        self.rowconfigure(self.num_of_options + 2, weight=0)  # Save btn
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        # Title
        self.lbl_example_bot_options = customtkinter.CTkLabel(master=self, text=f"{title} Options", text_font=("Roboto Medium", 14))
        self.lbl_example_bot_options.grid(row=0, column=0, padx=10, pady=20)

        # Dynamically place widgets
        for row, (key, value) in enumerate(option_info.items(), start=1):
            if isinstance(value, SliderInfo):
                self.create_slider(key, value, row)
            elif isinstance(value, CheckboxInfo):
                self.create_checkboxes(key, value, row)
            elif isinstance(value, OptionMenuInfo):
                self.create_menu(key, value, row)
            elif isinstance(value, TextEditInfo):
                self.create_text_edit(key, value, row)
            else:
                raise Exception("Unknown option type")

        # Save button
        self.btn_save = customtkinter.CTkButton(master=self, text="Save", command=lambda: self.save(window=parent))
        self.btn_save.grid(row=self.num_of_options + 2, column=0, columnspan=2, pady=20, padx=20)

    def change_slider_val(self, key, value):
        self.slider_values[key].configure(text=str(int(value * 100)))

    def create_slider(self, key, value: SliderInfo, row: int):
        """
        Creates a slider widget and adds it to the view.
        """
        # Slider label
        self.labels[key] = customtkinter.CTkLabel(master=self, text=value.title)
        self.labels[key].grid(row=row, column=0, sticky="nsew", padx=10, pady=20)
        # Slider frame
        self.frames[key] = customtkinter.CTkFrame(master=self)
        self.frames[key].columnconfigure(0, weight=1)
        self.frames[key].columnconfigure(1, weight=0)
        self.frames[key].grid(row=row, column=1, sticky="ew", padx=(0, 10))
        # Slider value indicator
        self.slider_values[key] = customtkinter.CTkLabel(master=self.frames[key], text=str(value.min))
        self.slider_values[key].grid(row=0, column=1)
        # Slider widget
        self.widgets[key] = customtkinter.CTkSlider(
            master=self.frames[key],
            from_=value.min / 100,
            to=value.max / 100,
            command=lambda x: self.change_slider_val(key, x),
        )
        self.widgets[key].grid(row=0, column=0, sticky="ew")
        self.widgets[key].set(value.min / 100)

    def create_checkboxes(self, key, value: CheckboxInfo, row: int):
        """
        Creates checkbox widgets and adds them to the view.
        """
        # Checkbox label
        self.labels[key] = customtkinter.CTkLabel(master=self, text=value.title)
        self.labels[key].grid(row=row, column=0, padx=10, pady=20)
        # Checkbox frame
        self.frames[key] = customtkinter.CTkFrame(master=self)
        for i in range(len(value.values)):
            self.frames[key].columnconfigure(i, weight=1)
        self.frames[key].grid(row=row, column=1, sticky="ew", padx=(0, 10))
        # Checkbox values
        self.widgets[key]: List[customtkinter.CTkCheckBox] = []
        for i, value in enumerate(value.values):
            self.widgets[key].append(customtkinter.CTkCheckBox(master=self.frames[key], text=value))
            self.widgets[key][i].grid(row=0, column=i, sticky="ew", padx=5, pady=5)

    def create_menu(self, key, value: OptionMenuInfo, row: int):
        self.labels[key] = customtkinter.CTkLabel(master=self, text=value.title)
        self.labels[key].grid(row=row, column=0, sticky="nsew", padx=10, pady=20)
        self.widgets[key] = customtkinter.CTkOptionMenu(master=self, values=value.values, fg_color=("gray75", "gray22"))
        self.widgets[key].grid(row=row, column=1, sticky="ew", padx=(0, 10))

    def create_text_edit(self, key, value: TextEditInfo, row: int):
        self.labels[key] = customtkinter.CTkLabel(master=self, text=value.title)
        self.labels[key].grid(row=row, column=0, sticky="nsew", padx=10, pady=20)
        self.widgets[key] = customtkinter.CTkEntry(master=self, corner_radius=5, placeholder_text=value.placeholder)
        self.widgets[key].grid(row=row, column=1, sticky="ew", padx=(0, 10))

    def save(self, window):
        """
        Gives controller a dictionary of options to save to the model. Destroys the window.
        """
        self.options = {}
        for key, value in self.widgets.items():
            if isinstance(value, customtkinter.CTkSlider):
                self.options[key] = int(value.get() * 100)
            elif isinstance(value, list):  # Checkboxes
                self.options[key] = [checkbox.text for checkbox in value if checkbox.get()]
            elif isinstance(value, (customtkinter.CTkOptionMenu, customtkinter.CTkEntry)):
                self.options[key] = value.get()
        # Send to controller
        self.controller.save_options(self.options)
        window.destroy()
