import ctypes
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pet_server', ROOT / 'desktop' / 'server.py')
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class DesktopTests(unittest.TestCase):
    def setUp(self):
        self.engine = server.Engine(server.find_library())
        self.addCleanup(self.engine.close)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'pet.json'

    def test_independent_binary_contract(self):
        expected = struct.pack('<4sHHIIIIHH10B', b'PET1', 1, 42, 0, 0, 0x50455431, 0,
                               480, 0, 75, 70, 85, 90, 100, 20, 0, 0, 0, 0)
        expected += struct.pack('<I', zlib.crc32(expected))
        self.assertEqual(self.engine.dump(), expected)
        self.engine.load(expected)
        self.assertEqual(self.engine.view()['name'], 'Ei')

    def test_save_reload_and_no_offline_in_manual_mode(self):
        sim = server.Simulator(self.engine, self.path, manual=True)
        self.engine.advance(600000)
        self.engine.button(1)
        sim.save()
        self.assertIsNone(sim.storage_error)
        other = server.Engine(server.find_library())
        self.addCleanup(other.close)
        server.Simulator(other, self.path, manual=True)
        self.assertEqual(self.engine.dump(), other.dump())
        self.assertEqual(other.view()['screen'], 0)

    def test_corrupt_save_preserved(self):
        self.path.write_text('{bad json', encoding='utf-8')
        with self.assertRaises(ValueError):
            server.Simulator(self.engine, self.path)
        self.assertEqual(self.path.read_text(), '{bad json')

    def test_write_failure_keeps_previous_file(self):
        sim = server.Simulator(self.engine, self.path, manual=True)
        sim.save()
        original = self.path.read_bytes()
        self.engine.advance(600000)
        with patch.object(server.os, 'replace', side_effect=OSError('disk unavailable')):
            sim.save()
        self.assertIn('disk unavailable', sim.storage_error)
        self.assertEqual(self.path.read_bytes(), original)
        sim.save()
        self.assertIsNone(sim.storage_error)
        self.assertNotEqual(self.path.read_bytes(), original)

    def test_offline_cap_and_clock_rollback(self):
        sim = server.Simulator(self.engine, self.path, manual=True)
        with patch.object(server.time, 'time', return_value=100000):
            sim.save()
        with patch.object(server.time, 'time', return_value=200000):
            restored = server.Simulator(self.engine, self.path)
        self.assertEqual(restored.offline_minutes, 480)
        self.assertEqual(self.engine.view()['age_minutes'], 480)
        with patch.object(server.time, 'time', return_value=90000):
            restored = server.Simulator(self.engine, self.path)
        self.assertEqual(restored.offline_minutes, 0)
        self.assertEqual(self.engine.view()['age_minutes'], 0)

    def test_semantically_bad_save_with_valid_crc(self):
        bad = bytearray(self.engine.dump())
        bad[36] = 2  # sleeping bool
        bad[38:] = struct.pack('<I', zlib.crc32(bad[:38]))
        original = self.engine.dump()
        with self.assertRaises(ValueError):
            self.engine.load(bad)
        self.assertEqual(self.engine.dump(), original)

    def test_invalid_abi_inputs_and_separate_instances(self):
        self.assertFalse(self.engine.lib.pp_button(self.engine.handle, 3))
        self.assertFalse(self.engine.lib.pp_load(self.engine.handle, None, 42))
        self.assertEqual(self.engine.lib.pp_save(self.engine.handle, None, 42), 0)
        other = server.Engine(server.find_library())
        self.addCleanup(other.close)
        self.engine.advance(600000)
        self.assertEqual(other.view()['species'], 0)
        self.assertEqual(self.engine.view()['species'], 1)

    def test_future_version_and_envelope_limits(self):
        for data in ({'version': 2}, {'version': True}, {'version': 1, 'saved_at': True},
                     {'version': 1, 'saved_at': 0, 'payload': 'x'*84}):
            self.path.write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaises(ValueError):
                server.Simulator(self.engine, self.path)

    def test_save_lock_rejects_second_writer_and_releases(self):
        with server.SaveLock(self.path):
            with self.assertRaises(OSError):
                with server.SaveLock(self.path):
                    self.fail('Second writer must not acquire save lock')
        with server.SaveLock(self.path):
            pass

    def test_pause_survives_long_host_suspend(self):
        sim = server.Simulator(self.engine, self.path)
        sim.speed = 0
        before = self.engine.dump()
        with patch.object(server.time, 'monotonic', return_value=sim.last_tick + 3600):
            sim.tick()
        self.assertEqual(self.engine.dump(), before)

    def test_long_host_suspend_ignores_demo_multiplier(self):
        sim = server.Simulator(self.engine, self.path)
        sim.speed = 3600
        with patch.object(server.time, 'monotonic', return_value=sim.last_tick + 600):
            sim.tick()
        self.assertEqual(self.engine.view()['age_minutes'], 10)


if __name__ == '__main__':
    unittest.main()
