# AGENTS.md — 微信读书知识库维护协议

> 本文件是知识库的"灵魂"：规定 AI 怎么读、怎么存、怎么连。每次让 WorkBuddy 处理微信读书笔记前，先读这一份。

## 目标
把用户在微信读书里的划线、想法、书评，沉淀为可复利的个人知识库。

## 分工
- `raw/weread/`：只读原始导出，作为不可变证据，**不要手改**。
- `wiki/`：由 AI 维护的提炼笔记，是检索与复利的主战场。

## 目录地盘
- 一本书一张卡 → `wiki/books/《书名》.md`
- 跨书共通主题 → `wiki/concepts/`
- 作者/人物 → `wiki/people/`
- 来源索引 → `wiki/sources/`

## 规矩（每次新划线下必做）
1. 先存 `raw/weread/《书名》-raw.md`（原始导出，带日期）。
2. 再更新 `wiki/books/《书名》.md`：按"核心观点 / 金句摘录 / 我的思考"组织。
3. 每张 wiki 笔记必须带 frontmatter（见下）。
4. 提炼时主动建立双向链接：连到相关 concepts / people / 其他 books。
5. 在 `log.md` 记一笔：日期 + 操作 + 涉及文件。

## Frontmatter 规范（每张 wiki 笔记开头）
```yaml
---
type: book | concept | person | source
title: 《书名》/ 概念名 / 人名
author: 作者（书）
source: weread
created: YYYY-MM-DD
tags: [微信读书, 主题名]
related: [[相关笔记1]], [[相关笔记2]]
---
```

## 命名约定
- 书名笔记文件名用《》包裹，例如 `wiki/books/《人类简史》.md`。
- 原始导出命名 `raw/weread/《人类简史》-raw.md`。
- 概念/人物用纯名称，例如 `wiki/concepts/复利.md`、`wiki/people/尤瓦尔·赫拉利.md`。
