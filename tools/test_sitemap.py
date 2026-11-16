"""Ensure only real, canonical, indexable pages enter the sitemap."""
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from update_sitemap import NS, SITE_URL, sitemap_xml


class SitemapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'articles').mkdir()
        (self.root / 'index.html').write_text(f'<link rel="canonical" href="{SITE_URL}"><h1>首頁</h1>')
        self.article = {'id': 'sample', 'title': '文章標題', 'body': ['第一段', '第二段', '第三段']}
        (self.root / 'articles/articles.json').write_text(json.dumps([self.article]))

    def urls(self):
        return [loc.text for loc in ET.fromstring(sitemap_xml(self.root)).findall(f'{{{NS}}}url/{{{NS}}}loc')]

    def page(self, content, canonical=None):
        path = self.root / 'articles/sample/index.html'
        path.parent.mkdir(exist_ok=True)
        path.write_text(f'<link rel="canonical" href="{canonical or SITE_URL + "articles/sample/"}">{content}')

    def test_hash_dialog_and_missing_page_are_not_included(self):
        self.assertEqual(self.urls(), [SITE_URL])
        self.assertNotIn(b'#sample', sitemap_xml(self.root))

    def test_real_static_article_updates_sitemap_and_removal_removes_url(self):
        self.page('<h1>文章標題</h1><p>第一段</p><p>第二段</p><p>第三段</p>')
        self.assertEqual(self.urls(), [SITE_URL, SITE_URL + 'articles/sample/'])
        (self.root / 'articles/sample/index.html').unlink()
        self.assertEqual(self.urls(), [SITE_URL])

    def test_noindex_article_is_excluded(self):
        self.page('<meta name="robots" content="noindex, follow">')
        self.assertEqual(self.urls(), [SITE_URL])

    def test_wrong_canonical_and_javascript_only_article_are_rejected(self):
        self.page('<h1>文章標題</h1>', canonical=SITE_URL + '#sample')
        with self.assertRaises(ValueError):
            self.urls()
        self.page('<script>文章標題 第一段 第二段 第三段</script>')
        with self.assertRaises(ValueError):
            self.urls()

    def test_noindex_homepage_and_path_traversal_are_rejected(self):
        (self.root / 'index.html').write_text(f'<link rel="canonical" href="{SITE_URL}"><meta name="googlebot" content="none">')
        with self.assertRaises(ValueError):
            self.urls()
        self.article['id'] = '../escape'
        (self.root / 'index.html').write_text(f'<link rel="canonical" href="{SITE_URL}">')
        (self.root / 'articles/articles.json').write_text(json.dumps([self.article]))
        with self.assertRaises(ValueError):
            self.urls()


if __name__ == '__main__':
    unittest.main()
