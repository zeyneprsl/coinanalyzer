import time
import threading
from datetime import datetime
from binance_websocket import BinanceWebSocket
from correlation_analyzer import CorrelationAnalyzer
from price_volume_analyzer import PriceVolumeAnalyzer
from correlation_change_tracker import CorrelationChangeTracker

class ContinuousAnalyzer:
    def __init__(self, analysis_interval_minutes=30):
        """
        Sürekli çalışan analiz servisi
        
        analysis_interval_minutes: Her kaç dakikada bir analiz yapılacak (varsayılan: 30 dakika)
        """
        self.analysis_interval = analysis_interval_minutes * 60  # Saniyeye çevir
        self.running = False
        self.ws = BinanceWebSocket()
        self.correlation_analyzer = CorrelationAnalyzer(
            min_data_points=50,
            correlation_threshold=0.7
        )
        self.price_volume_analyzer = PriceVolumeAnalyzer(
            correlation_threshold=0.5
        )
        self.change_tracker = CorrelationChangeTracker(
            threshold_change=0.1,  # %10 değişim eşiği
            min_correlation=0.7    # Minimum takip edilecek korelasyon
        )
        self.pairs = []
        self.analysis_thread = None
        self.last_analysis_time = None
        
    def initialize(self):
        """İlk kurulum - geçmiş veriler ve WebSocket başlatma"""
        print("="*80)
        print("BINANCE COIN KORELASYON ANALİZ SİSTEMİ - SÜREKLI ÇALIŞAN MOD")
        print("="*80)
        print(f"Analiz aralığı: {self.analysis_interval // 60} dakika")
        print("="*80)
        
        # USDT çiftlerini al
        print("\n[BAŞLATMA] USDT çiftleri alınıyor...")
        self.pairs = self.ws.get_usdt_pairs()
        
        if not self.pairs:
            print("❌ USDT çifti bulunamadı!")
            return False
        
        # Coin sayısını sınırla (performans için)
        max_coins = 100
        if len(self.pairs) > max_coins:
            print(f"\n⚠️  {len(self.pairs)} coin bulundu. İlk {max_coins} coin ile devam ediliyor...")
            self.pairs = self.pairs[:max_coins]
        else:
            print(f"✓ {len(self.pairs)} coin bulundu.")
        
        # İlk geçmiş veri analizi (bir kez)
        print("\n[BAŞLATMA] İlk geçmiş veri analizi yapılıyor...")
        try:
            correlation_analyzer = CorrelationAnalyzer(
                min_data_points=50,
                correlation_threshold=0.7
            )
            correlation_analyzer.analyze_historical_data(
                symbols=self.pairs,
                interval='1h',
                limit=200,
                use_returns=True,
                resample_interval='5min'
            )
            print("✓ Geçmiş veri analizi tamamlandı!")
        except Exception as e:
            print(f"⚠️  Geçmiş veri analizi hatası: {e}")
        
        # WebSocket'i başlat
        print("\n[BAŞLATMA] WebSocket bağlantıları kuruluyor...")
        self.ws.start_streaming()
        time.sleep(3)  # Bağlantıların kurulması için bekle
        
        print("✓ WebSocket bağlantıları aktif!")
        print("\n" + "="*80)
        print("✅ SİSTEM HAZIR - Otomatik analizler başlatılıyor...")
        print("="*80)
        
        return True
    
    def perform_analysis(self):
        """Tek bir analiz döngüsü çalıştır"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{'='*80}")
            print(f"[ANALİZ BAŞLADI] {timestamp}")
            print(f"{'='*80}")
            
            # Veri kontrolü
            price_data = self.ws.get_price_data()
            price_volume_data = self.ws.get_price_volume_data()
            
            total_price_points = sum(len(v) for v in price_data.values())
            total_pv_points = sum(len(v) for v in price_volume_data.values())
            
            print(f"Toplanan veri: {total_price_points} fiyat noktası, {total_pv_points} fiyat-volume noktası")
            
            if total_price_points < 50:
                print(f"⚠️  Yetersiz veri ({total_price_points} < 50). Bir sonraki analizde tekrar denenecek.")
                return
            
            # 1. Anlık verilerle korelasyon analizi
            print("\n[1/2] Anlık verilerle korelasyon analizi...")
            if price_data:
                correlation_matrix_realtime, high_corr_realtime, coin_analyses_realtime = \
                    self.correlation_analyzer.analyze_realtime_data(
                        price_data=price_data,
                        use_returns=True,
                        resample_interval='1min'
                    )
                print("✓ Korelasyon analizi tamamlandı!")
                
                # Korelasyon değişikliklerini tespit et ve kaydet
                if high_corr_realtime:
                    print("\n[KORELASYON TAKİBİ] Değişiklikler kontrol ediliyor...")
                    changes = self.change_tracker.analyze_and_save(high_corr_realtime)
                    if changes:
                        print(f"✓ {len(changes)} önemli değişiklik tespit edildi ve kaydedildi!")
            else:
                print("⚠️  Fiyat verisi bulunamadı!")
            
            # 2. Fiyat-Volume ve ani değişim analizi
            print("\n[2/2] Fiyat-Volume ve ani değişim analizi...")
            if price_volume_data:
                # Fiyat-Volume korelasyon analizi
                coin_analyses_pv = self.price_volume_analyzer.analyze_price_volume_relationship(
                    price_volume_data=price_volume_data,
                    resample_interval='1min'
                )
                
                # Ani fiyat değişimleri analizi
                sudden_analyses = self.price_volume_analyzer.analyze_sudden_price_changes(
                    price_volume_data=price_volume_data,
                    thresholds=[1.0, 2.0, 5.0, 10.0],
                    resample_interval='1min'
                )
                
                # Sonuçları kaydet (None kontrolü ile)
                if coin_analyses_pv:
                    self.price_volume_analyzer.save_analysis(coin_analyses_pv, 'price_volume_analysis.json')
                    print(f"✓ Fiyat-Volume analizi kaydedildi ({len(coin_analyses_pv)} coin)")
                else:
                    print("⚠️  Fiyat-Volume analizi sonucu boş!")
                
                if sudden_analyses:
                    self.price_volume_analyzer.save_sudden_analysis(sudden_analyses, 'sudden_price_volume_analysis.json')
                    print(f"✓ Ani değişim analizi kaydedildi ({len(sudden_analyses)} coin)")
                else:
                    print("⚠️  Ani değişim analizi sonucu boş!")
                
                print("✓ Fiyat-Volume analizi tamamlandı!")
            else:
                print("⚠️  Fiyat-volume verisi bulunamadı!")
            
            # Veri temizleme (son 1 saatlik veriyi tut, eskileri sil)
            print("\n[VERİ TEMİZLİĞİ] Eski veriler temizleniyor...")
            self.clean_old_data(keep_hours=1)
            
            self.last_analysis_time = datetime.now()
            print(f"\n✅ Analiz tamamlandı! Sonraki analiz: {self.analysis_interval // 60} dakika sonra")
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"\n❌ Analiz hatası: {e}")
            import traceback
            traceback.print_exc()
    
    def clean_old_data(self, keep_hours=1):
        """Eski verileri temizle (son N saatlik veriyi tut)"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(hours=keep_hours)
            
            cleaned_price = 0
            cleaned_pv = 0
            
            # Fiyat verilerini temizle
            for symbol in list(self.ws.price_data.keys()):
                original_len = len(self.ws.price_data[symbol])
                self.ws.price_data[symbol] = [
                    item for item in self.ws.price_data[symbol]
                    if item['timestamp'] >= cutoff_time
                ]
                cleaned_price += original_len - len(self.ws.price_data[symbol])
            
            # Fiyat-volume verilerini temizle
            for symbol in list(self.ws.price_volume_data.keys()):
                original_len = len(self.ws.price_volume_data[symbol])
                self.ws.price_volume_data[symbol] = [
                    item for item in self.ws.price_volume_data[symbol]
                    if item['timestamp'] >= cutoff_time
                ]
                cleaned_pv += original_len - len(self.ws.price_volume_data[symbol])
            
            if cleaned_price > 0 or cleaned_pv > 0:
                print(f"✓ Temizlendi: {cleaned_price} fiyat, {cleaned_pv} fiyat-volume verisi")
        except Exception as e:
            print(f"⚠️  Veri temizleme hatası: {e}")
    
    def analysis_loop(self):
        """Sürekli analiz döngüsü"""
        while self.running:
            try:
                self.perform_analysis()
                
                # Belirtilen süre kadar bekle
                wait_seconds = self.analysis_interval
                print(f"⏳ {wait_seconds // 60} dakika bekleniyor...")
                
                # Her 10 saniyede bir kontrol et (daha hızlı durdurma için)
                for _ in range(wait_seconds // 10):
                    if not self.running:
                        break
                    time.sleep(10)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Kullanıcı tarafından durduruldu!")
                self.stop()
                break
            except Exception as e:
                print(f"\n❌ Döngü hatası: {e}")
                import traceback
                traceback.print_exc()
                print("⏳ 30 saniye sonra tekrar denenecek...")
                time.sleep(30)
    
    def start(self):
        """Servisi başlat"""
        if self.running:
            print("⚠️  Servis zaten çalışıyor!")
            return
        
        if not self.initialize():
            print("❌ Başlatma başarısız!")
            return
        
        self.running = True
        self.analysis_thread = threading.Thread(target=self.analysis_loop, daemon=True)
        self.analysis_thread.start()
        
        print("\n✅ Servis başlatıldı! Çalışmaya devam ediyor...")
        print("Durdurmak için Ctrl+C tuşlarına basın.\n")
        
        # Ana thread'i çalışır durumda tut
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Durduruluyor...")
            self.stop()
    
    def stop(self):
        """Servisi durdur"""
        print("\n" + "="*80)
        print("SERVİS DURDURULUYOR...")
        print("="*80)
        self.running = False
        self.ws.running = False
        self.ws.stop_streaming()
        if self.analysis_thread:
            self.analysis_thread.join(timeout=5)
        print("✅ Servis durduruldu!")

def main():
    """Ana fonksiyon - sürekli çalışan servis"""
    analyzer = ContinuousAnalyzer(analysis_interval_minutes=5)
    analyzer.start()

if __name__ == "__main__":
    # 30 dakikada bir analiz yapılacak (daha mantıklı bir süre)
    analyzer = ContinuousAnalyzer(analysis_interval_minutes=30)
    analyzer.start()
