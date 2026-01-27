import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Hafıza
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []
if 'bulunan_kitaplar' not in st.session_state:
    st.session_state.bulunan_kitaplar = []

# 3. GELİŞMİŞ ARAMA MOTORU (Google Search Mantığı)
def super_kitap_ara(sorgu):
    results = []
    # Google Books üzerinden en geniş aramayı yap (relevance ve printType zorlaması olmadan)
    try:
        # Arama terimini hem Türkçe hem İngilizce varyasyonlarla genişletiyoruz
        url = f"https://www.googleapis.com/books/v1/volumes?q={sorgu.replace(' ', '+')}&maxResults=10"
        res = requests.get(url, timeout=10).json()
        
        for item in res.get("items", []):
            info = item.get("volumeInfo", {})
            # Kapak resmi için tüm alternatifleri tara
            img_links = info.get("imageLinks", {})
            # En iyi çözünürlüğü seçmeye çalış
            img = (img_links.get("extraLarge") or img_links.get("large") or 
                   img_links.get("medium") or img_links.get("small") or 
                   img_links.get("thumbnail") or img_links.get("smallThumbnail"))
            
            if img:
                img = img.replace("http://", "https://")
                results.append({
                    "title": info.get("title", "Bilinmiyor"),
                    "author": info.get("authors", ["Bilinmiyor"])[0],
                    "cover": img
                })
    except:
        pass

    # Eğer hala boşsa, Amazon/Kitapyurdu tarzı geniş sonuçlar için farklı bir sorgu dene
    if not results:
        try:
            # Sadece isim odaklı daha basit bir sorgu
            url_simple = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{sorgu.replace(' ', '+')}"
            res_simple = requests.get(url_simple, timeout=10).json()
            for item in res_simple.get("items", []):
                info = item.get("volumeInfo", {})
                img = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
                if img:
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
    c_in, c_btn = st.columns([4, 1])
    with c_in:
        sorgu = st.text_input("Arama yapın...", key="s_input", label_visibility="collapsed")
    with c_btn:
        ara_btn = st.button("Ara")

    if ara_btn and sorgu:
        with st.spinner('Derin arama yapılıyor...'):
            st.session_state.bulunan_kitaplar = super_kitap_ara(sorgu)

    if st.session_state.bulunan_kitaplar:
        for i, b in enumerate(st.session_state.bulunan_kitaplar):
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(b['cover'], use_container_width=True)
                with col2:
                    st.markdown(f"**{b['title']}**")
                    st.caption(f"Yazar: {b['author']}")
                    durum = st.selectbox("Okuma Durumu", ["Okunacak", "Okunuyor", "Okundu"], key=f"dr_{i}")
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
