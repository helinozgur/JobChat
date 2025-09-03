import json, re

def extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, flags=re.S)
        if not m:
            raise ValueError("LLM JSON parse failed")
        return json.loads(m.group(0))

def normalize_token(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[\s\-_]+", " ", s)
    s = s.replace("’","'").replace("`","'")
    s = s.replace(". net", ".net")
    return s

def uniq_preserve(xs):
    seen=set(); out=[]
    for x in xs or []:
        x=(x or "").strip()
        k=x.lower()
        if x and k not in seen:
            seen.add(k); out.append(x)
    return out

def normalize_token(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[\s\-_]+", " ", s)
    s = s.replace("’","'").replace("`","'")
    s = s.replace(". net", ".net")
    return s
