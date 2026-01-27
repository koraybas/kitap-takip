import streamlit as st
import requests

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Kitap Takip", page_icon="📚", layout="centered")

# 2. Veri Yönetimi
if 'kitaplik' not in st.session_state:
    st.session_state.kitaplik = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# 3. Gelişmiş Arama Fonksiyonu (Bilgisayar Hassasiyetinde)
def kitap_ara(sorgu):
    # Kısıtlamaları kaldırmak için ham sorgu yapısı
    url = f"https://www.googleapis.com/books/v1/volumes?q={sorgu.replace(' ', '+')}&maxResults=15"
    try:
        # Tarayıcı gibi davranan header
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10).json()
        
        results = []
        if "items" in res:
            for item in res["items"]:
                vol = item.get("volumeInfo", {})
                # Görseli en güvenli şekilde al
                img = vol.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
                if img:
                    results.append({
                        "title": vol.get("title", "Bilinmiyor"),
                        "author": vol.get("authors", ["Bilinmiyor"])[0],
                        "cover": img
                    })
        return results
    except:
        return []

# 4. Uygulama Arayüzü
st.title("📚 Dijital Kütüphanem")

tab1, tab2 = st.tabs(["🔍 Kitap Bul & Ekle", "📖 Benim Listem"])

with tab1:
    st.subheader("Kitap veya Yazar Ara")
    # Arama kutusu
    sorgu_kelimesi = st.text_input("Örn: Simyacı, Paulo Coelho, Şehit...", placeholder="Aramak istediğiniz kitabı yazın")
    
    if st.button("Sistemde Ara"):
        if sorgu_kelimesi:
            with st.spinner('Kütüphaneler taranıyor...'):
                st.session_state.search_results = kitap_ara(sorgu_kelimesi)
    
    # Arama Sonuçlarını Kart Şeklinde Göster
    if st.session_state.search_results:
        st.write("---")
        for i, b in enumerate(st.session_state.search_results):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(b['cover'], width=100)
            with col2:
                st.markdown(f"**{b['title']}**")
                st.caption(f"Yazar: {b['author']}")
                durum = st.selectbox("Durum Seçin", ["Okunacak", "Okunuyor", "Okundu"], key=f"durum_{i}")
                if st.button("Kütüphaneme Ekle", key=f"ekle_{i}"):
                    st.session_state.kitaplik.append({
                        "title": b['title'],
                        "author": b['author'],
                        "cover": b['cover'],
                        "status": durum
                    })
                    st.success(f"'{b['title']}' listenize eklendi!")

with tab2:
    if not st.session_state.kitaplik:
        st.info("Kütüphaneniz şu an boş. Arama yaparak kitap ekleyin!")
    else:
        # Kitapları göster (Son eklenen en üstte)
        for idx, k in enumerate(reversed(st.session_state.kitaplik)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.image(k['cover'], width=70)
            with c2:
                st.write(f"**{k['title']}**")
                st.caption(f"{k['author']} | {k['status']}")
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    pos = len(st.session_state.kitaplik) - 1 - idx
                    st.session_state.kitaplik.pop(pos)
                    st.rerun()
            st.divider()
