import json

from app.ai.brd_analyzer import analyze_brd
from app.ai.cleaner import clean_text
from app.ai.parser import parse_document


file_path = (
    "../generated/uploads/"
    "7977e73ffbe04c20acef364a7e99f2d9.docx"
)

print("Reading BRD...")

raw_text = parse_document(file_path)
cleaned_text = clean_text(raw_text)

print(f"Characters being sent: {len(cleaned_text)}")
print("Calling OpenAI API... This may take a few moments.")

analysis = analyze_brd(cleaned_text)

print("\n" + "=" * 80)
print("STRUCTURED BRD ANALYSIS")
print("=" * 80)

print(
    json.dumps(
        analysis.model_dump(),
        indent=2,
        ensure_ascii=False,
    )
)