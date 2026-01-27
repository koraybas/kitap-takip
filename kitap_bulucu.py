import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Hafıza (Session State)
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []

# 3. HİBRİT ARAMA MOTORU (Google + OpenLibrary)
def kitap_ara_gelismis(sorgu):
    sonuclar = []
    # ÖNCE GOOGLE BOOKS (Daha geniş kapsam)
    try:
        g_url = f"https://www.googleapis.com/books/v1/volumes?q={sorgu.replace(' ', '+')}&maxResults=5"
        g_res = requests.get(g_url, timeout=5).json()
        for item in g_res.get("items", []):
            info = item.get("volumeInfo", {})
            img = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
            if img:
                sonuclar.append({
                    "title": info.get("title", "Bilinmiyor"),
                    "author": info.get("authors", ["Bilinmiyor"])[0],
                    "cover": img
                })
    except:
        pass

    # EĞER GOOGLE AZ SONUÇ VERDİYSÉ OPEN LIBRARY'Yİ DE DENE
    if len(sonuclar) < 2:
        try:
            ol_url = f"https://openlibrary.org/search.json?q={sorgu.replace(' ', '+')}&limit=3"
            ol_res = requests.get(ol_url, timeout=5).json()
            for doc in ol_res.get("docs", []):
                cover_id = doc.get("cover_i")
                if cover_id:
                    sonuclar.append({
                        "title": doc.get("title", "Bilinmiyor"),
                        "author": doc.get("author_name", ["Bilinmiyor"])[0],
                        "cover": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                    })
        except:
            pass
    return sonuclar

# 4. Arayüz Tasarımı
st.title("📚 Dijital Kitaplığım")

tab_ekle, tab_liste = st.tabs(["🔍 Kitap Ara & Ekle", "📋 Kütüphanem"])

with tab_ekle:
    st.subheader("Kitap veya Yazar Yazın")
    with st.form("arama_formu"):
        sorgu = st.text_input("Örn: Simyacı veya Paulo Coelho")
        ara_btn = st.form_submit_button("Sistemde Ara")

    if ara_btn and sorgu:
        with st.spinner('Kapaklar yükleniyor...'):
            bulunanlar = kitap_ara_gelismis(sorgu)
            if not bulunanlar:
                st.error("Maalesef hiçbir kütüphanede bulamadık. İsmi kontrol eder misiniz?")
            else:
                for i, b in enumerate(bulunanlar):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(b['cover'], width=100)
                    with col2:
                        st.markdown(f"**{b['title']}**")
                        st.caption(f"Yazar: {b['author']}")
                        durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"dr_{i}")
                        if st.button("Kütüphaneme Ekle", key=f"add_{i}"):
                            st.session_state.kitap_listesi.append({
                                "title": b['title'], "author": b['author'], 
                                "cover": b['cover'], "status": durum
                            })
                            st.success("Eklendi!")

with tab_liste:
    if not st.session_state.kitap_listesi:
        st.info("Kütüphane boş.")
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
