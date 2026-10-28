import ctypes
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import time
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
        self.engine.button(1)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'pet.json'

    def test_independent_binary_contract(self):
        expected = struct.pack('<4sHHIIIIHH16B', b'PET1', 4, 48, 0, 0, 0x50455431, 0,
                               480, 0, 75, 70, 85, 90, 100, 20, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0)
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
        bad[44:] = struct.pack('<I', zlib.crc32(bad[:44]))
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

    def test_v1_migration_preserves_care_and_evolution(self):
        old = struct.pack('<4sHHIIIIHH10B', b'PET1', 1, 42, 1500, 12345, 0x50455431, 60,
                          1234, 0, 75, 70, 85, 90, 100, 70, 0, 3, 0, 0)
        old += struct.pack('<I', zlib.crc32(old))
        self.engine.load(old)
        view = self.engine.view()
        self.assertEqual((view['species'], view['starter'], view['age_minutes'], view['experience']), (3, 1, 1500, 60))
        self.assertTrue(view['starter_chosen'])
        self.assertEqual(len(self.engine.dump()), 48)
        self.assertEqual(self.engine.dump()[8:38], old[8:38])

    def test_profiles_remain_separate_from_saves(self):
        first = server.Engine(server.find_library(), 'Ada')
        second = server.Engine(server.find_library(), 'JÃ¶rg')
        self.addCleanup(first.close)
        self.addCleanup(second.close)
        second.button(2)
        second.button(1)
        second.advance(600000)
        self.assertEqual(second.view()['name'], 'Enton')
        self.assertEqual(first.view()['trainer_name'], 'Ada')
        self.assertEqual(second.view()['trainer_name'], 'JÃ¶rg')
        first.load(second.dump())
        self.assertEqual(first.view()['trainer_name'], 'Ada')
        with self.assertRaises(ValueError):
            server.Engine(server.find_library(), 'x'*25)

    def test_shared_sprite_assets_and_memory_budget(self):
        info = self.engine.info()
        self.assertEqual(info['memory_bytes']['sprites'], 908)
        self.assertLessEqual(info['memory_bytes']['game'], 128)
        self.assertLessEqual(info['memory_bytes']['animator'], 32)
        self.assertLess(info['memory_bytes']['animations'], 1024*1024)
        self.assertEqual(info['memory_bytes']['scene'], 21424)
        self.assertEqual(info['screen'], {'width': 240, 'height': 320, 'format': 'rgb565le'})

    def test_animation_is_cosmetic_and_follows_feeding(self):
        self.engine.advance(600000)
        before = self.engine.dump()
        self.engine.lib.pp_animation_seed(self.engine.handle, 42)
        other = server.Engine(server.find_library())
        self.addCleanup(other.close)
        other.load(before)
        self.engine.advance(4000)
        other.advance(4000)
        self.assertEqual(self.engine.dump(),other.dump())
        self.engine.button(1)
        self.engine.button(1)
        self.assertEqual(self.engine.view()['animation']['name'],'eat')
        pose = self.engine.view()['animation']
        self.engine.advance(1000,0)
        self.assertEqual(self.engine.view()['animation'],pose)
        self.engine.advance(2200)
        self.assertEqual(self.engine.view()['animation']['name'],'idle')

    def test_v2_migration_and_old_version_species_boundary(self):
        current=self.engine.dump()
        old=bytearray(current[:44]);old[4:6]=struct.pack('<H',2);old[6:8]=struct.pack('<H',44)
        old[40:]=struct.pack('<I',zlib.crc32(old[:40]))
        self.engine.load(bytes(old))
        self.assertEqual(self.engine.dump()[8:40],current[8:40])
        self.assertEqual(self.engine.dump()[4:8],b'\x04\x000\x00')
        old[38]=5;old[40:]=struct.pack('<I',zlib.crc32(old[:40]))
        with self.assertRaises(ValueError):self.engine.load(bytes(old))
        old[4:6]=struct.pack('<H',3);old[40:]=struct.pack('<I',zlib.crc32(old[:40]))
        self.engine.load(bytes(old))
        self.assertEqual(self.engine.view()['starter'],5)
        self.assertEqual(self.engine.view()['care_mistakes'],0)

    def test_catalog_metadata_and_evolution_lines(self):
        catalog=self.engine.catalog()
        self.assertEqual(len(catalog),130)
        self.assertEqual(len({p['species'] for p in catalog}),130)
        names={p['species']:p['name'] for p in catalog}
        lines={(p['name'],names.get(p['evolves_to'],'Psiana')) for p in catalog if p['evolves_to']}
        self.assertEqual(lines,{('Evoli','Psiana'),('Pichu','Pikachu'),('Lilminip','Dressella'),('Fynx','Rutena'),
                                ('Psiau','Psiaugon'),('Wuffels','Wolwerock'),('Typ:Null','Amigento')})
        self.assertEqual(self.engine.lib.pp_evolution_of(256),0)
        self.assertEqual(self.engine.lib.pp_species_name(255),b'Unbekannt')

    def test_device_frame_and_growth_scale(self):
        frame=self.engine.frame()
        self.assertEqual(len(frame),240*320*2)
        self.assertEqual(frame,self.engine.frame())
        header=struct.unpack_from('<H',frame,0)[0]
        self.assertEqual(header,(56>>3)<<11|(71>>2)<<5|(56>>3))
        self.engine.advance(60000,10)
        self.assertNotEqual(self.engine.frame(),frame)
        a=self.engine.view()['animation']
        self.assertEqual((a['scale'],self.engine.view()['stage_name']),(3,'Baby'))
        self.assertGreaterEqual(a['draw_y'],42)
        self.assertEqual(len(self.engine.frame(True)),240*320*2)
        self.assertFalse(self.engine.lib.pp_render(self.engine.handle,None,0,False))

    def test_raw_buttons_use_core_debounce_hold_and_repeat(self):
        sim=server.Simulator(self.engine,self.path,manual=True)
        self.engine.advance(600000)
        def at(ms,raw):
            with patch.object(server.time,'monotonic',return_value=1000+ms/1000):sim.set_buttons(raw)
        at(0,2);at(20,0);at(60,0)
        self.assertEqual(self.engine.view()['screen'],0,'glitch below debounce ignored')
        at(100,2);at(130,2);at(200,0);at(230,0)
        self.assertEqual(self.engine.view()['screen'],1,'short OK opens menu on release')
        at(300,4);at(330,4)
        self.assertEqual(self.engine.view()['selection'],1)
        at(780,4);at(940,4)
        self.assertEqual(self.engine.view()['selection'],3,'held side button repeats in menu')
        at(1000,0);at(1030,0)
        at(2000,2);at(2030,2);at(2730,2)
        self.assertEqual(self.engine.view()['screen'],0,'holding OK goes back once')
        at(2800,0);at(2830,0)
        self.assertEqual(self.engine.view()['screen'],0,'release after hold does not confirm')
        self.assertTrue(self.path.exists(),'reactions are saved')

    def test_http_frame_info_and_input_endpoints(self):
        import socket, threading, urllib.request
        with socket.socket() as probe:
            probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
        sim=server.Simulator(self.engine,self.path,manual=True)
        httpd=server.LocalServer(('127.0.0.1',port),server.handler_for(sim,port))
        thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start()
        self.addCleanup(httpd.server_close);self.addCleanup(httpd.shutdown)
        base=f'http://127.0.0.1:{port}'
        def post(path,data):
            request=urllib.request.Request(base+path,json.dumps(data).encode(),{'Content-Type':'application/json'})
            return json.loads(urllib.request.urlopen(request,timeout=5).read())
        with urllib.request.urlopen(base+'/api/frame',timeout=5) as response:
            self.assertEqual(response.headers['Content-Type'],'application/octet-stream')
            self.assertEqual(len(response.read()),240*320*2)
        info=json.loads(urllib.request.urlopen(base+'/api/info',timeout=5).read())
        self.assertEqual(info['starters'],130)
        self.assertEqual(post('/api/input',{'pressed':2})['buttons'],2)
        time.sleep(0.05);post('/api/input',{'pressed':2});post('/api/input',{'pressed':0})
        time.sleep(0.05);view=post('/api/input',{'pressed':0})
        self.assertTrue(view['starter_chosen'],'raw OK press confirms the starter')
        with self.assertRaises(urllib.error.HTTPError) as error:post('/api/input',{'pressed':8})
        self.assertEqual(error.exception.code,400)
        with self.assertRaises(urllib.error.HTTPError) as error:urllib.request.urlopen(base+'/api/assets',timeout=5)
        self.assertEqual(error.exception.code,404)

    def test_reset_is_disabled_by_default(self):
        sim=server.Simulator(self.engine,self.path)
        before=self.engine.dump()
        with self.assertRaises(ValueError):sim.reset_test_save()
        self.assertEqual(self.engine.dump(),before)
        self.assertFalse(sim.view()['test_controls'])

    def test_test_reset_preserves_profile_and_backup(self):
        self.engine.lib.pp_set_name(self.engine.handle,b'Ada',3)
        sim=server.Simulator(self.engine,self.path,manual=True,test_controls=True)
        self.engine.advance(60000,10)
        self.engine.button(1)
        for _ in range(5):self.engine.button(2)
        self.engine.button(1)
        self.assertEqual(self.engine.view()['screen'],8)
        self.engine.button(1)
        self.engine.advance(900)
        self.assertEqual(self.engine.view()['screen'],3)
        sim.speed=3600
        sim.save()
        old=self.path.read_bytes()
        sim.reset_test_save()
        view=sim.view()
        self.assertEqual((view['species'],view['age_minutes'],view['screen'],view['speed']),(0,0,5,1))
        self.assertFalse(view['starter_chosen'])
        self.assertEqual(view['trainer_name'],'Ada')
        self.assertEqual(next(self.path.parent.glob('pet.json.reset-*.bak')).read_bytes(),old)
        restored=server.Engine(server.find_library())
        try:
            restored.load(bytes.fromhex(json.loads(self.path.read_text())['payload']))
            self.assertEqual(restored.view()['screen'],5)
        finally:restored.close()

    def test_reset_write_failure_keeps_running_game_and_save(self):
        sim=server.Simulator(self.engine,self.path,test_controls=True)
        self.engine.advance(60000,10)
        sim.save()
        old_file=self.path.read_bytes();old_state=self.engine.dump();old_handle=self.engine.handle
        with patch.object(server.os,'replace',side_effect=OSError('test failure')):
            with self.assertRaises(OSError):sim.reset_test_save()
        self.assertEqual(self.path.read_bytes(),old_file)
        self.assertEqual(self.engine.dump(),old_state)
        self.assertEqual(self.engine.handle,old_handle)
        self.assertIn('Zuruecksetzen fehlgeschlagen',sim.storage_error)


if __name__ == '__main__':
    unittest.main()
