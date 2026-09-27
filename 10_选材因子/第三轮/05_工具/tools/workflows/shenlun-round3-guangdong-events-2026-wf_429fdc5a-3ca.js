export const meta = {
  name: 'shenlun-round3-guangdong-events-2026',
  description: '需求五：按月检索2026年1-9月广东重大事件时间线，每月独立复核',
  phases: [
    { title: '月度检索', detail: '9个月，每月一个检索员' },
    { title: '独立复核', detail: '每月一个复核员，重搜一遍报漏报错' },
  ],
}

const BASE = '/Users/jianguolingyun/公考/07_申论/申论/第三轮检索'
const MAT = BASE + '/_素材'

const COMMON = `
【规则 · 必须严格遵守】
1. 原文逐字粘贴，不改字、不删字、不概括。标题照抄，导语第一句照抄。
2. 每条写：日期｜事件｜来源标题｜链接｜是否打开了全文（是/否）。只看到搜索摘要的写"否"。
3. 找不到就写"未找到"。**绝对不要编造标题、链接、日期或原文。**
4. 只用公开来源（广东省政府网 gd.gov.cn、南方日报/南方+、新华社、人民日报、南方网、广东各地市政府网与官方媒体、央视、光明日报、羊城晚报、21世纪经济报道等）。
5. 不许用 WebFetch 取正文——它会把页面过一遍小模型做摘要，拿不到逐字原文。
   正确做法：curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" "<URL>" -o /tmp/p.html
   然后用 python3 去标签取正文（正则剥 <script>/<style>/<[^>]+>，再 html.unescape）。
   打不开就换来源或如实写"否"。
6. https 打不开（证书过期等）时可退回 http 再试，并在文件里注明。
7. 只负责找和贴，不做分析、不评价、不推测命题意图。
`

const MONTHS = [
  ['01', '2026年1月'], ['02', '2026年2月'], ['03', '2026年3月'],
  ['04', '2026年4月'], ['05', '2026年5月'], ['06', '2026年6月'],
  ['07', '2026年7月'], ['08', '2026年8月'], ['09', '2026年9月'],
]

const ROSTER = `【要覆盖的事件类型】
- 广东省委全会、省两会（省人代会/省政协）、省纪委全会
- 全省高质量发展大会（每年新春第一个工作日）
- 省委省政府重要会议、重要政策发布（省政府常务会议发布的重要文件、省政府令）
- 习近平总书记、中央领导对广东的重要讲话、考察、贺信、批示
- 广东承办或主办的重大活动（如2026年APEC相关活动在深圳、广交会、大湾区相关论坛、全运会等）
- 省主要领导（省委书记、省长）的重要调研、出访、会见
- 重大工程项目开工/建成、重大改革举措落地
- 重大自然灾害与应急处置（如有）
`

phase('月度检索')
const results = await pipeline(
  MONTHS,
  ([mm, name]) => agent(
`你是资料检索员，只负责找原文、贴原文，不做分析、不写总结。

【任务】按月列出 ${name} 广东省的重大会议、重大活动、重大政策发布、总书记和中央领导对广东的重要讲话或批示、省委全会（如有）。
日期｜事件｜来源标题｜链接。每条只照抄新闻标题和导语第一句，**不要自己概括**。

${ROSTER}
${COMMON}

【输出】把结果写入 /Users/jianguolingyun/公考/07_申论/申论/第三轮检索/_素材/广东大事_2026_${mm}.md
格式：
# 广东大事_2026_${mm}月

## ${name}
（按日期升序，每条一节）

### <日期 YYYY-MM-DD>
- 事件：<一句话，用官方口径>
- 来源标题：<逐字照抄标题>
- 导语第一句：<逐字照抄>
- 链接：<URL>
- 是否打开了全文：是/否
- 类型：省级会议 / 中央领导讲话 / 重大活动 / 政策发布 / 重大项目 / 其他

## 本月未找到的类别
（列出上面【要覆盖的事件类型】里本月确实没有的，写"本月无"；不确定的写"未查到"，不要猜）

【完成后】返回 JSON，字段：month, file, entries_count, opened_fulltext_count, types_covered(数组), not_found(数组), notes(字符串，写你遇到的困难或不确定处)。`,
    {
      label: `检索:${name}`, phase: '月度检索', agentType: 'general-purpose',
      schema: {
        type: 'object',
        properties: {
          month: { type: 'string' }, file: { type: 'string' },
          entries_count: { type: 'number' }, opened_fulltext_count: { type: 'number' },
          types_covered: { type: 'array', items: { type: 'string' } },
          not_found: { type: 'array', items: { type: 'string' } },
          notes: { type: 'string' },
        },
        required: ['month', 'file', 'entries_count', 'notes'],
      },
    }
  ),
  (r, [mm, name]) => {
    if (!r) return null
    return agent(
`你是复核员。有人交回了一份 ${name} 广东大事清单，存在 ${MAT}/广东大事_2026_${mm}.md。

【你的任务】**独立地**重新检索一遍 ${name} 广东的重大事件，**不要只看他写的那份**。
然后回答三个问题：
1. **漏**：本月广东还有哪些够格进时间线的重大事件，他没写？（尤其查：省委全会/省委常委会、省政府常务会议、省两会相关、中央领导对广东的讲话或批示、省主要领导重要活动、重大政策文件、重大活动）
2. **错**：他写的条目里，有没有日期错、把外省的事当广东的、标题与链接对不上的、或者链接打不开/指向别的内容的？逐条点出。
3. **编**：有没有看起来像编造的标题、链接或日期？**重点查这一条**。用 curl 实际打开每一条链接核对，打不开或内容不符的如实列出。

【反编造核对办法】
- 对每一条，用 curl 打开链接，确认页面里真的有这个标题。
- 抽查不出来的，写"无法核实"。
- 宁可报"无法核实"，也不要放过一条可疑的。

${COMMON}

【输出】返回 JSON。`,
      {
        label: `复核:${name}`, phase: '独立复核', agentType: 'general-purpose',
        schema: {
          type: 'object',
          properties: {
            month: { type: 'string' },
            missing: { type: 'array', items: { type: 'object', properties: { title: { type: 'string' }, date: { type: 'string' }, link: { type: 'string' }, why: { type: 'string' } }, required: ['title', 'why'] } },
            errors: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, problem: { type: 'string' } }, required: ['claim', 'problem'] } },
            fabricated: { type: 'array', items: { type: 'object', properties: { item: { type: 'string' }, evidence: { type: 'string' } }, required: ['item', 'evidence'] } },
            links_checked: { type: 'number' },
            links_broken: { type: 'number' },
            summary: { type: 'string' },
          },
          required: ['month', 'missing', 'errors', 'fabricated', 'links_checked', 'summary'],
        },
      }
    )
  }
)

const ok = results.filter(Boolean)
log(`月度复核完成 ${ok.length}/${MONTHS.length} 个月`)
return {
  months: ok.map(r => ({
    month: r.month,
    漏: (r.missing || []).length, 错: (r.errors || []).length, 疑编造: (r.fabricated || []).length,
    查链接: r.links_checked, 坏链接: r.links_broken,
    summary: r.summary,
  })),
  detail: ok,
}
