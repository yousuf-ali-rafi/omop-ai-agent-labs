"""Make the PlantUML diagrams visible on GitHub.

GitHub does not render .puml files. This script encodes every diagrams/*.puml file
into a PlantUML server URL and writes that URL into the image links in docs/*.md.
GitHub then shows the picture, generated live from the .puml source.

Image links it updates look like this (the title in quotes is the .puml file name):
    ![Use case](<any url> "01_use_case")

Run it again after you change a .puml file:
    python scripts/update_diagram_links.py
"""
import re
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = "https://www.plantuml.com/plantuml/svg/"
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"


def encode(text: str) -> str:
    """PlantUML text encoding: raw deflate + PlantUML's own base64 alphabet."""
    compressor = zlib.compressobj(9, zlib.DEFLATED, -15)
    data = compressor.compress(text.encode("utf-8")) + compressor.flush()
    out = []
    for i in range(0, len(data), 3):
        chunk = data[i:i + 3] + b"\0" * (3 - len(data[i:i + 3]))
        n = int.from_bytes(chunk, "big")
        out.append("".join(ALPHABET[(n >> s) & 0x3F] for s in (18, 12, 6, 0)))
    return "".join(out)


def main() -> None:
    urls = {p.stem: SERVER + encode(p.read_text(encoding="utf-8"))
            for p in sorted((ROOT / "diagrams").glob("*.puml"))}
    link = re.compile(r'!\[([^\]]*)\]\(\S+ "([\w-]+)"\)')

    for md in sorted((ROOT / "docs").glob("*.md")):
        text = md.read_text(encoding="utf-8")

        def repl(m):
            name = m.group(2)
            if name not in urls:
                return m.group(0)
            return f'![{m.group(1)}]({urls[name]} "{name}")'

        new = link.sub(repl, text)
        if new != text:
            md.write_text(new, encoding="utf-8")
            print("updated", md.relative_to(ROOT))
    print(f"{len(urls)} diagrams encoded")


if __name__ == "__main__":
    main()
