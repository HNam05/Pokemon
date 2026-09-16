"""Loopback-only PC simulator. Python transports data; all gameplay lives in C++."""
import argparse
import secrets
from collections import OrderedDict
import ctypes
import json
import os
from pathlib import Path
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'desktop' / 'web'


class Engine:
    def __init__(self, library, trainer_name=''):
        self.library = library
        self.lib = ctypes.CDLL(str(library))
        pointer = ctypes.c_void_p
        byte_pointer = ctypes.POINTER(ctypes.c_uint8)
        declarations = {
            'pp_create': ([], pointer),
            'pp_destroy': ([pointer], None),
            'pp_view': ([pointer], ctypes.c_char_p),
            'pp_advance': ([pointer, ctypes.c_uint32, ctypes.c_uint32], None),
            'pp_button': ([pointer, ctypes.c_int], ctypes.c_bool),
            'pp_save': ([pointer, byte_pointer, ctypes.c_size_t], ctypes.c_size_t),
            'pp_load': ([pointer, byte_pointer, ctypes.c_size_t], ctypes.c_bool),
            'pp_set_name': ([pointer, ctypes.c_char_p, ctypes.c_size_t], ctypes.c_bool),
            'pp_name': ([pointer], ctypes.c_char_p),
            'pp_back': ([pointer], None),
            'pp_menu_count': ([], ctypes.c_uint),
            'pp_menu_section': ([ctypes.c_uint], ctypes.c_char_p),
            'pp_need_low': ([ctypes.c_uint], ctypes.c_uint),
            'pp_menu_label': ([ctypes.c_uint], ctypes.c_char_p),
            'pp_menu_hint': ([pointer, ctypes.c_uint], ctypes.c_char_p),
            'pp_menu_enabled': ([pointer, ctypes.c_uint], ctypes.c_bool),
            'pp_care_hint': ([pointer], ctypes.c_char_p),
            'pp_sprite_size': ([ctypes.c_uint, ctypes.c_bool], ctypes.c_uint),
            'pp_sprite_pixel': ([ctypes.c_uint, ctypes.c_uint, ctypes.c_uint], ctypes.c_uint),
            'pp_memory_bytes': ([ctypes.c_uint], ctypes.c_uint),
            'pp_animation_seed': ([pointer, ctypes.c_uint32], None),
            'pp_animation': ([pointer], ctypes.c_char_p),
            'pp_frame_info': ([ctypes.c_uint]*4, ctypes.c_int),
            'pp_frame_pixel': ([ctypes.c_uint]*5, ctypes.c_uint),
            'pp_starter_count': ([], ctypes.c_uint),
            'pp_starter_at': ([ctypes.c_uint], ctypes.c_uint),
            'pp_species_name': ([ctypes.c_uint], ctypes.c_char_p),
            'pp_species_form': ([ctypes.c_uint], ctypes.c_char_p),
            'pp_species_credit': ([ctypes.c_uint], ctypes.c_char_p),
            'pp_species_scale': ([ctypes.c_uint], ctypes.c_uint),
            'pp_species_anchor': ([ctypes.c_uint], ctypes.c_int),
            'pp_scene_info': ([ctypes.c_uint], ctypes.c_uint),
            'pp_scene_pixel': ([ctypes.c_bool, ctypes.c_uint, ctypes.c_uint], ctypes.c_uint),
        }
        for name, (arguments, result) in declarations.items():
            method = getattr(self.lib, name)
            method.argtypes, method.restype = arguments, result
        encoded = trainer_name.encode('utf-8')
        self.handle = self.lib.pp_create()
        if not self.handle:
            raise MemoryError('C++-Spielkern konnte nicht angelegt werden.')
        self.lib.pp_animation_seed(self.handle, secrets.randbits(32))
        if not self.lib.pp_set_name(self.handle, encoded, len(encoded)):
            self.close()
            raise ValueError('Name: maximal 24 UTF-8-Bytes, keine Steuerzeichen.')

    def close(self):
        if self.handle:
            self.lib.pp_destroy(self.handle)
            self.handle = None

    def view(self):
        result = json.loads(self.lib.pp_view(self.handle))
        result['trainer_name'] = self.lib.pp_name(self.handle).decode('utf-8')
        result['animation'] = json.loads(self.lib.pp_animation(self.handle))
        result['starter_name'] = self.lib.pp_species_name(result['starter']).decode('utf-8')
        result['starter_form'] = self.lib.pp_species_form(result['starter']).decode('utf-8')
        result['care_hint'] = self.lib.pp_care_hint(self.handle).decode('utf-8')
        result['menu'] = [{'label': self.lib.pp_menu_label(i).decode('utf-8'),
                           'section':self.lib.pp_menu_section(i).decode('utf-8'),
                           'hint': self.lib.pp_menu_hint(self.handle, i).decode('utf-8'),
                           'enabled': self.lib.pp_menu_enabled(self.handle, i)}
                          for i in range(self.lib.pp_menu_count())]
        return result

    def catalog(self):
        entries=[]
        for i in range(self.lib.pp_starter_count()):
            species=self.lib.pp_starter_at(i)
            entries.append({'species':species,'name':self.lib.pp_species_name(species).decode('utf-8'),
                'form':self.lib.pp_species_form(species).decode('utf-8'),
                'credit':self.lib.pp_species_credit(species).decode('utf-8'),
                'scale':self.lib.pp_species_scale(species),'anchor_y':self.lib.pp_species_anchor(species)})
        return entries

    def assets(self, selected=None):
        ids=range(5) if selected is None else [selected]
        if selected is not None and selected not in {0,1,2,3,4,*[e['species'] for e in self.catalog()]}:
            raise ValueError('Unbekanntes Pokemon.')
        sprites = []
        for species in ids:
            width = self.lib.pp_sprite_size(species, False)
            height = self.lib.pp_sprite_size(species, True)
            pixels = [self.lib.pp_sprite_pixel(species, x, y) for y in range(height) for x in range(width)]
            sprites.append({'width': width, 'height': height, 'pixels': pixels})
        animations = []
        for species in ids:
            clips = []
            for motion in range(9):
                frames = []
                for frame in range(self.lib.pp_frame_info(species,motion,0,5)):
                    width,height,x,y,duration = (self.lib.pp_frame_info(species,motion,frame,p) for p in range(5))
                    frames.append({'width':width,'height':height,'x':x,'y':y,'duration':duration,
                        'draw_x':self.lib.pp_frame_info(species,motion,frame,6),
                        'draw_y':self.lib.pp_frame_info(species,motion,frame,7),
                        'scale':self.lib.pp_frame_info(species,motion,frame,8),
                        'pixels':[self.lib.pp_frame_pixel(species,motion,frame,px,py) for py in range(height) for px in range(width)]})
                clips.append(frames)
            animations.append(clips)
        scenes=[]
        if selected is None:
            width,height=(self.lib.pp_scene_info(i) for i in range(2))
            scenes=[{'width':width,'height':height,'pixels':[
                self.lib.pp_scene_pixel(night,x,y) for y in range(height) for x in range(width)]} for night in (False,True)]
        return {'sprites': sprites, 'animations':animations,'scenes':scenes,'scene_bytes':self.lib.pp_scene_info(2),'species_ids':list(ids),'catalog':self.catalog() if selected is None else [],
                'need_low':[self.lib.pp_need_low(i) for i in range(6)],
                'memory_bytes': dict(zip(('game', 'state', 'profile', 'sprites','animations','animator'),
                (self.lib.pp_memory_bytes(i) for i in range(6))))}

    def advance(self, milliseconds, speed=1):
        while milliseconds > 0:
            step = min(60000, milliseconds)
            self.lib.pp_advance(self.handle, step, speed)
            milliseconds -= step

    def button(self, value):
        if not self.lib.pp_button(self.handle, value):
            raise ValueError('Ungueltige Taste.')

    def dump(self):
        buffer = (ctypes.c_uint8 * 44)()
        size = self.lib.pp_save(self.handle, buffer, len(buffer))
        if size != 44:
            raise RuntimeError('Spielstand konnte nicht kodiert werden.')
        return bytes(buffer)

    def load(self, data):
        buffer = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        if not self.lib.pp_load(self.handle, buffer, len(data)):
            raise ValueError('Spielstand beschaedigt oder Version nicht unterstuetzt. Datei bleibt erhalten.')


