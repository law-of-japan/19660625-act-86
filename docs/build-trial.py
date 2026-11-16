"""One-shot construction of the local trial; never overwrites a generated snapshot."""
from pathlib import Path
import copy, hashlib, json, secrets, shutil, subprocess, yaml
yaml.SafeDumper.ignore_aliases = lambda self, data: True
repo = Path(__file__).resolve().parents[1]
root = repo.parent
def git(r,*args): return subprocess.check_output(['git','-C',str(r),*args],text=True,encoding='utf-8').strip()
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(s.encode('utf-8'))
def dump(p,o): write(p,yaml.safe_dump(o,allow_unicode=True,sort_keys=False,width=110))
def uid(n): return ''.join(secrets.choice('0123456789abcdefghjkmnpqrstvwxyz') for _ in range(n))
assert not (repo/'docs/trial-snapshot.json').exists()
revision=uid(8)
existing={p.stem.lower() for p in (root/'loj-registry/records').glob('*.yaml')}
ids=[]
while len(ids)<3:
    x=uid(10)
    if x not in existing and x not in ids: ids.append(x)
snapshot={'revision':revision,'relatedRecords':dict(zip(['総理府設置法','スポーツ振興法','老人福祉法'],ids)),
 'heads':{n:git(root/n,'rev-parse','HEAD') for n in ['19660625-act-86','19480720-law-178','loj-registry','loj-spec','loj-validator']},
 'legacyRefs':git(repo,'show-ref').splitlines()}
