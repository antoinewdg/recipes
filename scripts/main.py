from __future__ import annotations
from typing import Optional, List
from pathlib import Path
from dataclasses import dataclass
import shutil
from markdown import markdown
from bs4 import BeautifulSoup


def main():
    root_path = Path(__file__).parent.parent
    output_path = root_path / "build"
    output_path.mkdir(parents=True, exist_ok=True)

    recipes = []

    for path in sorted(root_path.glob("*")):
        output_folder_path = output_path / path.parent.relative_to(root_path)

        if path.suffix == ".css":
            shutil.copy(path, output_folder_path / path.name)
        elif path.suffix == ".md":
            body = markdown(path.read_text())
            html_path = output_folder_path / f"{path.stem}.html"
            html_content = _HTML_TEMPLATE.format(body=body)

            bs = BeautifulSoup(html_content, "html.parser")
            document = HtmlDocument(bs)
            main_title = document.get_one("h2")

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
            raise RuntimeError(f"Expected exactly one '{selector}', got {len(result )}")

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
</head>
<body>
    <div class="container">
        {body}
    </div>
</body>
</html>
"""

main()
