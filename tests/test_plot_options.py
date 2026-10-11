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

    def test_axis_names_caption_and_publication_style(self):
        from akta_plotter.plot import PlotSettings
        for direction in ('in', 'out', 'inout'):
            with self.subTest(direction=direction):
                figure = make_overlay([Curve(self.export, 'UV 280', caption='Sample A'),
                                       Curve(self.export, 'Conductivity', caption='Buffer')],
                    x_settings=AxisSettings(name='Volume (mL)', tick_direction=direction,
                                            axis_width=2, tick_size=14, label_size=18),
                    y_settings={'mAU': AxisSettings(name='Absorbance (mAU)', axis_width=3,
                                                   tick_size=12, label_size=16)},
                    plot_settings=PlotSettings(True, False, False))
                left, right = figure.axes
                self.assertEqual(left.get_xlabel(), 'Volume (mL)')
                self.assertEqual(left.get_ylabel(), 'Absorbance (mAU)')
                self.assertEqual(right.get_ylabel(), 'mS/cm')
                self.assertEqual(left.xaxis.label.get_fontsize(), 18)
                self.assertEqual(left.yaxis.label.get_fontsize(), 16)
                self.assertEqual(left.spines['bottom'].get_linewidth(), 2)
                self.assertEqual(left.spines['left'].get_linewidth(), 3)
                self.assertEqual(left.xaxis.get_major_ticks()[0].get_tickdir(), direction)
                self.assertEqual(left.xaxis.get_minor_ticks()[0].get_tickdir(), direction)
                self.assertEqual(left.xaxis.get_major_ticks()[0].label1.get_fontsize(), 14)
                self.assertFalse(left.spines['top'].get_visible())
                self.assertFalse(left.spines['right'].get_visible())
                self.assertTrue(right.spines['right'].get_visible())
                self.assertFalse(any(line.get_visible() for line in left.get_xgridlines()))
                self.assertEqual([text.get_text() for text in left.get_legend().get_texts()], ['Sample A', 'Buffer'])
                output = io.BytesIO()
                figure.savefig(output, format='svg')
                self.assertIn(b'Sample A', output.getvalue())
                self.assertIn(b'Volume (mL)', output.getvalue())
        figure = make_overlay([Curve(self.export, 'UV 280')], plot_settings=PlotSettings(False, False, True))
        self.assertIsNone(figure.axes[0].get_legend())
        self.assertFalse(figure.axes[0].spines['right'].get_visible())
        self.assertTrue(any(line.get_visible() for line in figure.axes[0].get_xgridlines()))

    def test_invalid_axis_appearance(self):
        for options in ({'axis_width': 0}, {'tick_size': -1}, {'label_size': float('nan')},
                        {'tick_direction': 'invalid'}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                make_overlay([Curve(self.export, 'UV 280')], x_settings=AxisSettings(**options))
