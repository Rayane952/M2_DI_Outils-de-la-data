from pathlib import Path

EMOJIS = [
    "🎯", "📋", "📦", "📊", "🎓", "📁",
    "✅", "💡", "📚", "🆘", "📤", "🚀",
    "📢", "📈", "📎", "🧭"
]

PATHS = [
    "exercices/exercice-01/README.md",
    "exercices/exercice-02/README.md",
    "exercices/exercice-03/README.md",
    "exercices/exercice-04/README.md",
    "exercices/exercice-05/README.md",
    "exercices/exercice-06/README.md",
    "exercices/exercice-07/README.md",
    "exercices/atelier-01/README.md",
    "exercices/atelier-02/README.md",
    "exercices/atelier-03/README.md",
    "exercices/README.md",
    "exercices/README_CORRECTIONS.md",
]

for path in PATHS:
    file_path = Path(path)
    if not file_path.exists():
        continue
    content = file_path.read_text(encoding="utf-8")
    for emoji in EMOJIS:
        content = content.replace(emoji, "")
    file_path.write_text(content, encoding="utf-8")

print("Emojis removed from README files.")

