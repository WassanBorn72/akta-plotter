"""Shared rendering and validated options for both user interfaces."""
from dataclasses import dataclass
import math

from matplotlib.figure import Figure
from matplotlib.ticker import AutoMinorLocator, MultipleLocator, ScalarFormatter
from .data import Export, label

COLORS = ['#2563eb', '#dc2626', '#059669', '#9333ea', '#d97706', '#0891b2']


@dataclass
class AxisSettings:
    minimum: float | None = None
    maximum: float | None = None
    major_step: float | None = None
    minor_step: float | None = None
    show_major_numbers: bool = True
    show_minor_numbers: bool = False

    def validate(self):
        for name in ('minimum', 'maximum', 'major_step', 'minor_step'):
            value = getattr(self, name)
            if value is not None and not math.isfinite(value):
                raise ValueError('軸の設定には有限の数値を入力してください。')
        if self.minimum is not None and self.maximum is not None and self.minimum >= self.maximum:
            raise ValueError('軸の最小値は最大値より小さくしてください。')
        for step in (self.major_step, self.minor_step):
            if step is not None and step <= 0:
                raise ValueError('目盛りの間隔は0より大きくしてください。')


@dataclass
class Curve:
    export: Export
    y: str
    x: str | None = None
    source: str = ''
    color: str = COLORS[0]
    width: float = 1.5

    @property
    def unit(self):
        return self.export.units.get(self.y) or 'unitless'

    @property
    def x_column(self):
        return self.export.signal_x[self.y] if self.export.signal_x else self.x

    @property
    def x_unit(self):
        unit = 'mL' if self.export.signal_x else self.export.units.get(self.x, self.x or '')
        return 'mL' if unit.lower() == 'ml' else unit


def parse_axis(values, show_major=True, show_minor=False):
    """Blank fields mean automatic; shared by desktop and browser."""
    try:
        numbers = [None if not str(v).strip() else float(v) for v in values]
    except (TypeError, ValueError):
        raise ValueError('軸の設定は数値で入力してください（空欄は自動）。') from None
    settings = AxisSettings(*numbers, show_major, show_minor)
    settings.validate()
    return settings


def apply_axis(axis, direction, settings):
    settings.validate()
    get_limits = axis.get_xlim if direction == 'x' else axis.get_ylim
    set_limits = axis.set_xlim if direction == 'x' else axis.set_ylim
    lower, upper = get_limits()
    lower = lower if settings.minimum is None else settings.minimum
    upper = upper if settings.maximum is None else settings.maximum
    if lower >= upper:
        raise ValueError('軸の最小値は最大値より小さくしてください。自動側の範囲も確認してください。')
    set_limits(lower, upper)
    target = axis.xaxis if direction == 'x' else axis.yaxis
    for step, setter in ((settings.major_step, target.set_major_locator),
                         (settings.minor_step, target.set_minor_locator)):
        if step is not None:
            if (upper - lower) / step > 1000:
                raise ValueError('目盛りが多すぎます。範囲を狭めるか間隔を大きくしてください。')
            setter(MultipleLocator(step))
    if settings.minor_step is None:
        target.set_minor_locator(AutoMinorLocator())
    if settings.show_minor_numbers:
        formatter = ScalarFormatter(useOffset=False)
        formatter.set_scientific(False)
        target.set_minor_formatter(formatter)
    axis.tick_params(axis=direction, which='major',
                     labelbottom=settings.show_major_numbers if direction == 'x' else False,
                     labelleft=settings.show_major_numbers if direction == 'y' and axis.yaxis.get_ticks_position() != 'right' else False,
                     labelright=settings.show_major_numbers if direction == 'y' and axis.yaxis.get_ticks_position() == 'right' else False)
    axis.tick_params(axis=direction, which='minor',
                     labelbottom=settings.show_minor_numbers if direction == 'x' else False,
                     labelleft=settings.show_minor_numbers if direction == 'y' and axis.yaxis.get_ticks_position() != 'right' else False,
                     labelright=settings.show_minor_numbers if direction == 'y' and axis.yaxis.get_ticks_position() == 'right' else False)
    target.get_offset_text().set_visible(settings.show_major_numbers)


def make_overlay(curves, title='', x_settings=None, y_settings=None, group_units=True):
    if not curves:
        raise ValueError('表示する曲線を選択してください。')
    if len({c.x_unit for c in curves}) != 1:
        raise ValueError('横軸の単位が異なる曲線は重ねられません。各ファイルのX列を確認してください。')
    keys = [c.unit if group_units else 'shared' for c in curves]
    groups = list(dict.fromkeys(keys))
    figure = Figure(figsize=(10 + .7 * max(0, len(groups) - 2), 6), layout='constrained')
    base = figure.add_subplot(111)
    base.set_xlabel(curves[0].x_unit)
    base.set_title(title)
    base.grid(alpha=.25)
    axes, lines = {}, []
    for curve, key in zip(curves, keys):
        if not math.isfinite(curve.width) or curve.width <= 0:
            raise ValueError('線の太さは0より大きい有限の数値にしてください。')
        if key not in axes:
            index = len(axes)
            axis = base if index == 0 else base.twinx()
            if index > 1:
                axis.spines['right'].set_position(('outward', 60 * (index - 1)))
            axis.set_ylabel(key if group_units else (curves[0].unit if len({c.unit for c in curves}) == 1 else 'Value'))
            axes[key] = axis
        valid = curve.export.frame[[curve.x_column, curve.y]].dropna()
        if valid.empty:
            raise ValueError(f'{curve.y}: 選択したX列と共通する数値データがありません。')
        name = label(curve.export, curve.y)
        if curve.source:
            name = f'{curve.source} / {name}'
        lines.extend(axes[key].plot(valid[curve.x_column], valid[curve.y], color=curve.color,
                                    linewidth=curve.width, label=name))
    for key, axis in axes.items():
        apply_axis(axis, 'y', (y_settings or {}).get(key, AxisSettings()))
    apply_axis(base, 'x', x_settings or AxisSettings())
    base.legend(handles=lines, loc='best')
    return figure


def make_figure(export, x, ys, title='', separate_axes=True):
    if not ys or x in ys:
        raise ValueError('X列以外から、表示する曲線を選択してください。')
    curves = [Curve(export, y, x, color=COLORS[i % len(COLORS)]) for i, y in enumerate(ys)]
    return make_overlay(curves, title, group_units=bool(export.signal_x) or separate_axes)
