#!/usr/bin/env python3
"""Reproducible source/APK inventory. No screenshots, sessions or user data are copied.
Run from any directory: python3 .../verify_goal_artifacts.py --apk /abs/app-debug.apk
UTC execution timestamp; no stochastic seed, cohort, metrics denominator or dedupe estimate.
The input file manifest is fixed here. Comparison reference defaults to 8d6871e.
"""
import argparse,csv,hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--apk',required=True,type=Path);p.add_argument('--base',default='8d6871e');p.add_argument('--out',type=Path,default=root/'reports/goal-workspace');args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
names=['CampusActivity','CampusToolsActivity','CharacterWorkspaceActivity','DiscoveryProviders','GoalDiscoveryActivity','GoalHomeActivity','GoalRules','GoalStore','GoalUi','MediaRepository','TaskActivity','TaskStore']
files=[root/f'mobile-aside-mvp/app/src/main/java/ai/decisionos/aside/{n}.java' for n in names]
files += [root/'mobile-aside-mvp/app/src/main/AndroidManifest.xml',root/'mobile-aside-mvp/app/build.gradle',root/'mobile-aside-mvp/app/src/main/assets/goal_extract.js',root/'mobile-aside-mvp/app/src/experimental/AndroidManifest.xml',args.apk]
hash=lambda data:hashlib.sha256(data).hexdigest()
rows=[]
for f in files:
 if not f.is_file():raise SystemExit('Missing input '+str(f))
 try:key=str(f.relative_to(root))
 except ValueError:key='APK/'+f.name
 rows.append({'path':key,'bytes':f.stat().st_size,'sha256':hash(f.read_bytes())})
report={'generated_at':datetime.now(timezone.utc).isoformat(),'timezone':'UTC','base_commit':args.base,'files':rows,'scope':'Source/package bytes only. Does not assert provider live results or deployment approval.'}
(args.out/'sha256_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
with (args.out/'old_vs_new_diff.csv').open('w') as out:
 w=csv.writer(out);w.writerow(['path','base_sha256','current_sha256','status'])
 for r in rows:
  old=subprocess.run(['git','show',args.base+':'+r['path']],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
  digest=hash(old.stdout) if old.returncode==0 else ''
  w.writerow([r['path'],digest,r['sha256'],'unchanged' if digest==r['sha256'] else 'changed' if digest else 'new'])
with (args.out/'reproduction_check.csv').open('w') as out:
 w=csv.writer(out);w.writerow(['check','result','scope'])
 for r,f in zip(rows,files):w.writerow([r['path'],'PASS' if hash(f.read_bytes())==r['sha256'] else 'FAIL','repeat byte hash, not functional or live-provider validation'])
print('Wrote',len(rows),'file hashes to',args.out)
