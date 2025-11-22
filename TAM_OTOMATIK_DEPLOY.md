# 🚀 Tam Otomatik Deploy Rehberi (Railway)

## ✅ Artık Her Şey Otomatik!

`main.py` artık Railway'de çalıştığında:
- ✅ Otomatik analiz yapar (her 30 dakikada bir)
- ✅ JSON dosyalarını otomatik GitHub'a pushlar
- ✅ Streamlit Cloud otomatik güncellenir
- ✅ **Müşteriler her zaman güncel verileri görür!**

---

## 🚂 Railway'de Deploy (3 Adım)

### 1. Railway Hesabı Oluşturun
- https://railway.app adresine gidin
- "Start a New Project" → "Deploy from GitHub repo"
- GitHub hesabınızı bağlayın
- `zeyneprsl/coinanalyzer` repo'sunu seçin

### 2. Service Type Seçin
- **Worker** seçin (Web servisi değil!)
- Railway otomatik olarak `Procfile`'dan `python main.py` komutunu çalıştırır

### 3. GitHub Token Ayarlayın (ÖNEMLİ!)

Railway'de otomatik push için GitHub token gerekli:

**Adımlar:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)" tıklayın
3. Token'a bir isim verin (örn: "Railway Auto Push")
4. Şu izinleri seçin:
   - ✅ `repo` (Full control of private repositories)
5. "Generate token" tıklayın
6. Token'ı kopyalayın (bir daha gösterilmeyecek!)

**Railway'de Ayarlama:**
1. Railway projenizde → "Variables" sekmesi
2. "New Variable" tıklayın
3. Şu değişkenleri ekleyin:

```
GITHUB_TOKEN = [kopyaladığınız token]
```

**VEYA** Railway otomatik olarak `RAILWAY_ENVIRONMENT` variable'ını ekler, bu yeterli!

---

## ⚙️ Otomatik Push Nasıl Çalışır?

### Lokal Bilgisayar:
```bash
python main.py
```
- ❌ Otomatik push YOK (manuel push yapabilirsiniz)
- ✅ Analiz yapılır, JSON dosyaları oluşur

### Railway/Render:
```bash
python main.py  # Railway otomatik çalıştırır
```
- ✅ Otomatik push VAR
- ✅ Her analiz sonrası GitHub'a pushlanır
- ✅ Streamlit Cloud otomatik güncellenir

---

## 🔄 Çalışma Akışı

```
Railway'de main.py çalışır
    ↓
Her 30 dakikada bir:
├── Veri toplama (WebSocket)
├── Korelasyon analizi
├── Fiyat-Volume analizi
├── JSON dosyalarını kaydet
└── Otomatik GitHub push
    ↓
Streamlit Cloud otomatik güncellenir
    ↓
Müşteriler güncel verileri görür! ✅
```

---

## 📋 Railway Ayarları

### Environment Variables:
```
GITHUB_TOKEN = [GitHub token]
```

### Service Type:
- **Worker** (arka plan servisi)

### Start Command:
Railway otomatik olarak `Procfile`'dan alır:
```
worker: python main.py
```

---

## ✅ Kontrol Listesi

- [ ] Railway hesabı oluşturuldu
- [ ] GitHub repo bağlandı
- [ ] Service Type: Worker seçildi
- [ ] GitHub token eklendi (GITHUB_TOKEN)
- [ ] Deploy başlatıldı
- [ ] Logs'da "Otomatik GitHub push aktif!" mesajı görünüyor
- [ ] Her 30 dakikada bir GitHub'a push yapılıyor

---

## 🐛 Sorun Giderme

### "Git push hatası" görüyorsanız:
1. ✅ `GITHUB_TOKEN` environment variable'ı ekli mi?
2. ✅ Token'ın `repo` izni var mı?
3. ✅ Railway'de git yapılandırması doğru mu?

### "Nothing to commit" görüyorsanız:
- ✅ Normal! Dosyalar zaten güncel demektir

### Push yapılmıyorsa:
- Railway logs'u kontrol edin
- `GITHUB_TOKEN` kontrol edin
- Git config kontrol edin

---

## 🎯 Sonuç

Artık:
- ✅ Railway'de `main.py` sürekli çalışır
- ✅ Her 30 dakikada analiz yapar
- ✅ Otomatik GitHub'a pushlar
- ✅ Streamlit Cloud otomatik güncellenir
- ✅ **Müşteriler her zaman güncel verileri görür!**
- ✅ **Bilgisayarınızı açık tutmanıza gerek yok!**

---

## 💡 Alternatif: Render

Render kullanmak isterseniz:
1. Render.com → New Background Worker
2. GitHub repo'yu bağlayın
3. `RENDER=true` environment variable ekleyin
4. `GITHUB_TOKEN` ekleyin
5. Deploy!

Render'da da otomatik push çalışacak!

