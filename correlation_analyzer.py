import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
import json
from collections import defaultdict

class CorrelationAnalyzer:
    def __init__(self, base_url="https://api.binance.com/api/v3", 
                 min_data_points=50, correlation_threshold=0.7):
        """
        base_url: Binance REST API base URL
        min_data_points: Minimum veri noktası sayısı (korelasyon için yeterli veri)
        correlation_threshold: Yüksek korelasyon eşiği (0.7 = %70 korelasyon)
        """
        self.base_url = base_url
        self.min_data_points = min_data_points
        self.correlation_threshold = correlation_threshold
        
    # ==================== GEÇMİŞ VERİ ÇEKME (REST API) ====================
    
    def fetch_historical_data(self, symbol, interval='1m', limit=500):
        """Binance REST API'den geçmiş fiyat verilerini çek
        
        symbol: Coin çifti (örn: 'BTCUSDT')
        interval: Zaman aralığı ('1m', '5m', '1h', '1d' vb.)
        limit: Kaç veri noktası (maksimum 1000)
        """
        try:
            url = f"{self.base_url}/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Klines formatı: [Open time, Open, High, Low, Close, Volume, ...]
            # Close price'ı al (index 4)
            prices = []
            timestamps = []
            
            for kline in data:
                timestamp = datetime.fromtimestamp(kline[0] / 1000)  # Unix timestamp (ms)
                close_price = float(kline[4])  # Close price
                timestamps.append(timestamp)
                prices.append(close_price)
            
            return {
                'symbol': symbol,
                'timestamps': timestamps,
                'prices': prices
            }
            
        except Exception as e:
            print(f"  {symbol} geçmiş veri çekme hatası: {e}")
            return None
    
    def fetch_all_historical_data(self, symbols, interval='1m', limit=500, delay=0.1):
        """Tüm coinler için geçmiş verileri çek
        
        symbols: Coin çiftleri listesi
        interval: Zaman aralığı
        limit: Her coin için kaç veri noktası
        delay: İstekler arası bekleme (rate limit için)
        """
        print(f"\n{'='*80}")
        print("GEÇMİŞ VERİLER ÇEKİLİYOR (REST API)")
        print(f"{'='*80}")
        print(f"Toplam {len(symbols)} coin için veri çekiliyor...")
        print(f"Interval: {interval}, Limit: {limit}")
        
        historical_data = {}
        successful = 0
        failed = 0
        
        for i, symbol in enumerate(symbols, 1):
            print(f"[{i}/{len(symbols)}] {symbol} çekiliyor...", end=' ')
            
            data = self.fetch_historical_data(symbol, interval, limit)
            
            if data and len(data['prices']) > 0:
                historical_data[symbol] = data
                successful += 1
                print(f"✓ ({len(data['prices'])} veri)")
            else:
                failed += 1
                print("✗")
            
            # Rate limit için bekleme
            if i < len(symbols):
                time.sleep(delay)
        
        print(f"\n✓ Başarılı: {successful}, ✗ Başarısız: {failed}")
        return historical_data
    
    def prepare_historical_dataframe(self, historical_data):
        """Geçmiş verileri DataFrame'e dönüştür"""
        print("\nGeçmiş veriler DataFrame'e dönüştürülüyor...")
        
        price_series = {}
        
        for symbol, data in historical_data.items():
            if len(data['prices']) < 2:
                continue
            
            # Series oluştur
            series = pd.Series(data['prices'], index=data['timestamps'], name=symbol)
            price_series[symbol] = series
        
        if not price_series:
            print("Yeterli geçmiş veri bulunamadı!")
            return None
        
        # DataFrame oluştur
        df = pd.DataFrame(price_series)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        print(f"Geçmiş veri DataFrame hazırlandı: {len(df)} satır, {len(df.columns)} coin")
        return df
    
    # ==================== ANLIK VERİ İŞLEME (WEBSOCKET) ====================
    
    def prepare_realtime_dataframe(self, price_data):
        """WebSocket'ten gelen anlık verileri DataFrame'e dönüştür
        
        price_data: binance_websocket'ten gelen price_data dict'i
        Format: {symbol: [{'timestamp': datetime, 'price': float}, ...]}
        """
        print("\nAnlık veriler DataFrame'e dönüştürülüyor...")
        
        price_series = {}
        
        for symbol, data_list in price_data.items():
            if len(data_list) < 2:
                continue
            
            # Timestamp ve price'ı ayır
            timestamps = [item['timestamp'] for item in data_list]
            prices = [item['price'] for item in data_list]
            
            # Series oluştur
            series = pd.Series(prices, index=timestamps, name=symbol)
            price_series[symbol] = series
        
        if not price_series:
            print("Yeterli anlık veri bulunamadı!")
            return None
        
        # DataFrame oluştur
        df = pd.DataFrame(price_series)
        df.index = pd.to_datetime(df.index)
        
        # Duplicate timestamp'leri temizle
        df = df.groupby(df.index).first()
        df = df.sort_index()
        
        print(f"Anlık veri DataFrame hazırlandı: {len(df)} satır, {len(df.columns)} coin")
        return df
    
    # ==================== VERİ İŞLEME ====================
    
    def resample_data(self, df, interval='1min'):
        """Verileri belirli aralıklarla yeniden örnekle"""
        print(f"Veriler {interval} aralığıyla yeniden örnekleniyor...")
        resampled = df.resample(interval).last().ffill()
        resampled = resampled.dropna(how='all')
        print(f"Yeniden örnekleme tamamlandı: {len(resampled)} satır")
        return resampled
    
    def calculate_returns(self, df):
        """Fiyat değişimlerini hesapla (yüzde değişim)"""
        print("Fiyat değişimleri (returns) hesaplanıyor...")
        returns_df = df.pct_change() * 100
        returns_df = returns_df.dropna()
        print(f"Returns hesaplandı: {len(returns_df)} satır")
        return returns_df
    
    # ==================== KORELASYON HESAPLAMA ====================
    
    def calculate_correlation_matrix(self, df):
        """Korelasyon matrisini hesapla"""
        print("\nKorelasyon matrisi hesaplanıyor...")
        
        # Yeterli veri olan coinleri filtrele
        valid_columns = []
        for col in df.columns:
            non_null_count = df[col].notna().sum()
            if non_null_count >= self.min_data_points:
                valid_columns.append(col)
            else:
                print(f"  {col}: Yetersiz veri ({non_null_count} < {self.min_data_points})")
        
        if len(valid_columns) < 2:
            print("Yeterli coin bulunamadı!")
            return None
        
        df_valid = df[valid_columns]
        correlation_matrix = df_valid.corr()
        
        print(f"Korelasyon matrisi hesaplandı: {len(correlation_matrix)}x{len(correlation_matrix)}")
        return correlation_matrix
    
    def find_high_correlations(self, correlation_matrix):
        """Yüksek korelasyonlu coin çiftlerini bul"""
        print(f"\nYüksek korelasyonlu çiftler aranıyor (eşik: {self.correlation_threshold})...")
        
        high_correlations = []
        
        for i, coin1 in enumerate(correlation_matrix.columns):
            for j, coin2 in enumerate(correlation_matrix.columns):
                if i < j:
                    correlation = correlation_matrix.loc[coin1, coin2]
                    
                    if not np.isnan(correlation) and abs(correlation) >= self.correlation_threshold:
                        high_correlations.append({
                            'coin1': coin1,
                            'coin2': coin2,
                            'correlation': correlation,
                            'abs_correlation': abs(correlation)
                        })
        
        high_correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
        print(f"{len(high_correlations)} yüksek korelasyonlu çift bulundu")
        return high_correlations
    
    def get_correlations_for_coin(self, correlation_matrix, target_coin):
        """Belirli bir coin için tüm korelasyonları bul
        
        target_coin: Analiz edilecek coin (örn: 'BTCUSDT')
        """
        if target_coin not in correlation_matrix.columns:
            print(f"{target_coin} bulunamadı!")
            return []
        
        correlations = []
        
        for other_coin in correlation_matrix.columns:
            if other_coin != target_coin:
                corr = correlation_matrix.loc[target_coin, other_coin]
                
                if not np.isnan(corr):
                    correlations.append({
                        'coin': other_coin,
                        'correlation': corr,
                        'abs_correlation': abs(corr)
                    })
        
        # Korelasyona göre sırala
        correlations.sort(key=lambda x: x['abs_correlation'], reverse=True)
        return correlations
    
    def analyze_by_coin(self, correlation_matrix, top_n=10):
        """Her coin için en yüksek korelasyonlu coinleri bul"""
        print(f"\n{'='*80}")
        print(f"HER COIN İÇİN EN YÜKSEK {top_n} KORELASYON")
        print(f"{'='*80}")
        
        coin_analyses = {}
        
        for coin in correlation_matrix.columns:
            correlations = self.get_correlations_for_coin(correlation_matrix, coin)
            high_corrs = [c for c in correlations if abs(c['correlation']) >= self.correlation_threshold]
            
            coin_analyses[coin] = {
                'all_correlations': correlations,
                'high_correlations': high_corrs,
                'top_correlations': correlations[:top_n]
            }
            
            # Her coin için sonuçları göster
            print(f"\n{coin}:")
            print(f"  Toplam {len(correlations)} coin ile korelasyon")
            print(f"  {len(high_corrs)} yüksek korelasyonlu (≥{self.correlation_threshold})")
            print(f"  En yüksek {top_n} korelasyon:")
            
            for i, corr_data in enumerate(correlations[:top_n], 1):
                corr = corr_data['correlation']
                status = "Pozitif" if corr > 0 else "Negatif"
                print(f"    {i}. {corr_data['coin']:<15} {corr:>8.4f} ({status})")
        
        return coin_analyses
    
    # ==================== GÖRÜNTÜLEME VE KAYDETME ====================
    
    def display_correlations(self, high_correlations, top_n=20):
        """Yüksek korelasyonlu çiftleri göster"""
        if not high_correlations:
            print("Yüksek korelasyonlu çift bulunamadı!")
            return
        
        print(f"\n{'='*80}")
        print(f"EN YÜKSEK {top_n} KORELASYONLU COIN ÇİFTİ")
        print(f"{'='*80}")
        print(f"{'Coin 1':<15} {'Coin 2':<15} {'Korelasyon':<15} {'Durum':<20}")
        print(f"{'-'*80}")
        
        for i, pair in enumerate(high_correlations[:top_n], 1):
            coin1 = pair['coin1']
            coin2 = pair['coin2']
            corr = pair['correlation']
            status = "Pozitif (Aynı yön)" if corr > 0 else "Negatif (Ters yön)"
            print(f"{coin1:<15} {coin2:<15} {corr:>14.4f}  {status:<20}")
    
    def save_correlations(self, high_correlations, filename='correlations.json'):
        """Korelasyon sonuçlarını JSON dosyasına kaydet"""
        try:
            output = []
            for pair in high_correlations:
                output.append({
                    'coin1': pair['coin1'],
                    'coin2': pair['coin2'],
                    'correlation': float(pair['correlation']),
                    'abs_correlation': float(pair['abs_correlation'])
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            print(f"\nSonuçlar {filename} dosyasına kaydedildi")
            return True
        except Exception as e:
            print(f"Kaydetme hatası: {e}")
            return False
    
    def save_coin_analyses(self, coin_analyses, filename='coin_correlations.json'):
        """Her coin için korelasyon analizlerini kaydet"""
        try:
            output = {}
            for coin, analysis in coin_analyses.items():
                output[coin] = {
                    'high_correlations': [
                        {
                            'coin': c['coin'],
                            'correlation': float(c['correlation']),
                            'abs_correlation': float(c['abs_correlation'])
                        }
                        for c in analysis['high_correlations']
                    ],
                    'top_correlations': [
                        {
                            'coin': c['coin'],
                            'correlation': float(c['correlation']),
                            'abs_correlation': float(c['abs_correlation'])
                        }
                        for c in analysis['top_correlations']
                    ]
                }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            print(f"Coin analizleri {filename} dosyasına kaydedildi")
            return True
        except Exception as e:
            print(f"Kaydetme hatası: {e}")
            return False
    
    def save_correlation_matrix(self, correlation_matrix, filename='correlation_matrix.csv'):
        """Korelasyon matrisini CSV dosyasına kaydet"""
        try:
            correlation_matrix.to_csv(filename)
            print(f"Korelasyon matrisi {filename} dosyasına kaydedildi")
            return True
        except Exception as e:
            print(f"Kaydetme hatası: {e}")
            return False
    
    # ==================== ANA ANALİZ FONKSİYONLARI ====================
    
    def analyze_historical_data(self, symbols, interval='1m', limit=500, 
                                use_returns=True, resample_interval='1min'):
        """Geçmiş verilerle korelasyon analizi
        
        symbols: Coin çiftleri listesi
        interval: Binance klines interval ('1m', '5m', '1h', '1d')
        limit: Her coin için kaç veri noktası
        use_returns: True ise fiyat değişimleri, False ise fiyatlar
        resample_interval: Veri yeniden örnekleme aralığı
        """
        print("\n" + "="*80)
        print("GEÇMİŞ VERİLERLE KORELASYON ANALİZİ")
        print("="*80)
        
        # 1. Geçmiş verileri çek
        historical_data = self.fetch_all_historical_data(symbols, interval, limit)
        
        if not historical_data:
            print("Geçmiş veri çekilemedi!")
            return None, None, None
        
        # 2. DataFrame hazırla
        df = self.prepare_historical_dataframe(historical_data)
        if df is None:
            return None, None, None
        
        # 3. Yeniden örnekle (isteğe bağlı)
        if resample_interval:
            df = self.resample_data(df, resample_interval)
        
        # 4. Returns veya fiyatlar
        if use_returns:
            df = self.calculate_returns(df)
        else:
            df = df.dropna()
        
        # 5. Korelasyon matrisi
        correlation_matrix = self.calculate_correlation_matrix(df)
        if correlation_matrix is None:
            return None, None, None
        
        # 6. Yüksek korelasyonları bul
        high_correlations = self.find_high_correlations(correlation_matrix)
        
        # 7. Her coin için analiz
        coin_analyses = self.analyze_by_coin(correlation_matrix)
        
        # 8. Sonuçları göster
        self.display_correlations(high_correlations)
        
        # 9. Kaydet
        self.save_correlations(high_correlations, 'historical_correlations.json')
        self.save_coin_analyses(coin_analyses, 'historical_coin_correlations.json')
        self.save_correlation_matrix(correlation_matrix, 'historical_correlation_matrix.csv')
        
        return correlation_matrix, high_correlations, coin_analyses
    
    def analyze_realtime_data(self, price_data, use_returns=True, resample_interval='1min'):
        """Anlık WebSocket verileriyle korelasyon analizi
        
        price_data: binance_websocket'ten gelen price_data dict'i
        use_returns: True ise fiyat değişimleri, False ise fiyatlar
        resample_interval: Veri yeniden örnekleme aralığı
        """
        print("\n" + "="*80)
        print("ANLIK VERİLERLE KORELASYON ANALİZİ")
        print("="*80)
        
        # 1. DataFrame hazırla
        df = self.prepare_realtime_dataframe(price_data)
        if df is None:
            return None, None, None
        
        # 2. Yeniden örnekle
        if resample_interval:
            df = self.resample_data(df, resample_interval)
        
        # 3. Returns veya fiyatlar
        if use_returns:
            df = self.calculate_returns(df)
        else:
            df = df.dropna()
        
        # 4. Korelasyon matrisi
        correlation_matrix = self.calculate_correlation_matrix(df)
        if correlation_matrix is None:
            return None, None, None
        
        # 5. Yüksek korelasyonları bul
        high_correlations = self.find_high_correlations(correlation_matrix)
        
        # 6. Her coin için analiz
        coin_analyses = self.analyze_by_coin(correlation_matrix)
        
        # 7. Sonuçları göster
        self.display_correlations(high_correlations)
        
        # 8. Kaydet
        self.save_correlations(high_correlations, 'realtime_correlations.json')
        self.save_coin_analyses(coin_analyses, 'realtime_coin_correlations.json')
        self.save_correlation_matrix(correlation_matrix, 'realtime_correlation_matrix.csv')
        
        return correlation_matrix, high_correlations, coin_analyses