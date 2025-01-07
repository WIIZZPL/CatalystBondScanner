import datetime
import tkinter.font
import ttkbootstrap as ttk
from PIL.ImageTk import PhotoImage
from pytablericons import TablerIcons, FilledIcon, OutlineIcon
from db_access import DatabaseHandler

class HomeTab(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.master: ttk.Notebook = kwargs['master']

        self.tab_icon_img = PhotoImage(TablerIcons.load(FilledIcon.HOME))
        self.pack(fill='both', expand=True)

        self.master.add(self, compound=ttk.TOP, image=self.tab_icon_img, text='Powitanie')

        self.frame = ttk.Frame(self)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')

        self.logo_icon_img = PhotoImage(TablerIcons.load(OutlineIcon.SEARCH, 100))
        self.logo_label = ttk.Label(self.frame, image=self.logo_icon_img)
        self.logo_label.pack()

        self.welcome_label = ttk.Label(self.frame, text="Skaner Obligacji GPW", font=(tkinter.font.nametofont('TkDefaultFont'), 32))
        self.welcome_label.pack()

        self.update_frame = ttk.Frame(self.frame)
        self.update_frame.pack(pady=10)

        self.last_update_text_label = ttk.Label(self.update_frame, text="Ostatnio aktualizowane: ")
        self.last_update_text_label.pack(side='left')

        self.last_update_date_label = ttk.Label(self.update_frame)
        self.last_update_date_label.pack(side='left')

        self.update_button = ttk.Button(self.update_frame, text='Aktualizuj', command=lambda:self.master.master.switch_and_sync(), bootstyle=ttk.INFO)
        self.update_button.pack(padx=10)

    def on_tab_show(self):
        # last modify date update
        last_modified_date: datetime.date = self.master.master.get_database_handler().get_last_modified_date()

        if last_modified_date is None:
            self.last_update_date_label.configure(bootstyle='inverse-danger')
            self.last_update_date_label['text'] = 'NIGDY'
        else:
            self.last_update_date_label['text'] = last_modified_date
            days_diff = abs((last_modified_date - datetime.date.today()).days)

            if days_diff != 0:
                self.update_button.forget()
            else:
                self.update_button.pack(padx=10)

            if days_diff < 7:
                self.last_update_date_label.config(bootstyle='inverse-success')
            elif days_diff < 30:
                self.last_update_date_label.config(bootstyle='inverse-warning')
            else:
                self.last_update_date_label.config(bootstyle='inverse-danger')