class Simulator:
    def __init__(self, engine, save_path, manual=False, test_controls=False):
        self.engine, self.save_path, self.manual = engine, save_path, manual
        self.test_controls = test_controls
        self.speed = 1
        self.storage_error = None
        self.offline_minutes = 0
        if save_path.exists():
            if save_path.stat().st_size > 4096:
                raise ValueError('Spielstand ist zu gross. Datei bleibt erhalten.')
            data = json.loads(save_path.read_text(encoding='utf-8'))
            if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1:
                raise ValueError('Unbekannte Spielstandhuelle.')
            timestamp = data.get('saved_at')
            if type(timestamp) is not int or not 0 <= timestamp <= 253402300799:
                raise ValueError('Ungueltiger Speicherzeitpunkt.')
            if not isinstance(data.get('payload'), str) or len(data['payload']) not in (84, 88):
                raise ValueError('Ungueltige Spielstanddaten.')
            engine.load(bytes.fromhex(data['payload']))
            # Clock rollback never subtracts age; offline care is capped at 8 hours.
            elapsed = max(0, min(8 * 3600, int(time.time()) - timestamp))
            self.offline_minutes = elapsed // 60 if not manual else 0
            if not manual:
                engine.advance(elapsed * 1000)
        self.last_tick = time.monotonic()
        self.last_save = self.last_tick

    def tick(self):
        now = time.monotonic()
        milliseconds = int((now - self.last_tick) * 1000)
        self.last_tick += milliseconds / 1000
        if not self.manual:
            # Suspend/resume is real offline time, never multiplied by a demo speed.
            speed = self.speed if milliseconds < 5000 or self.speed == 0 else 1
            self.engine.advance(min(milliseconds, 8 * 3600000), speed)
        if now - self.last_save >= 30:
            self.save()

    def write_save(self, data):
        temporary = self.save_path.with_suffix('.tmp')
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {'version': 1, 'saved_at': int(time.time()), 'payload': data.hex()}
        with temporary.open('w', encoding='utf-8', newline='\n') as stream:
            json.dump(payload, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.save_path)

    def save(self):
        try:
            self.write_save(self.engine.dump())
            self.storage_error = None
        except OSError as error:
            self.storage_error = f'Speichern fehlgeschlagen: {error}'
        self.last_save = time.monotonic()

    def reset_test_save(self):
        if not self.test_controls:
            raise ValueError('Testfunktionen sind deaktiviert.')
        name = self.engine.view()['trainer_name']
        fresh = Engine(self.engine.library, name)
        try:
            if self.manual:
                fresh.lib.pp_animation_seed(fresh.handle, 42)
            if self.save_path.exists():
                backup = self.save_path.with_name(f'{self.save_path.name}.reset-{time.time_ns()}.bak')
                with backup.open('xb') as stream:
                    stream.write(self.save_path.read_bytes())
                    stream.flush()
                    os.fsync(stream.fileno())
            # Persist first; a failed write must not replace the running session.
            self.write_save(fresh.dump())
            self.engine.handle, fresh.handle = fresh.handle, self.engine.handle
            self.speed = 1
            self.offline_minutes = 0
            self.storage_error = None
            self.last_tick = self.last_save = time.monotonic()
        except OSError as error:
            self.storage_error = f'Zuruecksetzen fehlgeschlagen: {error}'
            raise
        finally:
            fresh.close()

    def view(self):
        return {**self.engine.view(), 'speed': self.speed, 'manual_clock': self.manual,
                'test_controls': self.test_controls,
                'storage_error': self.storage_error, 'offline_minutes': self.offline_minutes}


