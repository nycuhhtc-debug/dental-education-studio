"""檢查 articles/articles.json 是否符合 AGENTS.md 第 3 節的格式。

用法：python3 tools/check_articles.py
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from image_rules import check_image

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ["id", "title", "category", "summary", "body", "references", "review_status", "updated"]
CATEGORIES = {"智齒拔除", "植牙", "顳顎關節", "術後照護", "口腔黏膜", "牙周與日常保健"}
STATUSES = {"待醫師審核", "醫師已審核"}
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true", help="阻擋尚未核准的文章或圖片")
    args = parser.parse_args()
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
    try:
        settings = json.loads((ROOT / 'articles/image-settings.json').read_text(encoding='utf-8'))
        errors.extend(check_image(settings.get('default_cover'), '統一預設封面', ROOT, args.publish))
    except (OSError, ValueError, AttributeError):
        errors.append('無法讀取有效的 articles/image-settings.json')
    for i, a in enumerate(data, 1):
        tag = f"第 {i} 篇（{a.get('id', '無 id')}）"
        if args.publish and a.get('review_status') != '醫師已審核':
            errors.append(f'{tag} 文章尚未經醫師審核，禁止發布')
        if 'image' in a:
            errors.append(f'{tag} 舊 image 欄位請遷移至 images 陣列')
        if 'cover' in a:
            errors.extend(check_image(a['cover'], f'{tag} 封面', ROOT, args.publish))
        if not isinstance(a.get('images', []), list):
            errors.append(f'{tag} images 必須是陣列')
        else:
            for index, image in enumerate(a.get('images', []), 1):
                errors.extend(check_image(image, f'{tag} 示意圖 {index}', ROOT, args.publish))
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
