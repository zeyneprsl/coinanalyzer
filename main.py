import time
import threading
from binance_websocket import BinanceWebSocket
from correlation_analyzer import CorrelationAnalyzer
from price_volume_analyzer import PriceVolumeAnalyzer

def main():
    print("="*80)
    print("BINANCE COIN KORELASYON ANALİZ SİSTEMİ")
    print("="*80)
    print("Program başlatılıyor... Tüm analizler otomatik çalıştırılacak.")
    print("="*80)
    
    # Modülleri başlat
    ws = BinanceWebSocket()
    correlation_analyzer = CorrelationAnalyzer(
        min_data_points=50,
        correlation_threshold=0.7
    )
    price_volume_analyzer = PriceVolumeAnalyzer(
        correlation_threshold=0.5
    )
    
    # USDT çiftlerini al
    print("\n[ADIM 1/5] USDT çiftleri alınıyor...")
    pairs = ws.get_usdt_pairs()
    
    if not pairs:
        print("USDT çifti bulunamadı!")
        return
    
    # Coin sayısını sınırla (performans için)
    max_coins = 100
    if len(pairs) > max_coins:
        print(f"\n⚠️  {len(pairs)} coin bulundu. İlk {max_coins} coin ile devam ediliyor (performans için)...")
        pairs = pairs[:max_coins]
    else:
        print(f"✓ {len(pairs)} coin bulundu.")
    
    print("\n" + "="*80)
    print("TÜM ANALİZLER ÇALIŞTIRILIYOR")
    print("="*80)
    
    # 1. Geçmiş verilerle korelasyon analizi
    print("\n" + "-"*80)
    print("[ANALİZ 1/4] Geçmiş Verilerle Korelasyon Analizi")
    print("-"*80)
    print("Binance REST API'den geçmiş veriler çekiliyor...")
    
    correlation_matrix_hist, high_corr_hist, coin_analyses_hist = correlation_analyzer.analyze_historical_data(
        symbols=pairs,
        interval='1h',  # 1 saatlik veriler
        limit=200,  # Her coin için 200 veri noktası
        use_returns=True,
        resample_interval='5min'
    )
    
    print("✓ Geçmiş verilerle korelasyon analizi tamamlandı!")
    
    # 2. WebSocket ile anlık veri toplama
    print("\n" + "-"*80)
    print("[ANALİZ 2/4] Anlık Veri Toplama (WebSocket)")
    print("-"*80)
    
    collection_time = 10  # 10 dakika veri toplama
    print(f"WebSocket bağlantıları kuruluyor...")
    print(f"{collection_time} dakika boyunca veri toplanacak...")
    
    # WebSocket'i başlat
    ws.start_streaming()
    
    # Veri toplama sürecini göster
    print(f"\nVeri toplanıyor... (Toplam {collection_time} dakika)")
    total_seconds = collection_time * 60
    
    for i in range(0, total_seconds, 10):
        remaining = total_seconds - i
        mins = remaining // 60
        secs = remaining % 60
        progress = (i / total_seconds) * 100
        print(f"İlerleme: {progress:.1f}% | Kalan süre: {mins:02d}:{secs:02d}", end='\r')
        time.sleep(10)
    
    print(f"\n✓ Veri toplama tamamlandı! ({collection_time} dakika)")
    
    # 3. Anlık verilerle korelasyon analizi
    print("\n" + "-"*80)
    print("[ANALİZ 3/4] Anlık Verilerle Korelasyon Analizi")
    print("-"*80)
    
    price_data = ws.get_price_data()
    
    if price_data:
        print(f"Toplanan veri: {sum(len(v) for v in price_data.values())} veri noktası")
        correlation_matrix_realtime, high_corr_realtime, coin_analyses_realtime = correlation_analyzer.analyze_realtime_data(
            price_data=price_data,
            use_returns=True,
            resample_interval='1min'
        )
        print("✓ Anlık verilerle korelasyon analizi tamamlandı!")
    else:
        print("⚠️  Yeterli anlık veri bulunamadı!")
    
    # 4. Fiyat-Volume ilişkisi analizi
    print("\n" + "-"*80)
    print("[ANALİZ 4/4] Fiyat-Volume İlişkisi ve Ani Değişim Analizi")
    print("-"*80)
    
    price_volume_data = ws.get_price_volume_data()
    
    if price_volume_data:
        # Fiyat-Volume korelasyon analizi
        print("\n4.1. Fiyat-Volume korelasyon analizi yapılıyor...")
        coin_analyses_pv = price_volume_analyzer.analyze_price_volume_relationship(
            price_volume_data=price_volume_data,
            resample_interval='1min'
        )
        price_volume_analyzer.display_analysis(coin_analyses_pv, top_n=20)
        print("✓ Fiyat-Volume korelasyon analizi tamamlandı!")
        
        # Ani fiyat değişimleri analizi
        print("\n4.2. Ani fiyat değişimlerinde volume analizi yapılıyor...")
        sudden_analyses = price_volume_analyzer.analyze_sudden_price_changes(
            price_volume_data=price_volume_data,
            thresholds=[1.0, 2.0, 5.0, 10.0],  # %1, %2, %5, %10 eşikleri
            resample_interval='1min'
        )
        price_volume_analyzer.display_sudden_price_analysis(sudden_analyses, threshold=2.0, top_n=20)
        print("✓ Ani fiyat değişim analizi tamamlandı!")
    else:
        print("⚠️  Yeterli fiyat-volume verisi bulunamadı!")
    
    # Özet
    print("\n" + "="*80)
    print("✅ TÜM ANALİZLER TAMAMLANDI!")
    print("="*80)
    print("\nOluşturulan dosyalar:")
    print("  - historical_correlation_matrix.csv")
    print("  - historical_correlations.json")
    print("  - historical_coin_correlations.json")
    print("  - realtime_correlation_matrix.csv")
    print("  - realtime_correlations.json")
    print("  - realtime_coin_correlations.json")
    print("  - price_volume_analysis.json")
    print("  - sudden_price_volume_analysis.json")
    print("\n" + "="*80)
    print("📊 Sonuçları görselleştirmek için dashboard'u çalıştırın:")
    print("   streamlit run dashboard.py")
    print("="*80)

if __name__ == "__main__":
    main()