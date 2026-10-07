import json, re, sys, html, collections, os
R='/home/user/shenlun/04_文件原文/'
REPS=[('粤26','01_2026广东省政府工作报告.md')]
TXT={}
for tag,f in REPS:
    t=open(R+f,encoding='utf-8').read()
    t=re.sub(r'^(标题|发布|来源|媒体|日期|取法|是否|两来源|通过).*$','',t,flags=re.M)
    t=re.sub(r'[#>*`|]','',t)
    TXT[tag]=t
final=json.load(open(sys.argv[1]))
cands={c['w']:c for c in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'candidates.json')))}
SPECIAL={'……好':r'(?:落实|贯彻|发挥|保障|维护|服务|建设|管理|守护|传承|利用|抓|做|办|用|管|建|当|搞|守|打|走|讲|下|答|干)好(?![处的])',
 '……—……%':r'\d+(?:\.\d+)?%?\s*[—\-－~～至]\s*\d+(?:\.\d+)?%'}
def pat(w):
    if w in SPECIAL: return re.compile(SPECIAL[w])
    parts=[p for p in re.split(r'…+|\.{3,}|——',w) if p]
    if len(parts)>1: return re.compile('[^。；\n]{0,40}?'.join(map(re.escape,parts)))
    return re.compile(re.escape(parts[0] if parts else w))
def counts(w):
    if len(w)==1 and w in cands:
        return {t:cands[w]['by'].get('粤2026',0) for t,_ in REPS}, True
    p=pat(w); return {t:len(p.findall(TXT[t])) for t,_ in REPS}, False
def example(w):
    p=pat(w)
    for t in ['粤26']:
        sents=[c.strip() for c in re.split(r'[。；！？\n]',TXT[t]) if p.search(c)]
        if not sents: continue
        best=None
        for s in sents:
            m=p.search(s)
            cl=[(mm.start(),mm.end()) for mm in re.finditer(r'[^，：]+[，：]?',s)]
            i=next(k for k,(a,b) in enumerate(cl) if a<=m.start()<b)
            j=next((k for k,(a,b) in enumerate(cl) if a<m.end()<=b),i)
            a,b=cl[i][0],cl[j][1]
            while b-a<14 and j+1<len(cl): j+=1; b=cl[j][1]
            while b-a<14 and i>0: i-=1; a=cl[i][0]
            frag=s[a:b].rstrip('，：')
            if len(frag)>56:
                ms=p.search(frag); st=max(0,ms.start()-20); en=min(len(frag),ms.end()+28)
                frag=frag[st:en]; pre='…' if st>0 else ''; post='…' if en<len(s[a:b].rstrip('，：')) else ''
            else:
                pre='…' if a>0 else ''; post='…' if b<len(s) else ''
            cand=(pre+frag+post, s[m.start():m.end()])
            if best is None or abs(len(cand[0])-30)<abs(len(best[0])-30): best=cand
        return t,best[0],best[1]
    return None,'',''
cats=final['categories']; ents=final['entries']
order={c['code']:i for i,c in enumerate(cats)}
bycat=collections.defaultdict(list)
missing=[]
for e in ents:
    cnt,approx=counts(e['w']); e['cnt']=cnt; e['tot']=sum(cnt.values())
    e['ex_src'],e['ex'],e['hit']=example(e['w'])
    if e['tot']==0: missing.append(e['w'])
    bycat[e['cat']].append(e)
unknown=[k for k in bycat if k not in order]
print('entries',len(ents),'cats',len(cats),'zero-count',len(missing),missing[:40],'unknown cats',unknown)

groups=[]
for c in cats:
    if c['group'] not in groups: groups.append(c['group'])
def dots(s):
    return '<span class="dots" title="强度 %d/5">'%s + ''.join('<i class="on"></i>' if i<s else '<i></i>' for i in range(5)) + '</span>' if s else '<span class="dots na" title="不分软硬">—</span>'
