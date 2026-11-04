export const meta = {
  name: 'shenlun-reason-library',
  description: '为广东申论大作文建一本道理库，并用真题、仿真卷和预测题测覆盖率',
  phases: [
    { title: 'Mine', detail: '6 路从大方向解读和大词卡挖候选道理' },
    { title: 'Merge', detail: '只合并同一个机制，不设条数上限' },
    { title: 'Verify', detail: '逐批查真、稳，再查锚、白' },
    { title: 'Forecast', detail: '预测 12 道今年可能的作文题' },
    { title: 'Derive', detail: '每道题独立列出需要的道理，一个代理 3 道' },
    { title: 'Match', detail: '拿道理库对每条需要判命中，一个代理 4 道' },
    { title: 'Patch', detail: '补缺、复核、重判' },
    { title: 'Critic', detail: '找漏并补最后几条' },
  ],
}

const CTX = `背景：一位考生在备考 2026 年 12 月 7 日的广东省考申论。仓库在 /home/user/shenlun，只读，不要改任何文件，不要 commit。他的大作文改走"直觉流"：先用大白话想明白广东在这件事上真正卡在哪、为什么这么干，再用材料里的事实写出来。他没时间把大白话翻成考场上能写的句子，所以我们替他做一本"道理库"：几十条能反复用的真道理，每条是一句考场能写的白描句。三条标准：
- 真：站在省里的位置看是真实的因果；材料承认代价时要写代价。不能把上电视的样板当普遍规律（"工厂变绿订单反而多了"是假道理，"绿色是门槛，跨过去的企业更有竞争力"才是真的）。
- 稳：观点正确，和中央、省委的提法一致，语气适合申论，不讥讽、不发牢骚。
- 白：一句只说一件事，名词具体，有因果就把"才""所以"写出来，不堆虚词，不喊口号，不超过 32 个字。
- 代价：只算省委在大会上会讲的那一层难处（如"环境承载力逼近极限""资源要素从乡村向城市净流出的局面尚未扭转"），操作层面的难处（申请繁琐、巡山危险）不算。`

const THEMES = `主题表（来自仓库的《大词卡》）：1 走在前列/挑大梁/1310 具体部署；2 高质量发展/新发展理念；3 新质生产力/高水平科技自立自强/产业科技互促双强；4 现代化产业体系/制造业当家/两业协同；5 人工智能+/数字广东；6 扩大内需/新发展格局/全国统一大市场/投资于物和投资于人；7 全面深化改革/有效市场和有为政府/营商环境/放得活管得好；8 高水平对外开放/粤港澳大湾区/制度型开放；9 百千万工程/乡村全面振兴/城乡融合/县域经济；10 海洋强省/海上新广东；11 绿色发展/绿美广东/双碳；12 文化强省/文化创新创造/岭南文化；13 保障和改善民生/共同富裕/基本公共服务均等化/投资于人；14 统筹发展和安全/法治广东/平安广东；15 城市高质量发展/人民城市/城市更新。`

const PAST = `历年广东省考大作文题：2020 县级"推进国家治理体系和治理能力现代化，推动新时代广东改革发展走在全国前列"；2021 县级"站在新起点，迈向新征程，推动广东高质量发展"；2022 县级"粤港澳大湾区建设取得的实效和经验"；2023 县级策论"把广东制造业这份厚实家当做优做强"；2024 一卷"高水平科技自立自强"（引语：是中国式现代化建设的关键）；2024 二卷"'百千万工程'是广东推动高质量发展的头号工程"；2025 省市"继续做好创新这篇大文章"；2025 县镇"乡村振兴关键在产业振兴"；2026 省市"绿色发展是高质量发展的底色"；2026 县镇"绿美广东生态建设是关系广东长远发展和民生福祉的重要工程"。选调：2024"堪当民族复兴重任的时代新人"，2025"广东全面推进海洋强省建设"，2026"激活文化创新创造活力"。`

