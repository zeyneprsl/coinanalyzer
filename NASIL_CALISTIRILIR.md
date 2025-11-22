# 📋 Analiz Dosyalarını Oluşturma Rehberi

## 🎯 Hızlı Başlangıç

Analiz dosyalarını görmek için `main.py`'yi lokal bilgisayarınızda çalıştırmanız gerekiyor.

### Adım 1: Terminal'i Açın

Windows'ta:
- `Win + R` tuşlarına basın
- `cmd` veya `powershell` yazın ve Enter'a basın
- Proje klasörüne gidin:
  ```bash
  cd "C:\Users\zeyne\OneDrive\Belgeler\coindata"
  ```

### Adım 2: main.py'yi Çalıştırın

```bash
python main.py
```

### Adım 3: Bekleyin

- Sistem otomatik olarak WebSocket bağlantılarını kuracak
- İlk geçmiş veri analizi yapılacak (yaklaşık 5-10 dakika)
- Sonra her 30 dakikada bir otomatik analiz yapılacak
- İlk analiz sonuçları için yaklaşık 30-40 dakika bekleyin

### Adım 4: Oluşan Dosyaları GitHub'a Pushlayın

Analiz tamamlandıktan sonra (JSON dosyaları oluştuğunda):

```bash
git add *.json
git commit -m "Analiz sonuçları eklendi"
git push origin main
```

### Adım 5: Streamlit Cloud'da Görüntüleyin

- Streamlit Cloud otomatik olarak güncellenecek
- Dashboard'da artık tüm analizler görünecek

---

## ⚠️ Önemli Notlar

1. **İlk Analiz:** İlk analiz için yeterli veri toplanması gereklidir (yaklaşık 30 dakika)
2. **Sürekli Çalışma:** `main.py` sürekli çalışır, durdurmak için `Ctrl+C` tuşlarına basın
3. **Dosyalar:** Aşağıdaki dosyalar oluşturulacak:
   - `price_volume_analysis.json`
   - `sudden_price_volume_analysis.json`
   - `realtime_correlation_matrix.csv`
   - `realtime_correlations.json`
   - `correlation_changes_history.json`

---

## 🔄 Alternatif: Hızlı Test İçin

Eğer sadece test etmek istiyorsanız, `main.py`'yi çalıştırıp birkaç dakika bekleyin. İlk analiz sonuçları görünecektir.

---

## 📞 Sorun mu Yaşıyorsunuz?

- Python yüklü mü? `python --version` komutuyla kontrol edin
- Gerekli paketler yüklü mü? `pip install -r requirements.txt`
- WebSocket bağlantısı çalışıyor mu? Terminal'de hata mesajı var mı kontrol edin

