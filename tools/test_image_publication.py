"""Regression tests for review gates and unsafe/missing image assets."""
import hashlib
import json
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import check_articles
from image_rules import check_image


class ImagePublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'articles/images').mkdir(parents=True)
        self.path = self.root / 'articles/images/test.svg'
        self.path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>')
        self.image = dict(src='articles/images/test.svg', alt='衛教圖', width=10, height=10,
                          source='本專案原創', license='專案使用', sha256=self.digest(),
                          review_status='待醫師審核', reviewed_on=None, reviewed_by=None)

    def digest(self):
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def approved(self):
        return dict(self.image, review_status='醫師已審核', reviewed_on='2026-11-17', reviewed_by='測試資料')

    def test_pending_image_passes_draft_but_blocks_publication(self):
        self.assertEqual(check_image(self.image, '圖', self.root), [])
        self.assertTrue(check_image(self.image, '圖', self.root, True))
        self.assertEqual(check_image(self.approved(), '圖', self.root, True), [])

    def test_missing_changed_and_external_assets_are_rejected(self):
        for src in ('https://example.com/a.svg', 'articles/images/../test.svg', 'articles/images/missing.svg'):
            with self.subTest(src=src):
                self.assertTrue(check_image(dict(self.image, src=src), '圖', self.root))
        self.path.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>changed</text></svg>')
        self.assertTrue(check_image(self.approved(), '圖', self.root, True))

    def test_executable_svg_and_missing_attribution_are_rejected(self):
        for content in ('<script/>', '<image href="https://example.com/a.png"/>', '<g onload="alert(1)"/>', '<style>@import "x";</style>'):
            self.path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg">{content}</svg>')
            image = dict(self.approved(), sha256=self.digest())
            self.assertTrue(check_image(image, '圖', self.root, True))
        self.assertTrue(check_image(dict(self.image, source='', license=''), '圖', self.root))

    def test_article_and_default_cover_gates(self):
        article = dict(id='test', title='測試', category='植牙', summary='摘要', body=['一', '二', '三'],
                       references=['測試來源'], review_status='醫師已審核', updated='2026-11-17')
        def run():
            (self.root / 'articles/articles.json').write_text(json.dumps([article]))
            with patch.object(check_articles, 'ROOT', self.root), patch.object(sys, 'argv', ['check', '--publish']):
                return check_articles.main()
        settings = self.root / 'articles/image-settings.json'
        settings.write_text(json.dumps({'default_cover': self.image}))
        self.assertEqual(run(), 1)
        settings.write_text(json.dumps({'default_cover': self.approved()}))
        self.assertEqual(run(), 0)
        article['review_status'] = '待醫師審核'
        self.assertEqual(run(), 1)

    def test_artifact_is_created_only_after_review_and_excludes_unused_assets(self):
        tools = self.root / 'tools'
        tools.mkdir()
        for name in ('build_site.py', 'check_articles.py', 'image_rules.py'):
            shutil.copyfile(Path(__file__).with_name(name), tools / name)
        article = dict(id='test', title='測試', category='植牙', summary='摘要', body=['一', '二', '三'],
                       references=['測試來源'], review_status='待醫師審核', updated='2026-11-17')
        articles_path = self.root / 'articles/articles.json'
        articles_path.write_text(json.dumps([article]))
        (self.root / 'articles/image-settings.json').write_text(json.dumps({'default_cover': self.approved()}))
        for name in ('index.html', 'styles.css', 'script.js'):
            (self.root / name).write_text('fixture')
        (self.root / 'articles/images/unused.svg').write_text('draft')
        output = self.root / 'artifact'
        command = [sys.executable, str(tools / 'build_site.py'), '--output', str(output)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())
        article['review_status'] = '醫師已審核'
        articles_path.write_text(json.dumps([article]))
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((output / 'articles/images/test.svg').exists())
        self.assertFalse((output / 'articles/images/unused.svg').exists())
        self.assertFalse((output / 'tools').exists())
        self.assertTrue((output / '.nojekyll').exists())


if __name__ == '__main__':
    unittest.main()
