"""Generate sitemap.xml from real indexable pages; hash dialogs are not separate URLs."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = 'https://nycuhhtc-debug.github.io/dental-education-studio/'
NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', NS)


def normalize(text):
    return ' '.join(text.split())


class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.noindex = False
        self.text = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'script', 'style', 'template', 'noscript'}:
            self.hidden += 1
        if tag == 'link' and 'canonical' in attrs.get('rel', '').lower().split():
            self.canonicals.append(attrs.get('href'))
        if tag == 'meta' and attrs.get('name', '').lower() in {'robots', 'googlebot'}:
            directives = re.split(r'[,\s]+', attrs.get('content', '').lower())
            self.noindex |= bool({'noindex', 'none'} & set(directives))

    def handle_endtag(self, tag):
        if tag in {'script', 'style', 'template', 'noscript'} and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.text.append(data)


def read_page(path, root):
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'頁面跳脫專案目錄：{path}')
    page = PageMetadata()
    page.feed(path.read_text(encoding='utf-8'))
    return page


def sitemap_urls(root=ROOT):
    homepage = read_page(root / 'index.html', root)
    if homepage.noindex or homepage.canonicals != [SITE_URL]:
        raise ValueError('首頁須可索引，且具有唯一正確的 canonical URL')
    urls = [SITE_URL]
    articles = json.loads((root / 'articles/articles.json').read_text(encoding='utf-8'))
    seen = set()
    for article in articles:
        article_id = article['id']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', article_id) or article_id in seen:
            raise ValueError(f'文章 ID 不合法或重複：{article_id}')
        seen.add(article_id)
        # This convention is considered only if a real static page already exists.
        # Never derive an indexable URL from the existing JavaScript #id dialogs.
        path = root / 'articles' / article_id / 'index.html'
        if not path.is_file():
            continue
        page = read_page(path, root)
        if page.noindex:
            continue
        url = f'{SITE_URL}articles/{article_id}/'
        if page.canonicals != [url]:
            raise ValueError(f'{path} 須設定唯一且指向自己的 canonical：{url}')
        text = normalize(' '.join(page.text))
        if any(normalize(value) not in text for value in [article['title'], *article['body']]):
            raise ValueError(f'{path} 未包含可直接讀取的文章標題與完整內文，不收錄空殼頁面')
        urls.append(url)
    return urls


def sitemap_xml(root=ROOT):
    urlset = ET.Element(f'{{{NS}}}urlset')
    for url in sitemap_urls(root):
        entry = ET.SubElement(urlset, f'{{{NS}}}url')
        ET.SubElement(entry, f'{{{NS}}}loc').text = url
    ET.indent(urlset, space='  ')
    # No fabricated lastmod, priority or changefreq values.
    return ET.tostring(urlset, encoding='utf-8', xml_declaration=True) + b'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='只檢查 sitemap.xml 是否與實際頁面同步')
    args = parser.parse_args()
    try:
        expected = sitemap_xml()
        path = ROOT / 'sitemap.xml'
        if args.check:
            if not path.is_file() or path.read_bytes() != expected:
                print('✗ Sitemap 尚未同步，請執行 python3 tools/update_sitemap.py')
                return 1
        else:
            path.write_bytes(expected)
        print(f'✓ Sitemap 已同步：{len(sitemap_urls())} 個真實頁面；不收錄 #片段網址')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'✗ 無法建立 Sitemap：{error}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