def esc(s): return html.escape(s or '')
def exhtml(e):
    if not e['ex']: return ''
    f=esc(e['ex']).replace(esc(e['hit']),'<b>'+esc(e['hit'])+'</b>',1)
    return f'<div class="ex"><span class="src">{e["ex_src"]}</span>{f}</div>'
body=[]; toc=[]
for g in groups:
    toc.append(f'<li class="tg">{esc(g)}<ul>')
    body.append(f'<h2 id="g-{esc(g)}">{esc(g)}</h2>')
    for c in [c for c in cats if c['group']==g]:
        lst=sorted(bycat.get(c['code'],[]),key=lambda e:(-e['strength'],-e['tot']))
        if not lst: continue
        toc.append(f'<li><a href="#c-{esc(c["code"])}">{esc(c["name"])}<span class="n">{len(lst)}</span></a></li>')
        body.append(f'<section class="cat" id="c-{esc(c["code"])}"><h3><span class="code">{esc(c["code"])}</span>{esc(c["name"])}</h3><p class="desc">{esc(c["desc"])}</p><div class="list">')
        for e in lst:
            cn=' · '.join(f'{t} {e["cnt"][t]}' for t,_ in REPS)
            body.append(f'<div class="e" data-k="{esc(e["w"]+" "+e["note"])}"><div class="h"><span class="w">{esc(e["w"])}</span>{dots(e["strength"])}<span class="xu x-{esc(e["xu"])}">{esc(e["xu"])}</span><span class="tot">{e["tot"]} 次</span></div><div class="note">{esc(e["note"])}</div>{exhtml(e)}</div>')
        body.append('</div></section>')
    toc.append('</ul></li>')
