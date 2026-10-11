"""Check native file icons in built applications, not just source artwork."""
from pathlib import Path
import platform
import plistlib


def main():
    root = Path(__file__).resolve().parents[1]
    if platform.system() == 'Darwin':
        contents = root / 'dist' / 'AKTA-Plotter.app' / 'Contents'
        with (contents / 'Info.plist').open('rb') as source:
            info = plistlib.load(source)
        name = info['CFBundleIconFile']
        if not name.endswith('.icns'):
            name += '.icns'
        if (contents / 'Resources' / name).read_bytes()[:4] != b'icns':
            raise RuntimeError('Mac application icon is missing')
    elif platform.system() == 'Windows':
        import pefile
        with pefile.PE(str(root / 'dist' / 'AKTA-Plotter' / 'AKTA-Plotter.exe')) as executable:
            types = {entry.id for entry in executable.DIRECTORY_ENTRY_RESOURCE.entries}
            if not {3, 14} <= types:
                raise RuntimeError('Windows executable icon resources are missing')
    print('Native application icon check passed')


if __name__ == '__main__':
    main()
