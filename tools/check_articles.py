"""檢查 articles/articles.json 是否符合 AGENTS.md 第 3 節的格式。

用法：python3 tools/check_articles.py
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ["id", "title", "category", "summary", "body", "references", "review_status", "updated"]
CATEGORIES = {"智齒拔除", "植牙", "顳顎關節", "術後照護", "口腔黏膜", "牙周與日常保健"}
STATUSES = {"待醫師審核", "醫師已審核"}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def main() -> int:
    path = ROOT / "articles" / "articles.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"✗ JSON 格式錯誤：{e}")
        return 1

    if not isinstance(data, list):
        print("✗ articles.json 最外層必須是陣列")
        return 1

    errors, seen = [], set()
    for i, a in enumerate(data, 1):
        tag = f"第 {i} 篇（{a.get('id', '無 id')}）"
        missing = [f for f in FIELDS if f not in a]
        if missing:
            errors.append(f"{tag} 缺少欄位：{', '.join(missing)}")
            continue
        if not ID_RE.match(a["id"]):
            errors.append(f"{tag} id 必須是英文小寫加連字號")
        if a["id"] in seen:
            errors.append(f"{tag} id 重複")
        seen.add(a["id"])
        if a["category"] not in CATEGORIES:
            errors.append(f"{tag} 類別「{a['category']}」不在 AGENTS.md 類別清單中")
        if len(a["summary"]) > 80:
            errors.append(f"{tag} 摘要 {len(a['summary'])} 字，超過 80 字")
        if not (isinstance(a["body"], list) and 3 <= len(a["body"]) <= 6):
            errors.append(f"{tag} body 必須是 3–6 段的陣列")
        elif any("<" in p or ">" in p for p in a["body"]):
            errors.append(f"{tag} body 不可包含 HTML 標籤")
        if not (isinstance(a["references"], list) and a["references"]):
            errors.append(f"{tag} references 至少要有一筆（無來源請寫待查證）")
        if a["review_status"] not in STATUSES:
            errors.append(f"{tag} review_status 只能是 {' / '.join(STATUSES)}")
        try:
            date.fromisoformat(a["updated"])
        except (TypeError, ValueError):
            errors.append(f"{tag} updated 必須是 YYYY-MM-DD")

    if errors:
        print("\n".join("✗ " + e for e in errors))
        return 1
    pending = sum(a["review_status"] == "待醫師審核" for a in data)
    print(f"✓ 全部通過：共 {len(data)} 篇，其中 {pending} 篇待醫師審核")
    return 0


if __name__ == "__main__":
    sys.exit(main())
