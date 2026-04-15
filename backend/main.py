import io

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
import pdfplumber

# ----------------- Sabitler -----------------
MIN_TEXT_LEN = 30
MAX_TEXT_LEN = 5000

# ----------------- Uygulama -----------------
app = FastAPI(
    title="AI Destekli CV Analiz API",
    description="CV metni ile iş ilanı metni arasında benzerlik skoru ve beceri analizi yapan servis",
    version="0.4.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Embedding modeli 
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ---- Skill listesi (genişletilmiş) ----
SKILL_LIST = [
    # Diller
    "Python", "Java", "C#", "C++", "JavaScript", "TypeScript",
    "Go", "Ruby", "PHP", "Kotlin", "Swift",
    # Web / Backend
    "React", "Angular", "Vue", "Svelte",
    "Node.js", "Express", "Django", "Flask", "FastAPI",
    "ASP.NET", "Spring Boot",
    # Veri / DB
    "SQL", "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis",
    # DevOps / Cloud
    "Docker", "Kubernetes",
    "AWS", "Azure", "GCP", "CI/CD",
    # API
    "REST", "GraphQL",
    # Data / AI
    "Machine Learning", "Deep Learning",
    "TensorFlow", "PyTorch", "Scikit-Learn",
    "Pandas", "NumPy",
    # Araçlar
    "Git", "GitHub", "GitLab",
]


def extract_skills(text: str):
    """
    Verilen metin içinde SKILL_LIST'teki hangi beceriler geçiyor, onu bulur.
    Büyük/küçük harf duyarlılığını kaldırmak için metni lower() yapıyoruz.
    """
    text_lower = text.lower()
    found = []
    for skill in SKILL_LIST:
        if skill.lower() in text_lower:
            found.append(skill)
    return found


class MatchRequest(BaseModel):
    cv_text: str
    job_text: str


def validate_text_field(field_value: str, field_name: str):
    """
    Girdi doğrulama: boş mu, çok kısa mı, çok uzun mu?
    Geçersizse HTTPException fırlatır.
    """
    text = field_value.strip()
    if not text:
        raise HTTPException(status_code=400, detail=f"{field_name} alanı boş olamaz.")
    if len(text) < MIN_TEXT_LEN:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} alanı çok kısa. En az {MIN_TEXT_LEN} karakter olmalıdır."
        )
    if len(text) > MAX_TEXT_LEN:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} alanı çok uzun. En fazla {MAX_TEXT_LEN} karakter olmalıdır."
        )
    return text


@app.get("/")
def home():
    return {"message": "CV Analyzer API çalışıyor."}


@app.post("/match")
def match_texts(data: MatchRequest):
    # 0) Girdi doğrulama
    cv_text = validate_text_field(data.cv_text, "CV metni")
    job_text = validate_text_field(data.job_text, "İş ilanı metni")

    # 1) Benzerlik skoru (embedding ile)
    cv_embedding = model.encode(cv_text)
    job_embedding = model.encode(job_text)

    score = util.cos_sim(cv_embedding, job_embedding)
    compatibility = float(score * 100)

    # 2) Skill çıkarma
    cv_skills = extract_skills(cv_text)
    job_skills = extract_skills(job_text)

    matched_skills = sorted(list(set(cv_skills) & set(job_skills)))
    missing_skills = sorted(list(set(job_skills) - set(cv_skills)))

    return {
        "similarity_score": round(compatibility, 2),
        "cv_skills": cv_skills,
        "job_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


@app.post("/extract-cv-text")
async def extract_cv_text(file: UploadFile = File(...)):
    """
    CV dosyasından metin çıkarma endpoint'i.
    PDF veya düz metin (.txt) dosyalarını destekler.
    """
    content = await file.read()

    if file.content_type == "application/pdf":
        try:
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                full_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    full_text += page_text + "\n"
        except Exception:
            raise HTTPException(status_code=400, detail="PDF dosyası okunurken hata oluştu.")
    elif file.content_type.startswith("text/"):
        # txt, md vb.
        full_text = content.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(status_code=400, detail="Sadece PDF veya metin dosyaları desteklenmektedir.")

    # Biraz temizleyelim
    full_text = full_text.strip()
    if not full_text:
        raise HTTPException(status_code=400, detail="CV dosyasından metin çıkarılamadı.")

    return {"text": full_text}
