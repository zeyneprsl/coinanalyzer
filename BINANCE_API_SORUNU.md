# ⚠️ Binance API Bölge Kısıtlaması Sorunu

## ❌ Sorun

Railway'de Binance API'ye erişim engelleniyor:
```
HTTP 451: Service unavailable from a restricted location
```

**Neden:** Binance, Railway'in bulunduğu bölgeden (muhtemelen ABD) API erişimini kısıtlıyor.

---

## ✅ Çözüm Seçenekleri

### Seçenek 1: Railway Region Değiştirme (Önerilen)

Railway Dashboard'dan:
1. **Settings** → **Region**
2. **EU (Europe)** veya **Asia** seçin
3. Redeploy yapın

**Avantajlar:**
- ✅ Kolay ve hızlı
- ✅ Ücretsiz
- ✅ Binance API erişimi çalışır

---

### Seçenek 2: Binance API Proxy Kullanma

Binance API'yi proxy üzerinden çağırmak. Ancak bu karmaşık ve güvenlik riski var.

---

### Seçenek 3: Alternatif Platform Kullanma

Railway yerine EU'da bulunan bir platform kullanmak:
- **Render** (EU region seçilebilir)
- **Fly.io** (EU region seçilebilir)
- **DigitalOcean** (EU region seçilebilir)

---

### Seçenek 4: Lokal Bilgisayar (Geçici Çözüm)

Lokal bilgisayarınızda çalıştırmak:
```bash
python main.py
```

**Avantajlar:**
- ✅ Hemen çalışır
- ✅ Binance API erişimi sorunsuz

**Dezavantajlar:**
- ❌ Bilgisayarınızı açık tutmanız gerekir
- ❌ Sürekli çalışmaz

---

## 🎯 Önerilen Çözüm

**Railway Dashboard'dan Region'ı EU'ya değiştirin:**

1. Railway Dashboard → Projeniz → **Settings**
2. **Region** sekmesi
3. **EU (Europe)** seçin
4. **Save**
5. **Redeploy** yapın

Bu en kolay ve en hızlı çözümdür!

---

## 📝 Notlar

- Binance API, ABD ve bazı bölgelerden erişimi kısıtlıyor
- EU ve Asya bölgelerinden erişim genellikle sorunsuz
- Railway ücretsiz planda region değiştirme mümkün

---

## ✅ Kontrol

Region değiştirdikten sonra:
- ✅ Railway'de yeni deployment başlamalı
- ✅ Logs'da "✓ Toplam X USDT çifti bulundu" görünmeli
- ✅ "SİSTEM HAZIR" mesajı görünmeli

