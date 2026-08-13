# 微信读书 → Obsidian 知识库模板（LLM Wiki 范式）

> 把你在微信读书里的**划线、个人想法、以及「本人划线下的点赞评论」**一键导进本地 Obsidian，按 Karpathy 提出的 LLM Wiki 范式组织，让知识跨书、跨概念、跨人物**自动连成网、持续复利**。
>
> 配套公众号教程：《一步步教你把微信读书划线，自动长成 Obsidian 知识网络》（见 `工位上的猫miao`）。

---

## 1. 这个仓库给你什么

| 文件 / 目录 | 作用 |
|---|---|
| `SKILL.md` | **配置大脑**。把这份文件交给你的 AI 智能体（WorkBuddy / Cursor / Cline 等），它就能照着搭好整套知识库。 |
| `scripts/fetch_book.py` | 一键抓取单本书的划线 + 本人划线下的点赞评论，自动写进 `raw/` 和 `wiki/books/`。 |
| `vault/` | **直接拷贝进你 Obsidian 的骨架**：`AGENTS.md`（维护协议）、`index.md`（首页导航）、`log.md`（变更日志）、`templates/`（笔记模板）、`raw/`、`wiki/` 占位目录。 |
| `examples/半小时讲透第一性原理.md` | 一张**真实书卡**，让你先看清楚输出长什么样。 |

---

## 2. 前置准备（约 2 分钟）

1. **微信读书 API Key**
   - 浏览器打开 `https://weread.qq.com/r/weread-skills`
   - **用你有读书数据的微信账号扫码登录**（页面显示昵称才算登录成功）
   - 点「生成 / 复制 API Key」，形如 `wrk-xxxx`
   - 配成系统环境变量（Windows）：
     ```powershell
     setx WEREAD_API_KEY "wrk-你的key"
     ```
   - ⚠️ **坑位预警**：Key 必须「扫码登录后生成」才绑定账号。直接复制未登录的串会报 `-2010 用户不存在`（详见第 5 节）。

2. **weread-skills 已安装**（你的智能体要能调用微信读书接口）
   - 官方安装：`npx skills add Tencent/WeChatReading -g`
   - WorkBuddy 用户：把装好的 `SKILL.md` + `references/` 同步进 `~/.workbuddy/skills/weread-skills/` 即可。
   - `skill_version` 取 SKILL.md 顶部 `version` 字段（本仓库撰写时为 `1.0.4`）。

3. **Obsidian 已建好一个 Vault**，记下它的根路径（如 `E:\ObsidianVault\微信读书知识库`）。

---

## 3. 三步跑通

**第 1 步：把 `vault/` 拷进你的 Obsidian**
把本仓库 `vault/` 目录下的全部内容，复制进你 Obsidian Vault 的根目录（合并即可，不会覆盖你的笔记）。Obsidian 会自动识别这些 `.md`。

**第 2 步：验证 Key**
打开终端，确认环境变量生效：
```bash
echo %WEREAD_API_KEY%        # Windows
# 或 printenv WEREAD_API_KEY  # macOS / Linux
```
让智能体跑一句：`帮我验证微信读书 Key，列一下我的书架`。

**第 3 步：抓第一本书**
```bash
python3 scripts/fetch_book.py \
  --book 3300200209 \
  --vault "E:/ObsidianVault/微信读书知识库" \
  --title "半小时讲透第一性原理"
```
脚本会：验证 Key → 拉划线 → 拉「本人划线下的点赞评论」(`isLike==1`) → 写 `raw/weread/<书名>-raw.md` + `wiki/books/<书名>.md`。

---

## 4. 文件结构地图（每个文件是干嘛的）

```
<Vault>/
├── AGENTS.md          # 维护协议：规定 AI 怎么读、怎么存、怎么连（灵魂文件，别删）
├── index.md           # MOC 首页：知识库的中枢导航，新笔记进来补链接到这里
├── log.md             # 变更日志：每次新增/更新笔记，在顶部追加一行
├── raw/weread/        # 不可变原始抓取（API 原样存档，当证据，不要手改）
├── wiki/
│   ├── books/         # 每本书一张卡（核心观点 / 金句摘录 / 我的思考 + 双向链接）
│   ├── concepts/      # 概念页：跨书共通主题，把不同书里的同一概念聚到一起
│   └── people/        # 人物页：作者 / 你常点赞的评论者
└── templates/
    └── book-note.md   # 书卡模板（frontmatter + 三段式结构）
```

