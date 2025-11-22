"""
GitHub Actions için özel analiz scripti
CoinGecko API kullanılıyor - Maksimum coin sayısı ile
CoinGecko ücretsiz plan: 5-15 req/min
"""
import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import time

def fetch_top_coins_from_gecko(limit=100):
    """CoinGecko'dan en popüler coinleri çek (tek istek)"""
    try:
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',  # Market cap'e göre sırala
            'per_page': limit,  # Maksimum 250
            'page': 1,
            'sparkline': False
        }
        
        # Rate limit için bekleme
        time.sleep(2)
        
        response = requests.get(url, params=params, timeout=20)
        
        if response.status_code == 429:
            print('⚠️  Rate limit! 60 saniye bekleniyor...')
            time.sleep(60)
            response = requests.get(url, params=params, timeout=20)
        
        if response.status_code != 200:
            print(f'⚠️  Top coinler çekme hatası: HTTP {response.status_code}')
            return {}
        
        data = response.json()
        
        # Coin ID'lerini ve symbol'lerini eşleştir
        coin_mapping = {}
        for coin in data:
            coin_id = coin.get('id')
            symbol = coin.get('symbol', '').upper() + 'USDT'  # Binance formatına çevir
            coin_mapping[symbol] = coin_id
        
        print(f'✓ {len(coin_mapping)} coin bulundu (Top {limit})')
        return coin_mapping
    except Exception as e:
        print(f'⚠️  Top coinler çekme hatası: {e}')
        return {}

def fetch_current_prices_batch(coin_ids_list):
    """CoinGecko'dan toplu anlık fiyat verilerini çek (tek istek)"""
    try:
        # CoinGecko batch limit: 250 coin
        # Eğer daha fazla varsa, parçalara böl
        batch_size = 250
        all_prices = {}
        
        for i in range(0, len(coin_ids_list), batch_size):
            batch = coin_ids_list[i:i+batch_size]
            ids_str = ','.join(batch)
            
            url = f'https://api.coingecko.com/api/v3/simple/price'
            params = {
                'ids': ids_str,
                'vs_currencies': 'usd',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true'
            }
            
            # Rate limit için bekleme
            if i > 0:
                time.sleep(2)
            
            response = requests.get(url, params=params, timeout=20)
            
            if response.status_code == 429:
                print(f'⚠️  Rate limit (batch {i//batch_size + 1})! 60 saniye bekleniyor...')
                time.sleep(60)
                response = requests.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                batch_data = response.json()
                all_prices.update(batch_data)
            else:
                print(f'⚠️  Batch {i//batch_size + 1} hatası: HTTP {response.status_code}')
        
        return all_prices
    except Exception as e:
        print(f'⚠️  Batch fiyat çekme hatası: {e}')
        return {}

def fetch_historical_single(coin_id, days=7):
    """CoinGecko'dan tek coin için geçmiş fiyat ve volume verilerini çek"""
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart'
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'  # Günlük veri (daha az veri, daha hızlı)
        }
        
        # Rate limit için bekleme (CoinGecko: 5-15 req/min)
        time.sleep(6)  # Her istek arasında 6 saniye
        
        response = requests.get(url, params=params, timeout=20)
        
        if response.status_code == 429:
            print(f'⚠️  {coin_id}: Rate limit! 60 saniye bekleniyor...')
            time.sleep(60)
            response = requests.get(url, params=params, timeout=20)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        if 'prices' not in data or not data['prices']:
            return None
        
        # Format: [[timestamp_ms, price], ...]
        prices = [float(price) for _, price in data['prices']]
        timestamps = [datetime.fromtimestamp(ts / 1000) for ts, _ in data['prices']]
        
        # Volume verisi de çek (total_volumes)
        volumes = []
        if 'total_volumes' in data and data['total_volumes']:
            volumes = [float(vol) for _, vol in data['total_volumes']]
        else:
            volumes = [0] * len(prices)  # Volume yoksa 0
        
        return {
            'prices': prices,
            'volumes': volumes,
            'timestamps': timestamps
        }
    except Exception as e:
        return None

