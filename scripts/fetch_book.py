#!/usr/bin/env python3
"""fetch_book.py — 微信读书单本书 → Obsidian LLM Wiki 导入。

封装：验证 Key + 拉划线 + 拉本人划线下的点赞评论(isLike==1) + 写 raw/weread + 写 wiki/books 书卡。

依赖：环境变量 WEREAD_API_KEY
用法：
    python3 fetch_book.py --book 3300014116 --vault "E:/ObsidianVault/微信读书知识库" --title "聪明的投资者"

改 --book 即可对任意书重跑。章节标题由 /book/bookmarklist 的 chapters 字段自动映射。
"""
import json
import os
import sys
import urllib.request
import argparse
import datetime

GW = "https://i.weread.qq.com/api/agent/gateway"
VER = "1.0.4"


def call(api_name, **kw):
    body = {"api_name": api_name, "skill_version": VER}
    body.update(kw)
    req = urllib.request.Request(
        GW,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['WEREAD_API_KEY']}",
            "Content-Type": "application/json",
        },
    )
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())


def safe(name):
    return "".join(c for c in name if c not in '\\/:*?"<>|').strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, help="微信读书 bookId")
    ap.add_argument("--vault", required=True, help="Obsidian Vault 根路径")
    ap.add_argument("--title", default=None, help="书名（不给则回退用 bookId）")
    args = ap.parse_args()

    if not os.environ.get("WEREAD_API_KEY"):
        sys.exit("❌ 未设置环境变量 WEREAD_API_KEY（请用 setx 配置 wrk- 开头的 Key）")

    book_id = args.book
    title = args.title or book_id
    today = datetime.date.today().isoformat()

    # 0) 验证 Key
    try:
        probe = call("/shelf/sync")
        if probe.get("errcode") in (-2010, -1):
            sys.exit(f"❌ Key 验证失败：{probe.get('errmsg')}（请用读书账号扫码登录后重新生成 Key）")
    except Exception as e:
        print(f"⚠️ Key 验证请求异常（继续尝试）：{e}")

    # 1) 划线
    bm = call("/book/bookmarklist", bookId=book_id)
    marks = bm.get("updated", [])
    chapters = {}
    ch_raw = bm.get("chapters", {})
    if isinstance(ch_raw, dict):
        for k, v in ch_raw.items():
            try:
                chapters[int(k)] = v.get("title", f"第{k}章")
            except ValueError:
                chapters[k] = v.get("title", str(k))
    elif isinstance(ch_raw, list):
        for item in ch_raw:
            uid = item.get("chapterUid") or item.get("chapterId")
            if uid is None:
                continue
            try:
                chapters[int(uid)] = item.get("title", f"第{uid}章")
            except (ValueError, TypeError):
                chapters[uid] = item.get("title", str(uid))

    # 2) 本人划线下的点赞评论 (isLike == 1，整数！)
    liked = {}  # f"{chapterUid}|{range}" -> [ {name, content, reviewId} ]
    for m in marks:
        ch = m.get("chapterUid")
        rng = m.get("range")
        try:
            rr = call(
                "/book/readreviews",
                bookId=book_id,
                chapterUid=ch,
                reviews=[{"range": rng, "maxIdx": 0, "count": 50, "synckey": 0}],
            )
        except Exception as e:
            print(f"  ⚠️ 跳过划线 ch={ch} range={rng}: {e}")
            continue
        for rv in rr.get("reviews", []):
            for pr in rv.get("pageReviews", []):
                r = pr.get("review", {})
                if r.get("isLike") == 1:  # 关键：整数 1，不是布尔 True
                    author = r.get("author", {})
                    name = author.get("name") if isinstance(author, dict) else str(author)
                    liked.setdefault(f"{ch}|{rng}", []).append(
                        {
                            "name": name,
                            "content": (r.get("content") or "").strip(),
                            "reviewId": r.get("reviewId"),
                        }
                    )

    raw_dir = os.path.join(args.vault, "raw", "weread")
    book_dir = os.path.join(args.vault, "wiki", "books")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(book_dir, exist_ok=True)

    # 3) 写 raw（不可变原始存档）
    raw_path = os.path.join(raw_dir, f"{safe(title)}-raw.md")
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(f"---\ntype: raw\nsource: weread\nbook: {title}\nbookId: {book_id}\ncreated: {today}\n---\n\n")
        f.write(f"# {title} — 原始抓取（API）\n\n")
        for i, m in enumerate(marks, 1):
            ch = m.get("chapterUid")
            rng = m.get("range")
            txt = (m.get("markText") or m.get("content") or "").strip()
            f.write(f"## 划线 {i} · {chapters.get(int(ch) if str(ch).isdigit() else ch, ch)}\n\n> {txt}\n\n")
            for c in liked.get(f"{ch}|{rng}", []):
                f.write(f"- **[{c['name']}]** (赞过) {c['content']}  \n  reviewId={c['reviewId']}\n")
            f.write("\n")

    # 4) 写 wiki 书卡（划线 + 对应点赞评论）
    card_path = os.path.join(book_dir, f"{safe(title)}.md")
    with open(card_path, "w", encoding="utf-8") as f:
        f.write(f"---\ntype: book\ntitle: {title}\nsource: weread\ncreated: {today}\nupdated: {today}\ntags: [微信读书]\n---\n\n")
        f.write(f"# {title}\n\n")
        f.write(
            f"> 来源：微信读书 · 划线 {len(marks)} 条，其中 "
            f"{len(liked)} 条划线下有本人点赞评论 · 导入 {today}\n\n"
        )
        f.write("## 划线与对应点赞评论\n\n")
        for i, m in enumerate(marks, 1):
            ch = m.get("chapterUid")
            rng = m.get("range")
            txt = (m.get("markText") or m.get("content") or "").strip()
            ch_title = chapters.get(int(ch) if str(ch).isdigit() else ch, ch)
            f.write(f"### 划线 {i} · {ch_title}\n\n> {txt}\n\n")
            cs = liked.get(f"{ch}|{rng}", [])
            if cs:
                f.write("💬 **本条下你点赞的评论**：\n\n")
                for c in cs:
                    f.write(f"- **[{c['name']}]**：{c['content']}\n")
            else:
                f.write("_（本条划线下没有你点赞的评论）_\n")
            f.write("\n")

    n_liked = sum(len(v) for v in liked.values())
    print(f"✅ 完成：{len(marks)} 条划线，{n_liked} 条本人划线下的点赞评论")
    print(f"  raw : {raw_path}")
    print(f"  书卡: {card_path}")


if __name__ == "__main__":
    main()
