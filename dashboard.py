import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

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

# Sidebar - Menü
st.sidebar.title("Menü")
page = st.sidebar.selectbox(
    "Sayfa Seçin",
    ["Ana Sayfa", "Korelasyon Analizi", "Fiyat-Volume Analizi", "Ani Değişim Analizi"]
)

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
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Metrikler
    correlations = load_json_file('historical_correlations.json') or load_json_file('realtime_correlations.json')
    
    if correlations:
        col1, col2, col3, col4 = st.columns(4)
        high_corr = [c for c in correlations if abs(c.get('correlation', 0)) > 0.7]
        col1.metric("Toplam Korelasyon", len(correlations))
        col2.metric("Yüksek Korelasyon", len(high_corr))
        col3.metric("Ortalama Korelasyon", f"{np.mean([abs(c.get('correlation', 0)) for c in correlations]):.3f}")
        col4.metric("Maksimum Korelasyon", f"{max([abs(c.get('correlation', 0)) for c in correlations]):.3f}")
        
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
        
        # Korelasyon dağılımı
        st.subheader("📊 Korelasyon Dağılımı")
        st.markdown("""
        **Bu grafikler ne gösteriyor?**
        - **Histogram (Sol)**: Tüm korelasyon değerlerinin dağılımını gösterir. Hangi korelasyon aralığında daha fazla coin çifti olduğunu görürsünüz.
        - **Box Plot (Sağ)**: Korelasyon değerlerinin istatistiksel dağılımını gösterir. Ortalama, medyan, çeyrekler ve aykırı değerleri görürsünüz.
        - **Pozitif değerler (mavi)**: Coinler aynı yönde hareket ediyor (biri yükselirse diğeri de yükselir)
        - **Negatif değerler (kırmızı)**: Coinler ters yönde hareket ediyor (biri yükselirse diğeri düşer)
        """)
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram
            fig = px.histogram(
                df_corr,
                x='correlation',
                nbins=30,
                title="Korelasyon Değerleri Dağılımı",
                labels={'correlation': 'Korelasyon', 'count': 'Frekans'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Box plot
            fig = px.box(
                df_corr,
                y='correlation',
                title="Korelasyon Değerleri Box Plot",
                labels={'correlation': 'Korelasyon'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Korelasyon matrisi (önizleme)
        st.markdown("---")
        st.subheader("🗺️ Korelasyon Matrisi Önizleme")
        
        # Veri kaynağı seçimi
        data_source = st.radio(
            "Veri Kaynağı",
            ["Geçmiş Veriler", "Anlık Veriler"],
            horizontal=True,
            key="home_page_source"
        )
        
        if data_source == "Geçmiş Veriler":
            corr_matrix_file = "historical_correlation_matrix.csv"
        else:
            corr_matrix_file = "realtime_correlation_matrix.csv"
        
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
            
            st.dataframe(
                filtered_corr[['coin1', 'coin2', 'correlation', 'abs_correlation']],
                use_container_width=True
            )
            
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
                
                # Korelasyon tablosu
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
                
                # Tablo göster
                st.dataframe(
                    df_pairs,
                    use_container_width=True,
                    height=400
                )
                
                # En yüksek korelasyonlu çiftler
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
                
                if len(high_corr_pairs) > 0:
                    # Grafik
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=high_corr_pairs['Coin 1'] + ' ↔ ' + high_corr_pairs['Coin 2'],
                        y=high_corr_pairs['Korelasyon'],
                        marker_color=high_corr_pairs['Korelasyon'],
                        marker_colorscale='RdBu',
                        text=high_corr_pairs['Korelasyon'].round(3),
                        textposition='outside',
                        hovertemplate='%{x}<br>Korelasyon: %{y:.3f}<extra></extra>'
                    ))
                    fig.update_layout(
                        title=f"Yüksek Korelasyonlu Coin Çiftleri (Eşik: ≥{threshold_multi})",
                        xaxis_title="Coin Çifti",
                        yaxis_title="Korelasyon",
                        height=500,
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
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

# ==================== FİYAT-VOLUME ANALİZİ ====================
elif page == "Fiyat-Volume Analizi":
    st.header("📈 Fiyat-Volume İlişkisi")
    
    pv_data = load_json_file('price_volume_analysis.json')
    
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

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Binance Coin Korelasyon Dashboard - Streamlit</div>",
    unsafe_allow_html=True
)