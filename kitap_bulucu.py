import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Hafıza
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []
if 'bulunan_kitaplar' not in st.session_state:
    st.session_state.bulunan_kitaplar = []

# 3. BİLGİSAYAR HASSASİYETİNDE ARAMA (Deep Search)
def derin_kitap_ara(sorgu):
    results = []
    # Bilgisayardaki Google araması gibi davranması için sorguyu zenginleştiriyoruz
    # 'intitle' veya 'inauthor' zorlaması olmadan, en geniş internet indeksi
    q = sorgu.strip().replace(' ', '+')
    
    # Google'ın en geniş veritabanı kapısı
    url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=15&printType=books"
    
    try:
        res = requests.get(url, timeout=10).json()
        if "items" in res:
            for item in res["items"]:
                info = item.get("volumeInfo", {})
                
                # Kapak resmi için tüm ihtimalleri zorla (Bilgisayardaki gibi net görseller için)
                img_links = info.get("imageLinks", {})
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

t_ekle, t_liste = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Kütüphanem"])

with t_ekle:
    st.subheader("Kitap veya Yazar Yazın")
    # Arama kutusu (Bilgisayar klavyesi gibi hızlı tepki için)
    sorgu = st.text_input("Örn: Şehit Kaveh Akbar, Radley Ailesi...", key="s_input")
    ara_btn = st.button("Sistemde Ara")

    if ara_btn and sorgu:
        with st.spinner('Bilgisayar hassasiyetinde taranıyor...'):
            st.session_state.bulunan_kitaplar = derin_kitap_ara(sorgu)

    if st.session_state.bulunan_kitaplar:
        st.write(f"🔍 {len(st.session_state.bulunan_kitaplar)} sonuç bulundu:")
        for i, b in enumerate(st.session_state.bulunan_kitaplar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(b['cover'], width=100)
                with c2:
                    st.markdown(f"**{b['title']}**")
                    st.caption(f"Yazar: {b['author']}")
                    durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"dr_{i}")
                    if st.button("Ekle", key=f"add_{i}"):
                        st.session_state.kitap_listesi.append({
                            "title": b['title'], "author": b['author'], 
                            "cover": b['cover'], "status": durum
                        })
                        st.success("Eklendi!")
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
                    st.session_state.kitap_listesi.pop(len(st.session_state.kitap_listesi)-1-idx)
                    st.rerun()
            st.divider()
