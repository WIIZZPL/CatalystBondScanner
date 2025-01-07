import  ttkbootstrap as ttk
from PIL.ImageTk import PhotoImage
from pytablericons import TablerIcons, FilledIcon

class IssuerTab(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        master: ttk.Notebook = kwargs['master']

        self.pack(fill='both', expand=True)

        self.tab_icon_img = PhotoImage(TablerIcons.load(FilledIcon.USER))

        label1 = ttk.Label(self, text="Issuer Tab")
        label1.pack()

        master.add(self, compound=ttk.TOP, image=self.tab_icon_img, text='Emitenci')