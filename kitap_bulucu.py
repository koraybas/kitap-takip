import streamlit as st
import requests

st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []

def get_books(q):
    try:
        # Aramayı daha geniş (intitle: yerine genel sorgu) ve 10 sonuç dönecek şekilde güncelledik
        url = f"https://www.googleapis.com/books/v1/volumes?q={q.replace(' ', '+')}&maxResults=10"
        res = requests.get(url, timeout=10).json()
        items = res.get("items", [])
        results = []
        for item in items:
            info = item.get("volumeInfo", {})
            results.append({
                "title": info.get("title", "Bilinmiyor"),
                "author": info.get("authors", ["Bilinmiyor"])[0],
                "cover": info.get("imageLinks", {}).get("thumbnail", "https://via.placeholder.com/150x220?text=No+Cover").replace("http://", "https://")
            })
        return results
    except:
        return []

st.title("📚 Dijital Kütüphanem")
tab_liste, tab_ekle = st.tabs(["📋 Kütüphanem", "🔍 Kitap Ara & Ekle"])

with tab_ekle:
    st.subheader("Kitap Ara")
    with st.form("arama_formu"):
        sorgu = st.text_input("Kitap veya Yazar Adı")
        ara_butonu = st.form_submit_button("Ara")
    
    if ara_butonu and sorgu:
        sonuclar = get_books(sorgu)
        if not sonuclar:
            st.warning("Google'da tam eşleşme bulunamadı. Lütfen Manuel Ekleme kısmını kullanın veya ismi kontrol edin.")
        else:
            for i, s in enumerate(sonuclar):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(s['cover'], width=100)
                with col2:
                    st.write(f"**{s['title']}**")
                    st.write(f"*{s['author']}*")
                    durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"durum_{i}")
                    if st.button("Kütüphaneye Ekle", key=f"btn_{i}"):
                        st.session_state.kitap_listesi.append({"title": s['title'], "author": s['author'], "cover": s['cover'], "status": durum})
                        st.success(f"'{s['title']}' eklendi!")

    st.divider()
    # MANUEL EKLEME BÖLÜMÜ (Google bulamazsa can simidi)
    with st.expander("➕ Aradığınız Kitabı Bulamadınız mı? Manuel Ekleyin"):
        m_isim = st.text_input("Kitap Adı (Manuel)")
        m_yazar = st.text_input("Yazar Adı (Manuel)")
        m_durum = st.selectbox("Okuma Durumu (Manuel)", ["Okunacak", "Okunuyor", "Okundu"])
        if st.button("Manuel Olarak Ekle"):
            if m_isim and m_yazar:
                st.session_state.kitap_listesi.append({
                    "title": m_isim,
                    "author": m_yazar,
                    "cover": "https://via.placeholder.com/150x220?text=Manuel+Kayit",
                    "status": m_durum
                })
                st.success("Kitap manuel olarak eklendi!")
            else:
                st.error("Lütfen isim ve yazar alanlarını doldurun.")

with tab_liste:
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
