"""
{
  "e": "24hrTicker",   // event type
  "E": 1699420500000,  // event time
  "s": "BTCUSDT",      // symbol
  "p": "100.00",       // price change
  "c": "34567.89",     // last price
  "h": "34800.00",     // high price
  "l": "34000.00",     // low price
  "v": "1200.123",     // volume
  ...
}

"""
#WebSocket : anlık veri ,WebSocket’ten gelen mesaj string formatında olur. bunu Python dictionary’ye çevir
"""stream_data = data.get('data', data)
dict.get(key, default) şunu yapar: Eğer key sözlükte varsa → değeri döndürür.Yoksa → default değeri döndür
"""
#Rest apı:  exchangeInfo :Binance’te hangi coin çiftleri var (örneğin BTCUSDT, ETHUSDT, SOLUSDT...):WebSocket’te exchangeInfo akışı yoktur.

############################################################# veri kullanılışı
"""
#tek stream veri
{
    "s": "ETHUSDT",
    "c": "1925.34",
    "P": "0.53",
    ...
}

#çoklu stream veri
{
  "stream": "ethusdt@ticker",
  "data": {
    "s": "ETHUSDT",
    "c": "1925.34",
    "P": "0.53",
    ...
  }
}
bu yüzdem 
if "data" in data;
stream_data = data['data']  # datanın "data" kısmını kullan diiyoruz
            else:
                stream_data = data
"""