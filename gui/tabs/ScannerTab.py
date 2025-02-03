import  ttkbootstrap as ttk
import ttkbootstrap.tableview
from PIL.ImageTk import PhotoImage
from bs4.diagnose import rword
from pytablericons import TablerIcons, OutlineIcon

class ScannerTab(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.master: ttk.Notebook = kwargs['master']

        self.tab_icon_img = PhotoImage(TablerIcons.load(OutlineIcon.SEARCH))
        self.pack(fill='both', expand=True)

        self.master.add(self, compound=ttk.TOP, image=self.tab_icon_img, text='Skaner')


        coldata = [
            'code',
            'issuer',
            'type',
            'price',
            'market'
        ]
        self.table = ttkbootstrap.tableview.Tableview(master=self, coldata=coldata, paginated=True)
        self.table.pack(fill='both', expand=True)
        self.update_table()

    def update_table(self):
        values = self.master.master.get_database_handler().select_bonds_view()
        rows = self.table.tablerows

        for value in values:
            for row in rows:
                if row.values[0] == value[0] and row.values[-1] == value[-1]:
                    values.remove(value)
                    rows.remove(row)
                    row.refresh()
                    break

        print(len(values))
        for value in values:
            self.table.insert_row('end', value)
            self.table.tablerows[-1].build()

        self.table.load_table_data()

        self.after(1000, self.update_table)