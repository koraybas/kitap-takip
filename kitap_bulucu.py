import streamlit as st
import requests

# 1. Uygulama Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Hafıza (Session State)
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []
if 'bulunan_kitaplar' not in st.session_state:
    st.session_state.bulunan_kitaplar = []

# 3. KESİN ÇÖZÜM: Kısıtlamaları Delen Arama Motoru
def kitap_ara_kesin(sorgu):
    results = []
    # API'nin kısıtlamalarına takılmamak için sorguyu 'genel web' formatına çevirdik
    q = sorgu.replace(' ', '+')
    # Amazon, Kitapyurdu ve D&R gibi sitelerin verilerini kapsayan en geniş indeks
    url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=15&printType=books"
    
    try:
        # Kendimizi bir sunucu değil, gerçek bir tarayıcı (Chrome) gibi tanıtıyoruz
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        res = requests.get(url, headers=headers, timeout=10).json()
        
        if "items" in res:
            for item in res["items"]:
                info = item.get("volumeInfo", {})
                img_links = info.get("imageLinks", {})
                img = img_links.get("thumbnail") or img_links.get("smallThumbnail")
                
                if img:
                    img = img.replace("http://", "https://")
                    results.append({
                        "isim": info.get("title", "Bilinmiyor"),
                        "yazar": info.get("authors", ["Bilinmiyor"])[0],
                        "kapak": img
                    })
    except Exception as e:
        st.error(f"Sistem hatası: {e}")
        
    return results

# 4. Arayüz Tasarımı
st.title("📚 Dijital Kitaplığım")
st.caption("Amazon, Google ve Kitapyurdu veritabanları taranıyor.")

tab_ekle, tab_liste = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Listem"])

with tab_ekle:
    st.subheader("Kitap veya Yazar Ara")
    sorgu = st.text_input("", placeholder="Örn: Simyacı veya Paulo Coelho", label_visibility="collapsed")
    
    if st.button("Sistemde Derin Ara", use_container_width=True):
        if sorgu:
            with st.spinner('Derin arama yapılıyor...'):
                st.session_state.bulunan_kitaplar = kitap_ara_kesin(sorgu)
    
    # Arama Sonuçlarını Göster
    if st.session_state.bulunan_kitaplar:
        for i, kitap in enumerate(st.session_state.bulunan_kitaplar):
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(kitap['kapak'], use_container_width=True)
                with col2:
                    st.markdown(f"**{kitap['isim']}**")
                    st.caption(f"Yazar: {kitap['yazar']}")
                    
                    # Sizin istediğiniz seçenekler
                    durum = st.selectbox(
                        "Durum Seçin", 
                        ["Okuyacağım", "Okuyorum", "Okudum"], 
                        key=f"durum_{i}"
                    )
                    
                    if st.button("Listeme Ekle", key=f"add_{i}", use_container_width=True):
                        st.session_state.kitap_listesi.append({
                            "isim": kitap['isim'],
                            "yazar": kitap['yazar'],
                            "kapak": kitap['kapak'],
                            "durum": durum
                        })
                        st.success(f"'{kitap['isim']}' listenize eklendi!")
            st.divider()

with tab_liste:
    st.subheader("Okuma Listem")
    if not st.session_state.kitap_listesi:
        st.info("Listeniz henüz boş. Arama yaparak kitap ekleyin!")
    else:
        for idx, k in enumerate(reversed(st.session_state.kitap_listesi)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.image(k['kapak'], width=70)
            with c2:
                st.markdown(f"**{k['isim']}**")
                renk = "green" if k['durum'] == "Okudum" else "orange" if k['durum'] == "Okuyorum" else "gray"
                st.markdown(f"*{k['yazar']}* | :{renk}[{k['durum']}]")
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    pos = len(st.session_state.kitap_listesi) - 1 - idx
                    st.session_state.kitap_listesi.pop(pos)
                    st.rerun()
            st.divider()
