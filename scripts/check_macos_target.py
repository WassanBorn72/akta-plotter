"""Reject bundled Mach-O files requiring a newer macOS than advertised."""
from pathlib import Path
import argparse
import plistlib
from macholib.MachO import MachO
from macholib import mach_o

MAGIC = {bytes.fromhex(value) for value in
         ('feedface', 'cefaedfe', 'feedfacf', 'cffaedfe', 'cafebabe', 'bebafeca', 'cafebabf', 'bfbafeca')}


def version_tuple(value):
    return value >> 16, (value >> 8) & 255, value & 255


def check_bundle(bundle, maximum='12.0'):
    target = tuple(int(part) for part in maximum.split('.'))
    target = (target + (0, 0))[:3]
    bundle = Path(bundle)
    count = 0
    violations = []
    for path in bundle.rglob('*'):
        if not path.is_file() or path.is_symlink():
            continue
        with path.open('rb') as source:
            if source.read(4) not in MAGIC:
                continue
        binary = MachO(str(path))
        count += 1
        for header in binary.headers:
            for command, data, _ in header.commands:
                if command.cmd == mach_o.LC_BUILD_VERSION:
                    required = version_tuple(data.minos)
                elif command.cmd == mach_o.LC_VERSION_MIN_MACOSX:
                    required = version_tuple(data.version)
                else:
                    continue
                if required > target:
                    violations.append(f'{path.relative_to(bundle)}: {required}')
    if count == 0:
        raise ValueError('No native binaries were checked')
    with (bundle / 'Contents' / 'Info.plist').open('rb') as source:
        minimum = plistlib.load(source).get('LSMinimumSystemVersion')
    if minimum != maximum:
        violations.append(f'LSMinimumSystemVersion={minimum!r}, expected {maximum!r}')
    if violations:
        raise ValueError('macOS compatibility check failed:\n' + '\n'.join(violations))
    print(f'Checked {count} native binaries: macOS {maximum} deployment requirements passed')
    return count


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--maximum', default='12.0')
    args = parser.parse_args()
    check_bundle(args.bundle, args.maximum)
