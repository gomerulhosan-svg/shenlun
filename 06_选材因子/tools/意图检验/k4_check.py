import re, os, sys, itertools, random
from math import comb
os.chdir('/home/user/shenlun')
P = '10_选材因子/溯源结果/页面快照/'
FILES = {
 2021: P+'_cache_2022乡镇/母文件_2021年广东省政府工作报告_eesia.txt',
 2022: P+'_cache/2022年广东省政府工作报告.txt',
 2023: P+'_cache/2023年广东省政府工作报告.txt',
 2024: P+'_cache/2024_政府工作报告_eesia.txt',
 2025: P+'_cache/2025年广东省政府工作报告_163.txt',
 2026: P+'_cache/2026年广东省政府工作报告_163.txt',
}
def norm(s): return re.sub(r'[\s　“”"‘’「」]', '', s)
SEC={}; FULL={}
for y,f in FILES.items():
    t=norm(open(f,encoding='utf-8',errors='ignore').read()); FULL[y]=t
    m=re.search(r'[一二三四五六]、%d年工作安排'%y,t); s=m.end()
    e=min([i for i in (t.find('各位代表',s+3000),t.find('附件',s+3000)) if i>0] or [len(t)])
    SEC[y]=t[s:e]
# A Fisher one-sided 6/9 vs 7/33
def fisher_greater(a,b,c,d):
    n1=a+b; n2=c+d; k=a+c; N=n1+n2
    p=0
    for x in range(a, min(n1,k)+1):
        p+=comb(n1,x)*comb(n2,k-x)/comb(N,k)
    return p
print('A. v1 Fisher 单侧 6/9 vs 7/33: p=%.4f'%fisher_greater(6,3,7,26))
# counts
for w in ['零碳园区','古树名木','绿色工厂','红树林','海洋牧场','土特产','强化企业科技创新主体地位','百县千镇万村高质量发展工程','产业科技创新']:
    print('  %s 各年工作安排出现次数:'%w, {y:SEC[y].count(w) for y in SEC}, ' 2025全文:',FULL[2025].count(w))

print('\n2024 全文 海洋牧场:',FULL[2024].count('海洋牧场'),' 2024 全文长度',len(FULL[2024]),' 各年全文长度',{y:len(FULL[y]) for y in FULL})
# B. core objects (v1 list, excluding no-object)
src=open('10_选材因子/tools/report_baseline.py',encoding='utf-8').read()
Q=eval(src[src.index('Q = [')+4: src.index(']\nfrom collections')+1])
NEAR={'2022':2021,'2023':2023,'2024':2024,'2025':2025,'2026':2025}
rows=[]
for sid,q,grp,obj,near,_ in Q:
    y=sid[:4]
    if y not in NEAR or obj.startswith('（'): continue
    rows.append((sid,q,obj,NEAR[y],{ry:(obj in SEC[ry]) for ry in SEC}))
post=[r for r in rows if r[0][:4] in('2025','2026')]
print('\nB. 9 道"发布后"题：2025报告命中 %d/9；2026报告（2026-01发布，晚于两年所有考试）命中 %d/9；2024报告命中 %d/9'%(
  sum(r[4][2025] for r in post), sum(r[4][2026] for r in post), sum(r[4][2024] for r in post)))
for r in post: print('   ',r[0],r[1],r[2],'2024:',int(r[4][2024]),'2025:',int(r[4][2025]),'2026:',int(r[4][2026]))
# C. permutation / conditional test: under null, nearest report is exchangeable with the other 5
def cond_test(rr,label):
    obs=sum(r[4][r[3]] for r in rr)
    # exact distribution: each question contributes Bernoulli(k_i/6) independently
    ps=[sum(r[4].values())/6 for r in rr]
    # exact via DP
    dist=[1.0]
    for p in ps:
        nd=[0]*(len(dist)+1)
        for i,v in enumerate(dist):
            nd[i]+=v*(1-p); nd[i+1]+=v*p
        dist=nd
    pval=sum(dist[obs:])
    print('C. %s: 观测最近报告命中 %d/%d；零假设期望 %.2f；单侧 p=%.3f'%(label,obs,len(rr),sum(ps),pval))
cond_test(rows,'全部27题（六份报告可交换）')
rr=[r for r in rows if r[0][:4] in('2024','2025','2026')]
cond_test(rr,'2024–26 共13题')
cond_test(post,'2025–26 共9题')
ss=[r for r in rows if '省市' in r[0] or '一卷' in r[0] or '二卷' in r[0]]
cond_test(ss,'省市/一卷/二卷 共%d题'%len(ss))
# restricted null: only reports within ±2 years of nearest, which have similar "policy era"
def cond_test_window(rr,label,w=1):
    obs=0; exp=0; ps=[]
    for r in rr:
        ys=[y for y in SEC if abs(y-r[3])<=w]
        k=sum(r[4][y] for y in ys); p=k/len(ys); ps.append(p); obs+=r[4][r[3]]
    dist=[1.0]
    for p in ps:
        nd=[0]*(len(dist)+1)
        for i,v in enumerate(dist): nd[i]+=v*(1-p); nd[i+1]+=v*p
        dist=nd
    print('C\'. %s（只和最近报告±%d年比）: 观测 %d，期望 %.2f，单侧 p=%.3f'%(label,w,obs,sum(ps),sum(dist[obs:])))
