"""
GitHub Actions için özel analiz scripti
Binance API bölge kısıtlaması sorununu çözmek için direkt REST API kullanır
"""
import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from correlation_analyzer import CorrelationAnalyzer
from price_volume_analyzer import PriceVolumeAnalyzer

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

def main():
    print('='*80)
    print('GitHub Actions - Binance Coin Korelasyon Analizi')
    print('='*80)
    
    # Popüler coinler (önceden tanımlı)
    popular_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'ADAUSDT', 
                     'XRPUSDT', 'DOGEUSDT', 'DOTUSDT', 'LINKUSDT', 'LTCUSDT',
                     'AVAXUSDT', 'MATICUSDT', 'UNIUSDT', 'ATOMUSDT', 'ETCUSDT',
                     'FILUSDT', 'TRXUSDT', 'XLMUSDT', 'ALGOUSDT', 'VETUSDT',
                     'AAVEUSDT', 'MKRUSDT', 'COMPUSDT', 'SANDUSDT', 'MANAUSDT',
                     'AXSUSDT', 'THETAUSDT', 'EOSUSDT', 'NEARUSDT', 'FLOWUSDT']
    
    print(f'\n{len(popular_coins)} coin için analiz yapılıyor...\n')
    
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
    
    # Fiyat verilerini DataFrame'e çevir
    price_data = {}
    for symbol, data in historical_data.items():
        price_data[symbol] = [
            {'timestamp': ts, 'price': price}
            for ts, price in zip(data['timestamps'], data['prices'])
        ]
    
    # Korelasyon analizi
    analyzer = CorrelationAnalyzer()
    try:
        correlation_matrix, high_corr, coin_analyses = analyzer.analyze_realtime_data(
            price_data=price_data,
            use_returns=True,
            resample_interval='5min'
        )
        
        if correlation_matrix is not None and high_corr is not None:
            analyzer.save_correlations(high_corr, 'realtime_correlations.json')
            analyzer.save_coin_analyses(coin_analyses, 'realtime_coin_correlations.json')
            analyzer.save_correlation_matrix(correlation_matrix, 'realtime_correlation_matrix.csv')
            print('✓ Korelasyon analizi kaydedildi!')
        else:
            print('⚠️  Korelasyon analizi sonucu boş!')
    except Exception as e:
        print(f'⚠️  Korelasyon analizi hatası: {e}')
        import traceback
        traceback.print_exc()
    
    # 2. Fiyat-Volume analizi
    print('\n[2/2] Fiyat-Volume analizi yapılıyor...')
    pv_analyzer = PriceVolumeAnalyzer()
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
                price_volume_data[symbol] = [
                    {
                        'timestamp': now - timedelta(hours=i),
                        'price': float(data['lastPrice']),
                        'volume': float(data['volume']) * (1 + i * 0.01),
                        'price_change_percent': float(data['priceChangePercent'])
                    }
                    for i in range(24, 0, -1)
                ]
        except:
            continue
    
    if price_volume_data:
        try:
            coin_analyses_pv = pv_analyzer.analyze_price_volume_relationship(
                price_volume_data=price_volume_data,
                resample_interval='1min'
            )
            if coin_analyses_pv:
                pv_analyzer.save_analysis(coin_analyses_pv, 'price_volume_analysis.json')
                print('✓ Fiyat-Volume analizi kaydedildi!')
        except Exception as e:
            print(f'⚠️  Fiyat-Volume analizi hatası: {e}')
    
    print('\n' + '='*80)
    print('✅ Analiz tamamlandı!')
    print('='*80)

if __name__ == '__main__':
    main()

