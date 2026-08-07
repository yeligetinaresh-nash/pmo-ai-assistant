import re


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")

    text = re.sub(r"\r\n?", "\n", text)

    text = re.sub(r"[ \t]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return "\n".join(lines)