const DIR = '/home/user/shenlun/01_大方向解读/'
const CARD = '/home/user/shenlun/04_文件原文/00_大词卡.md'
const MINERS = [
  { name: '通用，加干部和党建', files: DIR + '00_总入口.md、' + DIR + '00_五条线_看懂中国的政治.md、' + DIR + '干部和党建/ 下 3 个文件，以及 /home/user/shenlun/04_文件原文/01_2026广东省政府工作报告.md 第 51 行（"同时我们清醒地看到"那一段）', cards: '43—258 行（第 1、2 张卡）', n: '14—18' },
  { name: '产业体系，加新基建和人工智能', files: DIR + '产业体系/ 下 7 个文件、' + DIR + '新基建和人工智能/ 下 3 个文件', cards: '259—522 行（第 3、4、5 张卡）', n: '12—16' },
  { name: '大湾区和开放、改革，加扩内需', files: DIR + '大湾区和开放/ 下 6 个文件、' + DIR + '扩内需/ 下 5 个文件', cards: '523—655 行（第 6、7、8 张卡）', n: '12—16' },
  { name: '民生（一老一小、上学、看病、饭碗和兜底），加城市', files: DIR + '民生/ 下的 00_总览.md、一老一小.md、上学.md、看病.md、饭碗和兜底.md，以及 ' + DIR + '城市/ 下 6 个文件', cards: '910—980 行和 1051—1103 行（第 13、15 张卡）', n: '12—16' },
  { name: '民生（绿美、绿色转型、文化），加海洋', files: DIR + '民生/ 下的 绿美的山和水.md、绿色转型.md、文化.md，以及 ' + DIR + '海洋/ 下 5 个文件', cards: '711—909 行（第 10、11、12 张卡）', n: '12—16' },
  { name: '法治平安，加百千万', files: DIR + '法治平安/ 下 7 个文件、' + DIR + '百千万/ 下 7 个文件', cards: '656—710 行和 981—1050 行（第 9、14 张卡）', n: '12—16' },
]

const T = '/home/user/shenlun/03_真题/文本/'
const S = '/home/user/shenlun/02_仿真卷/'
const TESTS = [
  { key: 'R2020', set: '真题', title: '推进国家治理体系和治理能力现代化，推动新时代广东改革发展走在全国前列', path: T + '2020_县级卷.txt' },
  { key: 'R2021', set: '真题', title: '站在新起点，迈向新征程，推动广东高质量发展', path: T + '2021_县级卷.txt' },
  { key: 'R2022', set: '真题', title: '粤港澳大湾区建设取得的实效和经验', path: T + '2022_县级卷.txt' },
  { key: 'R2023', set: '真题', title: '把广东制造业这份厚实家当做优做强（策论文）', path: T + '2023_县级卷.txt' },
  { key: 'R2024A', set: '真题', title: '高水平科技自立自强（引语：是中国式现代化建设的关键）', path: T + '2024_一卷.txt' },
  { key: 'R2024B', set: '真题', title: '"百千万工程"是广东推动高质量发展的头号工程', path: T + '2024_二卷.txt' },
  { key: 'R2025A', set: '真题', title: '继续做好创新这篇大文章', path: T + '2025_省市卷.txt' },
  { key: 'R2025B', set: '真题', title: '乡村振兴关键在产业振兴', path: T + '2025_县镇卷.txt' },
  { key: 'R2026A', set: '真题', title: '绿色发展是高质量发展的底色', path: T + '2026_省市卷.txt' },
  { key: 'R2026B', set: '真题', title: '绿美广东生态建设是关系广东长远发展和民生福祉的重要工程', path: T + '2026_县镇卷.txt' },
  { key: 'X2024', set: '选调', title: '堪当民族复兴重任的时代新人', path: T + '2024_选调.txt', note: '这份文本的材料可能有拼错的地方，以题干和读得通的材料为准。' },
  { key: 'X2025', set: '选调', title: '广东全面推进海洋强省建设', path: T + '2025_选调.txt' },
  { key: 'X2026', set: '选调', title: '激活文化创新创造活力', path: T + '2026_选调.txt' },
  { key: 'S1', set: '仿真', title: '努力将科研创造力转化为现实生产力', path: S + '第1套_科技产业融合/试卷.md' },
  { key: 'S2', set: '仿真', title: '以全面深化改革开放推动高质量发展', path: S + '第2套_改革开放/试卷.md' },
  { key: 'S3', set: '仿真', title: '城市发展正从大规模增量扩张阶段转向存量提质增效为主的阶段', path: S + '第3套_城市/试卷.md' },
  { key: 'S4', set: '仿真', title: '高效开发利用海洋，推动海洋经济高质量发展', path: S + '第4套_海洋/试卷.md' },
  { key: 'S5', set: '仿真', title: '推动更多公共服务向基层下沉、向农村覆盖、向边远地区和生活困难群众倾斜', path: S + '第5套_公共服务/试卷.md' },
  { key: 'S6', set: '仿真', title: '一体推进兴业、强县、富民', path: S + '第6套_百千万/试卷.md' },
  { key: 'S7', set: '仿真', title: '形成既"放得活"又"管得好"的经济秩序', path: S + '第7套_营商环境与改革/试卷.md' },
]

