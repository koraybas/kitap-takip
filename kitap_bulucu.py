import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Hafıza
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []
if 'bulunan_kitaplar' not in st.session_state:
    st.session_state.bulunan_kitaplar = []

# 3. YENİ NESİL ARAMA (API Kısıtlamalarını Baypas Eder)
def kitap_bulucu_v3(sorgu):
    results = []
    # Arama terimini zenginleştiriyoruz
    q = sorgu.replace(' ', '+')
    # Google'ın en serbest arama kapısı
    url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=12"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "items" in data:
            for item in data["items"]:
                info = item.get("volumeInfo", {})
                img_links = info.get("imageLinks", {})
                # En kaliteli resmi bul
                img = img_links.get("thumbnail") or img_links.get("smallThumbnail")
                
                if img:
                    img = img.replace("http://", "https://")
                    results.append({
                        "title": info.get("title", "Bilinmiyor"),
                        "author": info.get("authors", ["Bilinmiyor"])[0],
                        "cover": img
                    })
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        
    return results

# 4. Arayüz
st.title("📚 Dijital Kütüphanem")
st.info("Bilgisayar hassasiyetinde arama aktif.")

t_ekle, t_liste = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Kütüphanem"])

with t_ekle:
    # Arama Bölümü
    sorgu = st.text_input("Kitap, Yazar veya ISBN yazın", placeholder="Örn: Şehit Kaveh Akbar")
    ara_butonu = st.button("Sistemde Derin Ara")

    if ara_butonu and sorgu:
        with st.spinner('İnternet taranıyor...'):
            st.session_state.bulunan_kitaplar = kitap_bulucu_v3(sorgu)

    if st.session_state.bulunan_kitaplar:
        for i, b in enumerate(st.session_state.bulunan_kitaplar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(b['cover'], width=100)
                with c2:
                    st.markdown(f"**{b['title']}**")
                    st.caption(f"Yazar: {b['author']}")
                    durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"dr_{i}")
                    if st.button("Kütüphaneme Ekle", key=f"add_{i}"):
                        st.session_state.kitap_listesi.append({
                            "title": b['title'], "author": b['author'], 
                            "cover": b['cover'], "status": durum
                        })
                        st.success(f"'{b['title']}' eklendi!")
            st.divider()

with t_liste:
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
                    pos = len(st.session_state.kitap_listesi) - 1 - idx
                    st.session_state.kitap_listesi.pop(pos)
                    st.rerun()
            st.divider()
