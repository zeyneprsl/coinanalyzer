# Streamlit Cloud Deploy Talimatları

Projeniz zaten GitHub'da: https://github.com/zeyneprsl/coinanalyzer

## 🚀 Hızlı Deploy Adımları

### 1. Yeni Dosyaları GitHub'a Pushlayın

Terminal/Command Prompt'ta şu komutları çalıştırın:

```bash
cd "C:\Users\zeyne\OneDrive\Belgeler\coindata"

# Yeni dosyaları ekle
git add .

# Commit yap
git commit -m "Streamlit Cloud deploy için yapılandırma dosyaları eklendi"

# GitHub'a pushla
git push origin main
```

**Not:** Eğer Git yüklü değilse:
- Git'i indirin: https://git-scm.com/download/win
- Veya GitHub Desktop kullanın: https://desktop.github.com/

### 2. Streamlit Cloud'a Deploy Edin

1. **Streamlit Cloud'a gidin:**
   - https://share.streamlit.io adresine gidin
   - GitHub hesabınızla giriş yapın (Sign in with GitHub)

2. **Yeni App Oluşturun:**
   - "New app" butonuna tıklayın
   - **Repository:** `zeyneprsl/coinanalyzer` seçin
   - **Branch:** `main` seçin
   - **Main file path:** `dashboard.py` yazın
   - **App URL:** İstediğiniz URL'i seçin (örn: `coinanalyzer`)

3. **Deploy!**
   - "Deploy!" butonuna tıklayın
   - Birkaç dakika bekleyin

4. **Link Paylaşın:**
   - Deploy tamamlandıktan sonra size bir link verilecek
   - Format: `https://coinanalyzer.streamlit.app` (veya seçtiğiniz URL)
   - Bu linki istediğiniz kişiyle paylaşabilirsiniz!

## ✅ Kontrol Listesi

Deploy etmeden önce:
- [x] `.streamlit/config.toml` dosyası var
- [x] `requirements.txt` güncel
- [x] `dashboard.py` ana dosya olarak ayarlanmış
- [x] Tüm Python dosyaları GitHub'da

## 🔄 Güncellemeler

Kodunuzu güncelledikten sonra:
```bash
git add .
git commit -m "Güncelleme açıklaması"
git push origin main
```

Streamlit Cloud otomatik olarak yeniden deploy edecektir!

## 📝 Notlar

- Streamlit Cloud ücretsizdir
- GitHub'a her push yaptığınızda otomatik deploy olur
- Link herkese açık olacaktır (paylaşabilirsiniz)

## 🆘 Sorun Giderme

Eğer deploy sırasında hata alırsanız:
1. `requirements.txt` dosyasının doğru olduğundan emin olun
2. `dashboard.py` dosyasının çalıştığından emin olun
3. Streamlit Cloud loglarına bakın (deploy sayfasında)

---

**Hazır!** Artık projenizi deploy edebilirsiniz! 🎉

