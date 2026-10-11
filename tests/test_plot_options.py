import io
from pathlib import Path
import unittest
from matplotlib.ticker import MultipleLocator
from akta_plotter.data import read_export
from akta_plotter.plot import AxisSettings, Curve, make_overlay, parse_axis


class PlotOptionsTests(unittest.TestCase):
    def setUp(self):
        self.export = read_export((Path(__file__).resolve().parents[1] / 'examples/mixed_units.tsv').read_bytes())

    def test_overlay_styles_axes_and_image(self):
        second = read_export(b'Volume,UV\nml,mAU\n0,30\n1,60\n2,20\n')
        curves = [Curve(self.export, 'UV 280', source='run A', color='#123456', width=3),
                  Curve(second, 'UV', 'Volume', 'run B', '#ff0000', 2),
                  Curve(self.export, 'Conductivity', source='run A', color='#00aa00', width=1)]
        figure = make_overlay(curves, 'Overlay', AxisSettings(0, 5, 1, .25, False, True),
                              {'mAU': AxisSettings(-10, 120, 20, 5, True, False),
                               'mS/cm': AxisSettings(0, 20, 5, 1, False, False)})
        self.assertEqual(len(figure.axes), 2)
        left, right = figure.axes
        self.assertEqual(left.get_xlim(), (0, 5))
        self.assertEqual(left.get_ylim(), (-10, 120))
        self.assertEqual(right.get_ylim(), (0, 20))
        self.assertEqual(left.lines[0].get_color(), '#123456')
        self.assertEqual(left.lines[0].get_linewidth(), 3)
        self.assertEqual(list(left.lines[1].get_ydata()), [30, 60, 20])
        self.assertIn('run B', left.lines[1].get_label())
        self.assertIsInstance(left.xaxis.get_major_locator(), MultipleLocator)
        figure.canvas.draw()
        self.assertFalse(any(t.label1.get_visible() for t in left.xaxis.get_major_ticks()))
        self.assertTrue(any(t.label1.get_visible() for t in left.xaxis.get_minor_ticks()))
        self.assertFalse(any(t.label2.get_visible() for t in right.yaxis.get_major_ticks()))
        self.assertIn(20, left.get_yticks())
        for fmt in ('png', 'svg', 'pdf'):
            output = io.BytesIO()
            figure.savefig(output, format=fmt, dpi=100)
            self.assertGreater(len(output.getvalue()), 1000)

    def test_invalid_axis_settings(self):
        for values in (['2', '1', '', ''], ['', '', '0', ''],
                       ['', '', '', '-1'], ['nan', '', '', ''], ['abc', '', '', '']):
            with self.subTest(values=values), self.assertRaises(ValueError):
                parse_axis(values)
        with self.assertRaises(ValueError):
            make_overlay([Curve(self.export, 'UV 280')], x_settings=AxisSettings(0, 5, .00001))
        self.assertIsNone(parse_axis(['', '', '', '']).maximum)

    def test_reject_incompatible_x_units_and_width(self):
        time = read_export(b'Time,UV\nmin,mAU\n0,1\n1,2\n')
        with self.assertRaises(ValueError):
            make_overlay([Curve(self.export, 'UV 280'), Curve(time, 'UV', 'Time')])
        with self.assertRaises(ValueError):
            make_overlay([Curve(self.export, 'UV 280', width=0)])
