"""Loopback-only PC simulator. Python transports data; all gameplay lives in C++."""
import argparse
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
    def __init__(self, library):
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
        }
        for name, (arguments, result) in declarations.items():
            method = getattr(self.lib, name)
            method.argtypes, method.restype = arguments, result
        self.handle = self.lib.pp_create()
        if not self.handle:
            raise MemoryError('C++-Spielkern konnte nicht angelegt werden.')

    def close(self):
        if self.handle:
            self.lib.pp_destroy(self.handle)
            self.handle = None

    def view(self):
        return json.loads(self.lib.pp_view(self.handle))

    def advance(self, milliseconds, speed=1):
        while milliseconds > 0:
            step = min(60000, milliseconds)
            self.lib.pp_advance(self.handle, step, speed)
            milliseconds -= step

    def button(self, value):
        if not self.lib.pp_button(self.handle, value):
            raise ValueError('Ungueltige Taste.')

    def dump(self):
        buffer = (ctypes.c_uint8 * 42)()
        size = self.lib.pp_save(self.handle, buffer, len(buffer))
        if size != 42:
            raise RuntimeError('Spielstand konnte nicht kodiert werden.')
        return bytes(buffer)

    def load(self, data):
        buffer = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        if not self.lib.pp_load(self.handle, buffer, len(data)):
            raise ValueError('Spielstand beschaedigt oder Version nicht unterstuetzt. Datei bleibt erhalten.')


class Simulator:
    def __init__(self, engine, save_path, manual=False):
        self.engine, self.save_path, self.manual = engine, save_path, manual
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
            if not isinstance(data.get('payload'), str) or len(data['payload']) != 84:
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

    def save(self):
        temporary = self.save_path.with_suffix('.tmp')
        try:
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {'version': 1, 'saved_at': int(time.time()), 'payload': self.engine.dump().hex()}
            with temporary.open('w', encoding='utf-8', newline='\n') as stream:
                json.dump(payload, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.save_path)
            self.storage_error = None
        except OSError as error:
            self.storage_error = f'Speichern fehlgeschlagen: {error}'
        self.last_save = time.monotonic()

    def view(self):
        return {**self.engine.view(), 'speed': self.speed, 'manual_clock': self.manual,
                'storage_error': self.storage_error, 'offline_minutes': self.offline_minutes}


def handler_for(simulator, port):
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
                    if simulator.engine.view()['screen'] == 3:
                        raise ValueError('Zeitsprung erst nach dem Minispiel.')
                    simulator.engine.advance(minutes * 60000)
                    simulator.save()
                elif self.path == '/api/save':
                    simulator.save()
                else:
                    self.send_body(404, {'error': 'Nicht gefunden.'})
                    return
            except (ValueError, UnicodeDecodeError) as error:
                self.send_body(400, {'error': str(error)})
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
    parser.add_argument('--save', type=Path, default=ROOT / 'saves' / 'pet.json')
    parser.add_argument('--manual-clock', action='store_true', help='Deterministische Testuhr')
    args = parser.parse_args()
    engine = Engine(find_library())
    try:
        with SaveLock(args.save.resolve()):
            simulator = Simulator(engine, args.save.resolve(), args.manual_clock)
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
