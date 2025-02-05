import  ttkbootstrap as ttk
import ttkbootstrap.tableview
from PIL.ImageTk import PhotoImage
from pytablericons import TablerIcons, OutlineIcon

from gui import CatalystBondScanner


class ScannerTab(ttk.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.master: ttk.Notebook = kwargs['master']
        self.app :CatalystBondScanner = self.master.master
        self.tab_icon_img = PhotoImage(TablerIcons.load(OutlineIcon.SEARCH))
        self.pack(fill='both', expand=True)
        self.master.add(self, compound=ttk.TOP, image=self.tab_icon_img, text='Skaner')

        self.control_panel = ttk.LabelFrame(master=self, text='Ustawienia')
        self.control_panel.pack(fill='x', padx=10, pady=10)

        self.background = ttk.Label(master=self.control_panel, background='red')
        self.background.pack(fill='both', expand=True)


        coldata = [
            {'text': 'Obligacja', 'stretch': False},
            {'text': 'Emitent', 'stretch': False},
            {'text': 'Typ obligacji', 'stretch': False},
            {'text': 'Cena', 'stretch': False},
            {'text': 'Segment', 'stretch': False}
        ]
        self.table = ttkbootstrap.tableview.Tableview(master=self, coldata=coldata, autofit=True, searchable=True, delimiter=';', bootstyle=ttk.INFO)
        self.table.pack(fill='both', expand=True, padx=10, pady=10)
        self.update_table()

    def update_table(self):
        values = self.app.get_database_handler().select_bonds_view()
        rows = self.table.get_rows()

        for row in rows[::-1]:
            row_value = row.values
            row_found = False
            for value in values:
                #print(f'Comparing: {value[0]} with {row_value[0]} and {value[4]} with {row_value[4]}')
                if value[0] == row_value[0]:
                    row.configure(values=value)
                    values.remove(value)
                    row_found = True
                    break

            if not row_found:
                rows.remove(row)

        self.table.insert_rows('end', values)
        self.table.load_table_data()

        self.after(1000, self.update_table)