**为什么这样分？**
- `raw/` 是「证据层」：原样存接口返回，万一以后要重算，有据可查。
- `wiki/` 是「提炼层」：AI 读 raw，产出人类友好的笔记，并在此建立 `[[双向链接]]`。
- `concepts/` 和 `people/` 是「复利层」：读《聪明的投资者》时记下的「安全边际」，会在你读下一本投资书时自动浮现、彼此印证——这才是知识库长网的地方。

---

## 5. 踩坑专节：`-2010 用户不存在`

**现象**：调用任何接口都返回 `errcode: -2010, errmsg: 用户不存在`，连公开的 `/store/search` 都报。

**根因**：`wrk-` 开头的 Key 是「账号授权凭证」，必须在 `weread.qq.com/r/weread-skills` 页面**用读书账号扫码登录后生成**才绑定到你的微信读书用户。你手里那个串如果没走「扫码登录」这一步，后端根本不知道它属于谁。

**排查清单**：
1. 打开 `https://weread.qq.com/r/weread-skills`，确认页面顶部显示了你的**微信读书昵称**（不是微信昵称）。
2. 在该页面点「生成 / 复制 API Key」，**不要**从别的渠道拷现成串。
3. 用 `setx WEREAD_API_KEY "wrk-新生成的key"` 重新配置，重启终端。
4. 仍报 `-2010`？检查：扫码登录的微信，和你 App 里**真正在读书划线的微信**，是不是同一个账号。

---

## 6. API 能力边界（重要，避免白等）

| 能拿到 ✅ | 拿不到 ❌ |
|---|---|
| 本人划线（`/book/bookmarklist`） | 全局「我点赞过的评论」列表（接口不存在） |
| 本人想法 / 点评（`/review/list/mine`） | 划线下评论的**点赞总数**（`likesCount` 不返回） |
| 本人划线下的点赞评论（`/book/readreviews` 的 `isLike==1`） | 按点赞数排序（没有总数，无法排） |
| 公开书评（`/review/list`） | 他人划线的内容 |

**结论**：能沉淀的是「**你本人划线范围内的想法 + 你点过赞的评论**」。这是 API 的能力边界，不是配置问题——文章里说的「点赞评论」特指这一层。

---

## 7. 🤖 把这份仓库交给你的智能体（核心用法）

本仓库的设计目标之一：**读者把仓库 + `SKILL.md` 丢给自己的 AI，就能直接配出同款知识库，不用看长文。**

对你的智能体说（可直接复制）：

> 这是一个「微信读书 → Obsidian」知识库的模板仓库。请先读 `SKILL.md` 理解工作流与 API 避坑，再读 `vault/AGENTS.md` 的维护协议。然后：① 确认我已安装 weread-skills 并配好 `WEREAD_API_KEY`；② 把 `vault/` 目录拷进我的 Obsidian Vault 根；③ 用 `scripts/fetch_book.py` 帮我导《书名》（bookId 我稍后给）；④ 导完按 `AGENTS.md` 规矩写 `wiki/books/` 卡片并接好 `index.md` 双向链接。

智能体会自行处理目录结构、frontmatter、章节标题映射和 `isLike==1` 筛选——你只管读书和说书名。

---

## 8. 日常怎么长

1. 在微信读书正常读，划线 / 写想法 / 给喜欢的评论点赞。
2. 对智能体说：「帮我把《书名》的划线和书评，按 核心观点-金句摘录-我的思考 整理，存到 Obsidian。」
3. 智能体存 `raw/` → 写 `wiki/books/` → 在 `index.md` 补链接 → 在 `log.md` 记一笔。
4. 读书越多，概念页 / 人物页越密，网络自己生长。

---

## 9. 许可证

本仓库文件以 MIT 许可证开源，可自由拷贝、修改、二次发布。文末附 `LICENSE`。
