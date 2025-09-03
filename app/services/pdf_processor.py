import re, fitz

class PDFProcessor:
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        texts=[]
        for i in range(doc.page_count):
            t = doc[i].get_text("text")
            if t.strip():
                texts.append(t)
        doc.close()
        return re.sub(r"\s+", " ", " ".join(texts)).strip()
