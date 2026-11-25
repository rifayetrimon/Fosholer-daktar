import io
import re
from pypdf import PdfReader

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150
MIN_CHUNK_LENGTH = 80


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages)

def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore")

def extract_text(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    return extract_text_from_txt(file_bytes)

def chunk_text(text: str) -> list[str]:
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    paragraphs = text.split("\n\n")

    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current) + len(para) + 2 <= CHUNK_SIZE:
            current = (current + "\n\n" + para).strip()
        else:
            if current and len(current) >= MIN_CHUNK_LENGTH:
                chunks.append(current)
            if len(para) > CHUNK_SIZE:
                words = para.split()
                sub = ""
                for word in words:
                    if len(sub) + len(word) + 1 <= CHUNK_SIZE:
                        sub = (sub + " " + word).strip()
                    else:
                        if len(sub) >= MIN_CHUNK_LENGTH:
                            chunks.append(sub)
                        overlap_words = sub.split()[-20:]
                        sub = " ".join(overlap_words) + " " + word
                if len(sub) >= MIN_CHUNK_LENGTH:
                    chunks.append(sub)
                current = ""
            else:
                current = para

    if current and len(current) >= MIN_CHUNK_LENGTH:
        chunks.append(current)

    return chunks
