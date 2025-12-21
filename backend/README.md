# AI Destekli CV – İş İlanı Eşleştirme Sistemi

Bu proje, CV metinleri ile iş ilanlarını yapay zekâ destekli doğal dil işleme yöntemleri ile
karşılaştırarak benzerlik skoru ve beceri analizi yapan bir REST API uygulamasıdır.

## Kullanılan Teknolojiler
- Python
- FastAPI
- Sentence-BERT
- pdfplumber
- pytest

## Özellikler
- CV ve iş ilanı metinlerini analiz etme
- Anlamsal benzerlik skoru üretme
- Teknik beceri çıkarımı
- PDF ve TXT dosya desteği
- Unit test ve API testleri

## Çalıştırma
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
