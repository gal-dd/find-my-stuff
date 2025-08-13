def format_items_list_emojis(rows: list[tuple[str, str]]) -> str:
    """Emoji list, sorted + numbered. rows: [(item, location), ...]"""
    if not rows:
        return "אין חפצים שמורים כרגע."
    lines = []
    for i, (item, loc) in enumerate(sorted(rows, key=lambda x: x[0]), start=1):
        lines.append(f"#️⃣ {i}\n📦 {item}\n📍 {loc}\n")
    return "📋 כל החפצים\n\n" + "\n".join(lines)
