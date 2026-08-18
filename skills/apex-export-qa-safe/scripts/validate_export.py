#!/usr/bin/env python3
import argparse, hashlib, re, zipfile
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument('export_zip',type=Path); a=p.parse_args()
    try:
        with zipfile.ZipFile(a.export_zip) as z:
            names=z.namelist(); roots={x.split('/',1)[0] for x in names if '/' in x}
            if len(roots)!=1: raise ValueError('expected exactly one export root')
            root=roots.pop(); meta=z.read(f'{root}/readable/application/{root}.yaml').decode('utf-8','replace')
            checks=[f'{root}/install.sql' in names,any(x.startswith(f'{root}/readable/application/pages/') and x.endswith('.yaml') for x in names),any(x.startswith(f'{root}/application/pages/') and x.endswith('.sql') for x in names),bool(re.search(r'session-state-protection:\s*\n\s+enabled:\s*true',meta)), 'html-escaping-mode: Extended' in meta, 'theme: Universal Theme # 42' in meta]
            if not all(checks): raise ValueError('required structure or declared security setting is absent')
    except (OSError, ValueError, zipfile.BadZipFile) as err:
        print(f'STATIC_FAIL: {err}'); raise SystemExit(1)
    print(f'STATIC_PASS: {a.export_zip.name}'); print('sha256: '+hashlib.sha256(a.export_zip.read_bytes()).hexdigest())
if __name__=='__main__': main()
