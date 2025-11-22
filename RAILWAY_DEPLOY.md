# 🚂 Railway Deploy Rehberi

## Railway Neden Daha İyi?

### ✅ Railway Avantajları:
1. **Kolay Kurulum** - GitHub bağlantısı ile otomatik deploy
2. **WebSocket Desteği** - Mükemmel WebSocket desteği
3. **Sürekli Çalışma** - Arka plan servisleri için ideal
4. **Dosya Sistemi** - JSON dosyaları yazma/yazma desteği
5. **Ücretsiz Plan** - Aylık $5 kredi (genellikle yeterli)
6. **Hızlı Deploy** - 2-3 dakikada deploy

### ❌ Render Dezavantajları:
1. **Ücretsiz Plan Sınırlı** - 15 dakika inaktiflik sonrası uyku modu
2. **WebSocket Karmaşık** - Daha fazla yapılandırma gerekiyor
3. **Daha Yavaş** - Deploy daha uzun sürer

---

## 🚀 Railway'de Deploy Adımları

### 1. Railway Hesabı Oluşturun
- https://railway.app adresine gidin
- "Start a New Project" → "Deploy from GitHub repo"
- GitHub hesabınızı bağlayın

### 2. Projeyi Seçin
- `zeyneprsl/coinanalyzer` repo'sunu seçin
- Railway otomatik olarak Python projesi olduğunu algılar

### 3. Yapılandırma

Railway otomatik olarak şunları algılar:
- ✅ `requirements.txt` - Python paketleri
- ✅ `runtime.txt` - Python versiyonu
- ✅ `Procfile` - Başlatma komutu

### 4. Değişkenler (Gerekirse)

Railway'de Environment Variables ekleyebilirsiniz (şu an gerekli değil)

### 5. Deploy!

Railway otomatik olarak:
- Paketleri yükler
- `main.py`'yi çalıştırır
- Servisi başlatır

---

## 📝 Procfile Kontrolü

Railway için `Procfile` dosyası gerekli:

```
worker: python main.py
```

Bu dosya zaten mevcut ✅

---

## ⚙️ Railway Ayarları

### Service Type:
- **Worker** (arka plan servisi) seçin
- Web servisi değil!

### Start Command:
Railway otomatik olarak `Procfile`'dan alır:
```
python main.py
```

---

## 🔄 Otomatik Güncelleme

Railway GitHub'a push yaptığınızda otomatik deploy eder:
1. `main.py` çalışır
2. Analiz yapılır
3. JSON dosyaları oluşur
4. **NOT:** Railway'deki dosyalar GitHub'a otomatik pushlanmaz
5. **ÇÖZÜM:** Railway'deki dosyaları GitHub'a pushlamak için ek bir script gerekir

---

## 💡 Önerilen Çözüm

**Railway'de `main.py` çalıştırın:**
- ✅ Sürekli çalışır
- ✅ WebSocket bağlantıları açık kalır
- ✅ Her 30 dakikada analiz yapar

**Ancak JSON dosyalarını GitHub'a pushlamak için:**
- Railway'de bir script ekleyin (GitHub Actions veya webhook)
- VEYA lokal bilgisayarınızda `main.py` çalıştırın ve GitHub'a pushlayın

---

## 🎯 En Pratik Çözüm

**Seçenek 1: Railway (Önerilen)**
- `main.py` Railway'de çalışır
- Analiz sonuçları Railway'de kalır
- Dashboard Streamlit Cloud'da çalışır
- **SORUN:** JSON dosyaları GitHub'a otomatik pushlanmaz

**Seçenek 2: Lokal Bilgisayar (En Pratik)**
- `main.py` lokal bilgisayarınızda çalışır
- Analiz sonuçları GitHub'a pushlanır
- Dashboard Streamlit Cloud'da güncel verileri gösterir
- **AVANTAJ:** Herkes gerçek verileri görür

---

## 📊 Karşılaştırma

| Özellik | Railway | Render | Lokal |
|---------|---------|--------|-------|
| Sürekli Çalışma | ✅ | ⚠️ (Ücretsiz plan sınırlı) | ✅ |
| WebSocket | ✅ | ✅ | ✅ |
| Kolay Kurulum | ✅ | ⚠️ | ✅ |
| Ücretsiz | ✅ ($5 kredi) | ✅ (Sınırlı) | ✅ |
| GitHub Entegrasyonu | ✅ | ✅ | ✅ |
| JSON Pushlama | ❌ | ❌ | ✅ |

---

## 🏆 SONUÇ: Railway Önerilir

Railway daha kolay ve daha güvenilir. Ancak JSON dosyalarını GitHub'a pushlamak için ek bir çözüm gerekiyor.

