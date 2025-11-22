"""
GitHub Actions için özel analiz scripti
Binance API bölge kısıtlaması sorununu çözmek için direkt REST API kullanır
TAMAMEN BAĞIMSIZ - correlation_analyzer.py'yi import etmiyor
"""
import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os

def fetch_klines(symbol, interval='1h', limit=200):
    """Binance klines endpoint'inden veri çek (bölge kısıtlaması yok)"""
    try:
        url = f'https://api.binance.com/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 451:
            print(f'⚠️  {symbol}: Bölge kısıtlaması (HTTP 451) - atlanıyor')
            return None
        
        if response.status_code != 200:
            print(f'⚠️  {symbol}: HTTP {response.status_code} - atlanıyor')
            return None
        
        data = response.json()
        if not data:
            return None
        
        # Klines formatı: [Open time, Open, High, Low, Close, Volume, ...]
        prices = [float(k[4]) for k in data]  # Close price
        timestamps = [datetime.fromtimestamp(k[0] / 1000) for k in data]
        
        return {
            'prices': prices,
            'timestamps': timestamps
        }
    except Exception as e:
        print(f'⚠️  {symbol}: Hata - {e}')
        return None

def calculate_returns(prices):
    """Fiyat değişimlerini hesapla"""
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        else:
            returns.append(0)
    return returns

def calculate_correlation_matrix(price_data_dict, use_returns=True):
    """Korelasyon matrisi hesapla"""
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
    
    # NaN değerleri doldur (forward fill)
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

def analyze_price_volume_24hr(popular_coins):
    """24 saatlik ticker verilerinden fiyat-volume analizi"""
    price_volume_data = {}
    
    for symbol in popular_coins:
        try:
            url = f'https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}'
            response = requests.get(url, timeout=10)
            
            if response.status_code == 451:
                continue  # Bölge kısıtlaması - atla
            
            if response.status_code == 200:
                data = response.json()
                now = datetime.now()
                # Son 24 saatlik veriyi simüle et
                price_volume_data[symbol] = {
                    'price': float(data['lastPrice']),
                    'volume': float(data['volume']),
                    'price_change_percent': float(data['priceChangePercent']),
                    'timestamp': now
                }
        except:
            continue
    
    # Basit analiz sonuçları
    analyses = []
    for symbol, data in price_volume_data.items():
        analyses.append({
            'symbol': symbol,
            'price': data['price'],
            'volume': data['volume'],
            'price_change_percent': data['price_change_percent'],
            'timestamp': data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return analyses

def main():
    print('='*80)
    print('GitHub Actions - Binance Coin Korelasyon Analizi')
    print('='*80)
    
    # Popüler coinler (önceden tanımlı - exchangeInfo KULLANMIYORUZ)
    popular_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 
                     'XRPUSDT', 'DOGEUSDT', 'DOTUSDT', 'LINKUSDT', 'LTCUSDT',
                     'AVAXUSDT', 'MATICUSDT', 'UNIUSDT', 'ATOMUSDT', 'ETCUSDT',
                     'FILUSDT', 'TRXUSDT', 'XLMUSDT', 'ALGOUSDT', 'VETUSDT',
                     'AAVEUSDT', 'MKRUSDT', 'COMPUSDT', 'SANDUSDT', 'MANAUSDT',
                     'AXSUSDT', 'THETAUSDT', 'EOSUSDT', 'NEARUSDT', 'FLOWUSDT']
    
    print(f'\n{len(popular_coins)} coin için analiz yapılıyor...')
    print('⚠️  NOT: exchangeInfo endpoint\'i KULLANILMIYOR (bölge kısıtlaması yok)\n')
    
    # 1. Geçmiş veri çek ve korelasyon analizi
    print('[1/2] Geçmiş veri analizi yapılıyor...')
    historical_data = {}
    successful = 0
    
    for symbol in popular_coins:
        print(f'  {symbol} verisi çekiliyor...', end=' ')
        data = fetch_klines(symbol, interval='1h', limit=200)
        if data:
            historical_data[symbol] = data
            successful += 1
            print('✓')
        else:
            print('✗')
    
    print(f'\n✓ {successful}/{len(popular_coins)} coin için veri toplandı\n')
    
    if len(historical_data) < 2:
        print('❌ Yetersiz veri! En az 2 coin gerekli.')
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
    
    # 2. Fiyat-Volume analizi
    print('\n[2/2] Fiyat-Volume analizi yapılıyor...')
    try:
        analyses = analyze_price_volume_24hr(popular_coins)
        if analyses:
            # Basit JSON formatı
            pv_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'analyses': analyses
            }
            with open('price_volume_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(pv_data, f, indent=2, ensure_ascii=False)
            print(f'✓ Fiyat-Volume analizi kaydedildi! ({len(analyses)} coin)')
        else:
            print('⚠️  Fiyat-Volume analizi sonucu boş!')
    except Exception as e:
        print(f'⚠️  Fiyat-Volume analizi hatası: {e}')
        import traceback
        traceback.print_exc()
    
    print('\n' + '='*80)
    print('✅ Analiz tamamlandı!')
    print('='*80)

if __name__ == '__main__':
    main()
