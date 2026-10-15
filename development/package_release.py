from pathlib import Path
import zipfile,hashlib,json,sys
root=Path(__file__).resolve().parents[1]
output=Path(sys.argv[1]).resolve()
player='--end-user' in sys.argv[2:]
files=[p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.git' not in p.parts and p.name!='package-hashes.json' and (not player or p.relative_to(root).parts[0] in ('gamedata','fomod') or p.name in ('README_USER.md','meta.ini'))]
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(files):z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(output) as z:
 assert z.testzip() is None
 assert set(z.namelist())=={p.relative_to(root).as_posix() for p in files}
 for p in files:assert z.read(p.relative_to(root).as_posix())==p.read_bytes()
print('PASS',output.name,len(files),'files',output.stat().st_size,'bytes; bytes verified')
