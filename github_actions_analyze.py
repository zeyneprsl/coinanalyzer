"""
GitHub Actions için özel analiz scripti
CoinGecko API kullanılıyor - Rate limit yönetimi ile
CoinGecko ücretsiz plan: 5-15 req/min
"""
import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import time

# En popüler 15 coin (rate limit için azaltıldı)
COIN_IDS = {
    'BTCUSDT': 'bitcoin',
    'ETHUSDT': 'ethereum',
    'BNBUSDT': 'binancecoin',
    'SOLUSDT': 'solana',
    'ADAUSDT': 'cardano',
    'XRPUSDT': 'ripple',
    'DOGEUSDT': 'dogecoin',
    'DOTUSDT': 'polkadot',
    'LINKUSDT': 'chainlink',
    'LTCUSDT': 'litecoin',
    'AVAXUSDT': 'avalanche-2',
    'MATICUSDT': 'matic-network',
    'UNIUSDT': 'uniswap',
    'ATOMUSDT': 'cosmos',
    'ETCUSDT': 'ethereum-classic'
}

def fetch_current_prices_batch(coin_ids_list):
    """CoinGecko'dan toplu anlık fiyat verilerini çek (tek istek)"""
    try:
        ids_str = ','.join(coin_ids_list)
        url = f'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': ids_str,
            'vs_currencies': 'usd',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        
        # Rate limit için bekleme
        time.sleep(2)
        
        response = requests.get(url, params=params, timeout=20)
        
        if response.status_code == 429:
            print('⚠️  Rate limit! 60 saniye bekleniyor...')
            time.sleep(60)
            response = requests.get(url, params=params, timeout=20)
        
        if response.status_code != 200:
            print(f'⚠️  Batch fiyat çekme hatası: HTTP {response.status_code}')
            return {}
        
        data = response.json()
        return data
    except Exception as e:
        print(f'⚠️  Batch fiyat çekme hatası: {e}')
        return {}

def fetch_historical_single(coin_id, days=7):
    """CoinGecko'dan tek coin için geçmiş fiyat verilerini çek"""
    try:
        url = f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart'
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'  # Günlük veri (daha az veri, daha hızlı)
        }
        
        # Rate limit için uzun bekleme (CoinGecko: 5-15 req/min)
        time.sleep(8)  # Güvenli bekleme
        
        response = requests.get(url, params=params, timeout=20)
        
        if response.status_code == 429:
            print(f'⚠️  {coin_id}: Rate limit! 60 saniye bekleniyor...')
            time.sleep(60)
            response = requests.get(url, params=params, timeout=20)
        
        if response.status_code != 200:
            print(f'⚠️  {coin_id}: HTTP {response.status_code}')
            return None
        
        data = response.json()
        if 'prices' not in data or not data['prices']:
            return None
        
        # Format: [[timestamp_ms, price], ...]
        prices = [float(price) for _, price in data['prices']]
        timestamps = [datetime.fromtimestamp(ts / 1000) for ts, _ in data['prices']]
        
        return {
            'prices': prices,
            'timestamps': timestamps
        }
    except Exception as e:
        print(f'⚠️  {coin_id}: Hata - {e}')
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

def main():
    print('='*80)
    print('GitHub Actions - Coin Korelasyon Analizi (CoinGecko API)')
    print('='*80)
    
    popular_coins = list(COIN_IDS.keys())
    coin_ids_list = list(COIN_IDS.values())
    
    print(f'\n{len(popular_coins)} coin için analiz yapılıyor...')
    print('📡 CoinGecko API kullanılıyor (Rate limit: 5-15 req/min)')
    print('⏱️  Her istek arasında 8 saniye bekleniyor...\n')
    
    # 1. Geçmiş veri çek ve korelasyon analizi
    print('[1/2] Geçmiş veri analizi yapılıyor (CoinGecko)...')
    historical_data = {}
    successful = 0
    
    for i, (symbol, coin_id) in enumerate(COIN_IDS.items(), 1):
        print(f'  [{i}/{len(COIN_IDS)}] {symbol} ({coin_id}) verisi çekiliyor...', end=' ')
        data = fetch_historical_single(coin_id, days=7)  # Son 7 gün, günlük
        if data and len(data['prices']) > 0:
            historical_data[symbol] = data
            successful += 1
            print(f'✓ ({len(data["prices"])} veri)')
        else:
            print('✗')
    
    print(f'\n✓ {successful}/{len(popular_coins)} coin için veri toplandı\n')
    
    if len(historical_data) < 2:
        print('❌ Yetersiz veri! En az 2 coin gerekli.')
        print('💡 Not: CoinGecko rate limit nedeniyle bazı coinler atlanmış olabilir.')
        return
    
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
    
    # 2. Fiyat-Volume analizi (anlık veriler - batch)
    print('\n[2/2] Fiyat-Volume analizi yapılıyor (CoinGecko - Batch)...')
    try:
        current_prices = fetch_current_prices_batch(coin_ids_list)
        
        if current_prices:
            analyses = []
            for symbol, coin_id in COIN_IDS.items():
                if coin_id in current_prices:
                    data = current_prices[coin_id]
                    analyses.append({
                        'symbol': symbol,
                        'price': data.get('usd', 0),
                        'volume_24h': data.get('usd_24h_vol', 0),
                        'price_change_24h': data.get('usd_24h_change', 0),
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            if analyses:
                pv_data = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'analyses': analyses
                }
                with open('price_volume_analysis.json', 'w', encoding='utf-8') as f:
                    json.dump(pv_data, f, indent=2, ensure_ascii=False)
                print(f'✓ Fiyat-Volume analizi kaydedildi! ({len(analyses)} coin)')
            else:
                print('⚠️  Fiyat-Volume analizi sonucu boş!')
        else:
            print('⚠️  Anlık fiyat verisi alınamadı!')
    except Exception as e:
        print(f'⚠️  Fiyat-Volume analizi hatası: {e}')
        import traceback
        traceback.print_exc()
    
    print('\n' + '='*80)
    print('✅ Analiz tamamlandı!')
    print('='*80)

if __name__ == '__main__':
    main()
