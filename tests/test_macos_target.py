from pathlib import Path
import plistlib
import struct
import tempfile
import unittest
from scripts.check_macos_target import check_bundle


def native_binary(major):
    header = struct.pack('<IiiIIIII', 0xfeedfacf, 0x100000c, 0, 6, 1, 24, 0, 0)
    command = struct.pack('<IIIIII', 0x32, 24, 1, major << 16, 15 << 16, 0)
    return header + command


class MacOSTargetTests(unittest.TestCase):
    def make_bundle(self, root, major, advertised='12.0'):
        root = Path(root)
        contents = root / 'Contents'
        frameworks = contents / 'Frameworks'
        frameworks.mkdir(parents=True)
        (frameworks / 'native.dylib').write_bytes(native_binary(major))
        with (contents / 'Info.plist').open('wb') as out:
            plistlib.dump({'LSMinimumSystemVersion': advertised}, out)
        return root

    def test_monterey_compatible_binary(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(check_bundle(self.make_bundle(folder, 11)), 1)

    def test_newer_binary_cannot_be_hidden_by_plist(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'native.dylib'):
                check_bundle(self.make_bundle(folder, 14))

    def test_incorrect_advertised_version(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'LSMinimumSystemVersion'):
                check_bundle(self.make_bundle(folder, 11, '14.0'))
