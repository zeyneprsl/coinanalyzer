# ⚠️ Dashboard'da Veri Görünmüyor - Çözüm

## ❌ Sorun

Dashboard'da şu hatalar görünüyor:
- ⚠️ Fiyat-Volume analiz verisi bulunamadı
- ⚠️ Ani değişim analiz verisi bulunamadı

## 🔍 Neden?

Railway'deki "worker" servisi henüz başarıyla çalışmamış. Bu yüzden:
- ❌ `main.py` çalışmıyor
- ❌ Analiz yapılmıyor
- ❌ JSON dosyaları oluşturulmuyor
- ❌ GitHub'a pushlanmıyor
- ❌ Dashboard veri bulamıyor

## ✅ Çözüm Adımları

### 1. Railway'de "worker" Servisini Kontrol Edin

**Railway Dashboard → "worker" servisi → Logs**

Şunları kontrol edin:
- ✅ "SİSTEM HAZIR" mesajı görünüyor mu?
- ✅ "WebSocket bağlantıları aktif!" mesajı var mı?
- ✅ "Analiz tamamlandı!" mesajı görünüyor mu?

**Eğer hata görüyorsanız:**
- ❌ Python versiyonu hatası → `PYTHON_VERSION = 3.11` ekleyin
- ❌ Paket yükleme hatası → Logs'u kontrol edin
- ❌ WebSocket hatası → İnternet bağlantısını kontrol edin

### 2. Railway Variables Kontrolü

**Railway Dashboard → "worker" servisi → Variables**

Şu variable'lar olmalı:
- ✅ `PYTHON_VERSION = 3.11`
- ✅ `GITHUB_TOKEN = [token'ınız]` (opsiyonel, otomatik push için)

### 3. İlk Analiz Bekleyin

`main.py` çalıştığında:
1. İlk geçmiş veri analizi yapılır (~2-3 dakika)
2. WebSocket bağlantıları kurulur (~10 saniye)
3. İlk analiz yapılır (30 dakika sonra)
4. JSON dosyaları oluşturulur
5. GitHub'a pushlanır (~1 dakika)
6. Streamlit Cloud güncellenir (~1 dakika)

**Toplam süre:** ~35 dakika (ilk analiz için)

### 4. Dashboard'u Yenileyin

JSON dosyaları GitHub'a pushlandıktan sonra:
- Streamlit Cloud dashboard'unu yenileyin (F5)
- Veriler görünmeye başlamalı

---

## 🎯 Hızlı Kontrol Listesi

### Railway'de:
- [ ] "worker" servisi "Running" durumunda mı?
- [ ] Logs'da "SİSTEM HAZIR" mesajı var mı?
- [ ] `PYTHON_VERSION = 3.11` eklendi mi?
- [ ] İlk analiz tamamlandı mı? (35 dakika bekleyin)

### GitHub'da:
- [ ] `price_volume_analysis.json` dosyası var mı?
- [ ] `sudden_price_volume_analysis.json` dosyası var mı?
- [ ] `realtime_correlations.json` dosyası var mı?

### Streamlit Cloud'da:
- [ ] Dashboard yenilendi mi? (F5)
- [ ] Veriler görünüyor mu?

---

## 🚨 Hala Sorun Varsa

### Railway Logs'u Kontrol Edin:

1. Railway Dashboard → "worker" servisi → Logs
2. Son hataları kontrol edin
3. Hata mesajını bana gönderin

### Manuel Test (Opsiyonel):

Lokal bilgisayarınızda test edebilirsiniz:
```bash
python main.py
```

Eğer lokal çalışıyorsa ama Railway'de çalışmıyorsa:
- Railway yapılandırması sorunlu olabilir
- Python versiyonu sorunu olabilir
- Environment variable'lar eksik olabilir

---

## ✅ Başarılı Durum

Eğer her şey çalışıyorsa:
- ✅ Railway'de "worker" servisi "Running"
- ✅ Logs'da "Analiz tamamlandı!" mesajları
- ✅ GitHub'da JSON dosyaları var
- ✅ Dashboard'da veriler görünüyor

**Bu durumda sistem tamamen otomatik çalışıyor demektir!**

