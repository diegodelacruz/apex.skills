#!/usr/bin/env python3
import argparse, json, re, zipfile
from pathlib import Path

def lookup(text, name):
    found = re.search(rf"^\s*{re.escape(name)}:\s*(.+?)\s*$", text, re.M)
    return found.group(1).strip(" '\"") if found else None

def main():
    p=argparse.ArgumentParser(); p.add_argument('export_zip',type=Path); p.add_argument('--json',action='store_true'); a=p.parse_args()
    with zipfile.ZipFile(a.export_zip) as z:
        names=z.namelist(); roots={x.split('/',1)[0] for x in names if '/' in x}
        if len(roots)!=1: raise ValueError('expected exactly one export root')
        root=roots.pop(); meta_path=f'{root}/readable/application/{root}.yaml'
        if meta_path not in names: raise ValueError('missing readable application YAML')
        meta=z.read(meta_path).decode('utf-8','replace')
        out={'archive':a.export_zip.name,'root':root,'application_id':lookup(meta,'id'),'application_name':lookup(meta,'name'),'alias':lookup(meta,'alias'),'parsing_schema':lookup(meta,'parsing-schema'),'readable_pages':sum(x.startswith(f'{root}/readable/application/pages/') and x.endswith('.yaml') for x in names),'sql_pages':sum(x.startswith(f'{root}/application/pages/') and x.endswith('.sql') for x in names),'install_sql':f'{root}/install.sql' in names}
    print(json.dumps(out,ensure_ascii=False,indent=2) if a.json else '\n'.join(f'{k}: {v}' for k,v in out.items()))
if __name__=='__main__': main()
