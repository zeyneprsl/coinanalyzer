import pandas as pd
import numpy as np
from datetime import datetime
import json

class PriceVolumeAnalyzer:
    def __init__(self, correlation_threshold=0.5):
        """
        correlation_threshold: Fiyat-volüm korelasyonu eşiği
        """
        self.correlation_threshold = correlation_threshold
    
    def prepare_dataframe(self, price_volume_data):
        """Fiyat ve volume verilerini DataFrame'e dönüştür"""
        print("\nFiyat ve Volume verileri DataFrame'e dönüştürülüyor...")
        
        price_series = {}
        volume_series = {}
        price_change_series = {}
        
        for symbol, data_list in price_volume_data.items():
            if len(data_list) < 2:
                continue
            
            timestamps = [item['timestamp'] for item in data_list]
            prices = [item['price'] for item in data_list]
            volumes = [item['volume'] for item in data_list]
            price_changes = [item['price_change_percent'] for item in data_list]
            
            price_series[symbol] = pd.Series(prices, index=timestamps, name=f"{symbol}_price")
            volume_series[symbol] = pd.Series(volumes, index=timestamps, name=f"{symbol}_volume")
            price_change_series[symbol] = pd.Series(price_changes, index=timestamps, name=f"{symbol}_change")
        
        if not price_series:
            print("Yeterli veri bulunamadı!")
            return None, None, None
        
        # DataFrame'ler oluştur
        df_prices = pd.DataFrame(price_series)
        df_volumes = pd.DataFrame(volume_series)
        df_changes = pd.DataFrame(price_change_series)
        
        # Timestamp'leri index yap
        for df in [df_prices, df_volumes, df_changes]:
            df.index = pd.to_datetime(df.index)
            df = df.groupby(df.index).first()
            df = df.sort_index()
        
        print(f"DataFrame'ler hazırlandı: {len(df_prices)} satır, {len(df_prices.columns)} coin")
        return df_prices, df_volumes, df_changes
    
    def calculate_price_volume_correlation(self, df_prices, df_volumes):
        """Fiyat ve volume arasındaki korelasyonu hesapla"""
        print("\nFiyat-Volume korelasyonları hesaplanıyor...")
        
        correlations = {}
        
        # Her coin için fiyat ve volume değişimlerini hesapla
        for symbol in df_prices.columns:
            if symbol not in df_volumes.columns:
                continue
            
            # Coin adını temizle (sadece symbol kısmı)
            coin_name = symbol.replace('_price', '')
            volume_col = f"{coin_name}_volume"
            
            if volume_col not in df_volumes.columns:
                continue
            
            # Fiyat ve volume serilerini al
            price_series = df_prices[symbol]
            volume_series = df_volumes[volume_col]
            
            # Ortak index'e göre hizala
            combined = pd.DataFrame({
                'price': price_series,
                'volume': volume_series
            }).dropna()
            
            if len(combined) < 10:  # Minimum veri kontrolü
                continue
            
            # Fiyat değişimleri (returns)
            price_returns = combined['price'].pct_change().dropna()
            
            # Volume değişimleri
            volume_returns = combined['volume'].pct_change().dropna()
            
            # Ortak index'e göre hizala
            aligned = pd.DataFrame({
                'price_change': price_returns,
                'volume_change': volume_returns
            }).dropna()
            
            if len(aligned) < 10:
                continue
            
            # Korelasyon hesapla
            correlation = aligned['price_change'].corr(aligned['volume_change'])
            
            if not np.isnan(correlation):
                correlations[coin_name] = {
                    'correlation': correlation,
                    'abs_correlation': abs(correlation),
                    'data_points': len(aligned)
                }
        
        return correlations
    
    # ==================== YENİ: ANİ FİYAT DEĞİŞİMLERİ ANALİZİ ====================
    
    def analyze_sudden_price_changes(self, price_volume_data, thresholds=[1.0, 2.0, 5.0, 10.0], 
                                     resample_interval='1min'):
        """Ani fiyat değişimlerinde volume davranışını analiz et
        
        thresholds: Ani değişim eşikleri (yüzde olarak) [1%, 2%, 5%, 10%]
        """
        print("\n" + "="*80)
        print("ANİ FİYAT DEĞİŞİMLERİNDE VOLUME ANALİZİ")
        print("="*80)
        print(f"Eşikler: {thresholds}%")
        
        # 1. DataFrame'leri hazırla
        df_prices, df_volumes, df_changes = self.prepare_dataframe(price_volume_data)
        
        if df_prices is None:
            return None
        
        # 2. Yeniden örnekleme
        if resample_interval:
            print(f"Veriler {resample_interval} aralığıyla yeniden örnekleniyor...")
            df_prices = df_prices.resample(resample_interval).last().ffill()
            df_volumes = df_volumes.resample(resample_interval).last().ffill()
        
        # 3. Her coin ve her eşik için analiz
        all_analyses = {}
        
        for symbol in df_prices.columns:
            coin_name = symbol.replace('_price', '')
            volume_col = f"{coin_name}_volume"
            
            if volume_col not in df_volumes.columns:
                continue
            
            # Verileri birleştir
            combined = pd.DataFrame({
                'price': df_prices[symbol],
                'volume': df_volumes[volume_col]
            }).dropna()
            
            if len(combined) < 20:
                continue
            
            # Fiyat değişimleri (yüzde)
            price_returns = combined['price'].pct_change() * 100  # Yüzde olarak
            
            # Volume değişimleri (yüzde)
            volume_returns = combined['volume'].pct_change() * 100  # Yüzde olarak
            
            # Hizala
            aligned = pd.DataFrame({
                'price_change_pct': price_returns,
                'volume_change_pct': volume_returns,
                'price': combined['price'],
                'volume': combined['volume']
            }).dropna()
            
            if len(aligned) < 20:
                continue
            
            # Her eşik için analiz
            coin_analysis = {
                'total_data_points': len(aligned),
                'thresholds': {}
            }
            
            for threshold in thresholds:
                threshold_abs = abs(threshold)
                
                # Ani yükselişler (spike up)
                sudden_up = aligned[aligned['price_change_pct'] >= threshold_abs]
                
                # Ani düşüşler (spike down)
                sudden_down = aligned[aligned['price_change_pct'] <= -threshold_abs]
                
                # Normal değişimler (eşik içinde)
                normal = aligned[
                    (aligned['price_change_pct'] > -threshold_abs) & 
                    (aligned['price_change_pct'] < threshold_abs)
                ]
                
                threshold_stats = {
                    'threshold': threshold,
                    'sudden_up_count': len(sudden_up),
                    'sudden_down_count': len(sudden_down),
                    'normal_count': len(normal),
                }
                
                # Ani yükselişlerde volume analizi
                if len(sudden_up) > 0:
                    # Volume artış sayısı
                    vol_up_on_price_spike_up = (sudden_up['volume_change_pct'] > 0).sum()
                    vol_down_on_price_spike_up = (sudden_up['volume_change_pct'] < 0).sum()
                    
                    threshold_stats['sudden_up'] = {
                        'count': len(sudden_up),
                        'volume_increase_count': vol_up_on_price_spike_up,
                        'volume_decrease_count': vol_down_on_price_spike_up,
                        'volume_increase_pct': (vol_up_on_price_spike_up / len(sudden_up)) * 100,
                        'avg_price_change': sudden_up['price_change_pct'].mean(),
                        'avg_volume_change': sudden_up['volume_change_pct'].mean(),
                        'median_volume_change': sudden_up['volume_change_pct'].median(),
                        'max_volume_change': sudden_up['volume_change_pct'].max(),
                        'min_volume_change': sudden_up['volume_change_pct'].min(),
                    }
                
                # Ani düşüşlerde volume analizi
                if len(sudden_down) > 0:
                    vol_up_on_price_spike_down = (sudden_down['volume_change_pct'] > 0).sum()
                    vol_down_on_price_spike_down = (sudden_down['volume_change_pct'] < 0).sum()
                    
                    threshold_stats['sudden_down'] = {
                        'count': len(sudden_down),
                        'volume_increase_count': vol_up_on_price_spike_down,
                        'volume_decrease_count': vol_down_on_price_spike_down,
                        'volume_increase_pct': (vol_up_on_price_spike_down / len(sudden_down)) * 100,
                        'avg_price_change': sudden_down['price_change_pct'].mean(),
                        'avg_volume_change': sudden_down['volume_change_pct'].mean(),
                        'median_volume_change': sudden_down['volume_change_pct'].median(),
                        'max_volume_change': sudden_down['volume_change_pct'].max(),
                        'min_volume_change': sudden_down['volume_change_pct'].min(),
                    }
                
                # Normal durumlarda volume analizi (karşılaştırma için)
                if len(normal) > 0:
                    vol_up_on_normal = (normal['volume_change_pct'] > 0).sum()
                    threshold_stats['normal'] = {
                        'count': len(normal),
                        'volume_increase_pct': (vol_up_on_normal / len(normal)) * 100,
                        'avg_volume_change': normal['volume_change_pct'].mean(),
                    }
                
                coin_analysis['thresholds'][threshold] = threshold_stats
            
            all_analyses[coin_name] = coin_analysis
        
        return all_analyses
    
    def display_sudden_price_analysis(self, sudden_analyses, threshold=2.0, top_n=20):
        """Ani fiyat değişim analiz sonuçlarını göster"""
        if not sudden_analyses:
            print("Analiz sonucu bulunamadı!")
            return
        
        print(f"\n{'='*120}")
        print(f"ANİ FİYAT DEĞİŞİMLERİNDE VOLUME DAVRANIŞI (Eşik: ±{threshold}%)")
        print(f"{'='*120}")
        
        # İstatistikleri topla ve sırala
        coin_stats = []
        
        for coin_name, analysis in sudden_analyses.items():
            if threshold not in analysis.get('thresholds', {}):
                continue
            
            threshold_data = analysis['thresholds'][threshold]
            
            sudden_up = threshold_data.get('sudden_up', {})
            sudden_down = threshold_data.get('sudden_down', {})
            
            if len(sudden_up) == 0 and len(sudden_down) == 0:
                continue
            
            # Ani yükseliş istatistikleri
            up_count = sudden_up.get('count', 0)
            up_vol_increase_pct = sudden_up.get('volume_increase_pct', 0)
            up_avg_vol_change = sudden_up.get('avg_volume_change', 0)
            
            # Ani düşüş istatistikleri
            down_count = sudden_down.get('count', 0)
            down_vol_increase_pct = sudden_down.get('volume_increase_pct', 0)
            down_avg_vol_change = sudden_down.get('avg_volume_change', 0)
            
            # Toplam ani değişim
            total_sudden = up_count + down_count
            
            coin_stats.append({
                'coin': coin_name,
                'total_sudden': total_sudden,
                'sudden_up_count': up_count,
                'sudden_down_count': down_count,
                'up_vol_increase_pct': up_vol_increase_pct,
                'down_vol_increase_pct': down_vol_increase_pct,
                'up_avg_vol_change': up_avg_vol_change,
                'down_avg_vol_change': down_avg_vol_change,
            })
        
        # Ani değişim sayısına göre sırala
        coin_stats.sort(key=lambda x: x['total_sudden'], reverse=True)
        
        print(f"{'Coin':<12} {'Top.Ani':<10} {'Yükseliş':<10} {'Düşüş':<10} "
              f"{'Yükselişte Vol↑%':<18} {'Düşüşte Vol↑%':<18} "
              f"{'Yüks.Vol Ort.':<15} {'Düş.Vol Ort.':<15}")
        print(f"{'-'*120}")
        
        for stat in coin_stats[:top_n]:
            print(f"{stat['coin']:<12} {stat['total_sudden']:>9}  "
                  f"{stat['sudden_up_count']:>9}  {stat['sudden_down_count']:>9}  "
                  f"{stat['up_vol_increase_pct']:>17.2f}%  {stat['down_vol_increase_pct']:>17.2f}%  "
                  f"{stat['up_avg_vol_change']:>14.2f}%  {stat['down_avg_vol_change']:>14.2f}%")
        
        # Özet istatistikler
        print(f"\n{'='*120}")
        print("ÖZET İSTATİSTİKLER")
        print(f"{'='*120}")
        
        total_coins = len([s for s in coin_stats if s['total_sudden'] > 0])
        total_sudden_up = sum(s['sudden_up_count'] for s in coin_stats)
        total_sudden_down = sum(s['sudden_down_count'] for s in coin_stats)
        
        # Ortalama volume artış yüzdeleri
        avg_vol_up_on_spike_up = np.mean([
            s['up_vol_increase_pct'] for s in coin_stats 
            if s['sudden_up_count'] > 0
        ]) if coin_stats else 0
        
        avg_vol_up_on_spike_down = np.mean([
            s['down_vol_increase_pct'] for s in coin_stats 
            if s['sudden_down_count'] > 0
        ]) if coin_stats else 0
        
        print(f"Toplam Coin (ani değişim olan): {total_coins}")
        print(f"Toplam Ani Yükseliş: {total_sudden_up}")
        print(f"Toplam Ani Düşüş: {total_sudden_down}")
        print(f"\nOrtalama: Ani yükselişlerde volume artışı %{avg_vol_up_on_spike_up:.2f}")
        print(f"Ortalama: Ani düşüşlerde volume artışı %{avg_vol_up_on_spike_down:.2f}")
        
        # Eşik bazlı özet
        print(f"\n{'='*120}")
        print("EŞİK BAZLI ÖZET")
        print(f"{'='*120}")
        
        # Tüm eşikler için özet
        threshold_summary = {}
        for coin_name, analysis in sudden_analyses.items():
            for thresh, thresh_data in analysis.get('thresholds', {}).items():
                if thresh not in threshold_summary:
                    threshold_summary[thresh] = {
                        'total_up': 0,
                        'total_down': 0,
                        'up_vol_increase': [],
                        'down_vol_increase': []
                    }
                
                up_data = thresh_data.get('sudden_up', {})
                down_data = thresh_data.get('sudden_down', {})
                
                if up_data.get('count', 0) > 0:
                    threshold_summary[thresh]['total_up'] += up_data['count']
                    threshold_summary[thresh]['up_vol_increase'].append(up_data['volume_increase_pct'])
                
                if down_data.get('count', 0) > 0:
                    threshold_summary[thresh]['total_down'] += down_data['count']
                    threshold_summary[thresh]['down_vol_increase'].append(down_data['volume_increase_pct'])
        
        print(f"{'Eşik':<10} {'Ani Yükseliş':<15} {'Ani Düşüş':<15} "
              f"{'Yüks.Vol↑ Ort.%':<18} {'Düş.Vol↑ Ort.%':<18}")
        print(f"{'-'*80}")
        
        for thresh in sorted(threshold_summary.keys()):
            summary = threshold_summary[thresh]
            avg_up_vol = np.mean(summary['up_vol_increase']) if summary['up_vol_increase'] else 0
            avg_down_vol = np.mean(summary['down_vol_increase']) if summary['down_vol_increase'] else 0
            
            print(f"±{thresh:>6.1f}%  {summary['total_up']:>14}  {summary['total_down']:>14}  "
                  f"{avg_up_vol:>17.2f}%  {avg_down_vol:>17.2f}%")
    
    def save_sudden_analysis(self, sudden_analyses, filename='sudden_price_volume_analysis.json'):
        """Ani fiyat değişim analizini kaydet"""
        try:
            output = {}
            for coin_name, analysis in sudden_analyses.items():
                output[coin_name] = {}
                for threshold, threshold_data in analysis.get('thresholds', {}).items():
                    output[coin_name][f"threshold_{threshold}"] = {
                        k: (float(v) if isinstance(v, (np.float64, np.float32, float)) else v)
                        for k, v in threshold_data.items()
                        if k != 'threshold'
                    }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            print(f"\nAni fiyat değişim analizi {filename} dosyasına kaydedildi")
            return True
        except Exception as e:
            print(f"Kaydetme hatası: {e}")
            return False
    
    # ==================== MEVCUT FONKSİYONLAR ====================
    
    def analyze_price_volume_relationship(self, price_volume_data, resample_interval='1min'):
        """Fiyat-artışı ve volume-artışı ilişkisini analiz et"""
        print("\n" + "="*80)
        print("FİYAT-VOLUME İLİŞKİSİ ANALİZİ")
        print("="*80)
        
        # 1. DataFrame'leri hazırla
        df_prices, df_volumes, df_changes = self.prepare_dataframe(price_volume_data)
        
        if df_prices is None:
            return None
        
        # 2. Yeniden örnekleme (isteğe bağlı)
        if resample_interval:
            print(f"Veriler {resample_interval} aralığıyla yeniden örnekleniyor...")
            df_prices = df_prices.resample(resample_interval).last().ffill()
            df_volumes = df_volumes.resample(resample_interval).last().ffill()
            df_changes = df_changes.resample(resample_interval).last().ffill()
        
        # 3. Her coin için detaylı analiz
        coin_analyses = {}
        
        for symbol in df_prices.columns:
            coin_name = symbol.replace('_price', '')
            volume_col = f"{coin_name}_volume"
            change_col = f"{coin_name}_change"
            
            if volume_col not in df_volumes.columns:
                continue
            
            # Verileri birleştir
            combined = pd.DataFrame({
                'price': df_prices[symbol],
                'volume': df_volumes[volume_col],
                'price_change_24h': df_changes[change_col] if change_col in df_changes.columns else None
            }).dropna()
            
            if len(combined) < 10:
                continue
            
            # Fiyat değişimleri
            price_returns = combined['price'].pct_change().dropna()
            
            # Volume değişimleri
            volume_returns = combined['volume'].pct_change().dropna()
            
            # Hizala
            aligned = pd.DataFrame({
                'price_change': price_returns,
                'volume_change': volume_returns
            }).dropna()
            
            if len(aligned) < 10:
                continue
            
            # Korelasyon
            correlation = aligned['price_change'].corr(aligned['volume_change'])
            
            # Fiyat artışı olduğunda volume artışı analizi
            price_up = aligned[aligned['price_change'] > 0]
            price_down = aligned[aligned['price_change'] < 0]
            price_stable = aligned[aligned['price_change'] == 0]
            
            # İstatistikler
            stats = {
                'correlation': correlation,
                'abs_correlation': abs(correlation),
                'data_points': len(aligned),
                'price_up_count': len(price_up),
                'price_down_count': len(price_down),
                'price_stable_count': len(price_stable),
            }
            
            if len(price_up) > 0:
                stats['volume_increase_on_price_up'] = (price_up['volume_change'] > 0).sum()
                stats['volume_increase_on_price_up_pct'] = (price_up['volume_change'] > 0).mean() * 100
                stats['avg_volume_change_on_price_up'] = price_up['volume_change'].mean()
            
            if len(price_down) > 0:
                stats['volume_increase_on_price_down'] = (price_down['volume_change'] > 0).sum()
                stats['volume_increase_on_price_down_pct'] = (price_down['volume_change'] > 0).mean() * 100
                stats['avg_volume_change_on_price_down'] = price_down['volume_change'].mean()
            
            coin_analyses[coin_name] = stats
        
        return coin_analyses
    
    def display_analysis(self, coin_analyses, top_n=20):
        """Analiz sonuçlarını göster"""
        if not coin_analyses:
            print("Analiz sonucu bulunamadı!")
            return
        
        # Korelasyona göre sırala
        sorted_coins = sorted(
            coin_analyses.items(),
            key=lambda x: x[1].get('abs_correlation', 0),
            reverse=True
        )
        
        print(f"\n{'='*100}")
        print(f"FİYAT-VOLUME İLİŞKİSİ ANALİZİ - EN YÜKSEK {top_n} KORELASYON")
        print(f"{'='*100}")
        print(f"{'Coin':<12} {'Korelasyon':<12} {'Veri Noktası':<15} {'Fiyat↑+Vol↑':<15} {'Fiyat↑+Vol↑%':<15} {'Durum':<20}")
        print(f"{'-'*100}")
        
        for coin_name, stats in sorted_coins[:top_n]:
            correlation = stats.get('correlation', 0)
            data_points = stats.get('data_points', 0)
            vol_up_on_price_up_pct = stats.get('volume_increase_on_price_up_pct', 0)
            
            # Durum belirleme
            if correlation > 0.5:
                status = "Güçlü Pozitif ✓"
            elif correlation > 0.3:
                status = "Orta Pozitif"
            elif correlation > -0.3:
                status = "Zayıf İlişki"
            elif correlation > -0.5:
                status = "Orta Negatif"
            else:
                status = "Güçlü Negatif"
            
            print(f"{coin_name:<12} {correlation:>11.4f}  {data_points:>14}  "
                  f"{stats.get('volume_increase_on_price_up', 0):>14}  "
                  f"{vol_up_on_price_up_pct:>14.2f}%  {status:<20}")
        
        # Özet istatistikler
        print(f"\n{'='*100}")
        print("ÖZET İSTATİSTİKLER")
        print(f"{'='*100}")
        
        total_coins = len(coin_analyses)
        strong_positive = sum(1 for s in coin_analyses.values() if s.get('correlation', 0) > 0.5)
        moderate_positive = sum(1 for s in coin_analyses.values() if 0.3 < s.get('correlation', 0) <= 0.5)
        weak = sum(1 for s in coin_analyses.values() if -0.3 <= s.get('correlation', 0) <= 0.3)
        moderate_negative = sum(1 for s in coin_analyses.values() if -0.5 <= s.get('correlation', 0) < -0.3)
        strong_negative = sum(1 for s in coin_analyses.values() if s.get('correlation', 0) < -0.5)
        
        print(f"Toplam Coin: {total_coins}")
        print(f"Güçlü Pozitif Korelasyon (>0.5): {strong_positive} ({strong_positive/total_coins*100:.1f}%)")
        print(f"Orta Pozitif Korelasyon (0.3-0.5): {moderate_positive} ({moderate_positive/total_coins*100:.1f}%)")
        print(f"Zayıf İlişki (-0.3-0.3): {weak} ({weak/total_coins*100:.1f}%)")
        print(f"Orta Negatif Korelasyon (-0.5--0.3): {moderate_negative} ({moderate_negative/total_coins*100:.1f}%)")
        print(f"Güçlü Negatif Korelasyon (<-0.5): {strong_negative} ({strong_negative/total_coins*100:.1f}%)")
        
        # Fiyat artışında volume artışı yüzdesi
        avg_vol_up_on_price_up = np.mean([
            s.get('volume_increase_on_price_up_pct', 0) 
            for s in coin_analyses.values() 
            if s.get('price_up_count', 0) > 0
        ])
        
        print(f"\nOrtalama: Fiyat artışında volume artışı %{avg_vol_up_on_price_up:.2f}")
    
    def save_analysis(self, coin_analyses, filename='price_volume_analysis.json'):
        """Analiz sonuçlarını kaydet"""
        try:
            output = {}
            for coin_name, stats in coin_analyses.items():
                output[coin_name] = {
                    k: float(v) if isinstance(v, (np.float64, np.float32, float)) else v
                    for k, v in stats.items()
                }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            print(f"\nAnaliz sonuçları {filename} dosyasına kaydedildi")
            return True
        except Exception as e:
            print(f"Kaydetme hatası: {e}")
            return False