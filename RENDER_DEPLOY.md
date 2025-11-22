# 🎨 Render Deploy Rehberi

## Render Özellikleri

### ✅ Render Avantajları:
1. **Ücretsiz Plan** - Background Worker için ücretsiz
2. **GitHub Entegrasyonu** - Otomatik deploy
3. **Kolay Yapılandırma** - Web arayüzü ile kolay

### ⚠️ Render Dezavantajları:
1. **Uyku Modu** - Ücretsiz planda 15 dakika inaktiflik sonrası uyku modu
2. **Yavaş Başlatma** - Uyku modundan çıkış yavaş
3. **WebSocket Karmaşık** - Daha fazla yapılandırma gerekiyor
4. **Dosya Sistemi** - Ephemeral (geçici), yeniden başlatmada kaybolur

---

## 🚀 Render'da Deploy Adımları

### 1. Render Hesabı Oluşturun
- https://render.com adresine gidin
- "New +" → "Background Worker"
- GitHub hesabınızı bağlayın

### 2. Projeyi Seçin
- `zeyneprsl/coinanalyzer` repo'sunu seçin
- Branch: `main`

### 3. Yapılandırma

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python main.py
```

**Environment:**
- Python 3

### 4. Deploy!

---

## ⚠️ Render Sınırlamaları

1. **Uyku Modu:** Ücretsiz planda 15 dakika inaktiflik sonrası uyku modu
2. **Dosya Sistemi:** Ephemeral - yeniden başlatmada kaybolur
3. **JSON Dosyaları:** GitHub'a otomatik pushlanmaz

---

## 💡 Render İçin Öneri

Render kullanmak istiyorsanız:
- ✅ Background Worker olarak deploy edin
- ⚠️ Uyku modunu önlemek için ücretli plan gerekebilir
- ❌ JSON dosyalarını GitHub'a pushlamak için ek script gerekir

---

## 🏆 SONUÇ: Railway Daha İyi

Projeniz için Railway daha uygun çünkü:
- Sürekli çalışma garantisi
- Daha iyi WebSocket desteği
- Daha kolay kurulum
- Daha hızlı deploy

