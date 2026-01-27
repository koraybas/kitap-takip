import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Hafıza
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []
if 'bulunanlar' not in st.session_state:
    st.session_state.bulunanlar = []

# 3. Bilgisayar Hassasiyetinde Arama Fonksiyonu
def derin_arama(sorgu):
    results = []
    # Kısıtlamaları kaldırıp Google'ın tüm internet indeksini (web) tetikliyoruz
    q = sorgu.replace(' ', '+')
    # maxResults artırıldı, dil kısıtlaması kaldırıldı
    url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=15"
    
    try:
        res = requests.get(url, timeout=10).json()
        if "items" in res:
            for item in res["items"]:
                info = item.get("volumeInfo", {})
                img_links = info.get("imageLinks", {})
                # En net resmi bulmaya odaklan
                img = img_links.get("thumbnail") or img_links.get("smallThumbnail")
                if img:
                    img = img.replace("http://", "https://")
                    results.append({
                        "title": info.get("title", "Bilinmiyor"),
                        "author": info.get("authors", ["Bilinmiyor"])[0],
                        "cover": img
                    })
    except:
        pass
    return results

# 4. Arayüz
st.title("📚 Dijital Kütüphanem")
st.caption("Bilgisayardaki gibi geniş kapsamlı arama modu aktif.")

tab1, tab2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Listem"])

with tab1:
    col_in, col_btn = st.columns([4, 1])
    with col_in:
        sorgu = st.text_input("Kitap, Yazar veya ISBN...", key="s_input", placeholder="Örn: Şehit Kaveh Akbar")
    with col_btn:
        ara_btn = st.button("Ara")

    if ara_btn and sorgu:
        with st.spinner('İnternet taranıyor...'):
            st.session_state.bulunanlar = derin_arama(sorgu)

    if st.session_state.bulunanlar:
        for i, b in enumerate(st.session_state.bulunanlar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(b['cover'], width=100)
                with c2:
                    st.markdown(f"**{b['title']}**")
                    st.caption(f"Yazar: {b['author']}")
                    durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"sel_{i}")
                    if st.button("Ekle", key=f"add_{i}"):
                        st.session_state.kitap_listesi.append({
                            "title": b['title'], "author": b['author'], 
                            "cover": b['cover'], "status": durum
                        })
                        st.success(f"Eklendi!")
            st.divider()

with tab2:
    if not st.session_state.kitap_listesi:
        st.info("Kütüphaneniz şu an boş.")
    else:
        for idx, k in enumerate(reversed(st.session_state.kitap_listesi)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.image(k['cover'], width=80)
            with c2:
                st.write(f"**{k['title']}**")
                st.caption(f"{k['author']} | {k['status']}")
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    real_idx = len(st.session_state.kitap_listesi) - 1 - idx
                    st.session_state.kitap_listesi.pop(real_idx)
                    st.rerun()
            st.divider()