N=len(ents)
page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>2026 报告强度词表</title><style>
:root{{--bg:#f4f0e8;--paper:#fffdf8;--ink:#22201c;--ink2:#4a4640;--muted:#8a8378;--rule:#e4ddcf;--accent:#b23a26;--chip:#f1ece2;--soft:#2f5f7f;--hard:#b23a26;
--serif:"Songti SC","STSong","Noto Serif SC","Source Han Serif SC","SimSun",serif;--sans:-apple-system,"PingFang SC","Hiragino Sans GB","Noto Sans SC","Microsoft YaHei",sans-serif}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#17161a;--paper:#1e1d21;--ink:#e8e3da;--ink2:#c9c2b6;--muted:#8f897f;--rule:#34313a;--accent:#e0745e;--chip:#2b2925;--soft:#7fb2d3;--hard:#e0745e}}}}
:root[data-theme="dark"]{{--bg:#17161a;--paper:#1e1d21;--ink:#e8e3da;--ink2:#c9c2b6;--muted:#8f897f;--rule:#34313a;--accent:#e0745e;--chip:#2b2925;--soft:#7fb2d3;--hard:#e0745e}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.7}}
.wrap{{max-width:980px;margin:0 auto;padding:24px 16px 80px}}
h1{{font-family:var(--serif);font-size:28px;margin:8px 0 4px}}h2{{font-family:var(--serif);font-size:22px;margin:40px 0 8px;padding-bottom:6px;border-bottom:2px solid var(--accent)}}
h3{{font-family:var(--serif);font-size:18px;margin:28px 0 2px}}.code{{font-family:var(--sans);font-size:12px;color:var(--muted);margin-right:8px;border:1px solid var(--rule);border-radius:4px;padding:0 5px;vertical-align:2px}}
.intro{{color:var(--ink2);font-size:15px}}.desc{{color:var(--ink2);margin:0 0 10px;font-size:14px}}
.toc{{background:var(--paper);border:1px solid var(--rule);border-radius:10px;padding:12px 16px;margin:16px 0}}.toc ul{{list-style:none;margin:0;padding:0}}.toc>ul>li{{margin:6px 0}}.toc .tg{{font-weight:600;font-family:var(--serif)}}
.toc .tg ul{{display:flex;flex-wrap:wrap;gap:6px;margin-top:4px;font-weight:400;font-family:var(--sans)}}.toc a{{display:inline-block;font-size:13px;color:var(--ink);text-decoration:none;background:var(--chip);border-radius:6px;padding:2px 8px}}.toc .n{{color:var(--muted);margin-left:4px}}
.search{{position:sticky;top:0;z-index:5;background:var(--bg);padding:8px 0}}.search input{{width:100%;font-size:16px;padding:9px 12px;border:1px solid var(--rule);border-radius:8px;background:var(--paper);color:var(--ink)}}
.list{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:10px}}
.e{{background:var(--paper);border:1px solid var(--rule);border-radius:10px;padding:10px 12px;min-width:0}}
.h{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}.w{{font-family:var(--serif);font-size:19px;font-weight:700}}
.dots{{display:inline-flex;gap:3px}}.dots i{{width:8px;height:8px;border-radius:50%;background:var(--rule);display:inline-block}}.dots i.on{{background:var(--accent)}}.dots.na{{color:var(--muted);font-size:12px}}
.xu{{font-size:11px;border-radius:4px;padding:0 5px;border:1px solid var(--rule);color:var(--ink2)}}.tot{{margin-left:auto;font-size:12px;color:var(--muted)}}
.note{{font-size:14px;margin-top:4px}}.cn{{font-size:12px;color:var(--muted);margin-top:4px}}
.ex{{font-family:var(--serif);font-size:13.5px;color:var(--ink2);margin-top:6px;padding-top:6px;border-top:1px dashed var(--rule);overflow-wrap:anywhere}}.ex b{{color:var(--accent)}}.src{{font-family:var(--sans);font-size:11px;color:var(--muted);margin-right:6px}}
.cat,h2{{scroll-margin-top:64px}}.legend{{display:flex;flex-wrap:wrap;gap:14px;font-size:13px;color:var(--ink2);margin:8px 0}}.hide{{display:none}}
</style></head><body><div class="wrap">
<h1>2026 年广东省政府工作报告·强度词表</h1>
<p class="intro">从 2026 年广东省政府工作报告里收的表示力度、决心、急迫和留余地的词，共 {N} 个，实词、虚词和固定说法都有。同一件事，换一个这里的词，读的人就该读出力度变了。</p>
<div class="legend"><span><span class="dots"><i class="on"></i><i></i><i></i><i></i><i></i></span> 1 最软，还在研究、留着余地</span><span><span class="dots"><i class="on"></i><i class="on"></i><i class="on"></i><i></i><i></i></span> 3 常规推进</span><span><span class="dots"><i class="on"></i><i class="on"></i><i class="on"></i><i class="on"></i><i class="on"></i></span> 5 最硬，必须做到</span><span>— 只表范围或比较，不分软硬</span></div>
<p class="intro" style="font-size:13px">每个词右上角是它在报告里出现的次数，按字面数，个别词会把组成别的名词的情况也算进去（比如“基本公共服务”里的“基本”），只看相对多少。例句都是报告原文；同一类里按强度从硬到软、再按次数从多到少排。实词、虚词按《现代汉语》（黄廖本）分：副词算虚词，“要”“需要”这类能愿动词算实词，几个词拼成的格式标作短语。</p>
<nav class="toc"><ul>{''.join(toc)}</ul></nav>
<div class="search"><input id="q" type="search" placeholder="搜词或说明，如：稳妥、留余地、底线"></div>
{''.join(body)}
</div><script>
const q=document.getElementById('q');q.addEventListener('input',()=>{{const v=q.value.trim();document.querySelectorAll('.e').forEach(e=>{{e.classList.toggle('hide',v&&!e.dataset.k.includes(v))}});document.querySelectorAll('.cat').forEach(s=>{{s.classList.toggle('hide',v&&!s.querySelector('.e:not(.hide)'))}})}});
</script></body></html>'''
open(sys.argv[2],'w',encoding='utf-8').write(page); print('wrote',sys.argv[2])
