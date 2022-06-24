'''
Should provide the view(s) to be returned to the main view.
Should also use the script1_controller.
'''
import customtkinter
import tkinter as tk


class CerberusView(customtkinter.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # create widgets
        # label
        self.label = tk.Label(self, text='Cerb:')
        self.label.grid(row=1, column=0)

        # email entry
        self.email_var = tk.StringVar()
        self.email_entry = tk.Entry(self, textvariable=self.email_var, width=30)
        self.email_entry.grid(row=1, column=1, sticky=tk.NSEW)

        # save button
        self.save_button = tk.Button(self, text='Cerb')
        self.save_button.grid(row=1, column=3, padx=10)

        # message
        self.message_label = tk.Label(self, text='', foreground='red')
        self.message_label.grid(row=2, column=1, sticky=tk.W)
