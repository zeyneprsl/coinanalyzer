# Deploy Talimatları

Bu Streamlit uygulamasını deploy etmek için iki seçenek var:

## 🚀 Seçenek 1: Streamlit Cloud (ÖNERİLEN - En Kolay)

Streamlit uygulamaları için en uygun platform Streamlit Cloud'dur.

### Adımlar:

1. **GitHub'a yükleyin:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/KULLANICI_ADI/REPO_ADI.git
   git push -u origin main
   ```

2. **Streamlit Cloud'a gidin:**
   - https://share.streamlit.io adresine gidin
   - GitHub hesabınızla giriş yapın
   - "New app" butonuna tıklayın
   - Repository'nizi seçin
   - Main file path: `dashboard.py`
   - "Deploy!" butonuna tıklayın

3. **Link paylaşın:**
   - Deploy tamamlandıktan sonra size bir link verilecek (örn: `https://your-app.streamlit.app`)
   - Bu linki istediğiniz kişiyle paylaşabilirsiniz

### Avantajları:
- ✅ Ücretsiz
- ✅ Otomatik deploy (GitHub'a push yaptığınızda güncellenir)
- ✅ Streamlit için optimize edilmiş
- ✅ Kolay kullanım

---

## 🌐 Seçenek 2: Netlify (Daha Karmaşık)

**ÖNEMLİ:** Netlify Streamlit uygulamalarını doğrudan desteklemez. Bu yüzden bu yöntem çalışmayabilir.

### Alternatif Çözümler:

#### A) Netlify Functions ile Backend API
Streamlit'i bir API'ye dönüştürüp, frontend'i ayrı deploy etmek gerekir. Bu oldukça karmaşık bir süreçtir.

#### B) Heroku (Netlify alternatifi)
Heroku Python uygulamalarını destekler:

1. Heroku CLI'yı yükleyin
2. Heroku'da yeni bir app oluşturun:
   ```bash
   heroku create your-app-name
   ```
3. Deploy edin:
   ```bash
   git push heroku main
   ```

### Netlify için Not:
Netlify statik siteler için tasarlanmıştır ve Python runtime'ı desteklemez. Streamlit gibi Python uygulamaları için uygun değildir.

---

## 📝 Öneri

**Streamlit Cloud kullanmanızı şiddetle tavsiye ederim** çünkü:
- Streamlit uygulamaları için özel olarak tasarlanmış
- Ücretsiz ve kolay kullanım
- Otomatik deploy
- Link paylaşımı çok kolay

---

## 🔧 Gereksinimler

Deploy etmeden önce:
1. `requirements.txt` dosyasının güncel olduğundan emin olun
2. Tüm Python dosyalarının doğru çalıştığından emin olun
3. JSON ve CSV dosyalarının (analiz sonuçları) varsa GitHub'a yüklendiğinden emin olun

---

## 📞 Yardım

Sorun yaşarsanız:
- Streamlit Cloud dokümantasyonu: https://docs.streamlit.io/streamlit-cloud
- Streamlit forum: https://discuss.streamlit.io

