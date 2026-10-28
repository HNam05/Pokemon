"""Build with CMake, or --zig /path/to/zig for a portable compiler without an SDK."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zig', type=Path)
    args = parser.parse_args()
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    if args.zig:
        compiler = str(args.zig.resolve())
        flags = ['-std=c++17', '-Wall', '-Wextra', '-Wpedantic', '-Werror', '-O2', '-Iinclude']
        if sys.platform != 'win32':
            flags.append('-fPIC')
        sources = ['src/game.cpp', 'src/save.cpp', 'src/sprite.cpp', 'src/animation.cpp', 'src/input.cpp', 'src/render.cpp', 'src/device.cpp']
        suffix = '.dll' if sys.platform == 'win32' else ('.dylib' if sys.platform == 'darwin' else '.so')
        subprocess.run([compiler, 'c++', *flags, *sources, 'desktop/bridge.cpp', '-shared',
                        '-o', str(build / ('pet_bridge' + suffix))], cwd=ROOT, check=True)
        test = build / ('pet_tests.exe' if sys.platform == 'win32' else 'pet_tests')
        subprocess.run([compiler, 'c++', *flags, *sources, 'tests/core_tests.cpp', '-o', str(test)],
                       cwd=ROOT, check=True)
        subprocess.run([str(test)], cwd=ROOT, check=True)
    else:
        subprocess.run(['cmake', '-S', str(ROOT), '-B', str(build)], check=True)
        subprocess.run(['cmake', '--build', str(build), '--config', 'Release'], check=True)
        subprocess.run(['ctest', '--test-dir', str(build), '-C', 'Release', '--output-on-failure'], check=True)


if __name__ == '__main__':
    main()
