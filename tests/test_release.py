import hashlib
from pathlib import Path
import io
import tarfile
import tempfile
import unittest
import zipfile
from scripts.prepare_release import EXPECTED, prepare


class ReleaseTests(unittest.TestCase):
    def make_assets(self, directory):
        for name, entry in EXPECTED.items():
            path = directory / name
            if name.endswith('.zip'):
                with zipfile.ZipFile(path, 'w') as archive:
                    archive.writestr(entry, b'example executable')
            else:
                with tarfile.open(path, 'w:gz') as archive:
                    info = tarfile.TarInfo(entry)
                    info.size = len(b'example executable')
                    archive.addfile(info, io.BytesIO(b'example executable'))

    def test_complete_set_checksums(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            self.make_assets(directory)
            prepare(directory)
            entries = (directory / 'SHA256SUMS.txt').read_text().splitlines()
            self.assertEqual(len(entries), 4)
            for entry in entries:
                digest, name = entry.split('  ')
                self.assertEqual(digest, hashlib.sha256((directory / name).read_bytes()).hexdigest())

    def test_missing_platform_blocks_release(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            self.make_assets(directory)
            (directory / 'AKTA-Plotter-macos-intel.zip').unlink()
            with self.assertRaises(ValueError):
                prepare(directory)
            self.assertFalse((directory / 'SHA256SUMS.txt').exists())

    def test_archive_without_app_blocks_release(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            self.make_assets(directory)
            with zipfile.ZipFile(directory / 'AKTA-Plotter-windows-x64.zip', 'w') as archive:
                archive.writestr('README.txt', 'No executable')
            with self.assertRaises(ValueError):
                prepare(directory)
            self.assertFalse((directory / 'SHA256SUMS.txt').exists())
