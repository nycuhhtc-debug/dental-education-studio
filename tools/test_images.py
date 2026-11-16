"""Regression tests for image records and unsafe/missing assets."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import check_articles
from image_rules import check_image


class ImageTests(unittest.TestCase):
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

    def test_both_review_statuses_are_valid_records(self):
        self.assertEqual(check_image(self.image, '圖', self.root), [])
        self.assertEqual(check_image(self.approved(), '圖', self.root), [])
        self.assertTrue(check_image(dict(self.approved(), reviewed_by=''), '圖', self.root))

    def test_missing_changed_and_external_assets_are_rejected(self):
        for src in ('https://example.com/a.svg', 'articles/images/../test.svg', 'articles/images/missing.svg'):
            with self.subTest(src=src):
                self.assertTrue(check_image(dict(self.image, src=src), '圖', self.root))
        self.path.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>changed</text></svg>')
        self.assertTrue(check_image(self.approved(), '圖', self.root))

    def test_executable_svg_and_missing_attribution_are_rejected(self):
        for content in ('<script/>', '<image href="https://example.com/a.png"/>', '<g onload="alert(1)"/>', '<style>@import "x";</style>'):
            self.path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg">{content}</svg>')
            image = dict(self.approved(), sha256=self.digest())
            self.assertTrue(check_image(image, '圖', self.root))
        self.assertTrue(check_image(dict(self.image, source='', license=''), '圖', self.root))

    def test_pending_articles_and_default_cover_pass_format_checks(self):
        article = dict(id='test', title='測試', category='植牙', summary='摘要', body=['一', '二', '三'],
                       references=['測試來源'], review_status='待醫師審核', updated='2026-11-17')
        (self.root / 'articles/articles.json').write_text(json.dumps([article]))
        (self.root / 'articles/image-settings.json').write_text(json.dumps({'default_cover': self.image}))
        with patch.object(check_articles, 'ROOT', self.root):
            self.assertEqual(check_articles.main(), 0)


if __name__ == '__main__':
    unittest.main()
