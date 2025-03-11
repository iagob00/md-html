import os
import shutil
import markdown
import json
#import feedparser
from jinja2 import Environment, FileSystemLoader
from pygments.formatters.html import HtmlFormatter

# Diretórios de entrada e saída
DOCS_DIR = "./docs"
DIST_DIR = "./dist"
ASSETS_DIR = "assets"
SEARCH_INDEX = os.path.join(DIST_DIR, "search_index.json")
RSS_FEED = os.path.join(DIST_DIR, "feed.xml")

# Configurar Jinja2 para templates
env = Environment(loader=FileSystemLoader("templates"))

search_data = []


def copy_assets():
    """Copia os arquivos de assets para a pasta de distribuição"""
    src = os.path.join(DOCS_DIR, ASSETS_DIR)
    dest = os.path.join(DIST_DIR, ASSETS_DIR)
    if os.path.exists(src):
        shutil.copytree(src, dest, dirs_exist_ok=True)


def convert_md_to_html(md_path):
    """Converte um arquivo Markdown para HTML"""
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html_content = markdown.markdown(md_content, extensions=["fenced_code", "codehilite"])
    return html_content


def process_markdown_files():
    """Busca todos os arquivos .md e converte para HTML mantendo a estrutura"""
    global search_data
    for root, _, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".md"):
                md_path = os.path.join(root, file)
                rel_path = os.path.relpath(md_path, DOCS_DIR).replace(".md", ".html")
                output_path = os.path.join(DIST_DIR, rel_path)

                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                html_content = convert_md_to_html(md_path)
                title = file.replace(".md", "").replace("_", " ").title()
                search_data.append({"title": title, "url": rel_path, "content": html_content[:500]})

                template = env.get_template("base.html")
                final_html = template.render(content=html_content, title=title, breadcrumbs=rel_path.split(os.sep))

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(final_html)


def generate_syntax_highlight_css():
    """Gera um CSS para realce de código-fonte"""
    css_path = os.path.join(DIST_DIR, "pygments.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(HtmlFormatter().get_style_defs(".codehilite"))


def generate_search_index():
    """Cria um índice de busca local"""
    with open(SEARCH_INDEX, "w", encoding="utf-8") as f:
        json.dump(search_data, f, ensure_ascii=False, indent=4)


def generate_rss_feed():
    """Cria um feed RSS com os documentos convertidos"""
    feed = f"""
    <rss version="2.0">
    <channel>
        <title>Markdown Site Feed</title>
        <link>/</link>
        <description>Atualizações do site gerado</description>
        {''.join([f'<item><title>{doc["title"]}</title><link>{doc["url"]}</link></item>' for doc in search_data])}
    </channel>
    </rss>
    """
    with open(RSS_FEED, "w", encoding="utf-8") as f:
        f.write(feed)


def main():
    shutil.rmtree(DIST_DIR, ignore_errors=True)  # Limpa saída anterior
    os.makedirs(DIST_DIR, exist_ok=True)
    copy_assets()
    process_markdown_files()
    generate_syntax_highlight_css()
    generate_search_index()
    generate_rss_feed()
    print("Site gerado com sucesso!")

if __name__ == "__main__":
    main()
