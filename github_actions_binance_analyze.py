"""
GitHub Actions için Binance API analiz scripti
Her 5 dakikada bir çalışır ve anlık verileri toplar
"""
import requests
import json
from datetime import datetime
import time

def fetch_binance_usdt_pairs():
    """Binance'den tüm USDT çiftlerini al"""
    try:
        url = "https://api.binance.com/api/v3/exchangeInfo"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        pairs = [
            s['symbol'] 
            for s in data['symbols'] 
            if s['symbol'].endswith('USDT') and s.get('status') == 'TRADING'
        ]
        
        print(f"✓ {len(pairs)} USDT çifti bulundu")
        return pairs
    except Exception as e:
        print(f"❌ USDT çiftleri alınamadı: {e}")
        return []

def fetch_24h_ticker(symbols):
    """Binance'den 24 saatlik ticker verilerini al"""
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=30)
        data = response.json()
        
        # Sadece USDT çiftlerini filtrele
        usdt_data = [
            item for item in data 
            if item['symbol'] in symbols
        ]
        
        print(f"✓ {len(usdt_data)} coin için ticker verisi alındı")
        return usdt_data
    except Exception as e:
        print(f"❌ Ticker verisi alınamadı: {e}")
        return []

def analyze_price_volume(ticker_data):
    """Fiyat ve volume analizini yap"""
    analyses = {}
    
    for item in ticker_data:
        symbol = item['symbol']
        
        try:
            price_change = float(item['priceChangePercent'])
            volume = float(item['volume'])
            quote_volume = float(item['quoteVolume'])
            
            # Basit analiz
            analyses[symbol] = {
                'price': float(item['lastPrice']),
                'price_change_24h': price_change,
                'volume': volume,
                'quote_volume': quote_volume,
                'high_24h': float(item['highPrice']),
                'low_24h': float(item['lowPrice']),
                'trades': int(item['count']),
                'correlation': 0,  # WebSocket olmadan korelasyon hesaplanamaz
                'volume_increase_on_price_up_pct': 0,
                'avg_volume_change_on_price_up': 0
            }
        except (ValueError, KeyError) as e:
            print(f"⚠️  {symbol} parse edilemedi: {e}")
            continue
    
    print(f"✓ {len(analyses)} coin analiz edildi")
    return analyses

def analyze_sudden_changes(ticker_data, thresholds=[1.0, 2.0, 5.0, 10.0]):
    """Ani fiyat değişimlerini tespit et"""
    analyses = {}
    
    for item in ticker_data:
        symbol = item['symbol']
        
        try:
            price_change = float(item['priceChangePercent'])
            
            # Hangi eşikleri aştı?
            triggered_thresholds = [
                threshold for threshold in thresholds
                if abs(price_change) >= threshold
            ]
            
            if triggered_thresholds:
                analyses[symbol] = {
                    'coin': symbol,
                    'price': float(item['lastPrice']),
                    'price_change_24h': price_change,
                    'volume': float(item['volume']),
                    'quote_volume': float(item['quoteVolume']),
                    'triggered': True,
                    'triggered_thresholds': triggered_thresholds,
                    'max_threshold': max(triggered_thresholds)
                }
        except (ValueError, KeyError) as e:
            continue
    
    print(f"✓ {len(analyses)} coin ani değişim gösterdi")
    return analyses

def calculate_simple_correlations(ticker_data):
    """Basit korelasyon hesapla (BTC bazlı)"""
    # BTC'yi bul
    btc_data = None
    for item in ticker_data:
        if item['symbol'] == 'BTCUSDT':
            btc_data = item
            break
    
    if not btc_data:
        print("⚠️  BTCUSDT bulunamadı, korelasyon hesaplanamadı")
        return []
    
    btc_change = float(btc_data['priceChangePercent'])
    correlations = []
    
    for item in ticker_data:
        symbol = item['symbol']
        if symbol == 'BTCUSDT':
            continue
        
        try:
            coin_change = float(item['priceChangePercent'])
            
            # Basit korelasyon: aynı yönde hareket ediyorlar mı?
            # Bu gerçek korelasyon değil, sadece anlık yön benzerliği
            if btc_change * coin_change > 0:  # Aynı yön
                pseudo_correlation = min(abs(coin_change / btc_change), 1.0) if btc_change != 0 else 0
            else:  # Ters yön
                pseudo_correlation = -min(abs(coin_change / btc_change), 1.0) if btc_change != 0 else 0
            
            if abs(pseudo_correlation) >= 0.5:  # Eşik
                correlations.append({
                    'coin1': 'BTCUSDT',
                    'coin2': symbol,
                    'correlation': pseudo_correlation,
                    'abs_correlation': abs(pseudo_correlation)
                })
        except (ValueError, KeyError, ZeroDivisionError):
            continue
    
    # Korelasyona göre sırala
    correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
    print(f"✓ {len(correlations)} yüksek korelasyonlu çift bulundu")
    return correlations