const STR = { type: 'string' }
const STRS = { type: 'array', items: { type: 'string' } }
const INTS = { type: 'array', items: { type: 'integer' } }
const CAND_SCHEMA = { type: 'object', properties: { candidates: { type: 'array', items: { type: 'object', properties: { reason: STR, hook: STR, mechanism: STR, themes: INTS, signals: STRS, anchor: STR, anchor_source: STR, cost: { type: 'boolean' }, limit: STR }, required: ['reason', 'hook', 'mechanism', 'themes', 'signals', 'cost', 'limit'] } } }, required: ['candidates'] }
const ENTRY_PROPS = { id: STR, group: STR, core: { type: 'boolean' }, reason: STR, hook: STR, mechanism: STR, themes: INTS, signals: STRS, anchor: STR, anchor_source: STR, cost: { type: 'boolean' }, limit: STR }
const LIB_SCHEMA = { type: 'object', properties: { entries: { type: 'array', items: { type: 'object', properties: ENTRY_PROPS, required: ['id', 'group', 'core', 'reason', 'hook', 'mechanism', 'themes', 'signals', 'cost', 'limit'] } }, note: STR }, required: ['entries'] }
const VA_SCHEMA = { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: { id: STR, verdict: { type: 'string', enum: ['keep', 'fix', 'drop'] }, reason: STR, limit: STR, why: STR }, required: ['id', 'verdict', 'why'] } } }, required: ['items'] }
const VB_SCHEMA = { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: { id: STR, verdict: { type: 'string', enum: ['keep', 'fix'] }, reason: STR, hook: STR, signals: STRS, anchor: STR, anchor_source: STR, anchor_found: { type: 'boolean' }, why: STR }, required: ['id', 'verdict', 'anchor_found'] } } }, required: ['items'] }
const FORECAST_SCHEMA = { type: 'object', properties: { prompts: { type: 'array', items: { type: 'object', properties: { prompt: STR, type: STR, level: STR, why: STR, docs: STRS }, required: ['prompt', 'type', 'level', 'why', 'docs'] } } }, required: ['prompts'] }
const NEEDS_SCHEMA = { type: 'object', properties: { needs: { type: 'array', items: { type: 'object', properties: { role: { type: 'string', enum: ['开头', '段', '代价'] }, point: STR, reason: STR, evidence: STR }, required: ['role', 'point', 'reason', 'evidence'] } } }, required: ['needs'] }
const DERIVE_SCHEMA = { type: 'object', properties: { results: { type: 'array', items: { type: 'object', properties: { key: STR, needs: NEEDS_SCHEMA.properties.needs }, required: ['key', 'needs'] } } }, required: ['results'] }
const PROPOSAL = { type: 'object', properties: { reason: STR, hook: STR, mechanism: STR, themes: INTS, signals: STRS, cost: { type: 'boolean' }, limit: STR } }
const MATCH_SCHEMA = { type: 'object', properties: { results: { type: 'array', items: { type: 'object', properties: { key: STR, needs: { type: 'array', items: { type: 'object', properties: { idx: { type: 'integer' }, verdict: { type: 'string', enum: ['hit', 'partial', 'miss'] }, ids: STRS, note: STR, cue_ok: { type: 'boolean' }, proposal: PROPOSAL }, required: ['idx', 'verdict', 'ids', 'note', 'cue_ok'] } } }, required: ['key', 'needs'] } } }, required: ['results'] }
const RECHECK_SCHEMA = { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: { key: STR, idx: { type: 'integer' }, verdict: { type: 'string', enum: ['hit', 'partial', 'miss'] }, ids: STRS, note: STR }, required: ['key', 'idx', 'verdict', 'ids', 'note'] } } }, required: ['items'] }

const J = x => JSON.stringify(x)
const chunk = (arr, n) => { const out = []; for (let i = 0; i < arr.length; i += n) out.push(arr.slice(i, i + n)); return out }
const compact = es => es.map(e => ({ id: e.id, reason: e.reason, hook: e.hook, themes: e.themes, signals: e.signals }))

