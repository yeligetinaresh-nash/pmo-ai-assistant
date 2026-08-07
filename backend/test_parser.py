from app.ai.chunker import chunk_text
from app.ai.cleaner import clean_text
from app.ai.parser import parse_document

file_path = "../generated/uploads/7977e73ffbe04c20acef364a7e99f2d9.docx"

raw_text = parse_document(file_path)
cleaned_text = clean_text(raw_text)

chunks = chunk_text(
    cleaned_text,
    chunk_size=2000,
    overlap=200,
)

print("=" * 80)
print("PARAGRAPH-AWARE CHUNKING RESULT")
print("=" * 80)

print(f"Raw characters: {len(raw_text)}")
print(f"Cleaned characters: {len(cleaned_text)}")
print(f"Total chunks: {len(chunks)}")

for index, chunk in enumerate(chunks, start=1):
    print("-" * 80)
    print(f"Chunk {index}")
    print(f"Characters: {len(chunk)}")
    print(chunk[:500])