cond_test_window(rr,'2024–26 共13题',1)
cond_test_window(post,'2025–26 共9题',1)
cond_test_window(rows,'全部27题',1)

# D. baseline: quoted terms in the same papers' materials
print()
def materials(sid):
    t=open('10_选材因子/溯源包/%s_材料与题干.md'%sid,encoding='utf-8').read()
    a=t.index('### 给定材料'); b=t.index('### 题干') if '### 题干' in t else len(t)
    return t[a:b]
tot_hit=0; tot=0
per={}
for sid in ['2024一卷','2024二卷','2024选调','2025省市','2025县镇','2025选调','2026省市','2026县镇','2023县级','2023乡镇','2022县级','2022乡镇']:
    m=materials(sid)
    terms=set(x for x in re.findall(r'“([^”]{2,10})”',m) if not re.search(r'[，。、；：！？,.\s（）()《》]',x))
    y=NEAR[sid[:4]]
    hits=[x for x in terms if norm(x) in SEC[y]]
    other=[sum(norm(x) in SEC[ry] for x in terms)/max(len(terms),1) for ry in SEC if ry!=y]
    per[sid]=(len(hits),len(terms))
    print('D. %-8s 材料引号词 %3d 个，命中最近(%d)报告 %3d = %4.0f%%；其他各年平均 %4.0f%%  例：%s'%(sid,len(terms),y,len(hits),100*len(hits)/max(len(terms),1),100*sum(other)/len(other),'、'.join(sorted(hits)[:12])))

print()
ALT=[('2025省市问题二','科技成果转化'),('2025省市问题二','成果转化'),('2025县镇问题二','农业科技'),('2025县镇问题二','科技兴农'),('2025县镇问题一','荔枝'),
     ('2025选调问题一','金树林'),('2024选调问题一','返乡'),('2024选调问题一','下乡'),('2024选调问题一','青年'),('2023县级问题一','广东制造'),('2023县级问题一','质量强省'),('2023县级问题一','品牌'),
     ('2023县级问题二','制造业高质量发展'),('2022县级问题二','文化交流'),('2023乡镇问题三','积分'),('2026省市问题一','绿色制造'),('2026县镇问题二','古树'),
     ('2025省市问题一','科技创新主体'),('2021县级问题一','数字政府'),('2020县级问题一','社会治理')]
for q,w in ALT:
    print('E. %-14s %-10s'%(q,w),' '.join('%d:%s'%(y,'●' if w in SEC[y] else '·') for y in SEC))

print()
for y in (2025,2026):
    sents=[s for s in re.split(r'[。；]',SEC[y]) if len(s)>=6]
    prev=''.join(FULL[z] for z in FULL if z<y)
    prev1=FULL[y-1]
    def newgrams(s,ref,n=5):
        g=[s[i:i+n] for i in range(len(s)-n+1) if re.fullmatch(r'[一-鿿]{%d}'%n,s[i:i+n])]
        return [x for x in g if x not in ref]
    nnew_all=sum(1 for s in sents if len(newgrams(s,prev))>=3)
    nnew_1=sum(1 for s in sents if len(newgrams(s,prev1))>=3)
    print('F. %d 工作安排：句/分号段 %d 个；含≥3个此前所有报告都没有的5字串的 %d 个；相对上一年报告含≥3个新5字串的 %d 个'%(y,len(sents),nnew_all,nnew_1))

print()
rr=[r for r in rows if r[0][:4] in('2024','2025','2026')]
first=lambda r: min([y for y in r[4] if r[4][y]] or [9999])
rules={
 '最近报告里有':lambda r:r[4][r[3]],
 '最近报告里有且上一年报告没有（K4"新增"）':lambda r:r[4][r[3]] and not r[4].get(r[3]-1,False),
 '最近报告是首次出现（严格新）':lambda r:r[4][r[3]] and first(r)==r[3],
 '最近或上一份报告里有（两份并集）':lambda r:r[4][r[3]] or r[4].get(r[3]-1,False),
}
for k,f in rules.items():
    hit=[r[0]+r[1]+r[2] for r in rr if f(r)]
    print('G. %-28s 回溯召回 %d/13  %s'%(k,len(hit),'；'.join(hit)))
