# Backend - Fiş Analiz Servisi

Bu backend servisi, mobil uygulama tarafından gönderilen fiş görsellerini OpenAI Vision API kullanarak analiz eder ve yapılandırılmış veri döner.

## Windows PowerShell Kurulum ve Çalıştırma

### 1. Ortamı Hazırlama
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Yapılandırma
`.env.example` dosyasını `.env` olarak kopyalayın ve gerekli `OPENAI_API_KEY` ile diğer değerleri doldurun:
```powershell
cp .env.example .env
```

### 3. Çalıştırma
Servisi tüm ağ arayüzlerinde başlatmak için (Fiziksel cihaz testleri için gereklidir):
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Sağlık Kontrolü
```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
```

---
*Not: Gerçek cihazda test ederken mobil cihazınızın bilgisayarınızın yerel IP adresine (örneğin `http://192.168.1.XX:8000`) erişebildiğinden emin olun.*
