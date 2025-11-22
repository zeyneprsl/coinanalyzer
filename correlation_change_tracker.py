import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class CorrelationChangeTracker:
    """Korelasyon değişikliklerini takip eden sınıf"""
    
    def __init__(self, history_file='correlation_changes_history.json', 
                 threshold_change=0.1, min_correlation=0.7):
        """
        threshold_change: Önemli değişiklik eşiği (örn: 0.1 = %10 değişim)
        min_correlation: Takip edilecek minimum korelasyon değeri
        """
        self.history_file = history_file
        self.threshold_change = threshold_change
        self.min_correlation = min_correlation
        self.previous_correlations = self.load_previous_correlations()
    
    def load_previous_correlations(self) -> Dict:
        """Önceki korelasyon değerlerini yükle"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # En son analiz değerlerini al
                    if 'last_correlations' in data:
                        return data['last_correlations']
            except Exception as e:
                print(f"⚠️  Önceki korelasyon yükleme hatası: {e}")
        return {}
    
    def save_previous_correlations(self, correlations: List[Dict]):
        """Mevcut korelasyonları önceki değerler olarak kaydet"""
        try:
            # Mevcut veriyi yükle
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'changes_history': [], 'last_correlations': {}}
            
            # Yeni korelasyonları dict formatına çevir (hızlı erişim için)
            new_correlations = {}
            for corr in correlations:
                coin1 = corr.get('coin1', '')
                coin2 = corr.get('coin2', '')
                correlation = corr.get('correlation', 0)
                
                # Çifti sıralı olarak sakla (coin1 < coin2)
                pair_key = tuple(sorted([coin1, coin2]))
                new_correlations[pair_key] = {
                    'coin1': coin1,
                    'coin2': coin2,
                    'correlation': correlation,
                    'abs_correlation': abs(correlation)
                }
            
            data['last_correlations'] = new_correlations
            
            # Dosyaya kaydet
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Korelasyon kaydetme hatası: {e}")
            return False
    
    def detect_changes(self, current_correlations: List[Dict]) -> List[Dict]:
        """Mevcut korelasyonlarla önceki korelasyonları karşılaştır ve değişiklikleri tespit et"""
        changes = []
        timestamp = datetime.now()
        
        # Mevcut korelasyonları dict formatına çevir
        current_dict = {}
        for corr in current_correlations:
            coin1 = corr.get('coin1', '')
            coin2 = corr.get('coin2', '')
            correlation = corr.get('correlation', 0)
            abs_corr = abs(correlation)
            
            # Sadece yeterince yüksek korelasyonları takip et
            if abs_corr < self.min_correlation:
                continue
            
            pair_key = tuple(sorted([coin1, coin2]))
            current_dict[pair_key] = {
                'coin1': coin1,
                'coin2': coin2,
                'correlation': correlation,
                'abs_correlation': abs_corr
            }
        
        # Önceki korelasyonlarla karşılaştır
        checked_pairs = set()
        
        # 1. Mevcut korelasyonları kontrol et (yeni veya değişmiş)
        for pair_key, current_data in current_dict.items():
            checked_pairs.add(pair_key)
            coin1 = current_data['coin1']
            coin2 = current_data['coin2']
            current_corr = current_data['correlation']
            current_abs = current_data['abs_correlation']
            
            if pair_key in self.previous_correlations:
                # Önceki değer var - karşılaştır
                prev_data = self.previous_correlations[pair_key]
                prev_corr = prev_data.get('correlation', 0)
                prev_abs = prev_data.get('abs_correlation', 0)
                
                # Değişim miktarını hesapla
                abs_change = abs(current_abs - prev_abs)
                corr_change = current_corr - prev_corr
                
                # Önemli değişiklik var mı?
                if abs_change >= self.threshold_change:
                    change_type = self._determine_change_type(prev_abs, current_abs, prev_corr, current_corr)
                    
                    changes.append({
                        'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        'coin1': coin1,
                        'coin2': coin2,
                        'previous_correlation': round(prev_corr, 4),
                        'previous_abs_correlation': round(prev_abs, 4),
                        'current_correlation': round(current_corr, 4),
                        'current_abs_correlation': round(current_abs, 4),
                        'change_amount': round(corr_change, 4),
                        'abs_change_amount': round(abs_change, 4),
                        'change_type': change_type,
                        'status': self._get_status(prev_abs, current_abs)
                    })
            else:
                # Yeni yüksek korelasyonlu çift
                if current_abs >= self.min_correlation:
                    changes.append({
                        'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        'coin1': coin1,
                        'coin2': coin2,
                        'previous_correlation': None,
                        'previous_abs_correlation': None,
                        'current_correlation': round(current_corr, 4),
                        'current_abs_correlation': round(current_abs, 4),
                        'change_amount': None,
                        'abs_change_amount': None,
                        'change_type': 'NEW_HIGH_CORRELATION',
                        'status': 'YENİ YÜKSEK KORELASYON'
                    })
        
        # 2. Önceki korelasyonları kontrol et (kaybolan yüksek korelasyonlar)
        for pair_key, prev_data in self.previous_correlations.items():
            if pair_key not in checked_pairs:
                prev_abs = prev_data.get('abs_correlation', 0)
                
                # Önceki değer yüksek korelasyonluysa ve şimdi yoksa
                if prev_abs >= self.min_correlation:
                    coin1 = prev_data['coin1']
                    coin2 = prev_data['coin2']
                    prev_corr = prev_data.get('correlation', 0)
                    
                    changes.append({
                        'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        'coin1': coin1,
                        'coin2': coin2,
                        'previous_correlation': round(prev_corr, 4),
                        'previous_abs_correlation': round(prev_abs, 4),
                        'current_correlation': None,
                        'current_abs_correlation': None,
                        'change_amount': None,
                        'abs_change_amount': round(prev_abs, 4),  # Tamamen kayboldu
                        'change_type': 'LOST_HIGH_CORRELATION',
                        'status': 'YÜKSEK KORELASYON KAYBOLDU'
                    })
        
        return changes
    
    def _determine_change_type(self, prev_abs: float, current_abs: float, 
                               prev_corr: float, current_corr: float) -> str:
        """Değişiklik tipini belirle"""
        if prev_abs >= self.min_correlation and current_abs < self.min_correlation:
            return 'HIGH_TO_LOW'  # Yüksekten düşüğe
        elif prev_abs < self.min_correlation and current_abs >= self.min_correlation:
            return 'LOW_TO_HIGH'  # Düşükten yükseğe
        elif prev_abs >= self.min_correlation and current_abs >= self.min_correlation:
            if current_abs < prev_abs:
                return 'DECREASED'  # Azaldı ama hala yüksek
            else:
                return 'INCREASED'  # Arttı
        else:
            return 'CHANGED'  # Genel değişim
    
    def _get_status(self, prev_abs: float, current_abs: float) -> str:
        """Durum açıklaması"""
        if prev_abs >= self.min_correlation and current_abs < self.min_correlation:
            return f"YÜKSEK ({prev_abs:.3f}) → DÜŞÜK ({current_abs:.3f})"
        elif prev_abs < self.min_correlation and current_abs >= self.min_correlation:
            return f"DÜŞÜK ({prev_abs:.3f}) → YÜKSEK ({current_abs:.3f})"
        elif current_abs >= self.min_correlation:
            if current_abs < prev_abs:
                return f"AZALDI ({prev_abs:.3f} → {current_abs:.3f})"
            else:
                return f"ARTTI ({prev_abs:.3f} → {current_abs:.3f})"
        else:
            return f"DEĞİŞTİ ({prev_abs:.3f} → {current_abs:.3f})"
    
    def save_changes(self, changes: List[Dict]):
        """Değişiklikleri geçmişe kaydet"""
        if not changes:
            return
        
        try:
            # Mevcut geçmişi yükle
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'changes_history': [], 'last_correlations': {}}
            
            # Yeni değişiklikleri ekle
            if 'changes_history' not in data:
                data['changes_history'] = []
            
            data['changes_history'].extend(changes)
            
            # Son 1000 değişikliği tut (dosya boyutunu sınırla)
            if len(data['changes_history']) > 1000:
                data['changes_history'] = data['changes_history'][-1000:]
            
            # Dosyaya kaydet
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ {len(changes)} korelasyon değişikliği kaydedildi")
            
        except Exception as e:
            print(f"❌ Değişiklik kaydetme hatası: {e}")
    
    def get_recent_changes(self, limit: int = 50) -> List[Dict]:
        """Son değişiklikleri getir"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    changes = data.get('changes_history', [])
                    # En yeni değişiklikler önce
                    return sorted(changes, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
        except Exception as e:
            print(f"⚠️  Değişiklik okuma hatası: {e}")
        return []
    
    def analyze_and_save(self, current_correlations: List[Dict]):
        """Analiz yap, değişiklikleri tespit et ve kaydet"""
        # Değişiklikleri tespit et
        changes = self.detect_changes(current_correlations)
        
        # Önemli değişiklikleri göster
        if changes:
            print(f"\n{'='*80}")
            print(f"KORELASYON DEĞİŞİKLİKLERİ TESPİT EDİLDİ ({len(changes)} adet)")
            print(f"{'='*80}")
            
            for change in changes[:10]:  # İlk 10'unu göster
                coin1 = change['coin1']
                coin2 = change['coin2']
                change_type = change['change_type']
                status = change['status']
                
                if change['previous_correlation'] is not None:
                    prev = change['previous_correlation']
                    curr = change['current_correlation']
                    print(f"{coin1} ↔ {coin2}: {status} ({prev:.4f} → {curr:.4f})")
                else:
                    print(f"{coin1} ↔ {coin2}: {status}")
            
            if len(changes) > 10:
                print(f"... ve {len(changes) - 10} değişiklik daha")
        
        # Değişiklikleri kaydet
        self.save_changes(changes)
        
        # Mevcut korelasyonları önceki değerler olarak kaydet
        self.save_previous_correlations(current_correlations)
        
        return changes

