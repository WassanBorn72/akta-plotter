"""Build a native application on the current OS (no cross compilation)."""
from pathlib import Path
import argparse
import platform
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--console', action='store_true', help='Keep a console for diagnostics')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir',
               '--name', 'AKTA-Plotter', '--paths', str(root),
               '--distpath', str(root / 'dist'), '--workpath', str(root / 'build'),
               '--specpath', str(root / 'build'), '--collect-data', 'matplotlib',
               '--exclude-module', 'streamlit', '--exclude-module', 'pytest',
               '--exclude-module', 'IPython',
               '--hidden-import', 'matplotlib.backends.backend_agg',
               '--hidden-import', 'matplotlib.backends.backend_svg',
               '--hidden-import', 'matplotlib.backends.backend_pdf',
               '--hidden-import', 'matplotlib.backends.backend_tkagg']
    if platform.system() == 'Linux':
        # Some Python distributions keep Tcl/Tk outside the system loader paths.
        for pattern in ('libtcl*.so*', 'libtk*.so*'):
            for library in sorted((Path(sys.base_prefix) / 'lib').glob(pattern)):
                command.extend(['--add-binary', str(library) + ':.'])
    if platform.system() in ('Windows', 'Darwin') and not args.console:
        command.append('--windowed')
    if platform.system() == 'Darwin':
        command.extend(['--osx-bundle-identifier', 'com.aktaplotter.desktop'])
    command.append(str(root / 'scripts' / 'desktop_entry.py'))
    subprocess.run(command, cwd=root, check=True)


if __name__ == '__main__':
    main()
