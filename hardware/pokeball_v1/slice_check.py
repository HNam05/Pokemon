"""Optional local Bambu Studio smoke slicing. No printer connection or upload.

Profiles are flattened from the installed version, because the CLI does not resolve
all profile inheritance when given a system JSON directly. G-code is not shipped.
"""
import argparse
import json
from pathlib import Path
import subprocess
from build import OUT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--studio", type=Path, required=True)
    parser.add_argument("--parts", nargs="+", default=["01", "02", "03", "11", "12", "05"])
    args = parser.parse_args()
    profiles = args.studio.parent / "resources/profiles/BBL"
    dest = OUT / "slicer"
    dest.mkdir(exist_ok=True)

    def flatten(kind, name):
        data = json.loads((profiles/kind/f"{name}.json").read_text(encoding="utf-8"))
        parent = data.pop("inherits", None)
        merged = flatten(kind, parent) if parent else {}
        merged.update(data)
        return merged

    configs = {}
    for kind, name in (("machine","Bambu Lab A1 0.4 nozzle"),
                       ("process","0.20mm Standard @BBL A1"),
                       ("filament","Generic PLA @BBL A1")):
        data = flatten(kind, name)
        if kind == "process":
            data.update({"enable_support":"1", "support_type":"normal(auto)",
                         "support_on_build_plate_only":"0", "wall_loops":"4",
                         "sparse_infill_density":"15%", "brim_type":"outer_only",
                         "brim_width":"4"})
        path = dest/f"{kind}.json"
        path.write_text(json.dumps(data,indent=2),encoding="utf-8")
        configs[kind] = path
    for prefix in args.parts:
        path, = (OUT/"STL_print").glob(f"{prefix}_*.stl")
        folder = dest/path.stem
        folder.mkdir(exist_ok=True)
        command = [str(args.studio),"--debug","2","--load-settings",
                   f"{configs['machine']};{configs['process']}","--load-filaments",str(configs['filament']),
                   "--arrange","1","--orient","0","--slice","0","--outputdir",str(folder),
                   "--export-3mf",f"{path.stem}.3mf",str(path)]
        run = subprocess.run(command,capture_output=True,text=True,encoding="utf-8",errors="replace")
        (folder/"slice.log").write_text(run.stdout+run.stderr,encoding="utf-8")
        print(path.stem,run.returncode,[p.name for p in folder.iterdir()],flush=True)
        if run.returncode != 0:
            raise RuntimeError(f"Slice failed: {folder/'slice.log'}")
        if not list(folder.glob("*.3mf")):
            raise RuntimeError(f"No 3MF produced: {folder/'slice.log'}")


if __name__ == "__main__":
    main()
