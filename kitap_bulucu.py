import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Veri Saklama
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []
if 'arama_sonuclari' not in st.session_state:
    st.session_state.arama_sonuclari = []

# 3. Google API Sorgulama
def kitap_ara(kitap_adi):
    url = f"https://www.googleapis.com/books/v1/volumes?q={kitap_adi.replace(' ', '+')}&maxResults=3"
    try:
        res = requests.get(url, timeout=10).json()
        results = []
        if "items" in res:
            for item in res["items"]:
                info = item.get("volumeInfo", {})
                results.append({
                    "isim": info.get("title", "Bilinmiyor"),
                    "yazar": info.get("authors", ["Bilinmiyor"])[0],
                    "kapak": info.get("imageLinks", {}).get("thumbnail", "https://via.placeholder.com/150x220?text=No+Cover").replace("http://", "https://")
                })
        return results
    except:
        return []

# 4. Arayüz
st.title("📚 Dijital Kitaplığım")
t_liste, t_ekle = st.tabs(["📋 Listem", "🔍 Kitap Ara & Ekle"])

with t_ekle:
    st.subheader("Kitap Bul")
    arama_sorgusu = st.text_input("Kitap veya Yazar Adı Yazın")
    if st.button("Ara"):
        if arama_sorgusu:
            st.session_state.arama_sonuclari = kitap_ara(arama_sorgusu)
    
    if st.session_state.arama_sonuclari:
        st.write("---")
        for i, sonuc in enumerate(st.session_state.arama_sonuclari):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(sonuc['kapak'], width=100)
            with col2:
                st.markdown(f"**{sonuc['isim']}**")
                st.caption(f"Yazar: {sonuc['yazar']}")
                durum = st.selectbox(f"Durum #{i}", ["Okunacak", "Okunuyor", "Okundu"], key=f"sel_{i}")
                if st.button(f"Kütüphaneye Ekle", key=f"add_{i}"):
                    st.session_state.kitap_listesi.append({
                        "isim": sonuc['isim'],
                        "yazar": sonuc['yazar'],
                        "kapak": sonuc['kapak'],
                        "durum": durum
                    })
                    st.success(f"'{sonuc['isim']}' eklendi!")
            st.divider()

with t_liste:
    if not st.session_state.kitap_listesi:
        st.info("Kütüphaneniz boş.")
    else:
        for idx, k in enumerate(reversed(st.session_state.kitap_listesi)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.image(k['kapak'], width=70)
            with c2:
                st.markdown(f"**{k['isim']}**")
                st.caption(f"{k['yazar']} | {k['durum']}")
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    real_idx = len(st.session_state.kitap_listesi) - 1 - idx
                    st.session_state.kitap_listesi.pop(real_idx)
                    st.rerun()
            st.divider()
