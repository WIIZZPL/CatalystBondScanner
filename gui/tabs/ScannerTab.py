import  ttkbootstrap as ttk
from PIL.ImageTk import PhotoImage
from pytablericons import TablerIcons, OutlineIcon

class ScannerTab(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.master: ttk.Notebook = kwargs['master']

        self.tab_icon_img = PhotoImage(TablerIcons.load(OutlineIcon.SEARCH))
        self.pack(fill='both', expand=True)

        self.master.add(self, compound=ttk.TOP, image=self.tab_icon_img, text='Skaner')

        label1 = ttk.Label(self, text="Scanner Tab")
        label1.pack()
