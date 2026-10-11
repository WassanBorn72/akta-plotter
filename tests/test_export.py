import unittest
from pathlib import Path
from akta_plotter.data import read_export
from akta_plotter.plot import make_figure


class ExportTests(unittest.TestCase):
    def test_metadata_units_and_duplicate_columns(self):
        raw = b'Run: demo\nVolume,UV,Volume,Conductivity\nml,mAU,ml,mS/cm\n0,1,0,5\n1,2,1,6\n'
        export = read_export(raw)
        self.assertEqual(list(export.frame), ['Volume', 'UV', 'Volume (2)', 'Conductivity'])
        self.assertEqual(export.units['UV'], 'mAU')
        self.assertEqual(export.frame.shape, (2, 4))
        figure = make_figure(export, 'Volume', ['UV', 'Conductivity'])
        self.assertEqual(len(figure.axes), 2)
        self.assertEqual(list(figure.axes[0].lines[0].get_ydata()), [1, 2])

    def test_utf16_tab_and_missing_values(self):
        export = read_export('Volume\tUV\n0\t1\n1\t\n2\t3\n'.encode('utf-16'))
        figure = make_figure(export, 'Volume', ['UV'])
        self.assertEqual(list(figure.axes[0].lines[0].get_xdata()), [0, 2])

    def test_unicorn_signal_pairs_before_injection(self):
        text = ('Chrom.1\t\tChrom.1\t\tChrom.1\t\tChrom.1\t\n'
                'UV 3_480\t\tUV 1_280\t\tInjection\t\tUV derived\t\n'
                'ml\tmAU\tml\tmAU\tml\tInjection\tml\tmAU\n'
                '0\t10\t0.5\t20\t0\t\t0\t999\n'
                '1\t11\t0.6\t21\t\t\t1\t999\n'
                '\t\t0.7\t22\t\t\t2\t999\n')
        export = read_export(text.encode('utf-16'))
        self.assertEqual(list(export.signal_x), ['UV 3_480', 'UV 1_280'])
        self.assertNotIn('UV derived', export.frame)
        figure = make_figure(export, None, list(export.signal_x))
        self.assertEqual(len(figure.axes), 1)
        axis = figure.axes[0]
        self.assertEqual(axis.get_xlabel(), 'mL')
        self.assertEqual(axis.get_ylabel(), 'mAU')
        self.assertEqual(list(axis.lines[0].get_xdata()), [0, 1])
        self.assertEqual(list(axis.lines[1].get_xdata()), [.5, .6, .7])
        self.assertEqual(list(axis.lines[1].get_ydata()), [20, 21, 22])

    def test_mixed_units_share_only_matching_axes(self):
        export = read_export((Path(__file__).resolve().parents[1] / 'examples/mixed_units.tsv').read_bytes())
        self.assertEqual(list(export.signal_x),
                         ['UV 280', 'UV 480', 'Conductivity', 'Concentration', 'Pressure'])
        figure = make_figure(export, None, list(export.signal_x), separate_axes=False)
        self.assertEqual([a.get_ylabel() for a in figure.axes], ['mAU', 'mS/cm', '%', 'MPa'])
        self.assertEqual([len(a.lines) for a in figure.axes], [2, 1, 1, 1])
        self.assertEqual(list(figure.axes[0].lines[1].get_xdata()), [0, .8, 1.8, 2.8, 3.8])
        self.assertEqual(list(figure.axes[1].lines[0].get_ydata()), [5, 6, 8, 12, 15])
        single = make_figure(export, None, ['Pressure'])
        self.assertEqual(single.axes[0].get_ylabel(), 'MPa')
        self.assertEqual(len(single.axes), 1)

    def test_non_uv_pair_and_non_numeric_event(self):
        raw = ('Chrom.1\t\tChrom.1\t\tChrom.1\t\n'
               'Conductivity\t\tEvent\t\tInjection\t\n'
               'ml\tmS/cm\tml\tLogbook\tml\tInjection\n'
               '0\t5\t0\tStart\t0\tInject\n1\t6\t1\tEnd\t\t\n')
        export = read_export(raw.encode())
        self.assertEqual(list(export.signal_x), ['Conductivity'])
        self.assertEqual(make_figure(export, None, ['Conductivity']).axes[0].get_ylabel(), 'mS/cm')

    def test_decimal_comma(self):
        export = read_export(b'Volume;UV\n0,5;1,2\n1,5;2,3\n')
        self.assertEqual(export.frame.iloc[0, 0], .5)

    def test_reject_non_numeric(self):
        with self.assertRaises(ValueError):
            read_export(b'Name,Description\na,b\n')


if __name__ == '__main__':
    unittest.main()
