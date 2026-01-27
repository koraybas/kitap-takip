import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Hafıza (Session State)
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []
if 'bulunan_kitaplar' not in st.session_state:
    st.session_state.bulunan_kitaplar = []

# 3. Gelişmiş Arama Fonksiyonu
def kitap_ara_gelismis(sorgu):
    results = []
    # Google Books
    try:
        g_url = f"https://www.googleapis.com/books/v1/volumes?q={sorgu.replace(' ', '+')}&maxResults=5"
        g_res = requests.get(g_url, timeout=5).json()
        for item in g_res.get("items", []):
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
    
    # Open Library (Eğer sonuç azsa yedek güç)
    if len(results) < 2:
        try:
            ol_url = f"https://openlibrary.org/search.json?q={sorgu.replace(' ', '+')}&limit=3"
            ol_res = requests.get(ol_url, timeout=5).json()
            for doc in ol_res.get("docs", []):
                cover_id = doc.get("cover_i")
                if cover_id:
                    results.append({
                        "title": doc.get("title", "Bilinmiyor"),
                        "author": doc.get("author_name", ["Bilinmiyor"])[0],
                        "cover": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                    })
        except:
            pass
    return results

# 4. Arayüz Tasarımı
st.title("📚 Dijital Kütüphanem")

tab_ekle, tab_liste = st.tabs(["🔍 Kitap Ara & Ekle", "📋 Kütüphanem"])

with tab_ekle:
    st.subheader("Kitap veya Yazar Ara")
    # Formu kaldırdık, metin kutusu ve buton artık daha özgür
    sorgu = st.text_input("Örn: Simyacı veya Paulo Coelho", key="search_input")
    ara_btn = st.button("Sistemde Ara")

    if ara_btn and sorgu:
        with st.spinner('Kapaklar yükleniyor...'):
            st.session_state.bulunan_kitaplar = kitap_ara_gelismis(sorgu)

    if st.session_state.bulunan_kitaplar:
        st.write("---")
        for i, b in enumerate(st.session_state.bulunan_kitaplar):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(b['cover'], width=100)
            with col2:
                st.markdown(f"**{b['title']}**")
                st.caption(f"Yazar: {b['author']}")
                durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"dr_{i}")
                
                # EKLE BUTONU (Artık Form Dışında Olduğu İçin Çalışacak)
                if st.button("Kütüphaneme Ekle", key=f"add_{i}"):
                    st.session_state.kitap_listesi.append({
                        "title": b['title'], 
                        "author": b['author'], 
                        "cover": b['cover'], 
                        "status": durum
                    })
                    st.success(f"'{b['title']}' kütüphanenize eklendi!")

with tab_liste:
    if not st.session_state.kitap_listesi:
        st.info("Kütüphaneniz şu an boş.")
    else:
        # Kitapları listele (Son eklenen en üstte)
        for idx, k in enumerate(reversed(st.session_state.kitap_listesi)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.image(k['cover'], width=80)
            with c2:
                st.write(f"**{k['title']}**")
                st.caption(f"{k['author']} | {k['status']}")
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    # Listeden silme işlemi
                    pos = len(st.session_state.kitap_listesi) - 1 - idx
                    st.session_state.kitap_listesi.pop(pos)
                    st.rerun()
            st.divider()
