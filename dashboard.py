import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import time
from datetime import datetime

# Sayfa yapılandırması
st.set_page_config(
    page_title="Binance Coin Korelasyon Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stilleri
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Başlık
st.markdown('<h1 class="main-header">📊 Binance Coin Korelasyon Dashboard</h1>', unsafe_allow_html=True)

# Otomatik yenileme ayarları
st.sidebar.title("⚙️ Ayarlar")
auto_refresh = st.sidebar.checkbox("🔄 Otomatik Yenileme", value=True)
refresh_interval = st.sidebar.slider("Yenileme Aralığı (saniye)", min_value=10, max_value=300, value=60, step=10)

# Son güncelleme zamanını göster
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Sidebar - Menü
st.sidebar.title("Menü")
page = st.sidebar.selectbox(
    "Sayfa Seçin",
    ["Ana Sayfa", "Korelasyon Analizi", "Tüm Korelasyonlar", "Fiyat-Volume Analizi", "Ani Değişim Analizi", "Korelasyon Değişiklikleri"]
)

# Otomatik yenileme
if auto_refresh:
    # Son güncelleme zamanını göster
    elapsed = (datetime.now() - st.session_state.last_refresh).total_seconds()
    remaining = refresh_interval - elapsed
    st.sidebar.info(f"⏱️ Son yenileme: {int(elapsed)}s önce\n🔄 Sonraki: {int(remaining)}s")
    
    # Belirtilen süre sonra yenile
    if elapsed >= refresh_interval:
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    # Otomatik yenileme için placeholder (her çalıştırmada kontrol edilir)
    placeholder = st.sidebar.empty()
    placeholder.markdown(f"⏳ {int(remaining)} saniye sonra otomatik yenilenecek...")
    
else:
    # Manuel yenileme butonu
    if st.sidebar.button("🔄 Şimdi Yenile"):
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    # Son yenileme zamanını göster
    elapsed = (datetime.now() - st.session_state.last_refresh).total_seconds()
    st.sidebar.info(f"⏱️ Son yenileme: {int(elapsed)}s önce")

# JSON dosyalarını yükleme fonksiyonu
def load_json_file(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

# CSV dosyalarını yükleme fonksiyonu
def load_csv_file(filename):
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename, index_col=0)
        except:
            return None
    return None

# ==================== ANA SAYFA ====================
if page == "Ana Sayfa":
    st.header("📈 Genel Bakış")
        # Hoş geldin mesajı
    st.info("""
    🎯 **Binance Coin Korelasyon Dashboard**'a hoş geldiniz!
    
    Bu dashboard, Binance kripto paraları arasındaki korelasyonları ve fiyat-volume ilişkilerini analiz eder.
    
    **Kullanım:**
    - **Korelasyon Analizi**: Coinler arası korelasyonları inceleyin
    - **Fiyat-Volume Analizi**: Fiyat değişimleri ile volume ilişkisini görün
    - **Ani Değişim Analizi**: Ani fiyat değişimlerinde volume davranışını analiz edin
    """)
    
    st.markdown("---")
    
    # Metrikler - Coin ve analiz bilgileri
    correlations = load_json_file('historical_correlations.json') or load_json_file('realtime_correlations.json')
    corr_matrix_hist = load_csv_file('historical_correlation_matrix.csv')
    corr_matrix_realtime = load_csv_file('realtime_correlation_matrix.csv')
    
    if correlations or corr_matrix_hist is not None or corr_matrix_realtime is not None:
        col1, col2, col3, col4 = st.columns(4)
        
        # Toplam coin sayısı
        if corr_matrix_hist is not None:
            total_coins = len(corr_matrix_hist.columns)
        elif corr_matrix_realtime is not None:
            total_coins = len(corr_matrix_realtime.columns)
        else:
            # Korelasyonlardan coin sayısını çıkar
            unique_coins = set()
            for corr in correlations:
                unique_coins.add(corr.get('coin1', ''))
                unique_coins.add(corr.get('coin2', ''))
            total_coins = len(unique_coins)
        
        # Toplam korelasyon çifti sayısı
        total_pairs = len(correlations) if correlations else 0
        
        # Yüksek korelasyon sayısı
        high_corr = [c for c in correlations if abs(c.get('correlation', 0)) > 0.7] if correlations else []
        high_corr_count = len(high_corr)
        
        # Analiz edilen coin sayısı bilgisi
        col1.metric("📊 Analiz Edilen Coin", total_coins)
        col2.metric("🔗 Toplam Korelasyon Çifti", total_pairs)
        col3.metric("⭐ Yüksek Korelasyon (≥0.7)", high_corr_count)
        col4.metric("📈 Ortalama Korelasyon", f"{np.mean([abs(c.get('correlation', 0)) for c in correlations]):.3f}" if correlations else "N/A")
        
        st.markdown("---")
        
        # En yüksek korelasyonlu çiftler grafiği
        st.subheader("🏆 En Yüksek Korelasyonlu Coin Çiftleri")
        df_corr = pd.DataFrame(correlations)
        if 'abs_correlation' not in df_corr.columns:
            df_corr['abs_correlation'] = df_corr['correlation'].abs()
        df_corr = df_corr.sort_values('abs_correlation', ascending=False).head(20)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_corr['coin1'] + ' ↔ ' + df_corr['coin2'],
            y=df_corr['correlation'],
            marker_color=df_corr['correlation'],
            marker_colorscale='RdBu',
            text=df_corr['correlation'].round(3),
            textposition='outside',
            hovertemplate='%{x}<br>Korelasyon: %{y:.3f}<extra></extra>'
        ))
        fig.update_layout(
            title="Top 20 Yüksek Korelasyonlu Coin Çiftleri",
            xaxis_title="Coin Çifti",
            yaxis_title="Korelasyon",
            height=500,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Pozitif/Negatif ayrımı ile tablo
        st.markdown("---")
        st.subheader("📋 Detaylı Korelasyon Tablosu")
        
        # Pozitif ve Negatif ayrımı
        df_pos = df_corr[df_corr['correlation'] > 0].sort_values('correlation', ascending=False)
        df_neg = df_corr[df_corr['correlation'] < 0].sort_values('correlation', ascending=True)
        
        # Tab görünümü
        tab_all, tab_pos, tab_neg = st.tabs(["📊 Tümü", "📈 Pozitif Korelasyon", "📉 Negatif Korelasyon"])
        
        with tab_all:
            display_all = pd.DataFrame({
                'Coin 1': df_corr['coin1'],
                'Coin 2': df_corr['coin2'],
                'Korelasyon': df_corr['correlation'].apply(lambda x: f"{x:+.4f}"),
                'Mutlak Korelasyon': df_corr['abs_correlation'].apply(lambda x: f"{x:.4f}"),
                'İlişki Tipi': df_corr['correlation'].apply(
                    lambda x: "🟢 Pozitif (Aynı Yön)" if x > 0 else "🔴 Negatif (Ters Yön)"
                ),
                'Açıklama': df_corr['correlation'].apply(
                    lambda x: "Birlikte yükselir/düşer" if x > 0 else "Biri yükselirken diğeri düşer"
                )
            })
            st.dataframe(display_all, use_container_width=True, height=400)
        
        with tab_pos:
            st.info("💡 **Pozitif Korelasyon:** Coinler aynı yönde hareket eder. Biri yükselirse diğeri de yükselir.")
            if len(df_pos) > 0:
                display_pos = pd.DataFrame({
                    'Coin 1': df_pos['coin1'],
                    'Coin 2': df_pos['coin2'],
                    'Korelasyon': df_pos['correlation'].apply(lambda x: f"{x:+.4f}"),
                    'Mutlak Korelasyon': df_pos['abs_correlation'].apply(lambda x: f"{x:.4f}"),
                    'Güç': df_pos['correlation'].apply(
                        lambda x: "🟢🟢🟢 Çok Güçlü" if x > 0.9 else "🟢🟢 Güçlü" if x > 0.8 else "🟢 Orta"
                    )
                })
                st.dataframe(display_pos, use_container_width=True, height=400)
            else:
                st.warning("Pozitif korelasyon bulunamadı.")
        
        with tab_neg:
            st.info("💡 **Negatif Korelasyon:** Coinler ters yönde hareket eder. Biri yükselirse diğeri düşer.")
            if len(df_neg) > 0:
                display_neg = pd.DataFrame({
                    'Coin 1': df_neg['coin1'],
                    'Coin 2': df_neg['coin2'],
                    'Korelasyon': df_neg['correlation'].apply(lambda x: f"{x:+.4f}"),
                    'Mutlak Korelasyon': df_neg['abs_correlation'].apply(lambda x: f"{x:.4f}"),
                    'Güç': df_neg['correlation'].apply(
                        lambda x: "🔴🔴🔴 Çok Güçlü" if x < -0.9 else "🔴🔴 Güçlü" if x < -0.8 else "🔴 Orta"
                    )
                })
                st.dataframe(display_neg, use_container_width=True, height=400)
            else:
                st.warning("Negatif korelasyon bulunamadı.")
        
        # Korelasyon matrisi (önizleme)
        st.markdown("---")
        st.subheader("🗺️ Korelasyon Matrisi Önizleme")
        
        st.info("""
        **Veri Kaynağı Açıklaması:**
        - **Geçmiş Veriler**: Binance REST API'den çekilen geçmiş fiyat verileriyle yapılan korelasyon analizi (1 saatlik aralıklarla, 200 veri noktası)
        - **Anlık Veriler**: WebSocket üzerinden gerçek zamanlı olarak toplanan verilerle yapılan korelasyon analizi (her 5 dakikada bir güncellenir)
        """)
        
        # Veri kaynağı seçimi
        data_source = st.radio(
            "📊 Veri Kaynağı Seçin",
            ["Geçmiş Veriler", "Anlık Veriler"],
            horizontal=True,
            key="home_page_source",
            help="Geçmiş Veriler: REST API'den çekilen geçmiş veriler | Anlık Veriler: WebSocket'ten toplanan gerçek zamanlı veriler"
        )
        
        if data_source == "Geçmiş Veriler":
            corr_matrix_file = "historical_correlation_matrix.csv"
            st.caption("💡 Geçmiş Veriler: Binance REST API'den çekilen 1 saatlik aralıklarla 200 veri noktası kullanılarak hesaplanan korelasyonlar")
        else:
            corr_matrix_file = "realtime_correlation_matrix.csv"
            st.caption("💡 Anlık Veriler: WebSocket üzerinden gerçek zamanlı olarak toplanan verilerle hesaplanan korelasyonlar (her 5 dakikada bir güncellenir)")
        
        corr_matrix = load_csv_file(corr_matrix_file)
        
        if corr_matrix is not None:
            # İlk 15 coin'i göster (önizleme için)
            preview_coins = corr_matrix.columns[:15].tolist()
            preview_matrix = corr_matrix.loc[preview_coins, preview_coins]
            
            fig = px.imshow(
                preview_matrix,
                labels=dict(x="Coin", y="Coin", color="Korelasyon"),
                x=preview_matrix.columns,
                y=preview_matrix.columns,
                color_continuous_scale="RdBu",
                aspect="auto",
                title=f"Korelasyon Matrisi Önizleme (İlk 15 Coin) - {data_source}",
                text_auto=True
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("💡 **Detaylı analiz için:** Sol menüden 'Korelasyon Analizi' sayfasına gidin.")
        
        # Fiyat-Volume analizi önizleme
        st.markdown("---")
        st.subheader("📈 Fiyat-Volume İlişkisi Önizleme")
        st.markdown("""
        **Fiyat-Volume Analizi Nedir?**
        Bu analiz, coin fiyatlarındaki değişimler ile işlem hacmi (volume) değişimleri arasındaki ilişkiyi inceler.
        - **Yüksek pozitif korelasyon**: Fiyat arttığında volume da artıyor (güçlü alım satım ilgisi)
        - **Düşük korelasyon**: Fiyat ve volume arasında zayıf ilişki var
        - **Bu analiz**: Hangi coinlerde fiyat artışının volume artışıyla desteklendiğini gösterir
        """)
        
        pv_data = load_json_file('price_volume_analysis.json')
        if pv_data:
            df_pv = pd.DataFrame([
                {
                    'coin': coin,
                    'correlation': stats.get('correlation', 0),
                    'volume_increase_on_price_up_pct': stats.get('volume_increase_on_price_up_pct', 0),
                    'avg_volume_change_on_price_up': stats.get('avg_volume_change_on_price_up', 0)
                }
                for coin, stats in pv_data.items()
            ])
            if 'abs_correlation' not in df_pv.columns:
                df_pv['abs_correlation'] = df_pv['correlation'].abs()
            df_pv_sorted = df_pv.sort_values('abs_correlation', ascending=False)
            
            # Özet metrikler
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Toplam Coin", len(df_pv))
            col2.metric("Güçlü Pozitif (>0.5)", len(df_pv[df_pv['correlation'] > 0.5]))
            col3.metric("Ortalama Korelasyon", f"{df_pv['correlation'].mean():.3f}")
            col4.metric("Ort. Vol Artışı %", f"{df_pv['volume_increase_on_price_up_pct'].mean():.1f}%")
            
            # Top 20 grafik
            df_pv_top = df_pv_sorted.head(20)
            
            fig = px.scatter(
                df_pv_top,
                x='correlation',
                y='volume_increase_on_price_up_pct',
                size=[10]*len(df_pv_top),
                color='correlation',
                hover_name='coin',
                title="Top 20: Fiyat-Volume Korelasyonu vs Volume Artışı",
                labels={
                    'correlation': 'Fiyat-Volume Korelasyonu',
                    'volume_increase_on_price_up_pct': 'Fiyat Artışında Volume Artışı %'
                },
                color_continuous_scale='RdBu'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # En yüksek korelasyonlu coinler
            st.markdown("#### 🔝 En Yüksek Fiyat-Volume Korelasyonlu Coinler")
            st.dataframe(
                df_pv_sorted[['coin', 'correlation', 'volume_increase_on_price_up_pct']].head(10),
                use_container_width=True,
                hide_index=True
            )
            
            st.info("💡 **Detaylı analiz için:** Sol menüden 'Fiyat-Volume Analizi' sayfasına gidin.")
        else:
            st.warning("⚠️ Fiyat-Volume analiz verisi bulunamadı.")
        
        # Ani Değişim Analizi önizleme
        st.markdown("---")
        st.subheader("⚡ Ani Fiyat Değişimlerinde Volume Analizi Önizleme")
        st.markdown("""
        **Ani Değişim Analizi Nedir?**
        Bu analiz, ani fiyat değişimlerinde (spike) volume'un nasıl davrandığını inceler.
        - **Ani Yükseliş**: Fiyat kısa sürede belirli bir eşiğin üzerine çıkarsa (örn: %2, %5, %10)
        - **Ani Düşüş**: Fiyat kısa sürede belirli bir eşiğin altına düşerse
        - **Bu analiz**: Ani değişimlerde volume'un da artıp artmadığını gösterir (gerçek piyasa hareketi mi yoksa manipülasyon mu?)
        """)
        
        sudden_data = load_json_file('sudden_price_volume_analysis.json')
        if sudden_data:
            # Eşik seçimi (varsayılan %2)
            threshold_options = [1.0, 2.0, 5.0, 10.0]
            selected_threshold = st.selectbox(
                "Eşik Seçin (%)",
                threshold_options,
                index=1,  # Varsayılan %2
                key="home_sudden_threshold"
            )
            
            threshold_key = f"threshold_{selected_threshold}"
            
            # Verileri topla
            coin_stats = []
            for coin, data in sudden_data.items():
                if threshold_key in data:
                    thresh_data = data[threshold_key]
                    sudden_up = thresh_data.get('sudden_up', {})
                    sudden_down = thresh_data.get('sudden_down', {})
                    
                    if sudden_up.get('count', 0) > 0 or sudden_down.get('count', 0) > 0:
                        coin_stats.append({
                            'coin': coin,
                            'sudden_up_count': sudden_up.get('count', 0),
                            'sudden_down_count': sudden_down.get('count', 0),
                            'total_sudden': sudden_up.get('count', 0) + sudden_down.get('count', 0),
                            'up_vol_increase_pct': sudden_up.get('volume_increase_pct', 0),
                            'down_vol_increase_pct': sudden_down.get('volume_increase_pct', 0),
                            'up_avg_vol_change': sudden_up.get('avg_volume_change', 0),
                            'down_avg_vol_change': sudden_down.get('avg_volume_change', 0)
                        })
            
            if coin_stats:
                df_sudden = pd.DataFrame(coin_stats)
                df_sudden = df_sudden.sort_values('total_sudden', ascending=False).head(20)
                
                # Özet metrikler
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Toplam Ani Değişim", df_sudden['total_sudden'].sum())
                col2.metric("Ani Yükseliş", df_sudden['sudden_up_count'].sum())
                col3.metric("Ani Düşüş", df_sudden['sudden_down_count'].sum())
                col4.metric("Yükselişte Vol↑ Ort.%", 
                           f"{df_sudden[df_sudden['sudden_up_count']>0]['up_vol_increase_pct'].mean():.1f}%")
                
                # Grafik
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_sudden['coin'],
                    y=df_sudden['sudden_up_count'],
                    name='Ani Yükseliş',
                    marker_color='green'
                ))
                fig.add_trace(go.Bar(
                    x=df_sudden['coin'],
                    y=df_sudden['sudden_down_count'],
                    name='Ani Düşüş',
                    marker_color='red'
                ))
                fig.update_layout(
                    title=f"Ani Değişim Sayıları (Eşik: ±{selected_threshold}%) - Top 20",
                    xaxis_title="Coin",
                    yaxis_title="Sayı",
                    barmode='group',
                    height=400,
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # En fazla ani değişim yaşayan coinler
                st.markdown(f"#### 🔝 En Fazla Ani Değişim Yaşayan Coinler (Eşik: ±{selected_threshold}%)")
                st.dataframe(
                    df_sudden[['coin', 'total_sudden', 'sudden_up_count', 'sudden_down_count', 
                              'up_vol_increase_pct', 'down_vol_increase_pct']].head(10),
                    use_container_width=True,
                    hide_index=True
                )
                
                st.info("💡 **Detaylı analiz için:** Sol menüden 'Ani Değişim Analizi' sayfasına gidin.")
            else:
                st.warning(f"⚠️ {selected_threshold}% eşiği için veri bulunamadı.")
        else:
            st.warning("⚠️ Ani değişim analiz verisi bulunamadı.")
    else:
        st.warning("⚠️ Analiz dosyaları bulunamadı. Önce `python main.py` komutu ile analizleri çalıştırın.")
        st.markdown("""
        **Hızlı Başlangıç:**
        1. Terminal'de `python main.py` komutunu çalıştırın
        2. Analizler tamamlandıktan sonra dashboard'u yenileyin
        3. Sonuçları görselleştirin
        """)

# ==================== KORELASYON ANALİZİ ====================
elif page == "Korelasyon Analizi":
    st.header("🔗 Coin Korelasyon Analizi")
    
    # Veri kaynağı seçimi
    data_source = st.radio(
        "Veri Kaynağı",
        ["Geçmiş Veriler", "Anlık Veriler"],
        horizontal=True
    )
    
    if data_source == "Geçmiş Veriler":
        corr_matrix_file = "historical_correlation_matrix.csv"
        correlations_file = "historical_correlations.json"
        coin_correlations_file = "historical_coin_correlations.json"
    else:
        corr_matrix_file = "realtime_correlation_matrix.csv"
        correlations_file = "realtime_correlations.json"
        coin_correlations_file = "realtime_coin_correlations.json"
    
    # Korelasyon matrisi
    corr_matrix = load_csv_file(corr_matrix_file)
    
    if corr_matrix is not None:
        st.subheader("📊 Korelasyon Matrisi")
        
        # Coin seçimi
        coins = corr_matrix.columns.tolist()
        selected_coins = st.multiselect(
            "Coin Seçin (boş bırakırsanız tüm coinler gösterilir)",
            coins,
            default=coins[:20] if len(coins) > 20 else coins
        )
        
        if selected_coins:
            filtered_matrix = corr_matrix.loc[selected_coins, selected_coins]
            
            # Heatmap
            fig = px.imshow(
                filtered_matrix,
                labels=dict(x="Coin", y="Coin", color="Korelasyon"),
                x=filtered_matrix.columns,
                y=filtered_matrix.columns,
                color_continuous_scale="RdBu",
                aspect="auto",
                title="Korelasyon Matrisi Heatmap"
            )
            fig.update_layout(height=800)
            st.plotly_chart(fig, use_container_width=True)
        
        # Yüksek korelasyonlu çiftler
        st.subheader("🔗 Yüksek Korelasyonlu Çiftler")
        
        correlations = load_json_file(correlations_file)
        if correlations:
            df_corr = pd.DataFrame(correlations)
            
            # Filtreleme
            threshold = st.slider(
                "Minimum Korelasyon Eşiği",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.05
            )
            
            filtered_corr = df_corr[df_corr['abs_correlation'] >= threshold].sort_values(
                'abs_correlation', 
                ascending=False
            )
            
            # Pozitif ve Negatif korelasyonları ayır
            positive_corr = filtered_corr[filtered_corr['correlation'] > 0].sort_values('correlation', ascending=False)
            negative_corr = filtered_corr[filtered_corr['correlation'] < 0].sort_values('correlation', ascending=True)
            
            # Tab görünümü ile pozitif/negatif ayrımı
            tab1, tab2, tab3 = st.tabs(["📊 Tümü", "📈 Pozitif Korelasyon", "📉 Negatif Korelasyon"])
            
            with tab1:
                st.markdown("**Tüm Yüksek Korelasyonlu Çiftler**")
                # Renk kodlu tablo
                display_df = pd.DataFrame({
                    'Coin 1': filtered_corr['coin1'],
                    'Coin 2': filtered_corr['coin2'],
                    'Korelasyon': filtered_corr['correlation'].apply(lambda x: f"{x:+.4f}"),
                    'Mutlak Korelasyon': filtered_corr['abs_correlation'].apply(lambda x: f"{x:.4f}"),
                    'İlişki Tipi': filtered_corr['correlation'].apply(
                        lambda x: "🟢 Pozitif (Aynı Yön)" if x > 0 else "🔴 Negatif (Ters Yön)"
                    ),
                    'Açıklama': filtered_corr['correlation'].apply(
                        lambda x: "Birlikte yükselir/düşer" if x > 0 else "Biri yükselirken diğeri düşer"
                    )
                })
                st.dataframe(display_df, use_container_width=True, height=400)
            
            with tab2:
                st.markdown("**📈 Pozitif Korelasyonlu Çiftler**")
                st.info("💡 **Pozitif Korelasyon:** Coinler aynı yönde hareket eder. Biri yükselirse diğeri de yükselir, biri düşerse diğeri de düşer.")
                
                if len(positive_corr) > 0:
                    pos_display = pd.DataFrame({
                        'Coin 1': positive_corr['coin1'],
                        'Coin 2': positive_corr['coin2'],
                        'Korelasyon': positive_corr['correlation'].apply(lambda x: f"{x:+.4f}"),
                        'Mutlak Korelasyon': positive_corr['abs_correlation'].apply(lambda x: f"{x:.4f}"),
                        'Güç': positive_corr['correlation'].apply(
                            lambda x: "🟢🟢🟢 Çok Güçlü" if x > 0.9 else "🟢🟢 Güçlü" if x > 0.8 else "🟢 Orta"
                        ),
                        'Açıklama': "Birlikte yükselir/düşer"
                    })
                    st.dataframe(pos_display, use_container_width=True, height=400)
                    
                    # Pozitif korelasyon grafiği
                    fig_pos = go.Figure()
                    fig_pos.add_trace(go.Bar(
                        x=positive_corr['coin1'] + ' ↔ ' + positive_corr['coin2'],
                        y=positive_corr['correlation'],
                        marker_color='green',
                        text=positive_corr['correlation'].round(3),
                        textposition='outside',
                        hovertemplate='%{x}<br>Korelasyon: %{y:.3f}<br>Tip: Pozitif (Aynı Yön)<extra></extra>'
                    ))
                    fig_pos.update_layout(
                        title="Pozitif Korelasyonlu Coin Çiftleri",
                        xaxis_title="Coin Çifti",
                        yaxis_title="Korelasyon Değeri",
                        height=500,
                        xaxis_tickangle=-45,
                        yaxis_range=[0, 1]
                    )
                    st.plotly_chart(fig_pos, use_container_width=True)
                else:
                    st.warning("⚠️ Seçilen eşik için pozitif korelasyonlu çift bulunamadı.")
            
            with tab3:
                st.markdown("**📉 Negatif Korelasyonlu Çiftler**")
                st.info("💡 **Negatif Korelasyon:** Coinler ters yönde hareket eder. Biri yükselirse diğeri düşer, biri düşerse diğeri yükselir.")
                
                if len(negative_corr) > 0:
                    neg_display = pd.DataFrame({
                        'Coin 1': negative_corr['coin1'],
                        'Coin 2': negative_corr['coin2'],
                        'Korelasyon': negative_corr['correlation'].apply(lambda x: f"{x:+.4f}"),
                        'Mutlak Korelasyon': negative_corr['abs_correlation'].apply(lambda x: f"{x:.4f}"),
                        'Güç': negative_corr['correlation'].apply(
                            lambda x: "🔴🔴🔴 Çok Güçlü" if x < -0.9 else "🔴🔴 Güçlü" if x < -0.8 else "🔴 Orta"
                        ),
                        'Açıklama': "Biri yükselirken diğeri düşer"
                    })
                    st.dataframe(neg_display, use_container_width=True, height=400)
                    
                    # Negatif korelasyon grafiği
                    fig_neg = go.Figure()
                    fig_neg.add_trace(go.Bar(
                        x=negative_corr['coin1'] + ' ↔ ' + negative_corr['coin2'],
                        y=negative_corr['correlation'],
                        marker_color='red',
                        text=negative_corr['correlation'].round(3),
                        textposition='outside',
                        hovertemplate='%{x}<br>Korelasyon: %{y:.3f}<br>Tip: Negatif (Ters Yön)<extra></extra>'
                    ))
                    fig_neg.update_layout(
                        title="Negatif Korelasyonlu Coin Çiftleri",
                        xaxis_title="Coin Çifti",
                        yaxis_title="Korelasyon Değeri",
                        height=500,
                        xaxis_tickangle=-45,
                        yaxis_range=[-1, 0]
                    )
                    st.plotly_chart(fig_neg, use_container_width=True)
                else:
                    st.warning("⚠️ Seçilen eşik için negatif korelasyonlu çift bulunamadı.")
            
            # Özet istatistikler
            st.markdown("---")
            st.subheader("📊 Özet İstatistikler")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Toplam Çift", len(filtered_corr))
            col2.metric("📈 Pozitif", len(positive_corr), f"%{len(positive_corr)/len(filtered_corr)*100:.1f}" if len(filtered_corr) > 0 else "")
            col3.metric("📉 Negatif", len(negative_corr), f"%{len(negative_corr)/len(filtered_corr)*100:.1f}" if len(filtered_corr) > 0 else "")
            col4.metric("Ortalama", f"{filtered_corr['correlation'].mean():.3f}")
            
            # Grafik
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=filtered_corr['coin1'] + ' - ' + filtered_corr['coin2'],
                y=filtered_corr['correlation'],
                marker_color=filtered_corr['correlation'],
                marker_colorscale='RdBu',
                text=filtered_corr['correlation'].round(3),
                textposition='outside'
            ))
            fig.update_layout(
                title="Yüksek Korelasyonlu Coin Çiftleri",
                xaxis_title="Coin Çifti",
                yaxis_title="Korelasyon",
                height=600,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Coin bazlı analiz
        st.subheader("💰 Coin Bazlı Korelasyon Analizi")
        
        coin_correlations = load_json_file(coin_correlations_file)
        if coin_correlations:
            # Tek coin analizi
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_coin = st.selectbox("Coin Seçin", list(coin_correlations.keys()))
            
            with col2:
                show_all_coins = st.checkbox("Tüm coinlerle göster", value=False)
            
            if selected_coin:
                coin_data = coin_correlations[selected_coin]
                high_corr = coin_data.get('high_correlations', [])
                top_corr = coin_data.get('top_correlations', [])
                
                if top_corr:
                    df_coin = pd.DataFrame(top_corr)
                    
                    # Kaç coin gösterilecek
                    if not show_all_coins:
                        df_coin = df_coin.head(20)
                    
                    # Grafik
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=df_coin['coin'],
                        y=df_coin['correlation'],
                        marker_color=df_coin['correlation'],
                        marker_colorscale='RdBu',
                        text=df_coin['correlation'].round(3),
                        textposition='outside'
                    ))
                    fig.update_layout(
                        title=f"{selected_coin} - En Yüksek Korelasyonlu Coinler",
                        xaxis_title="Coin",
                        yaxis_title="Korelasyon",
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(df_coin, use_container_width=True)
        
        # Çoklu coin korelasyon analizi
        st.subheader("🔗 Çoklu Coin Korelasyon Analizi")
        st.markdown("**Seçilen coinlerin birbirleriyle olan korelasyonlarını görüntüleyin**")
        
        if corr_matrix is not None:
            available_coins = corr_matrix.columns.tolist()
            
            # Coin seçimi (multiselect)
            selected_coins_for_analysis = st.multiselect(
                "Analiz edilecek coinleri seçin (en az 2 coin)",
                available_coins,
                default=['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'ADAUSDT', 'LINKUSDT', 'DOGEUSDT'] if len(available_coins) > 7 else available_coins[:5]
            )
            
            if len(selected_coins_for_analysis) >= 2:
                # Seçilen coinlerin korelasyon matrisini al
                selected_matrix = corr_matrix.loc[selected_coins_for_analysis, selected_coins_for_analysis]
                
                # Heatmap
                st.markdown("### 📊 Seçilen Coinlerin Birbirleriyle Korelasyon Matrisi")
                fig = px.imshow(
                    selected_matrix,
                    labels=dict(x="Coin", y="Coin", color="Korelasyon"),
                    x=selected_matrix.columns,
                    y=selected_matrix.columns,
                    color_continuous_scale="RdBu",
                    aspect="auto",
                    text_auto=True,
                    title="Çoklu Coin Korelasyon Heatmap"
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
                
                # Korelasyon tablosu - Pozitif/Negatif ayrımı ile
                st.markdown("### 📋 Detaylı Korelasyon Tablosu")
                
                # Üst üçgen matrisi (duplicate'leri önlemek için)
                correlation_pairs = []
                for i, coin1 in enumerate(selected_coins_for_analysis):
                    for j, coin2 in enumerate(selected_coins_for_analysis):
                        if i < j:  # Üst üçgen
                            corr_value = selected_matrix.loc[coin1, coin2]
                            correlation_pairs.append({
                                'Coin 1': coin1,
                                'Coin 2': coin2,
                                'Korelasyon': corr_value,
                                'Mutlak Korelasyon': abs(corr_value)
                            })
                
                df_pairs = pd.DataFrame(correlation_pairs)
                df_pairs = df_pairs.sort_values('Mutlak Korelasyon', ascending=False)
                
                # Pozitif ve Negatif ayrımı
                df_pairs_positive = df_pairs[df_pairs['Korelasyon'] > 0].copy()
                df_pairs_negative = df_pairs[df_pairs['Korelasyon'] < 0].copy()
                
                # Tab görünümü
                tab_all, tab_pos, tab_neg = st.tabs(["📊 Tümü", "📈 Pozitif", "📉 Negatif"])
                
                with tab_all:
                    # Renk kodlu tablo
                    display_all = pd.DataFrame({
                        'Coin 1': df_pairs['Coin 1'],
                        'Coin 2': df_pairs['Coin 2'],
                        'Korelasyon': df_pairs['Korelasyon'].apply(lambda x: f"{x:+.4f}"),
                        'Mutlak Korelasyon': df_pairs['Mutlak Korelasyon'].apply(lambda x: f"{x:.4f}"),
                        'İlişki': df_pairs['Korelasyon'].apply(
                            lambda x: "🟢 Pozitif" if x > 0 else "🔴 Negatif" if x < 0 else "⚪ Sıfır"
                        ),
                        'Açıklama': df_pairs['Korelasyon'].apply(
                            lambda x: "Aynı yönde hareket" if x > 0 else "Ters yönde hareket" if x < 0 else "İlişki yok"
                        )
                    })
                    st.dataframe(display_all, use_container_width=True, height=400)
                
                with tab_pos:
                    st.markdown("**📈 Pozitif Korelasyonlu Çiftler (Aynı Yönde Hareket)**")
                    if len(df_pairs_positive) > 0:
                        display_pos = pd.DataFrame({
                            'Coin 1': df_pairs_positive['Coin 1'],
                            'Coin 2': df_pairs_positive['Coin 2'],
                            'Korelasyon': df_pairs_positive['Korelasyon'].apply(lambda x: f"{x:+.4f}"),
                            'Mutlak Korelasyon': df_pairs_positive['Mutlak Korelasyon'].apply(lambda x: f"{x:.4f}"),
                            'Güç': df_pairs_positive['Korelasyon'].apply(
                                lambda x: "🟢🟢🟢 Çok Güçlü" if x > 0.9 else "🟢🟢 Güçlü" if x > 0.8 else "🟢 Orta" if x > 0.6 else "🟢 Zayıf"
                            )
                        })
                        st.dataframe(display_pos, use_container_width=True, height=400)
                    else:
                        st.info("Seçilen coinler arasında pozitif korelasyon bulunamadı.")
                
                with tab_neg:
                    st.markdown("**📉 Negatif Korelasyonlu Çiftler (Ters Yönde Hareket)**")
                    if len(df_pairs_negative) > 0:
                        display_neg = pd.DataFrame({
                            'Coin 1': df_pairs_negative['Coin 1'],
                            'Coin 2': df_pairs_negative['Coin 2'],
                            'Korelasyon': df_pairs_negative['Korelasyon'].apply(lambda x: f"{x:+.4f}"),
                            'Mutlak Korelasyon': df_pairs_negative['Mutlak Korelasyon'].apply(lambda x: f"{x:.4f}"),
                            'Güç': df_pairs_negative['Korelasyon'].apply(
                                lambda x: "🔴🔴🔴 Çok Güçlü" if x < -0.9 else "🔴🔴 Güçlü" if x < -0.8 else "🔴 Orta" if x < -0.6 else "🔴 Zayıf"
                            )
                        })
                        st.dataframe(display_neg, use_container_width=True, height=400)
                    else:
                        st.info("Seçilen coinler arasında negatif korelasyon bulunamadı.")
                
                # En yüksek korelasyonlu çiftler - Pozitif/Negatif ayrımı ile
                st.markdown("### 🏆 En Yüksek Korelasyonlu Çiftler")
                
                threshold_multi = st.slider(
                    "Minimum Korelasyon Eşiği",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.7,
                    step=0.05,
                    key="multi_coin_threshold"
                )
                
                high_corr_pairs = df_pairs[df_pairs['Mutlak Korelasyon'] >= threshold_multi]
                high_pos = high_corr_pairs[high_corr_pairs['Korelasyon'] > 0]
                high_neg = high_corr_pairs[high_corr_pairs['Korelasyon'] < 0]
                
                if len(high_corr_pairs) > 0:
                    # Grafik - Pozitif ve Negatif birlikte
                    fig = go.Figure()
                    
                    if len(high_pos) > 0:
                        fig.add_trace(go.Bar(
                            x=high_pos['Coin 1'] + ' ↔ ' + high_pos['Coin 2'],
                            y=high_pos['Korelasyon'],
                            name='Pozitif Korelasyon',
                            marker_color='green',
                            text=high_pos['Korelasyon'].round(3),
                            textposition='outside',
                            hovertemplate='%{x}<br>Korelasyon: %{y:.3f}<br>Tip: Pozitif (Aynı Yön)<extra></extra>'
                        ))
                    
                    if len(high_neg) > 0:
                        fig.add_trace(go.Bar(
                            x=high_neg['Coin 1'] + ' ↔ ' + high_neg['Coin 2'],
                            y=high_neg['Korelasyon'],
                            name='Negatif Korelasyon',
                            marker_color='red',
                            text=high_neg['Korelasyon'].round(3),
                            textposition='outside',
                            hovertemplate='%{x}<br>Korelasyon: %{y:.3f}<br>Tip: Negatif (Ters Yön)<extra></extra>'
                        ))
                    
                    fig.update_layout(
                        title=f"Yüksek Korelasyonlu Coin Çiftleri (Eşik: ≥{threshold_multi})",
                        xaxis_title="Coin Çifti",
                        yaxis_title="Korelasyon Değeri",
                        height=500,
                        xaxis_tickangle=-45,
                        barmode='group',
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Özet tablo
                    st.markdown("#### 📊 Özet Tablo")
                    summary_df = pd.DataFrame({
                        'Coin 1': high_corr_pairs['Coin 1'],
                        'Coin 2': high_corr_pairs['Coin 2'],
                        'Korelasyon': high_corr_pairs['Korelasyon'].apply(lambda x: f"{x:+.4f}"),
                        'Mutlak Korelasyon': high_corr_pairs['Mutlak Korelasyon'].apply(lambda x: f"{x:.4f}"),
                        'Tip': high_corr_pairs['Korelasyon'].apply(
                            lambda x: "🟢 Pozitif" if x > 0 else "🔴 Negatif"
                        ),
                        'Açıklama': high_corr_pairs['Korelasyon'].apply(
                            lambda x: "Aynı yönde hareket" if x > 0 else "Ters yönde hareket"
                        )
                    })
                    st.dataframe(summary_df, use_container_width=True, height=300)
                    
                    # Özet istatistikler
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Toplam Çift", len(df_pairs))
                    col2.metric("Yüksek Korelasyon", len(high_corr_pairs))
                    col3.metric("Ortalama Korelasyon", f"{df_pairs['Korelasyon'].mean():.3f}")
                    col4.metric("Maksimum Korelasyon", f"{df_pairs['Korelasyon'].max():.3f}")
                else:
                    st.info(f"⚠️ Seçilen coinler arasında {threshold_multi} eşiğinden yüksek korelasyon bulunamadı.")
            elif len(selected_coins_for_analysis) == 1:
                st.warning("⚠️ En az 2 coin seçmelisiniz!")
            else:
                st.info("ℹ️ Analiz için coin seçin.")
    else:
        st.warning(f"⚠️ {corr_matrix_file} dosyası bulunamadı. Önce analiz çalıştırın.")

# ==================== TÜM KORELASYONLAR ====================
elif page == "Tüm Korelasyonlar":
    st.header("📊 Tüm Coin Çiftleri Korelasyon Listesi")
    
    st.info("""
    **Bu sayfada analiz edilen tüm coin çiftlerinin korelasyon değerlerini görebilirsiniz.**
    - Filtreleme, arama ve sıralama yapabilirsiniz
    - Pozitif/Negatif korelasyonları ayrı ayrı görüntüleyebilirsiniz
    - Excel'e aktarabilirsiniz
    """)
    
    # Veri kaynağı seçimi
    data_source = st.radio(
        "Veri Kaynağı",
        ["Geçmiş Veriler", "Anlık Veriler"],
        horizontal=True,
        key="all_correlations_source"
    )
    
    if data_source == "Geçmiş Veriler":
        correlations_file = "historical_correlations.json"
        corr_matrix_file = "historical_correlation_matrix.csv"
    else:
        correlations_file = "realtime_correlations.json"
        corr_matrix_file = "realtime_correlation_matrix.csv"
    
    correlations = load_json_file(correlations_file)
    corr_matrix = load_csv_file(corr_matrix_file)
    
    if correlations:
        df_all = pd.DataFrame(correlations)
        
        # abs_correlation kolonu yoksa ekle
        if 'abs_correlation' not in df_all.columns:
            df_all['abs_correlation'] = df_all['correlation'].abs()
        
        # Filtreleme ve arama
        st.subheader("🔍 Filtreleme ve Arama")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_correlation = st.slider(
                "Minimum Korelasyon",
                min_value=-1.0,
                max_value=1.0,
                value=-1.0,
                step=0.1,
                key="all_min_corr"
            )
        
        with col2:
            max_correlation = st.slider(
                "Maksimum Korelasyon",
                min_value=-1.0,
                max_value=1.0,
                value=1.0,
                step=0.1,
                key="all_max_corr"
            )
        
        with col3:
            correlation_type = st.selectbox(
                "Korelasyon Tipi",
                ["Tümü", "Pozitif", "Negatif"],
                key="all_corr_type"
            )
        
        # Coin arama
        search_coin = st.text_input("🔎 Coin Ara (örn: BTC, ETH)", "").upper()
        
        # Filtreleme
        filtered_df = df_all[
            (df_all['correlation'] >= min_correlation) & 
            (df_all['correlation'] <= max_correlation)
        ].copy()
        
        if correlation_type == "Pozitif":
            filtered_df = filtered_df[filtered_df['correlation'] > 0]
        elif correlation_type == "Negatif":
            filtered_df = filtered_df[filtered_df['correlation'] < 0]
        
        if search_coin:
            filtered_df = filtered_df[
                (filtered_df['coin1'].str.contains(search_coin, case=False, na=False)) |
                (filtered_df['coin2'].str.contains(search_coin, case=False, na=False))
            ]
        
        # Sıralama
        sort_by = st.selectbox(
            "Sıralama",
            ["Mutlak Korelasyon (Yüksekten Düşüğe)", "Mutlak Korelasyon (Düşükten Yükseğe)", 
             "Korelasyon (Yüksekten Düşüğe)", "Korelasyon (Düşükten Yükseğe)", 
             "Coin 1 (A-Z)", "Coin 2 (A-Z)"],
            key="all_sort"
        )
        
        if sort_by == "Mutlak Korelasyon (Yüksekten Düşüğe)":
            filtered_df = filtered_df.sort_values('abs_correlation', ascending=False)
        elif sort_by == "Mutlak Korelasyon (Düşükten Yükseğe)":
            filtered_df = filtered_df.sort_values('abs_correlation', ascending=True)
        elif sort_by == "Korelasyon (Yüksekten Düşüğe)":
            filtered_df = filtered_df.sort_values('correlation', ascending=False)
        elif sort_by == "Korelasyon (Düşükten Yükseğe)":
            filtered_df = filtered_df.sort_values('correlation', ascending=True)
        elif sort_by == "Coin 1 (A-Z)":
            filtered_df = filtered_df.sort_values('coin1', ascending=True)
        elif sort_by == "Coin 2 (A-Z)":
            filtered_df = filtered_df.sort_values('coin2', ascending=True)
        
        # Özet istatistikler
        st.markdown("---")
        st.subheader("📊 Özet İstatistikler")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Toplam Çift", len(df_all))
        col2.metric("Filtrelenmiş", len(filtered_df))
        col3.metric("📈 Pozitif", len(filtered_df[filtered_df['correlation'] > 0]))
        col4.metric("📉 Negatif", len(filtered_df[filtered_df['correlation'] < 0]))
        col5.metric("Ortalama", f"{filtered_df['correlation'].mean():.3f}")
        
        # Tab görünümü
        tab_all, tab_pos, tab_neg = st.tabs(["📊 Tümü", "📈 Pozitif Korelasyonlar", "📉 Negatif Korelasyonlar"])
        
        with tab_all:
            st.markdown(f"### Tüm Korelasyonlar ({len(filtered_df)} çift)")
            
            # Görüntüleme için DataFrame hazırla
            display_all = pd.DataFrame({
                'Coin 1': filtered_df['coin1'],
                'Coin 2': filtered_df['coin2'],
                'Korelasyon': filtered_df['correlation'].apply(lambda x: f"{x:+.4f}"),
                'Mutlak Korelasyon': filtered_df['abs_correlation'].apply(lambda x: f"{x:.4f}"),
                'İlişki Tipi': filtered_df['correlation'].apply(
                    lambda x: "🟢 Pozitif" if x > 0 else "🔴 Negatif" if x < 0 else "⚪ Sıfır"
                ),
                'Açıklama': filtered_df['correlation'].apply(
                    lambda x: "Aynı yönde hareket" if x > 0 else "Ters yönde hareket" if x < 0 else "İlişki yok"
                )
            })
            
            st.dataframe(display_all, use_container_width=True, height=600)
            
            # CSV indirme
            csv = filtered_df[['coin1', 'coin2', 'correlation', 'abs_correlation']].to_csv(index=False)
            st.download_button(
                label="📥 CSV Olarak İndir",
                data=csv,
                file_name=f"tum_korelasyonlar_{data_source.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
        
        with tab_pos:
            df_pos_all = filtered_df[filtered_df['correlation'] > 0].sort_values('correlation', ascending=False)
            st.markdown(f"### Pozitif Korelasyonlar ({len(df_pos_all)} çift)")
            
            if len(df_pos_all) > 0:
                display_pos = pd.DataFrame({
                    'Coin 1': df_pos_all['coin1'],
                    'Coin 2': df_pos_all['coin2'],
                    'Korelasyon': df_pos_all['correlation'].apply(lambda x: f"{x:+.4f}"),
                    'Mutlak Korelasyon': df_pos_all['abs_correlation'].apply(lambda x: f"{x:.4f}"),
                    'Güç': df_pos_all['correlation'].apply(
                        lambda x: "🟢🟢🟢 Çok Güçlü" if x > 0.9 else "🟢🟢 Güçlü" if x > 0.8 else "🟢 Orta" if x > 0.6 else "🟢 Zayıf"
                    )
                })
                st.dataframe(display_pos, use_container_width=True, height=600)
                
                csv_pos = df_pos_all[['coin1', 'coin2', 'correlation', 'abs_correlation']].to_csv(index=False)
                st.download_button(
                    label="📥 Pozitif Korelasyonları CSV Olarak İndir",
                    data=csv_pos,
                    file_name=f"pozitif_korelasyonlar_{data_source.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Filtrelenmiş sonuçlarda pozitif korelasyon bulunamadı.")
        
        with tab_neg:
            df_neg_all = filtered_df[filtered_df['correlation'] < 0].sort_values('correlation', ascending=True)
            st.markdown(f"### Negatif Korelasyonlar ({len(df_neg_all)} çift)")
            
            if len(df_neg_all) > 0:
                display_neg = pd.DataFrame({
                    'Coin 1': df_neg_all['coin1'],
                    'Coin 2': df_neg_all['coin2'],
                    'Korelasyon': df_neg_all['correlation'].apply(lambda x: f"{x:+.4f}"),
                    'Mutlak Korelasyon': df_neg_all['abs_correlation'].apply(lambda x: f"{x:.4f}"),
                    'Güç': df_neg_all['correlation'].apply(
                        lambda x: "🔴🔴🔴 Çok Güçlü" if x < -0.9 else "🔴🔴 Güçlü" if x < -0.8 else "🔴 Orta" if x < -0.6 else "🔴 Zayıf"
                    )
                })
                st.dataframe(display_neg, use_container_width=True, height=600)
                
                csv_neg = df_neg_all[['coin1', 'coin2', 'correlation', 'abs_correlation']].to_csv(index=False)
                st.download_button(
                    label="📥 Negatif Korelasyonları CSV Olarak İndir",
                    data=csv_neg,
                    file_name=f"negatif_korelasyonlar_{data_source.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Filtrelenmiş sonuçlarda negatif korelasyon bulunamadı.")
        
        # Grafik görünümü
        st.markdown("---")
        st.subheader("📈 Görselleştirme")
        
        if len(filtered_df) > 0:
            # İlk 50 çifti göster (performans için)
            show_count = min(50, len(filtered_df))
            df_chart = filtered_df.head(show_count)
            
            fig = go.Figure()
            
            # Pozitif korelasyonlar
            pos_data = df_chart[df_chart['correlation'] > 0]
            if len(pos_data) > 0:
                fig.add_trace(go.Bar(
                    x=pos_data['coin1'] + ' ↔ ' + pos_data['coin2'],
                    y=pos_data['correlation'],
                    name='Pozitif Korelasyon',
                    marker_color='green',
                    text=pos_data['correlation'].round(3),
                    textposition='outside',
                    hovertemplate='%{x}<br>Korelasyon: %{y:.3f}<br>Tip: Pozitif<extra></extra>'
                ))
            
            # Negatif korelasyonlar
            neg_data = df_chart[df_chart['correlation'] < 0]
            if len(neg_data) > 0:
                fig.add_trace(go.Bar(
                    x=neg_data['coin1'] + ' ↔ ' + neg_data['coin2'],
                    y=neg_data['correlation'],
                    name='Negatif Korelasyon',
                    marker_color='red',
                    text=neg_data['correlation'].round(3),
                    textposition='outside',
                    hovertemplate='%{x}<br>Korelasyon: %{y:.3f}<br>Tip: Negatif<extra></extra>'
                ))
            
            fig.update_layout(
                title=f"Korelasyon Görselleştirmesi (İlk {show_count} çift)",
                xaxis_title="Coin Çifti",
                yaxis_title="Korelasyon Değeri",
                height=600,
                xaxis_tickangle=-45,
                barmode='group',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if len(filtered_df) > show_count:
                st.info(f"💡 Grafikte ilk {show_count} çift gösteriliyor. Toplam {len(filtered_df)} çift var.")
        else:
            st.warning("Filtrelenmiş sonuç bulunamadı.")
    else:
        st.warning(f"⚠️ {correlations_file} dosyası bulunamadı. Önce analiz çalıştırın.")

# ==================== FİYAT-VOLUME ANALİZİ ====================
elif page == "Fiyat-Volume Analizi":
    st.header("📈 Fiyat-Volume İlişkisi")
    
    pv_data = load_json_file('price_volume_analysis.json')
    
    if not pv_data:
        st.warning("⚠️ price_volume_analysis.json dosyası bulunamadı.")
        st.info("""
        **Bu analiz için `main.py` çalıştırılmalıdır.**
        
        **Nasıl Çalışır?**
        1. Terminal'de `python main.py` komutunu çalıştırın
        2. Sistem otomatik olarak WebSocket'ten veri toplamaya başlar
        3. Her 30 dakikada bir analiz yapılır ve dosyalar güncellenir
        4. Bu sayfada sonuçları görüntüleyebilirsiniz
        
        **Not:** İlk analiz için yeterli veri toplanması gereklidir (yaklaşık 30 dakika).
        """)
        st.stop()
    
    if pv_data:
        df_pv = pd.DataFrame([
            {
                'coin': coin,
                'correlation': stats.get('correlation', 0),
                'abs_correlation': stats.get('abs_correlation', 0),
                'data_points': stats.get('data_points', 0),
                'volume_increase_on_price_up_pct': stats.get('volume_increase_on_price_up_pct', 0),
                'avg_volume_change_on_price_up': stats.get('avg_volume_change_on_price_up', 0)
            }
            for coin, stats in pv_data.items()
        ])
        
        # Filtreleme
        threshold = st.slider(
            "Minimum Korelasyon",
            min_value=-1.0,
            max_value=1.0,
            value=0.0,
            step=0.1
        )
        
        filtered_pv = df_pv[df_pv['abs_correlation'] >= abs(threshold)].sort_values(
            'abs_correlation',
            ascending=False
        )
        
        # Metrikler
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Toplam Coin", len(df_pv))
        col2.metric("Ortalama Korelasyon", f"{df_pv['correlation'].mean():.3f}")
        col3.metric("Güçlü Pozitif (>0.5)", len(df_pv[df_pv['correlation'] > 0.5]))
        col4.metric("Fiyat↑'da Vol↑ Ort.%", f"{df_pv['volume_increase_on_price_up_pct'].mean():.2f}%")
        
        # Grafikler
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(
                filtered_pv,
                x='correlation',
                y='volume_increase_on_price_up_pct',
                size='data_points',
                color='correlation',
                hover_name='coin',
                title="Korelasyon vs Volume Artışı",
                labels={
                    'correlation': 'Fiyat-Volume Korelasyonu',
                    'volume_increase_on_price_up_pct': 'Fiyat Artışında Volume Artışı %'
                },
                color_continuous_scale='RdBu'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=filtered_pv.head(20)['coin'],
                y=filtered_pv.head(20)['correlation'],
                marker_color=filtered_pv.head(20)['correlation'],
                marker_colorscale='RdBu',
                text=filtered_pv.head(20)['correlation'].round(3),
                textposition='outside'
            ))
            fig.update_layout(
                title="En Yüksek Korelasyonlu Coinler (Top 20)",
                xaxis_title="Coin",
                yaxis_title="Korelasyon",
                height=400,
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Tablo
        st.subheader("📊 Detaylı Sonuçlar")
        st.dataframe(filtered_pv, use_container_width=True)
    else:
        st.warning("⚠️ price_volume_analysis.json dosyası bulunamadı. Önce analiz çalıştırın.")

# ==================== ANİ DEĞİŞİM ANALİZİ ====================
elif page == "Ani Değişim Analizi":
    st.header("⚡ Ani Fiyat Değişimlerinde Volume Analizi")
    
    sudden_data = load_json_file('sudden_price_volume_analysis.json')
    
    if not sudden_data:
        st.warning("⚠️ sudden_price_volume_analysis.json dosyası bulunamadı.")
        st.info("""
        **Bu analiz için `main.py` çalıştırılmalıdır.**
        
        **Nasıl Çalışır?**
        1. Terminal'de `python main.py` komutunu çalıştırın
        2. Sistem otomatik olarak WebSocket'ten veri toplamaya başlar
        3. Her 30 dakikada bir analiz yapılır ve dosyalar güncellenir
        4. Bu sayfada ani fiyat değişimlerindeki volume davranışlarını görüntüleyebilirsiniz
        
        **Ani Değişim Analizi Nedir?**
        - Ani fiyat değişimlerinde (spike) volume'un nasıl davrandığını inceler
        - %1, %2, %5, %10 eşiklerinde analiz yapılır
        - Hangi coinlerde ani değişimlerde volume artışı olduğunu gösterir
        
        **Not:** İlk analiz için yeterli veri toplanması gereklidir (yaklaşık 30 dakika).
        """)
        st.stop()
    
    if sudden_data:
        # Eşik seçimi
        thresholds = set()
        for coin_data in sudden_data.values():
            for key in coin_data.keys():
                if key.startswith('threshold_'):
                    thresh = float(key.replace('threshold_', ''))
                    thresholds.add(thresh)
        
        selected_threshold = st.selectbox(
            "Eşik Seçin (%)",
            sorted(thresholds),
            index=0 if thresholds else None
        )
        
        if selected_threshold:
            threshold_key = f"threshold_{selected_threshold}"
            
            # Verileri topla
            coin_stats = []
            for coin, data in sudden_data.items():
                if threshold_key in data:
                    thresh_data = data[threshold_key]
                    sudden_up = thresh_data.get('sudden_up', {})
                    sudden_down = thresh_data.get('sudden_down', {})
                    
                    coin_stats.append({
                        'coin': coin,
                        'sudden_up_count': sudden_up.get('count', 0),
                        'sudden_down_count': sudden_down.get('count', 0),
                        'total_sudden': sudden_up.get('count', 0) + sudden_down.get('count', 0),
                        'up_vol_increase_pct': sudden_up.get('volume_increase_pct', 0),
                        'down_vol_increase_pct': sudden_down.get('volume_increase_pct', 0),
                        'up_avg_vol_change': sudden_up.get('avg_volume_change', 0),
                        'down_avg_vol_change': sudden_down.get('avg_volume_change', 0)
                    })
            
            df_sudden = pd.DataFrame(coin_stats)
            df_sudden = df_sudden[df_sudden['total_sudden'] > 0].sort_values('total_sudden', ascending=False)
            
            # Metrikler
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Toplam Ani Değişim", df_sudden['total_sudden'].sum())
            col2.metric("Ani Yükseliş", df_sudden['sudden_up_count'].sum())
            col3.metric("Ani Düşüş", df_sudden['sudden_down_count'].sum())
            col4.metric("Yükselişte Vol↑ Ort.%", f"{df_sudden[df_sudden['sudden_up_count']>0]['up_vol_increase_pct'].mean():.2f}%")
            
            # Grafikler
            col1, col2 = st.columns(2)
            
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df_sudden.head(20)['coin'],
                    y=df_sudden.head(20)['sudden_up_count'],
                    name='Ani Yükseliş',
                    marker_color='green'
                ))
                fig.add_trace(go.Bar(
                    x=df_sudden.head(20)['coin'],
                    y=df_sudden.head(20)['sudden_down_count'],
                    name='Ani Düşüş',
                    marker_color='red'
                ))
                fig.update_layout(
                    title=f"Ani Değişim Sayıları (Eşik: ±{selected_threshold}%)",
                    xaxis_title="Coin",
                    yaxis_title="Sayı",
                    barmode='group',
                    height=400,
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_sudden['up_vol_increase_pct'],
                    y=df_sudden['down_vol_increase_pct'],
                    mode='markers',
                    text=df_sudden['coin'],
                    marker=dict(
                        size=df_sudden['total_sudden'],
                        color=df_sudden['total_sudden'],
                        colorscale='Viridis',
                        showscale=True
                    ),
                    name='Coinler'
                ))
                fig.update_layout(
                    title="Yükseliş vs Düşüş - Volume Artışı %",
                    xaxis_title="Yükselişte Volume Artışı %",
                    yaxis_title="Düşüşte Volume Artışı %",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Tablo
            st.subheader("📊 Detaylı Sonuçlar")
            st.dataframe(df_sudden, use_container_width=True)
    else:
        st.warning("⚠️ sudden_price_volume_analysis.json dosyası bulunamadı. Önce analiz çalıştırın.")

# ==================== KORELASYON DEĞİŞİKLİKLERİ ====================
elif page == "Korelasyon Değişiklikleri":
    st.header("📈 Korelasyon Değişiklik Takibi")
    
    st.info("""
    **Bu sayfa, coinler arasındaki korelasyon değişikliklerini gösterir.**
    - Her **30 dakikalık** analizde önceki analizle karşılaştırma yapılır
    - Yüksek korelasyonlu çiftlerin korelasyonu düşerse veya artarsa burada görünür
    - Yeni yüksek korelasyonlu çiftler veya kaybolan yüksek korelasyonlar takip edilir
    - Son **30 günlük** değişiklikler saklanır ve gösterilir (daha eski kayıtlar otomatik temizlenir)
    """)
    
    # Değişiklik geçmişini yükle (dosya yoksa oluştur)
    changes_data = load_json_file('correlation_changes_history.json')
    
    # Dosya yoksa veya boşsa, boş bir yapı oluştur
    if not changes_data:
        changes_data = {'changes_history': [], 'last_correlations': {}}
        # Dosyayı oluştur
        try:
            import json
            with open('correlation_changes_history.json', 'w', encoding='utf-8') as f:
                json.dump(changes_data, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    if changes_data and 'changes_history' in changes_data:
        changes = changes_data['changes_history']
        
        if changes:
            # Filtreleme seçenekleri
            st.subheader("🔍 Filtreleme")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                change_types = ['TÜMÜ'] + list(set([c.get('change_type', '') for c in changes]))
                selected_type = st.selectbox("Değişiklik Tipi", change_types)
            
            with col2:
                limit = st.slider("Gösterilecek Kayıt Sayısı", min_value=10, max_value=len(changes), value=min(50, len(changes)), step=10)
            
            with col3:
                show_only_significant = st.checkbox("Sadece Önemli Değişiklikler", value=False)
            
            # Filtreleme
            filtered_changes = changes
            if selected_type != 'TÜMÜ':
                filtered_changes = [c for c in filtered_changes if c.get('change_type') == selected_type]
            
            if show_only_significant:
                filtered_changes = [
                    c for c in filtered_changes 
                    if c.get('change_type') in ['HIGH_TO_LOW', 'LOST_HIGH_CORRELATION', 'LOW_TO_HIGH', 'NEW_HIGH_CORRELATION']
                ]
            
            # En yeni değişiklikler önce
            filtered_changes = sorted(filtered_changes, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
            
            # Özet metrikler
            st.subheader("📊 Özet İstatistikler")
            col1, col2, col3, col4 = st.columns(4)
            
            high_to_low = len([c for c in changes if c.get('change_type') == 'HIGH_TO_LOW'])
            low_to_high = len([c for c in changes if c.get('change_type') == 'LOW_TO_HIGH'])
            new_high = len([c for c in changes if c.get('change_type') == 'NEW_HIGH_CORRELATION'])
            lost_high = len([c for c in changes if c.get('change_type') == 'LOST_HIGH_CORRELATION'])
            
            col1.metric("Yüksekten Düşüş", high_to_low)
            col2.metric("Düşükten Yükseliş", low_to_high)
            col3.metric("Yeni Yüksek Korelasyon", new_high)
            col4.metric("Kaybolan Yüksek Korelasyon", lost_high)
            
            # Değişiklikler tablosu
            st.subheader(f"📋 Değişiklik Geçmişi ({len(filtered_changes)} kayıt)")
            
            if filtered_changes:
                # DataFrame oluştur
                df_changes = pd.DataFrame(filtered_changes)
                
                # Renklendirme için
                def get_status_color(status):
                    if 'YÜKSEK' in status and 'DÜŞÜK' in status:
                        return '🔴'
                    elif 'DÜŞÜK' in status and 'YÜKSEK' in status:
                        return '🟢'
                    elif 'KAYBOLDU' in status:
                        return '⚫'
                    elif 'YENİ' in status:
                        return '🆕'
                    elif 'ARTTI' in status:
                        return '📈'
                    elif 'AZALDI' in status:
                        return '📉'
                    else:
                        return '🔄'
                
                # Görüntüleme için DataFrame hazırla
                display_df = pd.DataFrame({
                    'Tarih/Saat': df_changes['timestamp'],
                    'Coin 1': df_changes['coin1'],
                    'Coin 2': df_changes['coin2'],
                    'Önceki Korelasyon': df_changes['previous_correlation'].apply(lambda x: f"{x:.4f}" if x is not None else "Yok"),
                    'Sonraki Korelasyon': df_changes['current_correlation'].apply(lambda x: f"{x:.4f}" if x is not None else "Yok"),
                    'Değişim': df_changes['change_amount'].apply(lambda x: f"{x:+.4f}" if x is not None else "Yeni/Kayıp"),
                    'Mutlak Değişim': df_changes['abs_change_amount'].apply(lambda x: f"{x:.4f}" if x is not None else "-"),
                    'Durum': df_changes['status'],
                    'Tip': df_changes['change_type']
                })
                
                # Tabloyu göster
                st.dataframe(display_df, use_container_width=True, height=600)
                
                # Detaylı görünüm
                st.subheader("📊 Detaylı Görünüm")
                
                for idx, change in enumerate(filtered_changes[:20]):  # İlk 20'sini göster
                    with st.expander(f"{change['timestamp']} - {change['coin1']} ↔ {change['coin2']} - {change['status']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Önceki Durum:**")
                            if change['previous_correlation'] is not None:
                                st.metric("Korelasyon", f"{change['previous_correlation']:.4f}")
                                st.metric("Mutlak Korelasyon", f"{change['previous_abs_correlation']:.4f}")
                            else:
                                st.info("Önceki veri yok (yeni çift)")
                        
                        with col2:
                            st.markdown("**Sonraki Durum:**")
                            if change['current_correlation'] is not None:
                                st.metric("Korelasyon", f"{change['current_correlation']:.4f}")
                                st.metric("Mutlak Korelasyon", f"{change['current_abs_correlation']:.4f}")
                            else:
                                st.warning("Korelasyon kayboldu")
                        
                        if change['change_amount'] is not None:
                            st.markdown("**Değişim:**")
                            st.metric("Değişim Miktarı", f"{change['change_amount']:+.4f}")
                            st.metric("Mutlak Değişim", f"{change['abs_change_amount']:.4f}")
                        
                        st.markdown(f"**Değişiklik Tipi:** {change['change_type']}")
            else:
                st.warning("Seçilen filtrelerle eşleşen değişiklik bulunamadı.")
        else:
            st.warning("⚠️  Henüz korelasyon değişikliği kaydedilmemiş. Birkaç analiz döngüsü sonrası veriler görünecektir.")
            
            st.info("""
            **Nasıl Çalışır?**
            1. `main.py` çalıştırıldığında her **30 dakikada** bir analiz yapılır
            2. Her analizde önceki analizle karşılaştırma yapılır
            3. Önemli değişiklikler (≥%10) otomatik kaydedilir
            4. Son **30 günlük** değişiklikler bu sayfada görüntülenir
            5. Daha eski kayıtlar otomatik olarak temizlenir
            """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Binance Coin Korelasyon Dashboard - Streamlit</div>",
    unsafe_allow_html=True
)