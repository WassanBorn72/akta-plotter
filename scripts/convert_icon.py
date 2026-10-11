"""Encode the approved icon artwork in native application formats."""
from pathlib import Path
import argparse
from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    output = Path(__file__).resolve().parents[1] / 'akta_plotter' / 'assets'
    output.mkdir(parents=True, exist_ok=True)
    with Image.open(args.source) as source:
        if source.width != source.height:
            raise ValueError('Application icon artwork must be square')
        icon = source.convert('RGBA').resize((1024, 1024), Image.Resampling.LANCZOS)
        icon.save(output / 'icon.png')
        icon.save(output / 'icon.ico', sizes=[(size, size) for size in (16, 24, 32, 48, 64, 128, 256)])
        icon.save(output / 'icon.icns')


if __name__ == '__main__':
    main()
