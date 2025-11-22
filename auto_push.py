"""
Otomatik GitHub Push Scripti
main.py çalışırken JSON dosyalarını otomatik olarak GitHub'a pushlar
"""
import os
import time
import subprocess
from datetime import datetime

def git_push():
    """JSON ve CSV dosyalarını GitHub'a pushla"""
    try:
        # Git durumunu kontrol et
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        # JSON ve CSV dosyalarını kontrol et
        json_files = [
            'realtime_correlations.json',
            'price_volume_analysis.json',
            'sudden_price_volume_analysis.json',
            'correlation_changes_history.json',
            'realtime_correlation_matrix.csv',
            'realtime_coin_correlations.json'
        ]
        
        changed_files = []
        for file in json_files:
            if os.path.exists(file):
                changed_files.append(file)
        
        if not changed_files:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Güncellenecek dosya yok")
            return False
        
        # Git add
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📤 GitHub'a pushlanıyor...")
        subprocess.run(['git', 'add'] + changed_files, cwd=os.getcwd())
        
        # Git commit
        commit_message = f"Analiz sonuçları güncellendi - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=os.getcwd())
        
        # Git push
        result = subprocess.run(['git', 'push', 'origin', 'main'], cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Başarıyla pushlandı!")
            return True
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Push başarısız!")
            return False
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Hata: {e}")
        return False

def main():
    """Ana döngü - her 30 dakikada bir push yap"""
    print("="*80)
    print("🚀 OTOMATİK GITHUB PUSH SERVİSİ")
    print("="*80)
    print("Her 30 dakikada bir JSON dosyalarını GitHub'a pushlayacak")
    print("Durdurmak için Ctrl+C tuşlarına basın")
    print("="*80)
    
    push_interval = 30 * 60  # 30 dakika (saniye cinsinden)
    
    try:
        while True:
            # İlk push'u hemen yap
            git_push()
            
            # 30 dakika bekle
            print(f"\n⏳ Sonraki push: 30 dakika sonra...")
            time.sleep(push_interval)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Servis durduruluyor...")
        print("✅ Servis durduruldu!")

if __name__ == "__main__":
    main()