def calculate_correlation_matrix(price_data_dict, use_returns=True):
    """Korelasyon matrisi hesapla"""
    if len(price_data_dict) < 2:
        return None
    
    # Tüm coinlerin ortak zaman noktalarını bul
    all_timestamps = set()
    for symbol, data in price_data_dict.items():
        all_timestamps.update(data['timestamps'])
    
    all_timestamps = sorted(list(all_timestamps))
    
    # Her coin için fiyat serisi oluştur
    price_series = {}
    for symbol, data in price_data_dict.items():
        ts_to_price = dict(zip(data['timestamps'], data['prices']))
        series = []
        for ts in all_timestamps:
            if ts in ts_to_price:
                series.append(ts_to_price[ts])
            else:
                series.append(np.nan)
        price_series[symbol] = series
    
    # DataFrame oluştur
    df = pd.DataFrame(price_series, index=all_timestamps)
    
    # NaN değerleri doldur
    df = df.fillna(method='ffill').fillna(method='bfill')
    
    # Returns hesapla
    if use_returns:
        df = df.pct_change().dropna()
    
    # Korelasyon matrisi
    correlation_matrix = df.corr()
    
    return correlation_matrix

def find_high_correlations(correlation_matrix, threshold=0.7):
    """Yüksek korelasyonları bul"""
    high_corr = []
    symbols = correlation_matrix.columns.tolist()
    
    for i, symbol1 in enumerate(symbols):
        for j, symbol2 in enumerate(symbols):
            if i < j:  # Sadece üst üçgen
                corr = correlation_matrix.loc[symbol1, symbol2]
                if not np.isnan(corr) and abs(corr) >= threshold:
                    high_corr.append({
                        'coin1': symbol1,
                        'coin2': symbol2,
                        'correlation': float(corr),
                        'abs_correlation': float(abs(corr))
                    })
    
    # Korelasyon değerine göre sırala
    high_corr.sort(key=lambda x: x['abs_correlation'], reverse=True)
    
    return high_corr

def save_correlations(high_corr, filename='realtime_correlations.json'):
    """Korelasyonları JSON'a kaydet"""
    data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'high_correlations': high_corr,
        'total_pairs': len(high_corr)
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_correlation_matrix(correlation_matrix, filename='realtime_correlation_matrix.csv'):
    """Korelasyon matrisini CSV'ye kaydet"""
    correlation_matrix.to_csv(filename)

def analyze_sudden_changes(current_prices, coin_mapping):
    """Ani fiyat değişimlerini analiz et"""
    sudden_analyses = {}
    
    # Eşikler: %1, %2, %5, %10
    thresholds = [1.0, 2.0, 5.0, 10.0]
    
    for symbol, coin_id in coin_mapping.items():
        if coin_id not in current_prices:
            continue
        
        data = current_prices[coin_id]
        price_change_24h = data.get('usd_24h_change', 0)
        volume_24h = data.get('usd_24h_vol', 0)
        
        # Ani değişim kontrolü (24 saatlik değişim %2'den fazlaysa)
        if abs(price_change_24h) >= 2.0:
            sudden_analyses[symbol] = {
                'price_change_24h': price_change_24h,
                'volume_24h': volume_24h,
                'price': data.get('usd', 0),
                'thresholds': {}
            }
            
            # Her eşik için kontrol
            for threshold in thresholds:
                if abs(price_change_24h) >= threshold:
                    sudden_analyses[symbol]['thresholds'][f'{threshold}%'] = {
                        'triggered': True,
                        'price_change': price_change_24h,
                        'volume': volume_24h
                    }
    
    return sudden_analyses

