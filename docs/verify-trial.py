from pathlib import Path
import hashlib,json,re,subprocess
repo=Path(__file__).resolve().parents[1];root=repo.parent
snapshot=json.loads((repo/'docs/trial-snapshot.json').read_text(encoding='utf-8'))
exe=root/'loj-validator/target/release/loj-validator.exe'
out=repo/'docs/validation';out.mkdir(exist_ok=True)
v=repo/'versions'/snapshot['revision']
related=[repo/'docs/related'/rid for rid in snapshot['relatedRecords'].values()]
jobs=[('package-L0',[str(v),'--level','L0']),('package-L1',[str(v),'--level','L1']),('history-L3',[str(repo),'--level','L3']),('rebuild',[str(repo),'--check','rebuild']),('registry',[str(root/'loj-registry'),'--check','registry','--registration-space','law-of-japan'])]
jobs += [(p.name+'-L3',[str(p),'--level','L3']) for p in related]
jobs += [('relations-L4',['--registry',str(root/'loj-registry'),'--repository',str(repo),'--repository',str(root/'19480720-law-178')]+sum([['--repository',str(p)] for p in related],[])+['--level','L4','--registration-space','law-of-japan'])]
results=[]
for name,args in jobs:
    args=[str(Path(a).relative_to(root)).replace('\\','/') if a.startswith(str(root)) else a for a in args]
    cmd=[str(exe),'check']+args+['--format','json']
    r=subprocess.run(cmd,capture_output=True,cwd=root)
    (out/(name+'.json')).write_bytes(r.stdout)
    report=json.loads(r.stdout)
    results.append({'name':name,'exitCode':r.returncode,'args':args,'results':report.get('results'),'diagnostics':report.get('diagnostics')})
    print(name,r.returncode,report.get('results'))
# loj-spec 668f400 types the paragraph-form main provision (PARA-03) and amendments (AMEND-01..03).
assert all(r['exitCode']==0 for r in results), 'Unexpected validation result'
assert not any(d.get('class')=='error' for r in results if r['name']=='package-L1' for d in r['diagnostics'])
pattern=r'<!-- loj:row key=[a-z0-9]{4} -->\n(.*?)<!-- loj:end-row -->'
def rows(p):
    return [re.findall(r'<!-- loj:cell -->\n(.*?)\n<!-- loj:end-cell -->',x,re.S) for x in re.findall(pattern,p.read_text(encoding='utf-8'),re.S)]
amending_rows=rows(v/'main.md')
holiday_rows=rows(root/'19480720-law-178/versions/gfah5dqe/main.md')
assert len(amending_rows)==3 and all(x in holiday_rows for x in amending_rows)
for d in json.loads((repo/'docs/sources/downloads.json').read_text(encoding='utf-8')):
    assert hashlib.sha256((repo/'docs/sources'/d['file']).read_bytes()).hexdigest()==d['sha256']
for line in snapshot['legacyRefs']:
    sha,ref=line.split(' ',1)
    # The trial was promoted to main after the snapshot, so main and its remote/HEAD moved by design.
    if '/trial/' in ref or ref in ('refs/heads/main','refs/remotes/origin/main','refs/remotes/origin/HEAD'):continue
    assert subprocess.check_output(['git','-C',str(repo),'rev-parse',ref],text=True).strip()==sha
assert subprocess.check_output(['git','-C',str(root/'19480720-law-178'),'rev-parse','HEAD'],text=True).strip()==snapshot['heads']['19480720-law-178']
supp=(v/'supplement.md').read_text(encoding='utf-8')
own=re.sub(r'<!-- loj:amendment-content -->.*?<!-- loj:end-amendment-content -->\n','',supp,flags=re.S)
assert own.count('<!-- loj:paragraph number=')==6
# The quoted 第五条 of 老人福祉法 is inside the amendment content of 附則第六項, never an article of this law.
assert '# 第五条' not in own and '# 第五条（敬老の日の行事）' in supp
assert all(s not in supp for s in ['附属磯関','の一都','を判り'])
summary={'checks':results,'sourceHashesMatch':True,'legacyRefsUnchanged':True,'holidayHeadUnchanged':True,'supplementParagraphs':6,'binarySha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'spec':snapshot['heads']['loj-spec']}
(out/'summary.json').write_bytes((json.dumps(summary,ensure_ascii=False,indent=2)+'\n').encode())
