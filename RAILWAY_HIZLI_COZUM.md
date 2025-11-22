# 🚂 Railway Hızlı Çözüm - Python Versiyonu Sorunu

## ❌ Sorun

Railway'de tüm servisler "Failed" durumunda. Python versiyonu bulunamıyor.

## ✅ HIZLI ÇÖZÜM (Railway Dashboard)

### Adım 1: Railway Dashboard'a Gidin
- https://railway.app → Projeniz → **Settings**

### Adım 2: Her Servis İçin Environment Variables Ekleyin

**"worker" servisi için:**
1. Railway Dashboard → **worker** servisi → **Variables**
2. Yeni variable ekleyin:
   - **Name:** `PYTHON_VERSION`
   - **Value:** `3.11`
3. Kaydedin

**"# Railway/Render için" servisi için:**
1. Railway Dashboard → **# Railway/Render için** servisi → **Variables**
2. Yeni variable ekleyin:
   - **Name:** `PYTHON_VERSION`
   - **Value:** `3.11`
3. Kaydedin

**"# Streamlit Cloud için" servisi için:**
1. Railway Dashboard → **# Streamlit Cloud için** servisi → **Variables**
2. Yeni variable ekleyin:
   - **Name:** `PYTHON_VERSION`
   - **Value:** `3.11`
3. Kaydedin

**"# web" servisi için:**
1. Railway Dashboard → **# web** servisi → **Variables**
2. Yeni variable ekleyin:
   - **Name:** `PYTHON_VERSION`
   - **Value:** `3.11`
3. Kaydedin

### Adım 3: Redeploy

Her servis için:
1. **Deployments** sekmesine gidin
2. **Redeploy** butonuna tıklayın
3. Build'in başarılı olmasını bekleyin

---

## 🎯 Sadece "worker" Servisi İçin (Önerilen)

Eğer sadece `main.py`'yi çalıştırmak istiyorsanız:

1. **"worker" servisini** kullanın
2. Diğer servisleri silebilirsiniz (opsiyonel)
3. **"worker" servisi** → **Variables** → `PYTHON_VERSION = 3.11` ekleyin
4. **Redeploy** yapın

---

## 📝 Notlar

- Railway bazen `runtime.txt` dosyasını doğru algılamayabilir
- Environment variable (`PYTHON_VERSION`) her zaman çalışır
- Python 3.11 yerine 3.10 da deneyebilirsiniz

---

## ✅ Kontrol

Deployment başarılı olduğunda:
- ✅ "worker" servisi "Running" durumunda olmalı
- ✅ Logs'da "SİSTEM HAZIR" mesajını görmelisiniz
- ✅ Her 30 dakikada analiz yapılmalı