const minePrompt = m => `${CTX}

你负责挖：${m.name}。两块都要挖到。
读：${m.files}。每个文件夹的 00_总览 全读；其余文件先用 grep '^#' 看小节标题，挑讲"为什么、卡在哪、难在哪、代价"的小节读，不必通读。再读大词卡 ${CARD} 的 ${m.cards}，只看"一句话""落点词""下面分几块""道理句""2026 年新提法"，跳过"考过没有"。不要读 03_真题/、02_仿真卷/、05_做题复盘/ 下的任何东西。

产出 ${m.n} 条候选道理。每条讲一个机制：为什么这件事非做不可，或者它靠什么起作用，或者它难在哪、代价是什么；不讲做了什么、成绩多大。优先：(1) 能挂在好几个主题上的；(2) 大方向解读里反复出现的硬道理（便宜用完了、门窄了、每块地上都有人、人比楼慢、明天谁来养、老规矩管不了新东西、新机会落在两翼和县）；(3) 至少两条讲代价或难处。

字段：
- reason：考场句，白描，不超过 32 字。
- hook：记忆钩子，不超过 16 字，大白话，可以糙但不带脏字，最好是考生自己会冒出来的那种话。
- mechanism：为什么成立，一句大白话，不超过 50 字。
- themes：适用的主题编号（见下表，可多个）。
- signals：2—5 个信号词：题干或材料里出现这些说法或现象，就该想到这条。用材料里常见的说法，如"守着青山绿水饿肚子""积极性不高""建成后没人管""卡脖子""短板在县"。
- anchor：支撑它的一句原文，必须是 /home/user/shenlun/04_文件原文/ 或 /home/user/shenlun/01_大方向解读/ 里逐字存在的话（用 grep 核对过），没有就留空，绝不编。
- anchor_source：文件路径:行号。
- cost：这条是不是讲代价或难处。
- limit：什么时候别用、别说过头，不超过 30 字。

${THEMES}`

const mergePrompt = cands => `${CTX}

下面是 6 个人从大方向解读和大词卡里挖出来的 ${cands.length} 条候选道理（JSON）。把它们合并成一本道理库。条数不设上限，不要压缩：只有讲同一个机制、而且说法的意象也一样的，才合成一条。意思相近但意象不同的分开留，比如"生态环境是长远发展的最大本钱"和"生态是发展的根基"：本钱有能拿来生利、亏了就没了的意思，根基没有，所以是两条。每条在 limit 里写清它和相近那条的区别（预计 60—100 条）：
- 讲同一个机制、意象也一样的合成一条，挑最白、最准的说法；themes 和 signals 取并集；anchor 留一条核对过的。
- group：写"通用"（能挂 4 个以上主题的硬道理），或者写主题编号，如"11"。
- 每个主题（1—15）至少有 3 条能用（算上通用的）；讲代价或难处的（cost=true）至少 10 条。
- core=true 标出最常用的 20 条左右，考生先背这些。
- id：通用的用 T01、T02……；主题的用"主题号-序号"，如 11-1、11-2。
- reason 不超过 32 字，hook 不超过 16 字。不要新增候选里没有的机制，可以改写措辞。
- note：用两三句话说明这本库是怎么组织的。

${THEMES}

候选：${J(cands)}`

const lensA = b => `${CTX}

你是挑刺的阅卷老师，专查"真"和"稳"。逐条检查下面这批道理（JSON）：
- 真：站在广东省的位置看，这个因果是不是真的？有没有把样板说成普遍、说过头（"决定""唯一""一定""全部"）、倒因为果？和现实对不对得上（可以查 /home/user/shenlun/01_大方向解读/ 里对应的文件）？
- 稳：观点正确吗？和中央、省委的提法一致吗？语气适合申论吗？有没有讥讽、发牢骚、否定政策方向，或考场上不宜写的说法？
- 用：阅卷人会把它当成一个理由，还是只当成口号？
每条给 verdict：keep（没问题）；fix（给出改好的 reason 和 limit，reason 仍不超过 32 字、白描）；drop（站不住或不宜写）。why 写一句理由。

这批：${J(b)}`

const lensB = b => `${CTX}

你专查"锚"和"白"。逐条处理下面这批道理（JSON）：
- 锚：用 grep 在 /home/user/shenlun/04_文件原文/ 和 /home/user/shenlun/01_大方向解读/ 里核对 anchor 是否逐字存在、行号对不对。不对就改正；找不到就另找一句真实存在、能支撑这条的原文（优先中央和省委文件），填进 anchor 和 anchor_source；还是找不到，anchor_found=false。绝不编造引文。
- 白：reason 是不是一句只说一件事、不超过 32 字、没有虚词堆砌？hook 是不是不超过 16 字、像人话、好记？signals 是不是材料里真会出现的说法？不合格就改，意思不能变；原句里的比喻和意象词（本钱、根基、底色、门槛之类）要保留，不要换成别的近义比喻。
每条给 verdict（keep/fix）、anchor_found，以及改过的字段。

这批：${J(b)}`

