"""
GitHub Actions için HIZLI analiz scripti
Sadece anlık fiyat verilerini çeker - Geçmiş veri çekmez
Çok daha hızlı: ~1-2 dakika
"""
import requests
import json
from datetime import datetime
import time

def fetch_all_coins_from_gecko(max_pages=20):
    """CoinGecko'dan TÜM coinleri çek (pagination ile)"""
    try:
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        coin_mapping = {}
        page = 1
        per_page = 250  # CoinGecko maksimum sayfa başına coin sayısı
        
        print(f'📡 Pagination ile coin çekiliyor (maksimum {max_pages} sayfa)...')
        
        while page <= max_pages:
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': per_page,
                'page': page,
                'sparkline': False
            }
            
            # Rate limit için bekleme (ilk sayfa hariç)
            if page > 1:
                time.sleep(2)
            
            response = requests.get(url, params=params, timeout=20)
            
            if response.status_code == 429:
                print(f'⚠️  Rate limit (sayfa {page})! 60 saniye bekleniyor...')
                time.sleep(60)
                response = requests.get(url, params=params, timeout=20)
            
            if response.status_code != 200:
                print(f'⚠️  Sayfa {page} çekme hatası: HTTP {response.status_code}')
                break
            
            data = response.json()
            
            if not data:
                print(f'  Sayfa {page}: Veri yok, son sayfaya ulaşıldı')
                break
            
            page_count = 0
            for coin in data:
                coin_id = coin.get('id')
                symbol = coin.get('symbol', '').upper() + 'USDT'
                coin_mapping[symbol] = coin_id
                page_count += 1
            
            print(f'  ✓ Sayfa {page}: {page_count} coin eklendi (Toplam: {len(coin_mapping)})')
            
            if len(data) < per_page:
                print(f'  Son sayfaya ulaşıldı (sayfa {page})')
                break
            
            page += 1
        
        print(f'\n✓ Toplam {len(coin_mapping)} coin bulundu ({page-1} sayfa)')
        return coin_mapping
    except Exception as e:
        print(f'⚠️  Coin çekme hatası: {e}')
        import traceback
        traceback.print_exc()
        return {}

def fetch_current_prices_batch(coin_ids_list):
    """CoinGecko'dan toplu anlık fiyat verilerini çek (tek istek)"""
    try:
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
                print(f'  ✓ Batch {i//batch_size + 1}: {len(batch_data)} coin fiyatı alındı')
            else:
                print(f'⚠️  Batch {i//batch_size + 1} hatası: HTTP {response.status_code}')
        
        return all_prices
    except Exception as e:
        print(f'⚠️  Batch fiyat çekme hatası: {e}')
        import traceback
        traceback.print_exc()
        return {}

def analyze_sudden_changes(current_prices, coin_mapping):
    """Ani fiyat değişimlerini analiz et"""
    sudden_analyses = {}
    
    thresholds = [1.0, 2.0, 5.0, 10.0]
    
    for symbol, coin_id in coin_mapping.items():
        if coin_id not in current_prices:
            continue
        
        data = current_prices[coin_id]
        price_change_24h = data.get('usd_24h_change', 0)
        volume_24h = data.get('usd_24h_vol', 0)
        
        # None kontrolü ve varsayılan değer
        if price_change_24h is None:
            price_change_24h = 0
        if volume_24h is None:
            volume_24h = 0
        
        # Sayısal değer kontrolü
        try:
            price_change_24h = float(price_change_24h)
            volume_24h = float(volume_24h)
        except (ValueError, TypeError):
            price_change_24h = 0
            volume_24h = 0
        
        # Ani değişim kontrolü (24 saatlik değişim %1'den fazlaysa)
        if abs(price_change_24h) >= 1.0:
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

def save_price_history(current_prices, coin_mapping, max_history=288):
    """Anlık fiyat verilerini geçmişe ekle (zaman serisi için)"""
    try:
        history_file = 'realtime_price_history.json'
        
        # Mevcut geçmişi yükle
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
        except:
            history_data = {'history': [], 'last_update': None}
        
        # Yeni veri noktası oluştur
        timestamp = datetime.now().isoformat()
        price_point = {
            'timestamp': timestamp,
            'prices': {}
        }
        
        # Her coin için fiyatı kaydet
        for symbol, coin_id in coin_mapping.items():
            if coin_id in current_prices:
                price_data = current_prices[coin_id]
                price_point['prices'][symbol] = {
                    'price': price_data.get('usd', 0),
                    'volume_24h': price_data.get('usd_24h_vol', 0),
                    'change_24h': price_data.get('usd_24h_change', 0)
                }
        
        # Geçmişe ekle
        history_data['history'].append(price_point)
        history_data['last_update'] = timestamp
        
        # Maksimum geçmiş sayısını kontrol et (en eski verileri sil)
        if len(history_data['history']) > max_history:
            history_data['history'] = history_data['history'][-max_history:]
        
        # Kaydet
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)
        
        return len(history_data['history'])
    except Exception as e:
        print(f'⚠️  Geçmiş kaydetme hatası: {e}')
        import traceback
        traceback.print_exc()
        return 0

