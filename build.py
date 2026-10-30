"""Build 読み物 (Yomimono) from app.html.

dist/web/  - standalone site for any static host (GitHub Pages); add to the iPad home screen from Safari.
app.html is already a complete page, so the build only copies it and adds the manifest and icons.
"""
import shutil
from pathlib import Path

root = Path(__file__).parent
web = root / "dist" / "web"
web.mkdir(parents=True, exist_ok=True)

shutil.copy(root / "app.html", web / "index.html")
(web / "manifest.webmanifest").write_text(
    '{"name":"読み物","short_name":"読み物","start_url":".","display":"standalone",\n'
    '"background_color":"#f6f1e6","theme_color":"#f6f1e6",\n'
    '"icons":[{"src":"icon-180.png","sizes":"180x180","type":"image/png"},'
    '{"src":"icon-512.png","sizes":"512x512","type":"image/png"}]}\n',
    encoding="utf-8",
)
for name in ("icon-180.png", "icon-512.png"):
    shutil.copy(root / "assets" / name, web / name)
if (root / "stories.json").exists():
    shutil.copy(root / "stories.json", web / "stories.json")
print("built", web)
