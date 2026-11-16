"""Local image schema, attribution and asset checks (standard library only)."""
import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import date

IMAGE_PATH = re.compile(r'^articles/images/[a-z0-9-]+\.(svg|png|webp|jpg|jpeg)$')
STATUSES = {'待醫師審核', '醫師已審核'}


def check_image(image, tag, root):
    errors = []
    if not isinstance(image, dict):
        return [f'{tag} 必須是圖片物件']
    for key in ('src', 'alt', 'source', 'license', 'sha256'):
        if not isinstance(image.get(key), str) or not image[key].strip():
            errors.append(f'{tag} 缺少有效的 {key}')
    if not isinstance(image.get('caption', ''), str):
        errors.append(f'{tag} caption 必須是字串')
    for key in ('width', 'height'):
        if type(image.get(key)) is not int or not 0 < image[key] <= 20000:
            errors.append(f'{tag} {key} 必須是 1–20000 的整數')
    status = image.get('review_status')
    if status not in STATUSES:
        errors.append(f'{tag} 缺少有效的圖片審核狀態')
    if status == '醫師已審核':
        try:
            date.fromisoformat(image.get('reviewed_on', ''))
        except (ValueError, TypeError):
            errors.append(f'{tag} 核准圖片需有 reviewed_on 日期')
        if not isinstance(image.get('reviewed_by'), str) or not image['reviewed_by'].strip():
            errors.append(f'{tag} 核准圖片需記錄 reviewed_by')
    src = image.get('src')
    if not isinstance(src, str) or not IMAGE_PATH.fullmatch(src):
        return errors + [f'{tag} 必須使用 articles/images/ 下的本地圖片，不允許遠端網址或路徑跳脫']
    path = root / src
    if (not path.resolve().is_relative_to(root.resolve()) or
            not path.resolve().is_relative_to((root / 'articles/images').resolve()) or
            path.is_symlink() or (root / 'articles/images').is_symlink()):
        return errors + [f'{tag} 圖片不得使用連結跳脫目錄']
    if not path.is_file():
        return errors + [f'{tag} 圖片檔案不存在：{src}']
    raw = path.read_bytes()
    if image.get('sha256') != hashlib.sha256(raw).hexdigest():
        errors.append(f'{tag} 圖片內容與 sha256 不符；修改圖片後請重新審核')
    if path.suffix == '.svg':
        try:
            svg = ET.fromstring(raw)
            if svg.tag != '{http://www.w3.org/2000/svg}svg':
                errors.append(f'{tag} 不是有效 SVG')
            for element in svg.iter():
                if element.tag.split('}')[-1].lower() in {'script', 'foreignobject', 'iframe', 'animate', 'set', 'animatetransform', 'animatemotion'}:
                    errors.append(f'{tag} SVG 不得含腳本、外嵌 HTML 或動畫')
                for key, value in element.attrib.items():
                    key = key.split('}')[-1].lower()
                    if key.startswith('on') or (key in {'href', 'src'} and not value.startswith('#')):
                        errors.append(f'{tag} SVG 不得含事件或外部引用')
            text = raw.decode('utf-8')
            if re.search(r'@import|url\s*\(|<!DOCTYPE|<!ENTITY', text, re.I):
                errors.append(f'{tag} SVG 不得含外部樣式或實體引用')
        except (ET.ParseError, UnicodeDecodeError):
            errors.append(f'{tag} SVG 無法解析')
    return errors
