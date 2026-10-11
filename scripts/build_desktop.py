"""Build a native application on the current OS (no cross compilation)."""
from pathlib import Path
import argparse
import ast
import runpy
import os
import platform
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--console', action='store_true', help='Keep a console for diagnostics')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    assets = root / 'akta_plotter' / 'assets'
    icon = assets / ('icon.icns' if platform.system() == 'Darwin' else 'icon.ico' if platform.system() == 'Windows' else 'icon.png')
    command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir',
               '--name', 'AKTA-Plotter', '--paths', str(root),
               '--distpath', str(root / 'dist'), '--workpath', str(root / 'build'),
               '--specpath', str(root / 'build'), '--collect-data', 'matplotlib',
               '--icon', str(icon),
               '--add-data', str(assets) + os.pathsep + 'akta_plotter/assets',
               '--exclude-module', 'pytest',
               '--exclude-module', 'IPython',
               '--hidden-import', 'matplotlib.backends.backend_agg',
               '--hidden-import', 'matplotlib.backends.backend_svg',
               '--hidden-import', 'matplotlib.backends.backend_pdf',
               '--hidden-import', 'matplotlib.backends.backend_tkagg',
               '--hidden-import', 'PIL._tkinter_finder',
               '--hidden-import', 'PIL._imagingtk']
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
    if platform.system() == 'Darwin' and not args.console:
        # Add bundle metadata before building, so signatures are not modified afterward.
        generated = [sys.executable, '-m', 'PyInstaller.utils.cliutils.makespec']
        index = 3
        while index < len(command):
            flag = command[index]
            if flag in ('--noconfirm', '--clean'):
                index += 1
                continue
            if flag in ('--distpath', '--workpath'):
                index += 2
                continue
            generated.append(flag)
            index += 1
        subprocess.run(generated, cwd=root, check=True)
        spec = root / 'build' / 'AKTA-Plotter.spec'
        tree = ast.parse(spec.read_text())
        metadata = {
            'LSMinimumSystemVersion': '12.0',
            'CFBundleShortVersionString': runpy.run_path(str(root / 'akta_plotter' / '__init__.py'))['__version__'],
        }
        bundles = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Name) and node.func.id == 'BUNDLE']
        if len(bundles) != 1:
            raise RuntimeError('Expected exactly one macOS application bundle')
        bundles[0].keywords.append(ast.keyword(arg='info_plist', value=ast.parse(repr(metadata), mode='eval').body))
        spec.write_text(ast.unparse(tree) + '\n')
        command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
                   '--distpath', str(root / 'dist'), '--workpath', str(root / 'build'), str(spec)]
    subprocess.run(command, cwd=root, check=True)


if __name__ == '__main__':
    main()
