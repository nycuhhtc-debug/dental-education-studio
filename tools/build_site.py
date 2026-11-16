"""Build a publication artifact only after all article/image review checks pass."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path, help='新建的輸出目錄，不得已存在')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or output == ROOT or ROOT.is_relative_to(output):
        parser.error('輸出目錄必須未存在，且不得覆蓋專案或其上層')
    result = subprocess.run([sys.executable, str(ROOT / 'tools/check_articles.py'), '--publish'], cwd=ROOT)
    if result.returncode:
        return result.returncode
    articles = json.loads((ROOT / 'articles/articles.json').read_text())
    settings = json.loads((ROOT / 'articles/image-settings.json').read_text())
    files = {'index.html', 'styles.css', 'script.js', 'articles/articles.json', 'articles/image-settings.json', settings['default_cover']['src']}
    for article in articles:
        if article.get('cover'):
            files.add(article['cover']['src'])
        files.update(image['src'] for image in article.get('images', []))
    for filename in sorted(files):
        dest = output / filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / filename, dest)
    (output / '.nojekyll').touch()
    print(f'發布檢查通過，已產生 {output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
