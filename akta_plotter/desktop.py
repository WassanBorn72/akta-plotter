"""Run with python -m akta_plotter.desktop."""
from pathlib import Path
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from . import __version__
from .data import read_export, label
from .plot import COLORS, Curve, make_overlay, parse_axis


class App:
    def __init__(self, root):
        self.root = root
        root.title(f'AKTA Plotter {__version__}')
        root.geometry('1300x850')
        self.figure = None
        self.files = []
        self.axis_values = {}
        self.x_settings = None
        self.y_settings = {}
        controls = ttk.Frame(root, padding=10)
        controls.pack(side='left', fill='y')
        ttk.Button(controls, text='CSVを追加（複数選択可）', command=self.open).pack(fill='x')
        ttk.Button(controls, text='全ファイルを解除', command=self.clear).pack(fill='x')
        self.title = tk.StringVar(value='AKTA overlay')
        ttk.Label(controls, text='グラフタイトル').pack(anchor='w')
        ttk.Entry(controls, textvariable=self.title).pack(fill='x')
        ttk.Button(controls, text='軸の設定', command=self.edit_axes).pack(fill='x', pady=6)
        ttk.Button(controls, text='プロット更新', command=self.draw).pack(fill='x')
        ttk.Button(controls, text='画像を保存', command=self.save).pack(fill='x', pady=6)
        self.dpi = tk.StringVar(value='200')
        ttk.Label(controls, text='出力解像度 (DPI: 72〜600)').pack(anchor='w')
        ttk.Entry(controls, textvariable=self.dpi).pack(fill='x')
        ttk.Label(controls, text='各曲線: 表示 / 色 / 太さ (pt)').pack(anchor='w', pady=8)
        canvas = tk.Canvas(controls, width=330, highlightthickness=0)
        scrollbar = ttk.Scrollbar(controls, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(fill='both', expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        self.file_area = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.file_area, anchor='nw')
        self.file_area.bind('<Configure>', lambda _: canvas.configure(scrollregion=canvas.bbox('all')))
        self.area = ttk.Frame(root)
        self.area.pack(side='right', fill='both', expand=True)

    def open(self):
        paths = filedialog.askopenfilenames(filetypes=[('CSV / TSV', '*.csv *.tsv *.txt'), ('All files', '*')])
        errors = []
        for path in paths:
            try:
                export = read_export(Path(path).read_bytes())
                source = f'{len(self.files) + 1}: {Path(path).name}'
                panel = ttk.LabelFrame(self.file_area, text=source, padding=5)
                panel.pack(fill='x', pady=6)
                columns = list(export.frame)
                x = tk.StringVar(value=columns[0])
                if not export.signal_x:
                    ttk.Label(panel, text='X軸').pack(anchor='w')
                    ttk.Combobox(panel, textvariable=x, values=columns, state='readonly', width=30).pack(fill='x')
                else:
                    ttk.Label(panel, text='X: mL / Y: 単位ごと').pack(anchor='w')
                candidates = list(export.signal_x) if export.signal_x else columns
                rows = []
                for index, name in enumerate(candidates):
                    row = ttk.Frame(panel)
                    row.pack(fill='x')
                    selected = tk.BooleanVar(value=name == (candidates[0] if export.signal_x else columns[1]))
                    color = tk.StringVar(value=COLORS[(len(self.files) + index) % len(COLORS)])
                    width = tk.StringVar(value='1.5')
                    ttk.Checkbutton(row, text=label(export, name), variable=selected).pack(side='left')
                    button = tk.Button(row, text='色', background=color.get(), width=2)
                    button.configure(command=lambda v=color, b=button: self.pick_color(v, b))
                    button.pack(side='right')
                    ttk.Entry(row, textvariable=width, width=5).pack(side='right')
                    rows.append((name, selected, color, width))
                self.files.append((export, source, x, rows))
            except Exception as exc:
                errors.append(f'{Path(path).name}: {exc}')
        if errors:
            messagebox.showerror('読み込みエラー', '\n'.join(errors))
        if self.files:
            self.draw()

    def pick_color(self, variable, button):
        _, color = colorchooser.askcolor(variable.get(), parent=self.root)
        if color:
            variable.set(color)
            button.configure(background=color)

    def clear(self):
        self.files.clear()
        for widget in self.file_area.winfo_children():
            widget.destroy()
        for widget in self.area.winfo_children():
            widget.destroy()
        self.figure = None
        self.axis_values.clear()
        self.x_settings = None
        self.y_settings.clear()

    def curves(self):
        curves = []
        for export, source, x, rows in self.files:
            for name, selected, color, width in rows:
                if selected.get() and (export.signal_x or name != x.get()):
                    try:
                        size = float(width.get())
                    except ValueError:
                        raise ValueError(f'{name}: 線の太さを数値で入力してください。') from None
                    curves.append(Curve(export, name, None if export.signal_x else x.get(), source, color.get(), size))
        return curves

    def edit_axes(self):
        try:
            curves = self.curves()
            if not curves:
                raise ValueError('表示する曲線を選択してください。')
        except Exception as exc:
            messagebox.showerror('軸の設定', str(exc))
            return
        dialog = tk.Toplevel(self.root)
        dialog.title('軸の設定（空欄は自動）')
        dialog.transient(self.root)
        dialog.grab_set()
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        units = list(dict.fromkeys(c.unit for c in curves))
        fields = {}
        for key, title in [('x', '横軸')] + [('y:' + unit, '縦軸 [' + unit + ']') for unit in units]:
            tab = ttk.Frame(notebook, padding=10)
            notebook.add(tab, text=title)
            stored = self.axis_values.get(key, ([''] * 4, True, False))
            values = []
            for i, text in enumerate(['最小値', '最大値', '主目盛り間隔', '副目盛り間隔']):
                ttk.Label(tab, text=text).grid(row=i, column=0, sticky='w')
                variable = tk.StringVar(value=stored[0][i])
                ttk.Entry(tab, textvariable=variable).grid(row=i, column=1, pady=3)
                values.append(variable)
            major, minor = tk.BooleanVar(value=stored[1]), tk.BooleanVar(value=stored[2])
            ttk.Checkbutton(tab, text='主目盛りの数値を表示', variable=major).grid(row=4, columnspan=2, sticky='w')
            ttk.Checkbutton(tab, text='副目盛りの数値を表示', variable=minor).grid(row=5, columnspan=2, sticky='w')
            fields[key] = (values, major, minor)

        def apply():
            try:
                saved = {key: ([v.get() for v in values], major.get(), minor.get())
                         for key, (values, major, minor) in fields.items()}
                parsed = {key: parse_axis(*value) for key, value in saved.items()}
                y_settings = {unit: parsed['y:' + unit] for unit in units}
                figure = make_overlay(curves, self.title.get(), parsed['x'], y_settings)
                self.axis_values.update(saved)
                self.x_settings, self.y_settings = parsed['x'], y_settings
                self.render(figure)
                dialog.destroy()
            except Exception as exc:
                messagebox.showerror('軸の設定エラー', str(exc), parent=dialog)
        ttk.Button(dialog, text='適用', command=apply).pack(pady=10)

    def render(self, figure):
        for widget in self.area.winfo_children():
            widget.destroy()
        self.figure = figure
        canvas = FigureCanvasTkAgg(figure, master=self.area)
        canvas.draw()
        NavigationToolbar2Tk(canvas, self.area).update()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def draw(self):
        try:
            figure = make_overlay(self.curves(), self.title.get(), self.x_settings, self.y_settings)
            self.render(figure)
        except Exception as exc:
            messagebox.showerror('プロットエラー', str(exc))

    def save(self):
        if not self.files:
            return
        try:
            # Render current controls, even when Update has not been pressed.
            figure = make_overlay(self.curves(), self.title.get(), self.x_settings, self.y_settings)
            dpi = int(self.dpi.get())
            if not 72 <= dpi <= 600:
                raise ValueError('DPIは72〜600の整数を入力してください。')
            path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG', '*.png'), ('SVG', '*.svg'), ('PDF', '*.pdf')])
            if path:
                figure.savefig(path, dpi=dpi)
                self.render(figure)
        except Exception as exc:
            messagebox.showerror('保存エラー', str(exc))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