const forecast1 = () => `${CTX}

你来预测 2026 年 12 月 7 日那场（2027 年度）广东省考申论的大作文题。${PAST} 规律：题目都是广东省委当年的重点工作；近三年省市卷、县镇卷各一题，多为关系型（"A 是 B 的底色/关键/头号工程""A 关系 B1 和 B2"），也有任务型（"做好 A"）。

读这些（看标题、开头和核心段落即可）：/home/user/shenlun/04_文件原文/ 下文件名以 M 开头的、N31—N54 开头的、01_2026广东省政府工作报告.md，以及 ${CARD} 每张卡里的"2026 年新提法"。不要读 03_真题/、02_仿真卷/、05_做题复盘/。

给出 6 道最可能的题：省市卷 3 道、县镇卷 3 道。写成真题题干的样子，可以带一句总书记或省委的引语；主题尽量不和 2024—2026 年已经考过的重复。每道写：prompt；type（关系型/任务型）；level（省市/县镇）；why（为什么可能考，引 1—2 个文件）；docs（命题人最可能取材的 2—4 个文件的完整路径）。`

const forecast2 = l1 => `${CTX}

同一件事，你来补充预测 2026 年 12 月 7 日那场广东省考申论的大作文题。${PAST}
已有 6 道：${J(l1.map(f => f.prompt))}
读 /home/user/shenlun/04_文件原文/ 下 N01—N30 开头的文件（2026 年中央文件和讲话），以及 04_中共中央关于制定十五五规划的建议.md、07_2026年国务院政府工作报告.md 的相关部分。不要读 03_真题/、02_仿真卷/、05_做题复盘/。
再给 6 道和已有主题不同的题：省市卷 3 道、县镇卷 3 道，字段同上（prompt、type、level、why、docs，docs 写完整路径）。`

const derivePrompt = t => `${CTX}

你来给一道作文题列"需要哪些道理"，当作测试道理库的标准。题：${t.title}（${t.set}）。读题干和全部给定材料：${t.path}，作文题在末尾。${t.note || ''}不要读答案、范文、复盘或道理库，也不要读 /home/user/shenlun/05_做题复盘/ 和 /home/user/shenlun/03_真题/答案_以此为准/。

想清楚：一篇论证严密的好作文，开头要立什么理，每个分论点段的第二句（"凭什么"）要放什么道理，哪里该写一句代价或难处。只写道理：为什么、靠什么起作用、难在哪。不写口号、引语、成绩。以材料自己的逻辑为准，材料承认的代价也算。策论文也一样，每一招背后"为什么要这么做"就是需要的道理。

给 4—6 条，每条：role（开头/段/代价）；point（这一处要论证什么，不超过 30 字）；reason（需要的那个道理，大白话，不超过 40 字）；evidence（材料几第几段里能撑它的事实或原话，不超过 40 字）。`

const deriveForecastPrompt = t => `${CTX}

你来给一道预测作文题列"需要哪些道理"，当作测试道理库的标准。题：${t.title}（${t.level}，${t.type}）。命题人可能取材的文件：${(t.docs || []).join('、')}。只读这些文件；路径不对就在 /home/user/shenlun/04_文件原文/ 里找同名文件。不要读 /home/user/shenlun/01_大方向解读/、03_真题/、02_仿真卷/、05_做题复盘/。

想清楚：一篇论证严密的好作文，开头要立什么理，每个分论点段的第二句（"凭什么"）要放什么道理，哪里该写一句代价或难处。只写道理：为什么、靠什么起作用、难在哪。不写口号、引语、成绩。

给 4—6 条，每条：role（开头/段/代价）；point（不超过 30 字）；reason（大白话，不超过 40 字）；evidence（文件里能撑它的原话，不超过 40 字，注明文件）。`