write(repo/'docs/trial-snapshot.json',json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n')
shutil.copyfile(root/'amending-act-trial-plan.md',repo/'docs/trial-plan.md')
for n in range(1,4): shutil.copyfile(root/f'19480720-law-178/docs/sources/goshomei-1966-{n}.jpg',repo/f'docs/sources/goshomei-1966-{n}.jpg')
shutil.copyfile(root/'19480720-law-178/docs/sources/goshomei-1966-manifest.json',repo/'docs/sources/manifest.json')
manifest=json.loads((repo/'docs/sources/manifest.json').read_text(encoding='utf-8'))
downloads=[{'file':f'goshomei-1966-{i+1}.jpg','url':c['images'][0]['resource']['@id'],'sha256':hashlib.sha256((repo/f'docs/sources/goshomei-1966-{i+1}.jpg').read_bytes()).hexdigest(),'viewed':True} for i,c in enumerate(manifest['sequences'][0]['canvases'])]
write(repo/'docs/sources/downloads.json',json.dumps(downloads,ensure_ascii=False,indent=2)+'\n')
source={'id':'src-goshomei-s41-86','kind':'promulgation','title':manifest['label'],'uri':'https://www.digital.archives.go.jp/file/686000','glyphPreservation':'preserved','fixed':'; '.join('docs/sources/'+d['file']+' SHA-256 '+d['sha256'] for d in downloads)}
def ev(loc): return [{'source':source['id'],'locator':loc}]
confirmed={'state':'confirmed'}
prom={'state':'date','value':'1966-06-25','raw':'昭和四十一年六月二十五日','precision':'day','evidence':ev('1画像 公布文'),'verification':{'state':'unverified','reason':'官報の発行日と未照合（REB-05）'}}
effective={'state':'derived','rule':'公布の日から','base':prom,'calc':{'op':'sameDay'},'value':'1966-06-25','raw':'この法律は、公布の日から施行する。','evidence':ev('3画像 附則第一項'),'verification':confirmed}
def table(cells,n=1):
    return f'<!-- loj:table number={n} -->\n<!-- loj:row key={uid(4)} -->\n'+''.join('<!-- loj:cell -->\n'+c+'\n<!-- loj:end-cell -->\n' for c in cells)+'<!-- loj:end-row -->\n<!-- loj:end-table -->\n'
main='国民の祝日に関する法律（昭和二十三年法律第百七十八号）の一部を次のように改正する。\n\n'
for n,(previous,cells) in enumerate([
 ('成人の日',['建国記念の日','政令で定める日','建国をしのび、国を愛する心を養う。']),
 ('こどもの日',['敬老の日','九月十五日','多年にわたり社会につくしてきた老人を敬愛し、長寿を祝う。']),
 ('秋分の日',['体育の日','十月十日','スポーツにしたしみ、健康な心身をつちかう。'])],1):
    main+='第二条'+previous+'の項の次に次のように加える。\n'+table(cells,n)+'\n'
paras=[('施行期日','この法律は、公布の日から施行する。'),
 ('建国記念の日となる日を定める政令の制定','改正後の第二条に規定する建国記念の日となる日を定める政令は、この法律の公布の日から起算して六月以内に制定するものとする。'),
 (None,'内閣総理大臣は、改正後の第二条に規定する建国記念の日となる日を定める政令の制定の立案をしようとするときは、建国記念日審議会に諮問し、その答申を尊重してしなければならない。'),
 ('総理府設置法の一部改正','総理府設置法（昭和二十四年法律第百二十七号）の一部を次のように改正する。\n第十五条第一項の表中同和対策協議会の項の次に次のように加える。\n'+table(['建国記念日審議会','内閣総理大臣の諮問に応じて建国記念の日となるべき日について調査審議すること。'])+'附則第四項中「附属機関のうち」の下に「、建国記念日審議会は、昭和四十一年十二月十五日まで」を加える。'),
 ('スポーツ振興法の一部改正','スポーツ振興法（昭和三十六年法律第百四十一号）の一部を次のように改正する。\n第五条の見出しを「（体育の日の行事）」に改め、同条第一項及び第二項を削り、同条第三項中「スポーツの日の趣旨にふさわしい事業」を「国民の祝日に関する法律（昭和二十三年法律第百七十八号）第二条に規定する体育の日において、国民の間にひろくスポーツについての理解と関心を深め、かつ、積極的にスポーツをする意欲を高揚するような行事」に改め、同項を同条とする。'),
 ('老人福祉法の一部改正','老人福祉法（昭和三十八年法律第百三十三号）の一部を次のように改正する。\n第五条を次のように改める。\n（敬老の日の行事）\n第五条　国及び地方公共団体は、国民の祝日に関する法律（昭和二十三年法律第百七十八号）第二条に規定する敬老の日において、ひろく国民が老人の福祉についての関心と理解を深め、かつ、老人が自らの生活の向上に努める意欲を高めるような行事が実施されるように努めなければならない。')]
supp='附則'
supp='# 附　則\n'+''.join(f'<!-- loj:paragraph number={i}'+(' caption=present' if cap else '')+' -->\n'+('（'+cap+'）\n' if cap else '')+'１２３４５６'[i-1]+'　'+s+'\n<!-- loj:end-paragraph -->\n' for i,(cap,s) in enumerate(paras,1))
v=repo/'versions'/revision
write(v/'main.md',main);write(v/'supplement.md',supp)
dump(v/'law.yaml',{'schemaVersion':'loj/v1alpha2','law':{'id':repo.name,'title':manifest['label'].split('・')[0],'type':'act','number':'法律第八十六号','promulgatedAt':'1966-06-25','language':'ja'},'unsupportedFeatures':['条を持たない本則と本則直下の改正指示・挿入表（main.md全体）','改正指示に引用された条文と複合改正操作（supplement.md附則第四〜六項）'],'supplements':[{'key':'original','title':'附　則'}],'documents':[{'path':'main.md','parent':'main'},{'path':'supplement.md','parent':'supplement/original'}]})
history={'schemaVersion':'loj-history/v1alpha1','record':{'id':repo.name},'sources':[source],'relations':[],'revisions':[{'id':revision,'origin':'enactment','effective':effective,'applicability':{'state':'unsurveyed'},'text':{'status':'complete','sources':ev('2画像 本則、3画像 附則第一〜三項、4画像 附則第四〜六項'),'glyphCheck':'unverified','correctionsSurveyed':{'state':'unsurveyed','reason':'官報未取得。官報正誤の網羅調査未実施。'}},'status':'active'}],'coverage':{'state':'unconfirmed'}}
dump(repo/'history.yaml',history)
commits=git(repo,'rev-list','--all').splitlines()
dump(repo/'rebuild.yaml',{'schemaVersion':'loj-rebuild/v1alpha1','record':{'id':repo.name},'legacy':{'repository':'https://github.com/law-of-japan/'+repo.name,'frozenAt':snapshot['heads'][repo.name]},'sourceChecks':[{'source':source['id'],'glyphPreservation':'preserved','evidence':ev('1〜5画像'),'note':'全5画像を閲覧。5画像左は次の法律の公布文で対象外。3・4画像には重複があり、4画像右で附則第四・五項を補う。官報未取得のため御署名原本を使用（REB-05）。字体全照合未了。'}],'mappings':[{'commit':c,'revisions':[] if c==snapshot['heads'][repo.name] else [revision],'verification':{'state':'unverified','reason':'旧ブランチのcommitを列挙。全文・字体の完全対応照合は未了。'}} for c in commits],'pending':[],'differences':[]})
reg=root/'loj-registry/records'
r=yaml.safe_load((reg/(repo.name+'.yaml')).read_text(encoding='utf-8'))
r['collection']={'state':'collected'};r['repository']={'location':'github.com/law-of-japan/'+repo.name,'canonicalBranch':'main'}
dump(reg/(repo.name+'.yaml'),r)
specs=[('総理府設置法','昭和二十四年','1949','百二十七','127','附則第四項',['第十五条第一項の表への建国記念日審議会の追加','附則第四項への設置期限の追加']),('スポーツ振興法','昭和三十六年','1961','百四十一','141','附則第五項',['第五条の見出し変更、第一項・第二項削除、第三項改正及び項番号削除']),('老人福祉法','昭和三十八年','1963','百三十三','133','附則第六項',['第五条の全部改正'])]
for rid,(title,era,year,kanji,num,loc,scopes) in zip(ids,specs):
    related=repo/'docs/related'/rid
    rs=copy.deepcopy(source);rs['fixed']='../../sources/manifest.json（同じ試行資料の御署名原本画像）'
    relation={'id':'rel-s41-86','type':'amends','from':{'id':repo.name},'promulgated':prom,'evidence':ev('4画像 '+loc),'verification':confirmed,'status':'active','items':[{'id':'i'+str(i),'scope':{'text':scope},'effective':effective,'evidence':ev('4画像 '+loc),'verification':confirmed} for i,scope in enumerate(scopes,1)]}
    dump(related/'history.yaml',{'schemaVersion':'loj-history/v1alpha1','record':{'id':rid,'label':title},'sources':[rs],'relations':[relation],'revisions':[{'id':uid(8),'origin':'coverageStart','effective':{'state':'unknown','reason':'本文未収録。収録開始時点は未調査。'},'applicability':{'state':'unsurveyed'},'text':{'status':'absent'},'status':'active'}],'coverage':{'state':'unconfirmed'}})
    dump(reg/(rid+'.yaml'),{'schemaVersion':'loj-registry/v1alpha1','id':rid,'label':title,'status':'active','identity':{'evidence':ev('4画像 '+loc),'verification':confirmed},'collection':{'state':'notCollected'},'repository':{'location':related.as_uri(),'canonicalBranch':'trial/amending-act-20261116'},'sources':[rs],'numbers':[{'id':'n1','state':'exists','raw':'法律第'+kanji+'号','structured':{'system':'法律','period':{'raw':era,'gregorian':{'from':year+'-01-01','to':year+'-12-31'}},'series':{'state':'regular'},'number':num},'evidence':ev('4画像 '+loc),'verification':confirmed,'decision':'adopted'}]})
write(repo/'.gitattributes','*.md text eol=lf\n*.py text eol=lf\n*.json text eol=lf\n*.yaml -text\nversions/** -text\ndocs/sources/** -text\n')
print(json.dumps(snapshot,ensure_ascii=False,indent=2))
