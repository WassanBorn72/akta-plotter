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
           'UV\t\tConductivity\t\tInjection\t\n'
           'ml\tmAU\tml\tmS/cm\tml\tInjection\n'
           '0\t10\t0\t5\t0\tInject\n1\t20\t1\t6\t\t\n').encode('utf-16')
    export = read_export(raw)
    figure = make_overlay([Curve(export, y) for y in export.signal_x],
                          x_settings=AxisSettings(0, 2, 1, .5))
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
                app.draw()
                if len(app.files) != 2 or len(app.figure.axes) != 2:
                    raise RuntimeError('GUI file overlay failed')
                target = Path(directory) / 'plot.png'
                desktop.filedialog.asksaveasfilename = lambda **kwargs: str(target)
                app.save()
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