def handler_for(simulator, port):
    assets = simulator.engine.assets()
    asset_cache = OrderedDict()
    allowed_hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
    allowed_origins = {f'http://{host}' for host in allowed_hosts}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, _format, *args):
            pass

        def send_body(self, status, payload, content_type='application/json; charset=utf-8'):
            body = payload if isinstance(payload, bytes) else json.dumps(payload).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            try:
                self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                pass  # A disconnected browser does not stop the pet.

        def valid_host(self):
            if self.headers.get('Host') not in allowed_hosts:
                self.send_body(403, {'error': 'Nur lokaler Zugriff erlaubt.'})
                return False
            return True

        def do_GET(self):
            if not self.valid_host():
                return
            if self.path == '/api/state':
                self.send_body(200, simulator.view())
                return
            if self.path == '/api/assets':
                self.send_body(200, assets)
                return
            if self.path.startswith('/api/assets/'):
                token=self.path.removeprefix('/api/assets/')
                if not token.isascii() or not token.isdecimal() or len(token)>3:
                    self.send_body(404,{'error':'Unbekannte Grafik.'}); return
                species=int(token)
                try:
                    if species not in asset_cache:
                        asset_cache[species]=simulator.engine.assets(species)
                        if len(asset_cache)>4: asset_cache.popitem(last=False)
                    asset_cache.move_to_end(species)
                    self.send_body(200,asset_cache[species])
                except ValueError as error:
                    self.send_body(404,{'error':str(error)})
                return
            if self.path == '/credits':
                self.send_body(200,(ROOT/'assets/ROSTER.md').read_bytes(),'text/plain; charset=utf-8')
                return
            files = {'/': ('index.html', 'text/html; charset=utf-8'),
                     '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                     '/style.css': ('style.css', 'text/css; charset=utf-8')}
            if self.path not in files:
                self.send_body(404, {'error': 'Nicht gefunden.'})
                return
            filename, mime = files[self.path]
            self.send_body(200, (WEB / filename).read_bytes(), mime)

        def do_POST(self):
            if not self.valid_host():
                return
            origin = self.headers.get('Origin')
            if origin is not None and origin not in allowed_origins:
                self.send_body(403, {'error': 'Fremder Ursprung abgewiesen.'})
                return
            if self.headers.get('Content-Type') != 'application/json':
                self.send_body(415, {'error': 'JSON erwartet.'})
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 1 <= length <= 1024:
                    raise ValueError('Ungueltige Anfragelaenge.')
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError('JSON-Objekt erwartet.')
                if self.path == '/api/button':
                    button = data.get('button')
                    if type(button) is not int or button not in (0, 1, 2):
                        raise ValueError('Taste muss 0, 1 oder 2 sein.')
                    simulator.engine.button(button)
                    simulator.save()
                elif self.path == '/api/back':
                    simulator.engine.lib.pp_back(simulator.engine.handle)
                    simulator.save()
                elif self.path == '/api/speed':
                    speed = data.get('speed')
                    if type(speed) is not int or speed not in (0, 1, 60, 3600):
                        raise ValueError('Unbekannte Geschwindigkeit.')
                    simulator.speed = speed
                elif self.path == '/api/advance' and simulator.manual:
                    ms = data.get('ms')
                    if type(ms) is not int or not 0 <= ms <= 60000:
                        raise ValueError('Zeitschritt muss zwischen 0 und 60000 ms liegen.')
                    simulator.engine.advance(ms, simulator.speed)
                elif self.path == '/api/skip':
                    minutes = data.get('minutes')
                    if type(minutes) is not int or minutes not in (10, 60):
                        raise ValueError('Nur 10 oder 60 Minuten erlaubt.')
                    if simulator.engine.view()['screen'] in (3, 7, 8):
                        raise ValueError('Zeitsprung erst nach dem Minispiel.')
                    simulator.engine.advance(minutes * 60000)
                    simulator.save()
                elif self.path == '/api/save':
                    simulator.save()
                elif self.path == '/api/reset' and simulator.test_controls:
                    if data.get('confirm') is not True:
                        raise ValueError('Zuruecksetzen muss bestaetigt werden.')
                    simulator.reset_test_save()
                else:
                    self.send_body(404, {'error': 'Nicht gefunden.'})
                    return
            except (ValueError, UnicodeDecodeError) as error:
                self.send_body(400, {'error': str(error)})
                return
            except OSError as error:
                self.send_body(500, {'error': f'Speicherzugriff fehlgeschlagen: {error}'})
                return
            self.send_body(200, simulator.view())

    return Handler


class LocalServer(HTTPServer):
    def get_request(self):
        connection, address = super().get_request()
        connection.settimeout(2)
        return connection, address


class SaveLock:
    """OS-owned lock releases even after a crash; stale lock files are harmless."""
    def __init__(self, path):
        self.path = path.with_suffix('.lock')
        self.stream = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open('a+b')
        try:
            if self.path.stat().st_size == 0:
                self.stream.write(b'0')
                self.stream.flush()
            self.stream.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            raise OSError('Dieser Spielstand wird bereits verwendet oder kann nicht gesperrt werden.') from None
        return self

    def __exit__(self, *_args):
        self.stream.close()


def find_library():
    names = ('pet_bridge.dll', 'libpet_bridge.so', 'pet_bridge.so', 'libpet_bridge.dylib', 'pet_bridge.dylib')
    for directory in (ROOT / 'build' / 'Release', ROOT / 'build'):
        for name in names:
            if (directory / name).is_file():
                return directory / name
    raise FileNotFoundError('C++-Bibliothek fehlt. Zuerst python scripts/build.py ausfuehren.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--save', type=Path)
    parser.add_argument('--profile', type=Path, help='Lokale JSON-Konfiguration mit trainer_name')
    parser.add_argument('--manual-clock', action='store_true', help='Deterministische Testuhr')
    parser.add_argument('--test-controls', action='store_true', help='Nur Entwicklung: Spielstand-Reset im Simulator erlauben')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        raise ValueError('Port muss zwischen 1 und 65535 liegen.')
    name = ''
    if args.profile:
        if args.profile.stat().st_size > 1024:
            raise ValueError('Profildatei ist zu gross.')
        profile = json.loads(args.profile.read_text(encoding='utf-8'))
        if not isinstance(profile, dict) or set(profile) != {'trainer_name'} or not isinstance(profile['trainer_name'], str):
            raise ValueError('Profil erwartet nur trainer_name als Text.')
        name = profile['trainer_name']
    if args.save is None:
        save_name = args.profile.stem if args.profile else 'pet'
        args.save = ROOT / 'saves' / f'{save_name}.json'
    engine = Engine(find_library(), name)
    if args.manual_clock:
        engine.lib.pp_animation_seed(engine.handle, 42)
    try:
        with SaveLock(args.save.resolve()):
            simulator = Simulator(engine, args.save.resolve(), args.manual_clock, args.test_controls)
            with LocalServer(('127.0.0.1', args.port), handler_for(simulator, args.port)) as server:
                server.timeout = 0.05
                print(f'Pocket Pet: http://127.0.0.1:{args.port} | Strg+C beendet und speichert.', flush=True)
                try:
                    while True:
                        simulator.tick()
                        server.handle_request()
                except KeyboardInterrupt:
                    simulator.save()
                    if simulator.storage_error:
                        print(simulator.storage_error, flush=True)
    finally:
        engine.close()


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(f'Simulator konnte nicht starten: {error}')
