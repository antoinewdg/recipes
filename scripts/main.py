from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from bs4 import BeautifulSoup
from markdown import markdown


def main():
    root_path = Path(__file__).absolute().parent.parent
    output_path = root_path / "build"
    output_path.mkdir(parents=True, exist_ok=True)

    recipes = []
    print("ROOT", root_path.absolute())

    for path in sorted(root_path.glob("*")):
        output_folder_path = output_path / path.parent.relative_to(root_path)

        if path.suffix in {".css", ".webmanifest", ".xml", ".png", ".ico"}:
            print(path)
            shutil.copy(path, output_folder_path / path.name)
        elif path.suffix == ".md":
            body = markdown(path.read_text())
            html_path = output_folder_path / f"{path.stem}.html"
            html_content = _HTML_TEMPLATE.format(body=body)

            bs = BeautifulSoup(html_content, "html.parser")
            document = HtmlDocument(bs)
            main_title = document.get_first("h2")

            recipe = Recipe(
                title=str(main_title.soup.string),
                path=html_path,
            )
            recipes.append(recipe)
            html_path.write_text(html_content)

    recipes_html = "\n".join(
        f'<li><a href="{recipe.path.relative_to(output_path)}">{recipe.title}</li>'
        for recipe in recipes
    )
    index_content = f"""
    <h2>Recettes de Toto</h2>
    <ul>
    {recipes_html}
    </ul>
    """
    index_html = _HTML_TEMPLATE.format(body=index_content)
    (output_path / "index.html").write_text(index_html)


@dataclass
class HtmlDocument:
    soup: BeautifulSoup

    def get_one(self, selector: str) -> HtmlDocument:
        result = self.soup.select(selector)
        if len(result) == 1:
            return HtmlDocument(result[0])
        else:
            raise RuntimeError(f"Expected exactly one '{selector}', got {len(result)}")

    def get_first(self, selector: str) -> HtmlDocument:
        result = self.soup.select(selector)
        if len(result) >= 1:
            return HtmlDocument(result[0])
        else:
            raise RuntimeError(f"Expected at least one '{selector}', got {len(result)}")

    def query_one(self, selector: str) -> Optional[HtmlDocument]:
        result = self.soup.select(selector)
        if not result:
            return None
        elif len(result) == 1:
            return HtmlDocument(result[0])
        else:
            raise RuntimeError(f"Expected maybe one '{selector}', got {len(result )}")


@dataclass
class Recipe:
    title: str
    path: Path


_HTML_TEMPLATE = """
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Recettes de toto</title>

  <link rel="stylesheet" href="reset.css">
  <link rel="stylesheet" href="style.css">

  <!-- favicon -->
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="mask-icon" href="/safari-pinned-tab.svg" color="#5bbad5">
  <meta name="msapplication-TileColor" content="#da532c">
  <meta name="theme-color" content="#ffffff">
</head>
<body>
    <div class="container">
        <section class="content">{body}</section>
        <footer>
            Favicon made by <a href="https://www.flaticon.com/authors/pixel-perfect" title="Pixel perfect">Pixel perfect</a>
            from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>
        </footer>
    </div>
</body>
</html>
"""

main()