def save_results(pv_analyses, sudden_analyses, correlations, total_pairs):
    """Sonuçları JSON dosyalarına kaydet"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Price-Volume Analysis
    pv_output = {
        'timestamp': timestamp,
        'source': 'Binance REST API',
        'exchange': 'Binance',
        'quote_currency': 'USDT',
        'pair_type': 'USDT çiftleri',
        'total_pairs_available': total_pairs,
        'total_coins': len(pv_analyses),
        'analyses': pv_analyses
    }
    with open('price_volume_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(pv_output, f, indent=2, ensure_ascii=False)
    print("✓ price_volume_analysis.json kaydedildi")
    
    # Sudden Changes
    sudden_output = {
        'timestamp': timestamp,
        'source': 'Binance REST API',
        'exchange': 'Binance',
        'quote_currency': 'USDT',
        'pair_type': 'USDT çiftleri',
        'total_pairs_available': total_pairs,
        'total_analyzed': len(pv_analyses),
        'triggered_coins': len(sudden_analyses),
        'analyses': sudden_analyses
    }
    with open('sudden_price_volume_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(sudden_output, f, indent=2, ensure_ascii=False)
    print("✓ sudden_price_volume_analysis.json kaydedildi")
    
    # Correlations
    corr_output = {
        'timestamp': timestamp,
        'source': 'Binance REST API (pseudo-correlation)',
        'exchange': 'Binance',
        'quote_currency': 'USDT',
        'pair_type': 'USDT çiftleri',
        'note': 'Gerçek zamanlı korelasyon için WebSocket gerekli',
        'total_pairs_available': total_pairs,
        'total_coins_analyzed': len(pv_analyses),
        'total_correlation_pairs': len(correlations),
        'correlations': correlations
    }
    with open('realtime_correlations.json', 'w', encoding='utf-8') as f:
        json.dump(corr_output, f, indent=2, ensure_ascii=False)
    print("✓ realtime_correlations.json kaydedildi")

def main():
    print("="*80)
    print("GITHUB ACTIONS - BİNANCE API ANALİZ")
    print("="*80)
    print(f"Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. USDT çiftlerini al
    print("[1/4] USDT çiftleri alınıyor...")
    pairs = fetch_binance_usdt_pairs()
    if not pairs:
        print("❌ USDT çiftleri alınamadı, çıkılıyor...")
        return
    
    # Rate limit için bekleme
    time.sleep(1)
    
    # 2. 24 saatlik ticker verilerini al
    print("\n[2/4] 24 saatlik ticker verileri alınıyor...")
    ticker_data = fetch_24h_ticker(pairs)
    if not ticker_data:
        print("❌ Ticker verileri alınamadı, çıkılıyor...")
        return
    
    # 3. Analizleri yap
    print("\n[3/4] Analizler yapılıyor...")
    pv_analyses = analyze_price_volume(ticker_data)
    sudden_analyses = analyze_sudden_changes(ticker_data, thresholds=[1.0, 2.0, 5.0, 10.0])
    correlations = calculate_simple_correlations(ticker_data)
    
    # 4. Sonuçları kaydet
    print("\n[4/4] Sonuçlar kaydediliyor...")
    save_results(pv_analyses, sudden_analyses, correlations, len(pairs))
    
    print("\n" + "="*80)
    print("✅ ANALİZ TAMAMLANDI")
    print(f"Bitiş: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"- {len(pv_analyses)} coin analiz edildi")
    print(f"- {len(sudden_analyses)} coin ani değişim gösterdi")
    print(f"- {len(correlations)} yüksek korelasyonlu çift bulundu")
    print("="*80)

if __name__ == "__main__":
    main()

