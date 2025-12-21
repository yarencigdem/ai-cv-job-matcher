# 1) Küçük bir Python imajı kullan
FROM python:3.11-slim

# 2) Çalışma dizini
WORKDIR /app

# 3) Gereksinimleri kopyala ve kur
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 4) Uygulama dosyalarını kopyala
COPY . /app

# 5) Uygulamanın dinlediği port
EXPOSE 8000

# 6) FastAPI uygulamasını uvicorn ile başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
