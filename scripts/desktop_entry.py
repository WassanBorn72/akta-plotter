"""Entry point for the standalone application and bundled runtime checks."""
import io
import sys
from pathlib import Path

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def self_test():
    from akta_plotter.data import read_export
    from akta_plotter.plot import AxisSettings, Curve, make_overlay
    raw = ('Chrom.1\t\tChrom.1\t\tChrom.1\t\n'
           'UV\t\tInjection\t\tConductivity\t\n'
           'ml\tmAU\tml\tInjection\tml\tmS/cm\n'
           '0\t10\t0\t99\t0\t5\n1\t20\t1\t99\t1\t6\n').encode('utf-16')
    export = read_export(raw)
    figure = make_overlay([Curve(export, y) for y in export.signal_x],
                          x_settings=AxisSettings(0, 2, 1, .5))
    if list(export.signal_x) != ['UV', 'Conductivity']:
        raise RuntimeError('Bundled signal exclusion/right-side check failed')
    if len(figure.axes) != 2 or figure.axes[0].get_xlabel() != 'mL':
        raise RuntimeError('Bundled plotting check failed')
    for fmt in ('png', 'svg', 'pdf'):
        buffer = io.BytesIO()
        figure.savefig(buffer, format=fmt)
        if len(buffer.getvalue()) < 1000:
            raise RuntimeError(f'Bundled {fmt} export failed')
    print('AKTA Plotter bundled CSV/plot/export self-test passed')


def main():
    if '--self-test' in sys.argv:
        self_test()
    elif '--gui-smoke-test' in sys.argv:
        import tkinter as tk
        from akta_plotter.desktop import App
        root = tk.Tk()
        root.withdraw()
        import tempfile
        import akta_plotter.desktop as desktop
        app = App(root)
        if app.window_icon.width() != 1024 or app.window_icon.height() != 1024:
            raise RuntimeError('Bundled application icon is missing or invalid')
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / 'A.csv', Path(directory) / 'B.csv']
            for path in paths:
                path.write_text('Volume,UV,Conductivity\nml,mAU,mS/cm\n0,10,5\n1,20,6\n')
            def fail(title, message, **kwargs):
                raise RuntimeError(f'{title}: {message}')
            original_open = desktop.filedialog.askopenfilenames
            original_save = desktop.filedialog.asksaveasfilename
            original_error = desktop.messagebox.showerror
            try:
                desktop.filedialog.askopenfilenames = lambda **kwargs: [str(p) for p in paths]
                desktop.messagebox.showerror = fail
                app.open()
                app.files[0][3][2][1].set(True)
                app.files[0][3][1][4].set('Edited caption')
                app.show_frame.set(False)
                app.show_grid.set(False)
                app.draw()
                if app.figure.axes[0].get_legend().get_texts()[0].get_text() != 'Edited caption':
                    raise RuntimeError('GUI caption editing failed')
                if app.figure.axes[0].spines['top'].get_visible():
                    raise RuntimeError('GUI frame setting failed')
                app.show_legend.set(False)
                if len(app.files) != 2 or len(app.figure.axes) != 2:
                    raise RuntimeError('GUI file overlay failed')
                target = Path(directory) / 'plot.png'
                desktop.filedialog.asksaveasfilename = lambda **kwargs: str(target)
                app.save()
                if app.figure.axes[0].get_legend() is not None:
                    raise RuntimeError('GUI legend visibility was not applied on save')
                if not target.exists() or target.stat().st_size < 1000:
                    raise RuntimeError('GUI save failed')
            finally:
                desktop.filedialog.askopenfilenames = original_open
                desktop.filedialog.asksaveasfilename = original_save
                desktop.messagebox.showerror = original_error
            root.update()
        root.destroy()
        print('AKTA Plotter bundled GUI overlay/save check passed')
    else:
        from akta_plotter.desktop import main as desktop_main
        desktop_main()


if __name__ == '__main__':
    main()
