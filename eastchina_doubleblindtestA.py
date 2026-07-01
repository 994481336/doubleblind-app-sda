from pathlib import Path


PARTS_DIR = Path(__file__).resolve().parent / "app_parts"
source = "".join(path.read_text(encoding="utf-8") for path in sorted(PARTS_DIR.glob("part_*.pyfrag")))
exec(compile(source, str(PARTS_DIR / "eastchina_doubleblindtestA.py"), "exec"))
