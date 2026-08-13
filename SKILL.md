---
name: weread-obsidian-library
description: 把微信读书的划线、个人想法、以及"本人划线下的点赞评论"导入本地 Obsidian，按 LLM Wiki 范式（raw/wiki + 概念页 + 人物页）搭建可复利增长的个人知识库。当用户想把微信读书笔记存到 Obsidian、要建"划线+点赞评论"知识库、或提到 weread/Obsidian/读书笔记沉淀时使用。
version: 1.0.0
---

# 微信读书 → Obsidian LLM Wiki 知识库

把微信读书的阅读数据（划线、个人想法、以及**你在本人的划线下点过赞的评论**）导入本地 Obsidian，按 Karpathy 的 LLM Wiki 范式组织，让知识跨书、跨概念、跨人物连成网、持续复利。

## 前置条件

1. **微信读书 API Key**：浏览器打开 `https://weread.qq.com/r/weread-skills`，**用你有读书数据的微信账号扫码登录**，页面显示你的昵称后，点"生成/复制 API Key"（格式 `wrk-xxxx`）。配成系统环境变量：
   ```powershell
   setx WEREAD_API_KEY "wrk-你的key"
   ```
   > ⚠️ Key 必须"扫码登录后生成"才绑定账号。直接复制未登录的串会报 `-2010 用户不存在`。
2. **weread-skills 已安装**：官方 `npx skills add Tencent/WeChatReading -g`（它装到 `~/.agents/skills`，需把 `SKILL.md`+能力文档再同步进 `~/.workbuddy/skills/weread-skills`，WorkBuddy 才认）。`skill_version` 取该 SKILL.md 顶部 version 字段（本文撰写时为 1.0.4）。
3. **Obsidian Vault**：已建仓库，记下 Vault 根路径（如 `E:\ObsidianVault\微信读书知识库`）。

## 关键 API 事实（踩坑总结，务必遵守）

- 网关：`POST https://i.weread.qq.com/api/agent/gateway`
- 鉴权：`Authorization: Bearer $WEREAD_API_KEY`；请求体**所有参数平铺**且必须带 `skill_version`。
- `-2010 用户不存在` ⇒ Key 未绑定账号（回到网页用读书账号扫码登录后重新生成）。
- `/book/readreviews`（本人划线下的评论）返回每条评论的 `isLike` 字段，**值是整数 `1`，不是布尔 `True`**——判断务必用 `== 1`，否则全部漏掉（这是最常见的 bug）。
- `/book/readreviews` **没有** `likesCount`；`/review/list` 虽有 `likesCount` 但只含顶层书评、不含划线下评论 ⇒ **无法按点赞数排序**。
- **"我点赞过的评论全局列表"接口不存在**。能拿到的只有：
  - (a) 本人划线下的评论里 `isLike==1` 的那条 → 用 `/book/readreviews` 逐条划线钻取；
  - (b) 本人想法 `/review/list/mine`；
  - (c) 公开书评 `/review/list`。

## Vault 目录结构（LLM Wiki）

```
<Vault>/
  AGENTS.md            # 维护协议（灵魂文件）
  index.md             # MOC 首页（导航）
  log.md               # 变更日志
  raw/weread/          # 不可变原始抓取
  wiki/books/          # 每本书一卡
  wiki/concepts/       # 概念页（跨书聚合）
  wiki/people/         # 人物页（作者/评论者）
  wiki/sources/
  templates/           # 笔记模板
```

## 标准工作流（端到端）

1. **验证 Key**：`/_list` 或 `/shelf/sync` 应返回你的书架。
2. **选书**：`/user/notebooks` 取 `bookId`、`title`、`noteCount`。
3. **拉划线**：`/book/bookmarklist`（`markText`+`range`+`chapterUid`；`chapters` 字段给章节标题映射）。
4. **拉本人想法**：`/review/list/mine`（`count` 大些）。
5. **拉本人划线下的点赞评论**：对每条划线调 `/book/readreviews`，收集 `isLike==1` 的评论（含 `author.name`、`content`、`reviewId`）。
6. **落盘**：
   - `raw/weread/<书名>-raw.md`：原始数据存档（划线 + 每条下全部评论含 isLike 标记）。
   - `wiki/books/<书名>.md`：逐条列划线原文 + 章节，下方挂本人点赞评论；无则标注"无"。
7. **建概念页**：从书卡提取已双链概念，写 `wiki/concepts/<概念>.md`（`type: concept`，含大白话解释 + 来源摘录 + 反向链接）。
8. **建人物页**：作者写 `wiki/people/<人名>.md`（`type: person`，含代表著作 + 核心思想 + 反向链接）。
9. **接入导航**：`index.md` 概念区/人物区、`log.md` 各追加一行。

## 复用脚本

`scripts/fetch_book.py` 封装了步骤 1（验证）+ 3–6（数据抓取 + raw + 书卡生成），用法：

```bash
python3 scripts/fetch_book.py --book <bookId> --vault "<Vault路径>" --title "<书名>"
```

改 `--book` 即可对任意书重跑；脚本自动按 `isLike==1` 筛选点赞评论、映射章节标题、写 raw 与 wiki 书卡。概念页/人物页因需内容提炼，建议按下方模板由模型生成。

## 概念页模板（wiki/concepts/<概念>.md）

```markdown
---
type: concept
title: <概念名>
aliases: [<别名/英文>]
created: <YYYY-MM-DD>
related: [[<来源书>]]
tags: [<领域>, 概念]
---

# <概念名>

> 一句话：<用大白话概括>

## 这是什么（大白话）
<类比/日常例子解释>

## 来源与摘录
### 来自 [[<来源书>]]
- 划线原文（第X章）：「...」
- 你点赞的评论 **[昵称]**：「...」

## 反向链接
- [[<来源书>]]
- [[<相关概念1>]] [[<相关概念2>]]

## 待补充
- <以后补充的方向>
```

## 人物页模板（wiki/people/<人名>.md）

```markdown
---
type: person
title: <人名>
aliases: [<英文名>]
created: <YYYY-MM-DD>
related: [[<代表著作>]]
tags: [人物, <领域>]
---

# <人名>

> 一句话：<身份定位>

## 身份
- <一句话背景>

## 代表著作
- [[<书名>]]

## 核心思想（在本知识库中）
- [[<概念>]]：<一句话>

## 在本知识库中的关联
- <与已入库书/评论的关系>

## 反向链接
- [[<书名>]] [[<概念>]]

## 待补充
- <以后补充的方向>
```

## 注意事项

- `obsidian-cli` 未装也能用——直接写 Markdown 文件，Obsidian 自动识别。
- **Key 绝不写进任何文件**，只用环境变量 `WEREAD_API_KEY` 注入。
- 每张卡片加 frontmatter（`type`/`title`/`created`/`tags`）便于 Dataview 与 AI 自动化。
- "点赞评论"只能按"本人划线范围"查，不能跨书全局查、也不能按点赞数排序——这是 API 能力边界，不是配置问题。
