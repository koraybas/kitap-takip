import streamlit as st
import requests

st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []

def get_books(q):
    try:
        # Arama terimini hem Türkçe hem global sonuçlara açıyoruz
        # 'country=TR' ve 'printType=books' zorlaması ekledik
        url = f"https://www.googleapis.com/books/v1/volumes?q={q.replace(' ', '+')}&maxResults=10&printType=books"
        res = requests.get(url, timeout=10).json()
        items = res.get("items", [])
        results = []
        for item in items:
            info = item.get("volumeInfo", {})
            # Kapak resmini daha büyük ve güvenli formatta çek
            img_links = info.get("imageLinks", {})
            kapak_url = img_links.get("thumbnail") or img_links.get("smallThumbnail")
            if not kapak_url:
                kapak_url = "https://via.placeholder.com/150x220?text=No+Cover"
            
            results.append({
                "title": info.get("title", "Bilinmiyor"),
                "author": info.get("authors", ["Bilinmiyor"])[0],
                "cover": kapak_url.replace("http://", "https://")
            })
        return results
    except:
        return []

st.title("📚 Dijital Kütüphanem")
t_liste, t_ekle = st.tabs(["📋 Kütüphanem", "🔍 Kitap Ara & Ekle"])

with t_ekle:
    st.subheader("Kitap Ara")
    # Form kullanımı butona basılınca veriyi korur
    with st.form("arama_formu", clear_on_submit=False):
        sorgu = st.text_input("Kitap veya Yazar Adı")
        ara_butonu = st.form_submit_button("Ara")
    
    if ara_butonu and sorgu:
        with st.spinner('Kütüphaneler taranıyor...'):
            sonuclar = get_books(sorgu)
            if not sonuclar:
                st.warning("Google kütüphanesinde sonuç bulunamadı. Lütfen Manuel girişi deneyin.")
            else:
                for i, s in enumerate(sonuclar):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(s['cover'], width=100)
                    with col2:
                        st.markdown(f"**{s['title']}**")
                        st.caption(f"Yazar: {s['author']}")
                        durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"d_{i}")
                        if st.button("Kütüphaneye Ekle", key=f"k_{i}"):
                            st.session_state.kitap_listesi.append({
                                "title": s['title'],
                                "author": s['author'],
                                "cover": s['cover'],
                                "status": durum
                            })
                            st.success(f"Eklendi: {s['title']}")

    st.divider()
    with st.expander("➕ Manuel Kayıt (Eğer yukarıda çıkmazsa)"):
        m_isim = st.text_input("Kitap Adı")
        m_yazar = st.text_input("Yazar Adı")
        m_img = st.text_input("Kapak Resim Linki (Opsiyonel)", placeholder="https://...jpg")
        m_durum = st.selectbox("Okuma Durumu", ["Okunacak", "Okunuyor", "Okundu"], key="m_durum")
        if st.button("Manuel Ekle"):
            img = m_img if m_img else "https://via.placeholder.com/150x220?text=Manuel+Kayit"
            st.session_state.kitap_listesi.append({"title": m_isim, "author": m_yazar, "cover": img, "status": m_durum})
            st.success("Manuel olarak eklendi!")

with t_liste:
    if not st.session_state.kitap_listesi:
        st.info("Kütüphane boş.")
    else:
        for idx, k in enumerate(reversed(st.session_state.kitap_listesi)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.image(k['cover'], width=70)
            with c2:
                st.write(f"**{k['title']}**")
                st.caption(f"{k['author']} | {k['status']}")
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    real_idx = len(st.session_state.kitap_listesi) - 1 - idx
                    st.session_state.kitap_listesi.pop(real_idx)
                    st.rerun()
            st.divider()