const deriveBatchPrompt = ts => `${CTX}

你来给 ${ts.length} 道作文题分别列"需要哪些道理"，当作测试道理库的标准。每道题单独想，不要互相借。
${ts.map(t => t.set === '预测'
  ? `- ${t.key}：${t.title}（预测题，${t.level}，${t.type}）。命题人可能取材的文件：${(t.docs || []).join('、')}。只读这些文件；路径不对就在 /home/user/shenlun/04_文件原文/ 里找同名文件。`
  : `- ${t.key}：${t.title}（${t.set}）。读题干和全部给定材料：${t.path}，作文题在末尾。${t.note || ''}`).join('\n')}

不要读答案、范文、复盘或道理库：不读 /home/user/shenlun/05_做题复盘/ 和 /home/user/shenlun/03_真题/答案_以此为准/；预测题也不读 /home/user/shenlun/01_大方向解读/。

每道题都想清楚：一篇论证严密的好作文，开头要立什么理，每个分论点段的第二句（"凭什么"）要放什么道理，哪里该写一句代价或难处。只写道理：为什么、靠什么起作用、难在哪。不写口号、引语、成绩。以材料自己的逻辑为准，材料承认的代价也算。策论文也一样，每一招背后"为什么要这么做"就是需要的道理。

每道题给 4—6 条，每条：role（开头/段/代价）；point（这一处要论证什么，不超过 30 字）；reason（需要的那个道理，大白话，不超过 40 字）；evidence（材料或文件里能撑它的事实或原话，不超过 40 字，注明出处）。results 里每道题写 key 和 needs。`

const matchPrompt = (tests, lib) => `${CTX}

你来测道理库的覆盖。道理库（JSON，每条 id/reason/hook/themes/signals）：${J(lib)}

下面是 ${tests.length} 道题各自需要的道理（JSON）：${J(tests)}

对每道题的每一条需要（按 idx）判：
- verdict：hit（库里有一条能直接放进这一处，最多改几个字）；partial（库里有相近的，要明显改写或两条拼起来）；miss（库里没有）。从严判：只是主题相同、道理不同，算 miss。
- ids：用到的库条目 id。
- note：怎么用，或者差在哪，不超过 24 字。
- cue_ok：hit 或 partial 时，这道题的题干或那条需要里，有没有那条库条目的信号词或同类说法，能让考生在考场上想起它。
- proposal：只在 miss 时给，写一条新道理（reason 不超过 32 字、hook 不超过 16 字、mechanism、themes、signals、cost、limit），要真、稳、白，能挂到别的题上更好。

results 里每道题写 key 和 needs。`

const patchPrompt = (props, lib) => `${CTX}

测试时发现道理库缺了下面这些道理（JSON，来自不同的题，有重复）：${J(props)}

现有道理库（JSON）：${J(lib)}

把缺的合并成新增条目：同一个机制合成一条；和现有条目重复的不要；措辞要真、稳、白。id 接着现有编号往下排（通用的用 T 开头，主题的用"主题号-序号"）。group、core、cost、limit 等字段和现有条目一样填。anchor：去 /home/user/shenlun/04_文件原文/ 或 /home/user/shenlun/01_大方向解读/ 用 grep 找一句逐字存在的支撑原文，找不到就留空。

${THEMES}`

const recheckPrompt = (items, lib) => `${CTX}

道理库补了新条目。重新判下面这些原来判成 miss 或 partial 的需要（JSON，含题目和需要的道理），看现在的库（JSON）能不能覆盖。规则同前：hit / partial / miss，从严判。每条写 key、idx、verdict、ids、note（不超过 24 字）。

需要：${J(items)}

道理库：${J(lib)}`

const criticPrompt = (lib, summary, fc) => `${CTX}

这是最终的道理库（JSON）和覆盖测试结果摘要。你来找漏：考生拿着这本库去考 2026 年 12 月的广东申论，最可能缺哪些道理？从三个角度查：
(1) 15 个主题里，哪个主题能用的条目太少；
(2) 常见的论证动作有没有缺：为什么是广东、为什么是现在、两难怎么兼顾、为什么要政府和市场一起、为什么要群众参与、为什么不能一刀切、为什么要久久为功；
(3) 预测题里有没有库撑不住的。
最多补 12 条新道理，每条说明补的是哪个缺口（字段和库一样，id 接着往下排），已经有的不要重复；没有就返回空数组。anchor 用 grep 核对过才填。

${THEMES}

道理库：${J(lib)}

覆盖摘要：${J(summary)}

预测题：${J(fc)}`

function applyA(batch, va, dropped) {
  const byId = {}
  ;((va && va.items) || []).forEach(it => { byId[it.id] = it })
  const out = []
  for (const e of batch) {
    const v = byId[e.id]
    if (v && v.verdict === 'drop') { dropped.push({ id: e.id, reason: e.reason, why: v.why }); continue }
    if (v && v.verdict === 'fix') out.push({ ...e, reason: v.reason || e.reason, limit: v.limit || e.limit })
    else out.push(e)
  }
  return out
}