def main():
    print('='*80)
    print('GitHub Actions - Coin Korelasyon Analizi (CoinGecko API)')
    print('='*80)
    
    # 1. Top coinleri çek (maksimum 100)
    print('\n[0/3] Top coinler çekiliyor (CoinGecko markets endpoint)...')
    coin_mapping = fetch_top_coins_from_gecko(limit=100)
    
    if not coin_mapping:
        print('❌ Coin listesi alınamadı!')
        return
    
    popular_coins = list(coin_mapping.keys())
    coin_ids_list = list(coin_mapping.values())
    
    print(f'\n{len(popular_coins)} coin için analiz yapılıyor...')
    print('📡 CoinGecko API kullanılıyor (Rate limit: 5-15 req/min)')
    print('⏱️  Her istek arasında 6 saniye bekleniyor...')
    print(f'⏱️  Tahmini süre: ~{min(len(popular_coins), 100) * 6 / 60:.1f} dakika (maksimum 100 coin)\n')
    
    # 2. Geçmiş veri çek ve korelasyon analizi (maksimum 100 coin - rate limit için)
    print('[1/3] Geçmiş veri analizi yapılıyor (CoinGecko)...')
    print(f'⚠️  Rate limit nedeniyle maksimum 100 coin için geçmiş veri çekiliyor...')
    
    historical_data = {}
    successful = 0
    max_coins_for_history = min(100, len(popular_coins))  # Rate limit için maksimum 100
    
    for i, (symbol, coin_id) in enumerate(list(coin_mapping.items())[:max_coins_for_history], 1):
        print(f'  [{i}/{max_coins_for_history}] {symbol} ({coin_id}) verisi çekiliyor...', end=' ')
        data = fetch_historical_single(coin_id, days=7)  # Son 7 gün, günlük
        if data and len(data['prices']) > 0:
            historical_data[symbol] = data
            successful += 1
            print(f'✓ ({len(data["prices"])} veri)')
        else:
            print('✗')
    
    print(f'\n✓ {successful}/{max_coins_for_history} coin için geçmiş veri toplandı\n')
    
    if len(historical_data) >= 2:
        # Korelasyon analizi
        print('Korelasyon matrisi hesaplanıyor...')
        try:
            correlation_matrix = calculate_correlation_matrix(historical_data, use_returns=True)
            
            if correlation_matrix is not None and not correlation_matrix.empty:
                # Yüksek korelasyonları bul
                high_corr = find_high_correlations(correlation_matrix, threshold=0.7)
                
                # Kaydet
                save_correlations(high_corr, 'realtime_correlations.json')
                save_correlation_matrix(correlation_matrix, 'realtime_correlation_matrix.csv')
                
                print(f'✓ Korelasyon analizi kaydedildi! ({len(high_corr)} yüksek korelasyon çifti)')
            else:
                print('⚠️  Korelasyon analizi sonucu boş!')
        except Exception as e:
            print(f'⚠️  Korelasyon analizi hatası: {e}')
            import traceback
            traceback.print_exc()
    
    # 3. Fiyat-Volume analizi (Geçmiş verilerden korelasyon hesapla)
    print('\n[2/3] Fiyat-Volume korelasyon analizi yapılıyor...')
    try:
        if historical_data:
            # Geçmiş verilerden fiyat-volume korelasyonu hesapla
            pv_analyses = {}
            
            for symbol, data in historical_data.items():
                prices = data['prices']
                volumes = data.get('volumes', [])
                timestamps = data['timestamps']
                
                # Volume verisi yoksa veya yetersizse, sıfırlarla doldur
                if not volumes or len(volumes) < len(prices):
                    volumes = [0] * len(prices)
                
                # Fiyat ve volume değişimlerini hesapla
                price_changes = []
                volume_changes = []
                
                for i in range(1, len(prices)):
                    if prices[i-1] != 0:
                        price_change = (prices[i] - prices[i-1]) / prices[i-1]
                        price_changes.append(price_change)
                    else:
                        price_changes.append(0)
                    
                    if volumes[i-1] != 0:
                        volume_change = (volumes[i] - volumes[i-1]) / volumes[i-1]
                        volume_changes.append(volume_change)
                    else:
                        # Volume yoksa veya sıfırsa, küçük bir değer kullan (korelasyon hesaplaması için)
                        volume_changes.append(0)
                
                # Korelasyon hesapla (en az 2 veri noktası gerekli)
                if len(price_changes) >= 2 and len(volume_changes) >= 2:
                    df_temp = pd.DataFrame({
                        'price_change': price_changes,
                        'volume_change': volume_changes
                    })
                    correlation = df_temp['price_change'].corr(df_temp['volume_change'])
                    
                    # NaN kontrolü ve volume verisi kontrolü
                    if np.isnan(correlation):
                        correlation = 0.0  # Volume verisi yoksa korelasyon 0
                    
                    # Volume verisi varsa ve geçerliyse korelasyonu kullan
                    has_volume_data = any(v != 0 for v in volumes) if volumes else False
                    
                    # Fiyat artışı olduğunda volume artışı analizi
                    price_up_indices = [i for i, pc in enumerate(price_changes) if pc > 0]
                    if price_up_indices and has_volume_data:
                        volume_changes_on_price_up = [volume_changes[i] for i in price_up_indices]
                        volume_increase_count = sum(1 for vc in volume_changes_on_price_up if vc > 0)
                        volume_increase_pct = (volume_increase_count / len(volume_changes_on_price_up)) * 100 if volume_changes_on_price_up else 0
                        avg_volume_change_on_price_up = np.mean(volume_changes_on_price_up) * 100 if volume_changes_on_price_up else 0
                    else:
                        volume_increase_pct = 0
                        avg_volume_change_on_price_up = 0
                    
                    # Volume verisi yoksa bile coin'i kaydet (korelasyon 0 olacak)
                    pv_analyses[symbol] = {
                        'correlation': float(correlation) if has_volume_data else 0.0,
                        'abs_correlation': float(abs(correlation)) if has_volume_data else 0.0,
                        'data_points': len(price_changes),
                        'volume_increase_on_price_up_pct': float(volume_increase_pct),
                        'avg_volume_change_on_price_up': float(avg_volume_change_on_price_up)
                    }
            
            if pv_analyses:
                # Eski format ile uyumlu kaydet
                with open('price_volume_analysis.json', 'w', encoding='utf-8') as f:
                    json.dump(pv_analyses, f, indent=2, ensure_ascii=False)
                print(f'✓ Fiyat-Volume korelasyon analizi kaydedildi! ({len(pv_analyses)} coin)')
            else:
                print('⚠️  Fiyat-Volume korelasyon analizi sonucu boş!')
        else:
            print('⚠️  Geçmiş veri olmadığı için fiyat-volume korelasyonu hesaplanamadı!')
    except Exception as e:
        print(f'⚠️  Fiyat-Volume analizi hatası: {e}')
        import traceback
        traceback.print_exc()
    
    # 4. Anlık fiyat verileri (TÜM coinler - batch)
    print('\n[3/4] Anlık fiyat verileri çekiliyor (CoinGecko - Batch - TÜM coinler)...')
    try:
        current_prices = fetch_current_prices_batch(coin_ids_list)
        
        if current_prices:
            # Anlık verileri ayrı bir dosyaya kaydet (isteğe bağlı)
            print(f'✓ {len(current_prices)} coin için anlık fiyat verisi alındı')
        else:
            print('⚠️  Anlık fiyat verisi alınamadı!')
    except Exception as e:
        print(f'⚠️  Anlık fiyat çekme hatası: {e}')
    
    # 5. Ani değişim analizi (TÜM coinler)
    print('\n[4/4] Ani değişim analizi yapılıyor (TÜM coinler)...')
    try:
        if current_prices:
            sudden_analyses = analyze_sudden_changes(current_prices, coin_mapping)
            
            if sudden_analyses:
                sudden_data = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'analyses': {}
                }
                
                # Format: { "BTCUSDT": { "thresholds": {...}, ... } }
                for symbol, analysis in sudden_analyses.items():
                    sudden_data['analyses'][symbol] = analysis
                
                with open('sudden_price_volume_analysis.json', 'w', encoding='utf-8') as f:
                    json.dump(sudden_data, f, indent=2, ensure_ascii=False)
                print(f'✓ Ani değişim analizi kaydedildi! ({len(sudden_analyses)} coin)')
            else:
                print('⚠️  Ani değişim analizi sonucu boş! (24 saatlik değişim %2\'den az)')
        else:
            print('⚠️  Anlık fiyat verisi olmadığı için ani değişim analizi yapılamadı!')
    except Exception as e:
        print(f'⚠️  Ani değişim analizi hatası: {e}')
        import traceback
        traceback.print_exc()
    
    print('\n' + '='*80)
    print('✅ Analiz tamamlandı!')
    print(f'📊 Toplam {len(popular_coins)} coin analiz edildi')
    print('='*80)

if __name__ == '__main__':
    main()
