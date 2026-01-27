import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Hafıza (Session State)
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []
if 'arama_sonuclari' not in st.session_state:
    st.session_state.arama_sonuclari = []

# 3. Kitap Arama Fonksiyonu
def kitap_ara(sorgu):
    results = []
    # Bilgisayar hassasiyetinde arama için temiz bir sorgu yapısı
    url = f"https://www.googleapis.com/books/v1/volumes?q={sorgu.replace(' ', '+')}&maxResults=10"
    
    try:
        # Tarayıcı gibi davranarak kısıtlamaları aşıyoruz
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10).json()
        
        if "items" in response:
            for item in response["items"]:
                info = item.get("volumeInfo", {})
                img_links = info.get("imageLinks", {})
                # Kapak resmini en güvenli şekilde al
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

# 4. Arayüz Tasarımı
st.title("📚 Dijital Kütüphanem")

tab_ekle, tab_liste = st.tabs(["🔍 Kitap Ara & Ekle", "📋 Listem"])

with tab_ekle:
    st.subheader("Kitap İsmi Yazın")
    # Arama kutusu ve butonu
    sorgu_input = st.text_input("Örn: Simyacı, Şehit, Radley Ailesi", key="input_ara")
    if st.button("Sistemde Ara"):
        if sorgu_input:
            with st.spinner('Kitaplar aranıyor...'):
                st.session_state.arama_sonuclari = kitap_ara(sorgu_input)

    # Arama Sonuçlarını Listele
    if st.session_state.arama_sonuclari:
        st.write("---")
        for i, b in enumerate(st.session_state.arama_sonuclari):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(b['cover'], width=100)
            with col2:
                st.markdown(f"**{b['title']}**")
                st.caption(f"Yazar: {b['author']}")
                durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"durum_{i}")
                if st.button("Kütüphaneye Ekle", key=f"ekle_{i}"):
                    st.session_state.kitap_listesi.append({
                        "title": b['title'], 
                        "author": b['author'], 
                        "cover": b['cover'], 
                        "status": durum
                    })
                    st.success(f"'{b['title']}' eklendi!")

with tab_liste:
    if not st.session_state.kitap_listesi:
        st.info("Kütüphaneniz şu an boş.")
    else:
        for idx, k in enumerate(reversed(st.session_state.kitap_listesi)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.image(k['cover'], width=70)
            with c2:
                st.write(f"**{k['title']}**")
                st.caption(f"{k['author']} | {k['status']}")
            with c3:
                if st.button("Sil", key=f"sil_{idx}"):
                    # Gerçek listeyi güncelle
                    real_idx = len(st.session_state.kitap_listesi) - 1 - idx
                    st.session_state.kitap_listesi.pop(real_idx)
                    st.rerun()
            st.divider()
