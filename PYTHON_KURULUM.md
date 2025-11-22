# 🐍 Python Kurulum Rehberi (Windows)

## ❌ Sorun: "Python bulunamadı"

Python sisteminizde yüklü değil veya PATH'e eklenmemiş.

---

## ✅ Çözüm 1: Python'u Yükleyin (Önerilen)

### Adım 1: Python İndirin
1. https://www.python.org/downloads/ adresine gidin
2. **"Download Python 3.11.x"** butonuna tıklayın (en son versiyon)
3. İndirilen `.exe` dosyasını çalıştırın

### Adım 2: Kurulum Sırasında ÖNEMLİ!
✅ **"Add Python to PATH"** kutusunu işaretleyin! (Çok önemli!)

```
☑️ Add Python to PATH  ← Bu kutuyu mutlaka işaretleyin!
```

### Adım 3: Kurulumu Tamamlayın
- "Install Now" butonuna tıklayın
- Kurulum tamamlanana kadar bekleyin

### Adım 4: Doğrulayın
PowerShell'i **YENİDEN AÇIN** ve şu komutu çalıştırın:

```powershell
python --version
```

Çıktı şöyle olmalı:
```
Python 3.11.x
```

---

## ✅ Çözüm 2: Python Zaten Yüklüyse PATH'e Ekleyin

### Python'un Nerede Yüklü Olduğunu Bulun

Genellikle şu konumlarda olur:
- `C:\Users\zeyne\AppData\Local\Programs\Python\Python311\`
- `C:\Python311\`
- `C:\Program Files\Python311\`

### PATH'e Ekleme Adımları

1. **Windows Ayarlarını Açın**
   - Windows tuşu + R → `sysdm.cpl` yazın → Enter

2. **Gelişmiş Sekmesi**
   - "Ortam Değişkenleri" butonuna tıklayın

3. **PATH'i Düzenleyin**
   - "Kullanıcı değişkenleri" altında "Path" seçin
   - "Düzenle" butonuna tıklayın
   - "Yeni" butonuna tıklayın
   - Python'un kurulu olduğu klasörü ekleyin:
     ```
     C:\Users\zeyne\AppData\Local\Programs\Python\Python311
     C:\Users\zeyne\AppData\Local\Programs\Python\Python311\Scripts
     ```

4. **Kaydedin ve PowerShell'i Yeniden Açın**

---

## ✅ Çözüm 3: Microsoft Store'dan Yükleyin (En Kolay)

1. Microsoft Store'u açın
2. "Python 3.11" arayın
3. "Python 3.11" veya "Python 3.12" yükleyin
4. Otomatik olarak PATH'e eklenir

---

## 🧪 Kurulum Sonrası Test

PowerShell'i **YENİDEN AÇIN** ve şu komutları çalıştırın:

```powershell
# Python versiyonunu kontrol et
python --version

# Python'un nerede olduğunu bul
where python

# Pip'in çalışıp çalışmadığını kontrol et
pip --version
```

---

## 🚀 main.py'yi Çalıştırma

Python kurulduktan sonra:

```powershell
# Proje klasörüne git
cd "C:\Users\zeyne\OneDrive\Belgeler\coindata"

# Gerekli paketleri yükle (ilk kez)
pip install -r requirements.txt

# main.py'yi çalıştır
python main.py
```

---

## ⚠️ Hala Çalışmıyorsa

### PowerShell'i Yönetici Olarak Açın
1. Windows tuşu + X
2. "Windows PowerShell (Yönetici)" seçin
3. Tekrar deneyin

### Alternatif: Python Tam Yol ile Çalıştırın
```powershell
# Python'un tam yolunu bulun (örnek)
C:\Users\zeyne\AppData\Local\Programs\Python\Python311\python.exe main.py
```

---

## 📝 Notlar

- PowerShell'i her PATH değişikliğinden sonra **YENİDEN AÇIN**
- Python 3.11 veya üzeri versiyon önerilir
- Kurulum sırasında "Add Python to PATH" mutlaka işaretlenmeli

---

## ✅ Başarılı Kurulum Sonrası

```powershell
python --version  # Python 3.11.x görmeli
pip --version     # pip 23.x görmeli
python main.py    # main.py çalışmalı
```

