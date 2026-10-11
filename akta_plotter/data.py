"""Read delimited exports without assuming a particular UNICORN version."""
import csv
import io
from dataclasses import dataclass, field

import pandas as pd


# Match whole signal names, so similarly named measured curves remain selectable.
EXCLUDED_SIGNALS = frozenset(name.casefold() for name in (
    'Injection', 'Run Log', 'Fraction', 'UV 1_280_CUT_TEMP@100,BASEM'))


@dataclass
class Export:
    frame: pd.DataFrame
    units: dict[str, str]
    encoding: str
    delimiter: str
    signal_x: dict[str, str] = field(default_factory=dict)


def read_export(raw: bytes) -> Export:
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        encoding = 'utf-16'
        text = raw.decode(encoding)
    else:
        for encoding in ('utf-8-sig', 'cp932', 'cp1252'):
            try:
                text = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError('CSVの文字コードを読み取れません。')
    try:
        delimiter = csv.Sniffer().sniff(text[:16384], delimiters=',;\t').delimiter
    except csv.Error:
        delimiter = max(',;\t', key=lambda d: max((line.count(d) for line in text.splitlines()), default=0))
    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
    # Locate the numeric table, allowing instrument metadata and a units row.
    def number(value):
        try:
            return float(value.strip().replace(',', '.'))
        except ValueError:
            return None
    first = next((i for i, row in enumerate(rows)
                  if sum(number(v) is not None for v in row) >= 2), None)
    if first is None:
        raise ValueError('2列以上の数値データが見つかりません。')
    # UNICORN exports name each signal on row 2, with its own X/Y pair.
    # Scan all X/Y pairs; exclude only the named event/derived signals.
    if len(rows) >= 4 and first == 3:
        header, unit_row = rows[1], rows[2]
        paired = any(
            header[i].strip() and i + 1 < len(unit_row)
            and unit_row[i].strip().casefold() == 'ml'
            and i + 1 < len(header) and not header[i + 1].strip()
            for i in range(len(header)))
        if paired:
            data, units, signal_x = {}, {}, {}
            for i in range(len(header)):
                if (not header[i].strip() or header[i].strip().casefold() in EXCLUDED_SIGNALS
                        or i + 1 >= len(header)
                        or i + 1 >= len(unit_row)
                        or unit_row[i].strip().casefold() != 'ml'
                        or i + 1 >= len(header) or header[i + 1].strip()):
                    continue
                xs = [number(row[i]) if i < len(row) else None for row in rows[first:]]
                ys = [number(row[i + 1]) if i + 1 < len(row) else None for row in rows[first:]]
                if not any(x is not None and y is not None for x, y in zip(xs, ys)):
                    continue
                name = header[i].strip()
                original, n = name, 2
                while name in data or f'{name} [volume]' in data:
                    name = f'{original} ({n})'
                    n += 1
                x_name = f'{name} [volume]'
                data[x_name] = xs
                data[name] = ys
                units[x_name], units[name] = 'mL', unit_row[i + 1].strip()
                signal_x[name] = x_name
            frame = pd.DataFrame(data).dropna(how='all')
            if not signal_x or frame.empty:
                raise ValueError('除外対象以外にmLに対応する数値曲線が見つかりません。')
            return Export(frame, units, encoding, delimiter, signal_x)
    width = len(rows[first])
    preceding = [row for row in rows[:first] if len(row) == width]
    header = preceding[-1] if preceding else [f'Column {i + 1}' for i in range(width)]
    units_row = None
    known_units = {'ml', 'mL', 'min', 's', 'mAU', 'AU', 'mS/cm', 'µS/cm', '%', 'MPa', 'bar', 'pH'}
    if len(preceding) >= 2 and any(v.strip() in known_units for v in header):
        units_row = header
        header = preceding[-2]
    names, used = [], {}
    for i, value in enumerate(header):
        name = value.strip() or f'Column {i + 1}'
        used[name] = used.get(name, 0) + 1
        names.append(name if used[name] == 1 else f'{name} ({used[name]})')
    values = [[number(v) for v in (row + [''] * width)[:width]] for row in rows[first:] if row]
    frame = pd.DataFrame(values, columns=names).dropna(how='all')
    frame = frame.dropna(axis=1, how='all')
    if len(frame.columns) < 2:
        raise ValueError('プロット可能な数値列が不足しています。')
    units = dict(zip(names, (v.strip() for v in units_row))) if units_row else {}
    return Export(frame, units, encoding, delimiter)


def label(export: Export, name: str) -> str:
    unit = export.units.get(name)
    return f'{name} [{unit}]' if unit else name
