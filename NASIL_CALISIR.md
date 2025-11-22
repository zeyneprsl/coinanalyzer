# ⚡ main.py Nasıl Çalışır?

## ✅ Python Çalıştırdığınızda Ne Olur?

### 1. Otomatik Başlatma
```bash
python main.py
```

**Ne yapar:**
- ✅ WebSocket bağlantıları kurulur (Binance'den gerçek zamanlı veri)
- ✅ İlk geçmiş veri analizi yapılır
- ✅ Sürekli çalışma moduna geçer

### 2. Sürekli Çalışma (Real-Time)
**Her 30 dakikada bir otomatik olarak:**
- ✅ Binance'den veri toplar (WebSocket)
- ✅ Korelasyon analizi yapar
- ✅ Fiyat-Volume analizi yapar
- ✅ Ani değişim analizi yapar
- ✅ Korelasyon değişikliklerini takip eder
- ✅ JSON dosyalarını günceller:
  - `realtime_correlations.json`
  - `price_volume_analysis.json`
  - `sudden_price_volume_analysis.json`
  - `correlation_changes_history.json`
  - `realtime_correlation_matrix.csv`

### 3. Otomatik Temizlik
- ✅ Eski verileri temizler (son 1 saatlik veriyi tutar)
- ✅ Bellek kullanımını optimize eder

---

## 🎯 Yapmanız Gerekenler

### ✅ Sadece Bir Kez:
```bash
python main.py
```

**Sonra:**
- ✅ **HİÇBİR ŞEY YAPMANIZA GEREK YOK!**
- ✅ Sürekli çalışır
- ✅ Otomatik analiz yapar
- ✅ JSON dosyalarını günceller

### ⚠️ Streamlit Cloud İçin (Opsiyonel):

Eğer Streamlit Cloud'da görmek istiyorsanız:

**Seçenek 1: Manuel Push (Her 30 dakikada bir)**
```bash
# Yeni terminal açın (main.py çalışırken)
git add *.json *.csv
git commit -m "Analiz sonuçları güncellendi"
git push origin main
```

**Seçenek 2: Otomatik Push (Önerilen)**
`auto_push.py` scriptini çalıştırın (ayrı terminal):
```bash
python auto_push.py
```

Bu script her 30 dakikada bir JSON dosyalarını GitHub'a pushlar.

---

## 🔄 Real-Time Çalışma Akışı

```
python main.py
    ↓
[BAŞLATMA]
├── WebSocket bağlantıları kurulur
├── İlk geçmiş veri analizi yapılır
└── Sürekli çalışma moduna geçer
    ↓
[HER 30 DAKİKADA BİR]
├── Veri toplama (WebSocket)
├── Korelasyon analizi
├── Fiyat-Volume analizi
├── Ani değişim analizi
├── JSON dosyalarını güncelle
└── Eski verileri temizle
    ↓
[SÜREKLI TEKRARLANIR]
```

---

## ⚠️ Dikkat Edilmesi Gerekenler

### 1. Python'u Kapatmayın!
- ❌ Terminal'i kapatmayın
- ❌ Bilgisayarı kapatmayın (veya uyku moduna almayın)
- ✅ Sürekli çalışması için açık bırakın

### 2. İnternet Bağlantısı
- ✅ İnternet bağlantısı olmalı
- ✅ Binance API'ye erişim olmalı

### 3. Hata Durumunda
- ✅ Otomatik yeniden bağlanma var
- ✅ Hata durumunda 30 saniye sonra tekrar dener
- ✅ WebSocket bağlantıları otomatik yenilenir

---

## 🛑 Durdurma

Durdurmak için:
```
Ctrl + C
```

Veya terminal'i kapatın.

---

## 📊 Dashboard'da Görmek İçin

### Lokal Bilgisayar:
```bash
streamlit run dashboard.py
```
✅ JSON dosyaları otomatik okunur

### Streamlit Cloud:
1. JSON dosyalarını GitHub'a pushlayın
2. Streamlit Cloud otomatik güncellenir

---

## ✅ Özet

**Python çalıştırdığınızda:**
- ✅ **Real-time çalışır** (sürekli)
- ✅ **Otomatik güncellenir** (her 30 dakikada)
- ✅ **Hiçbir şey yapmanıza gerek yok!**

**Streamlit Cloud için:**
- ⚠️ JSON dosyalarını GitHub'a pushlamanız gerekir (opsiyonel)
- ✅ Otomatik push scripti kullanabilirsiniz (`auto_push.py`)