function applyB(batch, vb) {
  const byId = {}
  ;((vb && vb.items) || []).forEach(it => { byId[it.id] = it })
  return batch.map(e => {
    const v = byId[e.id]
    if (!v) return e
    const n = { ...e }
    if (v.verdict === 'fix') {
      if (v.reason) n.reason = v.reason
      if (v.hook) n.hook = v.hook
      if (v.signals && v.signals.length) n.signals = v.signals
    }
    if (v.anchor_found === false) { n.anchor = ''; n.anchor_source = '' }
    else { if (v.anchor) n.anchor = v.anchor; if (v.anchor_source) n.anchor_source = v.anchor_source }
    return n
  })
}

function uniqIds(base, add) {
  const seen = new Set(base.map(e => e.id))
  return add.map(e => { let id = e.id; let k = 2; while (seen.has(id)) { id = e.id + '-' + k; k++ } seen.add(id); return { ...e, id } })
}

async function verifyEntries(entries, tag, dropped, ph) {
  const res = await pipeline(chunk(entries, 20),
    (b, _o, i) => agent(lensA(b), { label: `${tag}:真稳-${i + 1}`, phase: ph, schema: VA_SCHEMA }),
    (va, b, i) => {
      const fa = applyA(b, va, dropped)
      if (!fa.length) return []
      return agent(lensB(fa), { label: `${tag}:锚白-${i + 1}`, phase: ph, schema: VB_SCHEMA }).then(vb => applyB(fa, vb))
    })
  return res.filter(Boolean).flat()
}

const dropped = []

const libP = (async () => {
  const mined = await parallel(MINERS.map(m => () => agent(minePrompt(m), { label: `挖:${m.name}`, phase: 'Mine', schema: CAND_SCHEMA })))
  const cands = []
  mined.forEach((r, i) => { if (r && r.candidates) r.candidates.forEach(c => cands.push({ ...c, src: MINERS[i].name })) })
  log(`挖到候选 ${cands.length} 条`)
  const merged = await agent(mergePrompt(cands), { label: '合并', phase: 'Merge', schema: LIB_SCHEMA })
  const entries = uniqIds([], (merged && merged.entries) || [])
  log(`合并成 ${entries.length} 条`)
  const v = await verifyEntries(entries, '库', dropped, 'Verify')
  log(`复核后 ${v.length} 条，删掉 ${dropped.length} 条`)
  return { entries: v, cands: cands.length, mergedCount: entries.length, note: (merged && merged.note) || '' }
})()

const deriveBatch = ts => agent(deriveBatchPrompt(ts), { label: `列:${ts.map(t => t.key).join('+')}`, phase: 'Derive', schema: DERIVE_SCHEMA })
  .then(r => {
    const byKey = {}
    ;((r && r.results) || []).forEach(x => { byKey[x.key] = x })
    return ts.map(t => (byKey[t.key] && byKey[t.key].needs && byKey[t.key].needs.length) ? { ...t, needs: byKey[t.key].needs } : null)
  })

const fcP = (async () => {
  const f1 = await agent(forecast1(), { label: '预测:广东文件', phase: 'Forecast', schema: FORECAST_SCHEMA })
  const l1 = (f1 && f1.prompts) || []
  const f2 = await agent(forecast2(l1), { label: '预测:中央文件', phase: 'Forecast', schema: FORECAST_SCHEMA })
  const l2 = (f2 && f2.prompts) || []
  const fs = l1.concat(l2).map((f, i) => ({ key: 'F' + String(i + 1).padStart(2, '0'), set: '预测', title: f.prompt, level: f.level, type: f.type, why: f.why, docs: f.docs }))
  log(`预测题 ${fs.length} 道`)
  const ds = (await parallel(chunk(fs, 3).map(c => () => deriveBatch(c)))).filter(Boolean).flat()
  return { fs, ds }
})()

const realP = parallel(chunk(TESTS, 3).map(c => () => deriveBatch(c))).then(rs => rs.filter(Boolean).flat())

const [lib, realD, fc] = await Promise.all([libP, realP, fcP])

let library = lib.entries
const tests = realD.filter(Boolean).concat(fc.ds.filter(Boolean))
log(`测试题 ${tests.length} 道，道理库 ${library.length} 条`)

const testCompact = t => ({ key: t.key, title: t.title, needs: t.needs.map((n, idx) => ({ idx, role: n.role, point: n.point, reason: n.reason })) })
const matchedRaw = await parallel(chunk(tests, 4).map(p => () => agent(matchPrompt(p.map(testCompact), compact(library)), { label: `判:${p.map(t => t.key).join('+')}`, phase: 'Match', schema: MATCH_SCHEMA })))

