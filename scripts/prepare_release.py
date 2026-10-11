"""Validate the complete asset set and write release checksums."""
from pathlib import Path
import hashlib
import sys
import tarfile
import zipfile

EXPECTED = {
    'AKTA-Plotter-windows-x64.zip': 'AKTA-Plotter/AKTA-Plotter.exe',
    'AKTA-Plotter-macos-intel.zip': 'AKTA-Plotter.app/Contents/MacOS/AKTA-Plotter',
    'AKTA-Plotter-macos-apple-silicon.zip': 'AKTA-Plotter.app/Contents/MacOS/AKTA-Plotter',
    'AKTA-Plotter-linux-x64.tar.gz': 'AKTA-Plotter/AKTA-Plotter',
}


def prepare(directory):
    directory = Path(directory)
    files = {p.name for p in directory.iterdir() if p.is_file()} - {'SHA256SUMS.txt'}
    if files != set(EXPECTED):
        raise ValueError(f'Unexpected release assets: missing={set(EXPECTED) - files}, extra={files - set(EXPECTED)}')
    lines = []
    for name, entry in sorted(EXPECTED.items()):
        path = directory / name
        if name.endswith('.zip'):
            with zipfile.ZipFile(path) as archive:
                if archive.testzip() is not None or entry not in archive.namelist():
                    raise ValueError(f'Invalid application archive: {name}')
                if archive.getinfo(entry).file_size == 0:
                    raise ValueError(f'Empty executable: {name}')
        else:
            with tarfile.open(path) as archive:
                if archive.getmember(entry).size == 0:
                    raise ValueError(f'Empty executable: {name}')
                for member in archive:
                    if member.isfile():
                        with archive.extractfile(member) as source:
                            while source.read(1024 * 1024):
                                pass
        with path.open('rb') as source:
            digest = hashlib.file_digest(source, 'sha256').hexdigest()
        lines.append(f'{digest}  {name}\n')
    (directory / 'SHA256SUMS.txt').write_text(''.join(lines), encoding='utf-8')
    print('All four application archives validated; SHA256SUMS.txt written')


if __name__ == '__main__':
    prepare(sys.argv[1])
