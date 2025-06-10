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



        self.table_frame = ttk.Frame(master=self)
        self.table_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        #TODO Custom table widget
        coldata = [
            {'text': 'Obligacja'},
            {'text': 'Typ obligacji'},
            {'text': 'Emitent'},
            {'text': 'Wykup'},
            {'text': 'Nominał', 'anchor': 'e'},
            {'text': 'Waluta'},
            {'text': 'Cena', 'anchor': 'e'},
            {'text': 'Rynek'},
            {'text': 'Rentowność bierząca', 'anchor': 'e'},
            {'text': 'Rentowność YTM', 'anchor': 'e'},
            {'text': 'Oprocentowanie bierzące', 'anchor': 'e'},
            {'text': 'Oprocentowanie', 'anchor': 'e'}
        ]
        self.table = ttkbootstrap.tableview.Tableview(master=self.table_frame, coldata=coldata, autofit=True, searchable=True, delimiter=';', bootstyle=ttk.INFO)
        self.table.pack(side='left', fill='both', expand=True)

        self.table_scroll = ttk.Scrollbar(master=self.table_frame, command=self.table.view.yview)
        self.table.view.configure(yscrollcommand=self.table_scroll.set)
        self.table_scroll.pack(side='left', fill='y', padx=(10, 0))

        self.update_table()

    def update_table(self):
        values = self.app.get_database_handler().select_bonds_table()
        rows = self.table.get_rows()

        has_changed = False

        for row in rows[::-1]:
            row_value = row.values
            row_found = False
            for value in values:
                if value[0] == row_value[0] and value[7] == row_value[7]:
                    row.configure(values=value)
                    values.remove(value)
                    row_found = True
                    has_changed = True
                    break

            if not row_found:
                rows.remove(row)

        if len(values) > 0:
            has_changed = True
            self.table.insert_rows('end', values)

        self.table.load_table_data()

        if has_changed:
            self.table.autofit_columns()

        self.after(1000, self.update_table)