def calculate_correlation_from_history(history_data, min_data_points=5):
    """Geçmiş verilerden korelasyon hesapla"""
    try:
        import pandas as pd
        import numpy as np
        
        if not history_data or 'history' not in history_data:
            return None, None
        
        history = history_data['history']
        
        if len(history) < min_data_points:
            return None, None
        
        # Son N veriyi al (tüm geçmişi kullan)
        price_data = {}
        
        # Her coin için fiyat serisi oluştur
        for point in history:
            timestamp = point['timestamp']
            for symbol, data in point.get('prices', {}).items():
                if symbol not in price_data:
                    price_data[symbol] = []
                price_data[symbol].append(data['price'])
        
        # En az min_data_points verisi olan coinleri filtrele
        valid_coins = {k: v for k, v in price_data.items() if len(v) >= min_data_points}
        
        if len(valid_coins) < 2:
            return None, None
        
        # DataFrame oluştur
        df = pd.DataFrame(valid_coins)
        
        # Returns hesapla (fiyat değişimleri)
        df_returns = df.pct_change().dropna()
        
        if df_returns.empty or len(df_returns) < 2:
            return None, None
        
        # Korelasyon matrisi
        correlation_matrix = df_returns.corr()
        
        # Yüksek korelasyonları bul
        high_corr = []
        symbols = correlation_matrix.columns.tolist()
        
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols):
                if i < j:
                    corr = correlation_matrix.loc[symbol1, symbol2]
                    if not np.isnan(corr) and abs(corr) >= 0.7:
                        high_corr.append({
                            'coin1': symbol1,
                            'coin2': symbol2,
                            'correlation': float(corr),
                            'abs_correlation': float(abs(corr))
                        })
        
        # Korelasyon değerine göre sırala
        high_corr.sort(key=lambda x: x['abs_correlation'], reverse=True)
        
        return correlation_matrix, high_corr
    except Exception as e:
        print(f'⚠️  Korelasyon hesaplama hatası: {e}')
        import traceback
        traceback.print_exc()
        return None, None

def main():
    print('='*80)
    print('GitHub Actions - HIZLI Coin Analizi (Sadece Anlık Veriler)')
    print('='*80)
    
    start_time = time.time()
    
    # 1. TÜM coinleri çek
    print('\n[1/4] TÜM coinler çekiliyor...')
    coin_mapping = fetch_all_coins_from_gecko(max_pages=20)
    
    if not coin_mapping:
        print('❌ Coin listesi alınamadı!')
        return
    
    coin_ids_list = list(coin_mapping.values())
    print(f'✓ {len(coin_mapping)} coin bulundu\n')
    
    # 2. Anlık fiyat verileri (TÜM coinler - batch)
    print('[2/4] Anlık fiyat verileri çekiliyor (Batch - TÜM coinler)...')
    current_prices = fetch_current_prices_batch(coin_ids_list)
    
    if not current_prices:
        print('❌ Anlık fiyat verisi alınamadı!')
        return
    
    print(f'✓ {len(current_prices)} coin için anlık fiyat verisi alındı\n')
    
    # 3. Anlık verileri geçmişe ekle (zaman serisi için)
    print('[3/4] Anlık veriler geçmişe ekleniyor...')
    history_count = save_price_history(current_prices, coin_mapping, max_history=288)
    print(f'✓ Geçmiş veri noktası sayısı: {history_count}\n')
    
    # 4. Ani değişim analizi
    print('[4/4] Ani değişim analizi yapılıyor...')
    sudden_analyses = analyze_sudden_changes(current_prices, coin_mapping)
    
    if sudden_analyses:
        sudden_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analyses': {}
        }
        
        for symbol, analysis in sudden_analyses.items():
            sudden_data['analyses'][symbol] = analysis
        
        with open('sudden_price_volume_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(sudden_data, f, indent=2, ensure_ascii=False)
        print(f'✓ Ani değişim analizi kaydedildi! ({len(sudden_analyses)} coin)')
    else:
        print('⚠️  Ani değişim analizi sonucu boş! (24 saatlik değişim %1\'den az)')
    
    elapsed_time = time.time() - start_time
    print('\n' + '='*80)
    print('✅ HIZLI Analiz tamamlandı!')
    print(f'📊 Toplam {len(coin_mapping)} coin analiz edildi')
    print(f'📈 Geçmiş veri noktası: {history_count}')
    print(f'⏱️  Toplam süre: {elapsed_time:.1f} saniye (~{elapsed_time/60:.1f} dakika)')
    print('='*80)

if __name__ == '__main__':
    main()

