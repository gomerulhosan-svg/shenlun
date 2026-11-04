export const meta = {
  name: 'shenlun-round3-central-c6-eco-culture',
  description: '需求三补：生态环境与文化两个领域的中央文件及广东落地',
  phases: [
    { title: '检索', detail: '生态环境 / 文化 各一路' },
    { title: '复核', detail: '链接与编造核查' },
  ],
}

const BASE = '/Users/jianguolingyun/公考/07_申论/申论/第三轮检索'
const MAT = BASE + '/_素材'

const COMMON = `
【规则 · 必须严格遵守】
1. 原文逐字粘贴，不改字、不删字、不概括。导语照抄官方新闻稿，不要自己概括。
2. 每项写：文件名｜发文机关｜印发或施行日期｜链接｜一句话说明（照抄官方新闻稿导语）｜是否打开了全文（是/否）。
3. 找不到就写"未找到"。**绝对不要编造标题、链接、日期或原文。**
4. 只用公开来源（中国政府网 gov.cn、新华社、人民日报、求是网、各部委官网、广东省政府网 gd.gov.cn、南方日报/南方+、南方网、各地市政府网与官方媒体）。
5. **不许用 WebFetch 取正文**——它会把页面过一遍小模型做摘要，拿不到逐字原文。
   正确做法：curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" "<URL>" -o /tmp/p.html
   然后 python3 去标签取正文（正则剥 <script>/<style>/<[^>]+>，再 html.unescape）。
   打不开就换来源或如实写"否"。
6. https 打不开（证书过期等）可退回 http 再试，并在文件里注明。
7. 只负责找和贴，不做分析、不评价命题意图。
8. 时间范围：2025年7月 — 2026年9月。新施行法律法规也算在内。
`

const DOMAINS = [
  {
    code: 'C6',
    title: '生态环境',
    sub: '美丽中国先行区、绿美广东、碳达峰碳中和、污染防治攻坚战、生态保护修复、生物多样性、海洋生态、绿色低碳转型、生态环境法典／相关法规、生态产品价值实现、能耗双控转向碳排放双控',
  },
  {
    code: 'C7',
    title: '文化',
    sub: '文化强国、文化传承发展、中华文明探源、文物保护与考古、非物质文化遗产、文化产业与文化数字化、公共文化服务、文旅融合、全民阅读、网络文化治理、对外文化交流与文明互鉴、《求是》与人民日报关于文化建设的权威文章',
  },
]

phase('检索')
const found = await pipeline(
  DOMAINS,
  (d) => agent(
`你是资料检索员，只负责找原文、贴原文，不做分析、不写总结。

【任务】检索 2025年7月—2026年9月「${d.title}」领域的：
(1) 党中央、国务院、中办国办出台的重要文件；
(2) 国家部委重要文件；
(3) 新制定／新修订并新施行的法律法规。

【本领域重点子题】${d.sub}

【每一项都要写】文件名｜发文机关｜印发或施行日期｜链接｜一句话说明（**照抄官方新闻稿导语，不要自己概括**）｜是否打开了全文（是/否）

【然后逐项查广东落地】对上面每一项，查广东有没有对应的落地文件或报道（省政府、省直部门、地市三级都查）：
- 有广东文件的写：广东文件名｜发文机关｜日期｜链接｜是否打开全文
- 只有报道的写：报道标题｜媒体｜日期｜链接｜是否打开全文
- 没有的写"未查到广东对应落地"

【取原文】对其中最重要、对广东最有针对性的若干项（不少于6项），用 curl 逐字取回原文全文，附在文件末尾「逐字原文」一节。中央文件和广东文件都取。

${COMMON}

【输出】写入 ${MAT}/中央新部署_${d.code}.md
文件开头写：\`# 中央新部署 ${d.code} —— ${d.title}\`

【完成后】返回 JSON。`,
    {
      label: `检索:${d.title}`, phase: '检索', agentType: 'general-purpose',
      schema: {
        type: 'object',
        properties: {
          domain: { type: 'string' }, file: { type: 'string' },
          central_count: { type: 'number' }, gd_landed_count: { type: 'number' },
          fulltext_count: { type: 'number' },
          not_found: { type: 'array', items: { type: 'string' } },
          notes: { type: 'string' },
        },
        required: ['domain', 'file', 'central_count', 'fulltext_count', 'notes'],
      },
    }
  ),
  (r, d) => {
    if (!r) return null
    return agent(
`你是复核员。有人交回了一份「${d.title}」领域的中央文件清单，在 ${MAT}/中央新部署_${d.code}.md。

【你的任务】**独立地**重新检索一遍这个领域，不要只看他写的那份。然后回答：
1. **漏**：2025年7月—2026年9月「${d.title}」领域还有哪些够格的中央重要文件／新施行法规他没写？（重点查：${d.sub}）
2. **错**：他写的条目里，发文机关、日期、文号、链接有没有错的？逐条点出。
3. **编**：**重点查这一条**。用 curl 实际打开每一条链接，确认页面里真的有这份文件和这个标题。打不开、或标题内容对不上的，如实列出。宁可写"无法核实"，也不要放过。

${COMMON}

【输出】返回 JSON。`,
      {
        label: `复核:${d.title}`, phase: '复核', agentType: 'general-purpose',
        schema: {
          type: 'object',
          properties: {
            domain: { type: 'string' },
            missing: { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, issuer: { type: 'string' }, date: { type: 'string' }, link: { type: 'string' }, why: { type: 'string' } }, required: ['name', 'why'] } },
            errors: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, problem: { type: 'string' } }, required: ['claim', 'problem'] } },
            fabricated: { type: 'array', items: { type: 'object', properties: { item: { type: 'string' }, evidence: { type: 'string' } }, required: ['item', 'evidence'] } },
            links_checked: { type: 'number' }, links_broken: { type: 'number' },
            summary: { type: 'string' },
          },
          required: ['domain', 'missing', 'errors', 'fabricated', 'links_checked', 'summary'],
        },
      }
    )
  }
)

const ok = found.filter(Boolean)
log(`生态环境/文化 两路复核完成 ${ok.length}/${DOMAINS.length}`)
return { detail: ok }