const first = {}
matchedRaw.filter(Boolean).forEach(m => ((m && m.results) || []).forEach(r => {
  first[r.key] = first[r.key] || {}
  ;(r.needs || []).forEach(n => { first[r.key][n.idx] = n })
}))

function stats(get) {
  const out = {}
  for (const t of tests) {
    const s = out[t.set] = out[t.set] || { hit: 0, partial: 0, miss: 0, none: 0, total: 0 }
    t.needs.forEach((n, idx) => {
      const v = get(t.key, idx)
      s.total++
      if (v === 'hit' || v === 'partial' || v === 'miss') s[v]++
      else s.none++
    })
  }
  return out
}
const before = stats((k, i) => first[k] && first[k][i] && first[k][i].verdict)
log(`首轮：${J(before)}`)

const proposals = []
for (const t of tests) t.needs.forEach((n, idx) => {
  const v = first[t.key] && first[t.key][idx]
  if (v && v.verdict === 'miss' && v.proposal && v.proposal.reason) proposals.push({ ...v.proposal, from: t.key, need: n.reason })
})
log(`缺口提案 ${proposals.length} 条`)

let added = []
if (proposals.length) {
  const patch = await agent(patchPrompt(proposals, compact(library)), { label: '补缺', phase: 'Patch', schema: LIB_SCHEMA })
  const newEntries = uniqIds(library, (patch && patch.entries) || [])
  added = await verifyEntries(newEntries, '补', dropped, 'Patch')
  library = library.concat(added)
  log(`补进 ${added.length} 条`)
}

const finalV = {}
for (const t of tests) {
  finalV[t.key] = {}
  t.needs.forEach((n, idx) => { const v = first[t.key] && first[t.key][idx]; if (v) finalV[t.key][idx] = { verdict: v.verdict, ids: v.ids, note: v.note } })
}
const toRecheck = []
for (const t of tests) t.needs.forEach((n, idx) => {
  const v = first[t.key] && first[t.key][idx]
  if (!v || v.verdict !== 'hit') toRecheck.push({ key: t.key, title: t.title, idx, role: n.role, point: n.point, reason: n.reason })
})
if (toRecheck.length) {
  const rcs = await parallel(chunk(toRecheck, 40).map((c, i) => () => agent(recheckPrompt(c, compact(library)), { label: `重判-${i + 1}`, phase: 'Patch', schema: RECHECK_SCHEMA })))
  rcs.filter(Boolean).forEach(rc => ((rc && rc.items) || []).forEach(it => { if (finalV[it.key]) finalV[it.key][it.idx] = { verdict: it.verdict, ids: it.ids, note: it.note } }))
}
const after = stats((k, i) => finalV[k] && finalV[k][i] && finalV[k][i].verdict)
log(`补后：${J(after)}`)

const summary = { before, after, misses: [] }
for (const t of tests) t.needs.forEach((n, idx) => {
  const v = finalV[t.key] && finalV[t.key][idx]
  if (!v || v.verdict === 'miss') summary.misses.push(`${t.key}：${n.reason}`)
})
const critic = await agent(criticPrompt(compact(library), summary, fc.fs.map(f => f.title)), { label: '找漏', phase: 'Critic', schema: LIB_SCHEMA })
let criticAdded = []
if (critic && critic.entries && critic.entries.length) {
  criticAdded = await verifyEntries(uniqIds(library, critic.entries), '漏', dropped, 'Critic')
  library = library.concat(criticAdded)
  log(`找漏补进 ${criticAdded.length} 条`)
}

return {
  counts: { candidates: lib.cands, merged: lib.mergedCount, afterVerify: lib.entries.length, patched: added.length, critic: criticAdded.length, final: library.length, dropped: dropped.length },
  note: lib.note,
  library,
  dropped,
  forecast: fc.fs,
  stats: { before, after },
  coverage: tests.map(t => ({
    key: t.key, set: t.set, title: t.title,
    needs: t.needs.map((n, idx) => {
      const f = first[t.key] && first[t.key][idx]
      return { role: n.role, point: n.point, reason: n.reason, evidence: n.evidence,
        first: f ? { verdict: f.verdict, ids: f.ids, note: f.note, cue_ok: f.cue_ok } : null,
        final: (finalV[t.key] && finalV[t.key][idx]) || null }
    }),
  })),
}
