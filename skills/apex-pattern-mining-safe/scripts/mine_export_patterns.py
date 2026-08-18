#!/usr/bin/env python3
"""Read-only evidence inventory for split Oracle APEX ZIP exports."""
import argparse, collections, json, re, sys, zipfile
from pathlib import Path

try: sys.stdout.reconfigure(encoding='utf-8')
except AttributeError: pass

def field(text, name):
    match=re.search(rf'^\s*{re.escape(name)}:\s*(.+?)\s*$',text,re.M)
    return match.group(1).strip(" '\"") if match else None

def inspect(path):
    with zipfile.ZipFile(path) as z:
        names=z.namelist(); roots={n.split('/',1)[0] for n in names if '/' in n}
        if len(roots)!=1: raise ValueError(f'{path}: expected exactly one export root')
        root=roots.pop(); meta=z.read(f'{root}/readable/application/{root}.yaml').decode('utf-8','replace')
        pages=[n for n in names if n.startswith(f'{root}/readable/application/pages/') and n.endswith('.yaml')]
        text='\n'.join(z.read(n).decode('utf-8','replace') for n in pages)
        return {'archive':path.name,'application':{'id':field(meta,'id'),'name':field(meta,'name'),'alias':field(meta,'alias'),'schema':field(meta,'parsing-schema')},'pages':len(pages),'security':{'session_state_protection':bool(re.search(r'session-state-protection:\s*\n\s+enabled:\s*true',meta)),'extended_html_escaping':'html-escaping-mode: Extended' in meta,'deep_links_disabled':'deep-linking: Disabled' in meta,'frames_denied':'embed-in-frames: Deny' in meta},'component_types':collections.Counter(re.findall(r'^\s*type:\s*(.+?)\s*$',text,re.M)).most_common(20),'templates':collections.Counter(re.findall(r'^\s*template:\s*(.+?)\s*$',text,re.M)).most_common(20),'readable_pages':len(pages),'sql_pages':sum(n.startswith(f'{root}/application/pages/') and n.endswith('.sql') for n in names),'assets':sum('/app_static_files/' in n or '/theme_42/static_files/' in n for n in names)}

def main():
    p=argparse.ArgumentParser(); p.add_argument('export_zip',nargs='+',type=Path); p.add_argument('--json',action='store_true'); a=p.parse_args(); report=[inspect(x) for x in a.export_zip]
    print(json.dumps(report,ensure_ascii=False,indent=2) if a.json else '\n'.join(f"{x['archive']}: {x['application']['name']} ({x['pages']} readable pages)" for x in report))
if __name__=='__main__': main()
