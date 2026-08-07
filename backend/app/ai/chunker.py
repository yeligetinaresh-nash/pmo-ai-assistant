def chunk_text(
    text: str,
    chunk_size: int = 2000,
    overlap: int = 200,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n")
        if paragraph.strip()
    ]

    if not paragraphs:
        return []

    chunks: list[str] = []
    current_paragraphs: list[str] = []
    current_length = 0

    for paragraph in paragraphs:
        paragraph_length = len(paragraph)

        if (
            current_paragraphs
            and current_length + paragraph_length + 1 > chunk_size
        ):
            chunk = "\n".join(current_paragraphs)
            chunks.append(chunk)

            overlap_paragraphs: list[str] = []
            overlap_length = 0

            for previous_paragraph in reversed(current_paragraphs):
                item_length = len(previous_paragraph) + (
                    1 if overlap_paragraphs else 0
                )

                if overlap_length + item_length > overlap:
                    break

                overlap_paragraphs.insert(0, previous_paragraph)
                overlap_length += item_length

            current_paragraphs = overlap_paragraphs
            current_length = len("\n".join(current_paragraphs))

        if paragraph_length > chunk_size:
            words = paragraph.split()
            split_paragraphs: list[str] = []
            current_words: list[str] = []
            current_word_length = 0

            for word in words:
                additional_length = len(word) + (
                    1 if current_words else 0
                )

                if (
                    current_words
                    and current_word_length + additional_length > chunk_size
                ):
                    split_paragraphs.append(" ".join(current_words))
                    current_words = []
                    current_word_length = 0

                current_words.append(word)
                current_word_length += additional_length

            if current_words:
                split_paragraphs.append(" ".join(current_words))

            for split_paragraph in split_paragraphs:
                if current_paragraphs:
                    chunks.append("\n".join(current_paragraphs))
                    current_paragraphs = []

                chunks.append(split_paragraph)

            current_length = 0
            continue

        current_paragraphs.append(paragraph)
        current_length = len("\n".join(current_paragraphs))

    if current_paragraphs:
        chunks.append("\n".join(current_paragraphs))

    return chunks