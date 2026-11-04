import json,re,collections,statistics as st
from lib import *
SUR='王李张刘陈杨黄赵吴周徐孙马朱胡郭何高林罗郑梁谢宋唐许韩冯邓曹彭曾肖田董袁潘于蒋蔡余杜叶程苏魏吕丁任沈姚卢姜崔钟谭陆汪范金石廖贾夏韦付方白邹孟熊秦邱江尹薛闫段雷侯龙史陶黎贺顾毛郝龚邵万钱严覃武戴莫孔向汤喻苗阳温麦欧岑'
ANON=[r'(?<![A-Za-z])[A-Z]\s?(?:市|县|区|镇|乡|村|省|公司|企业|集团|科技|电子|银行|街道|社区|园区|学校|大学|医院|基地|合作社|协会|研究院|品牌|产业园)',
      r'某(?:市|县|区|镇|乡|村|公司|企业|集团|科技|电子|银行|街道|社区|园区|学校|大学|医院|基地|单位|部门|机构|平台|品牌|知名|新能源|钢铁|商业|工厂|制造|地)',
      r'(?<![一-鿿])['+SUR+r'](?:先生|女士|经理|教授|博士|研究员|处长|局长|书记|主任|老师|师傅|董事长|厂长|村长|站长|镇长|县长|组长|律师|工程师|总|阿姨|大姐|大哥|伯|叔|姐|哥|老板|支书|副镇长|队长|院长|所长|部长|科长|会长|理事长|同志)',
      r'(?:[一-鿿])['+SUR+r'](?:先生|女士|经理|教授|博士|研究员|处长|局长|书记|主任|老师|师傅|董事长|厂长|村长|站长|镇长|县长|组长|律师|工程师|阿姨|支书|副镇长|队长|院长|所长|部长|科长|会长|理事长)',
      r'(?<![一-鿿])[小老]['+SUR+r'](?![一-鿿]{0,0}[市县镇村])']
REAL=r'广州|深圳|珠海|汕头|佛山|韶关|河源|梅州|惠州|汕尾|东莞|中山|江门|阳江|湛江|茂名|肇庆|清远|潮州|揭阳|云浮|横琴|前海|南沙|河套|香港|澳门|顺德|南海|番禺|龙岗|南山|福田|宝安|从化|增城|惠东|博罗|台山|英德|连州'
DOC=r'《[^》]{2,40}》'
SPEECH=r'(?:说|表示|认为|介绍|坦言|感慨|直言|谈到|感叹道|告诉记者)|：“'
def metrics(text):
    L=len(re.sub(r'\s','',text))
    a=sum(len(re.findall(p,text)) for p in ANON)
    r=len(re.findall(REAL,text)); d=len(re.findall(DOC,text)); s=len(re.findall(SPEECH,text))
    dig=len(re.findall(r'\d+(?:\.\d+)?',text))
    k=1000/L if L else 0
    return dict(L=L,anon=a*k,real=r*k,doc=d*k,speech=s*k,dig=dig*k)
if __name__=='__main__':
    two=[s for s in dict.fromkeys(q['set_id'] for q in qs) if not any(q['set_id']==s and q['q']=='问题三' for q in qs)]
    rows=[]
    for sid in two:
        blocks=json.load(open(f'{B}/_pool/{sid}.json'))['blocks']
        role={}
        for q in qs:
            if q['set_id']!=sid: continue
            for b in q['blocks']: role[b]='Q1' if q['q']=='问题一' else 'Q2'
        for b,paras in blocks.items():
            m=metrics('\n'.join(paras)); m.update(sid=sid,block=b,role=role.get(b,'作文'))
            rows.append(m)
    json.dump(rows,open('anon_rows.json','w'),ensure_ascii=False)
    for r in rows: print(r['sid'],r['block'],r['role'],' '.join('%s=%.1f'%(k,r[k]) for k in['anon','real','doc','speech','dig']),r['L'])
    print()
    for role in['Q1','Q2','作文']:
        rs=[r for r in rows if r['role']==role]
        print(role,len(rs),' '.join('%s=%.2f(med %.2f)'%(k,st.mean(r[k] for r in rs),st.median(r[k] for r in rs)) for k in['anon','real','doc','speech','dig']))
    # per-set rank tests
    print()
    for k in['anon','real','doc','speech']:
        c=collections.Counter()
        for sid in two:
            rs=[r for r in rows if r['sid']==sid]
            ess=[r[k] for r in rs if r['role']=='作文']
            for role in['Q1','Q2']:
                v=[r[k] for r in rs if r['role']==role]
                if not v: continue
                v=st.mean(v)
                c[(role,'>max作文')]+= v>max(ess)
                c[(role,'>med作文')]+= v>st.median(ess)
                c[(role,'<min作文')]+= v<min(ess)
                c[(role,'n')]+=1
        print(k,dict(c))
