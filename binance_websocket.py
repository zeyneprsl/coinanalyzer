import requests
import websocket
import json
import threading
import time
from collections import defaultdict
from datetime import datetime

class BinanceWebSocket:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.stream_url = "wss://stream.binance.com:9443/stream"
        self.usdt_pairs = []
        self.price_data = defaultdict(list)
        self.price_volume_data = defaultdict(list)  # Fiyat ve volume birlikte
        self.ws_threads = []  # Her chunk için thread saklamak için
        self.ws_apps = []  # WebSocket uygulamalarını sakla
        self.running = False
        self.reconnect_delay = 5  # Yeniden bağlanma gecikmesi (saniye)

    # ---------------- REST API ile USDT çiftlerini alma ----------------
    def get_usdt_pairs(self):
        """Binance'den tüm USDT çiftlerini al"""
        print("USDT çiftleri alınıyor...")
        try:
            url = f"{self.base_url}/exchangeInfo"
            response = requests.get(url)
            data = response.json()
            self.usdt_pairs = []
            for symbol in data['symbols']:
                if symbol['symbol'].endswith('USDT') and symbol['status'] == 'TRADING':
                    self.usdt_pairs.append(symbol['symbol'])
            print(f"Toplam {len(self.usdt_pairs)} USDT çifti bulundu")
            return self.usdt_pairs
        except Exception as e:
            print(f"Hata: {e}")
            return []

    # ---------------- WebSocket eventleri ----------------
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            stream_data = data.get('data', data)  # combined veya single stream farkı
            
            symbol = stream_data.get('s')
            price = float(stream_data.get('c', 0))  # Close price (son fiyat)
            volume = float(stream_data.get('v', 0))  # Volume (24h volume)
            price_change = float(stream_data.get('P', 0))  # Price change percent (24h)
            timestamp = datetime.now()
            
            if symbol and price > 0:
                # Sadece fiyat (eski uyumluluk için)
                self.price_data[symbol].append({
                    'timestamp': timestamp, 
                    'price': price
                })
                
                # Fiyat ve volume birlikte (yeni analiz için)
                self.price_volume_data[symbol].append({
                    'timestamp': timestamp,
                    'price': price,
                    'volume': volume,
                    'price_change_percent': price_change
                })
                
                # İlk birkaç veriyi göster (test için)
                if len(self.price_volume_data[symbol]) <= 3:
                    print(f"{symbol}: {price} USDT | Vol: {volume:.2f} | Change: {price_change:.2f}% - {timestamp.strftime('%H:%M:%S')}")
                    
        except Exception as e:
            print(f"Mesaj işleme hatası: {e}")

    def on_error(self, ws, error):
        print(f"WebSocket hatası: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"WebSocket kapandı (kod: {close_status_code})")
        # Yeniden bağlanma run_forever içinde otomatik yapılacak

    def on_open(self, ws):
        print("WebSocket açıldı")

    # ---------------- Combined stream URL ----------------
    def create_stream_url(self, pairs_chunk):
        streams = [f"{pair.lower()}@ticker" for pair in pairs_chunk]
        return f"{self.stream_url}?streams={'/'.join(streams)}"

    # ---------------- Streaming başlat ---------------- 
    def start_streaming(self, auto_reconnect=True):
        """WebSocket streaming'i başlat
        
        auto_reconnect: Otomatik yeniden bağlanma (varsayılan: True)
        """
        self.running = True
        
        if not self.usdt_pairs:
            self.get_usdt_pairs()

        chunk_size = 200
        for i in range(0, len(self.usdt_pairs), chunk_size):
            chunk = self.usdt_pairs[i:i + chunk_size]
            url = self.create_stream_url(chunk)
            print(f"{len(chunk)} çift için stream başlatılıyor ({i + 1} - {i + len(chunk)})...")

            # Her chunk için ayrı WebSocket thread
            ws_app = websocket.WebSocketApp(
                url,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            self.ws_apps.append(ws_app)

            def run_with_reconnect(ws_app_instance, chunk_data):
                """Yeniden bağlanma ile çalıştır"""
                while self.running:
                    try:
                        ws_app_instance.run_forever()
                    except Exception as e:
                        if self.running:
                            print(f"⚠️  WebSocket hatası (yeniden bağlanılıyor): {e}")
                            time.sleep(self.reconnect_delay)
                        else:
                            break

            t = threading.Thread(target=run_with_reconnect, args=(ws_app, chunk))
            t.daemon = True  # Program kapanınca thread'ler de kapanır
            t.start()
            self.ws_threads.append(t)
    
    def stop_streaming(self):
        """WebSocket streaming'i durdur"""
        self.running = False
        for ws_app in self.ws_apps:
            try:
                ws_app.close()
            except:
                pass
        self.ws_apps = []
        self.ws_threads = []

    # ---------------- Fiyat verilerini alma ----------------
    def get_price_data(self):
        return self.price_data

    # ---------------- Fiyat ve Volume verilerini alma ----------------
    def get_price_volume_data(self):
        return self.price_volume_data

    # ---------------- Fiyat verilerini temizleme ----------------
    def clear_price_data(self):
        self.price_data = defaultdict(list)
        self.price_volume_data = defaultdict(list)