import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Hafıza (Session State)
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []
if 'bulunan_kitaplar' not in st.session_state:
    st.session_state.bulunan_kitaplar = []

# 3. Gelişmiş ve Yerelleştirilmiş Arama Fonksiyonu
def kitap_ara_profesyonel(sorgu):
    results = []
    try:
        # Türkçe öncelikli, kitap formatında ve en alakalı 10 sonucu getiren URL
        g_url = (f"https://www.googleapis.com/books/v1/volumes?q={sorgu.replace(' ', '+')}"
                 f"&langRestrict=tr&printType=books&orderBy=relevance&maxResults=10")
        
        g_res = requests.get(g_url, timeout=10).json()
        for item in g_res.get("items", []):
            info = item.get("volumeInfo", {})
            # Görseli en yüksek çözünürlükte yakalamaya çalış
            img_links = info.get("imageLinks", {})
            img = (img_links.get("thumbnail") or img_links.get("smallThumbnail", "")).replace("http://", "https://")
            
            if img:
                results.append({
                    "title": info.get("title", "Bilinmiyor"),
                    "author": info.get("authors", ["Bilinmiyor"])[0],
                    "cover": img
                })
    except:
        pass
    
    # Eğer Google'dan sonuç gelmezse global kütüphaneyi (Open Library) yedek olarak kullan
    if not results:
        try:
            ol_url = f"https://openlibrary.org/search.json?q={sorgu.replace(' ', '+')}&limit=5"
            ol_res = requests.get(ol_url, timeout=10).json()
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
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        sorgu = st.text_input("Örn: Simyacı, Sabahattin Ali...", key="search_input", label_visibility="collapsed")
    with col_btn:
        ara_btn = st.button("Ara")

    if ara_btn and sorgu:
        with st.spinner('Kütüphane taranıyor...'):
            st.session_state.bulunan_kitaplar = kitap_ara_profesyonel(sorgu)

    if st.session_state.bulunan_kitaplar:
        st.write("---")
        for i, b in enumerate(st.session_state.bulunan_kitaplar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(b['cover'], width=100)
                with c2:
                    st.markdown(f"**{b['title']}**")
                    st.caption(f"Yazar: {b['author']}")
                    durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"dr_{i}")
                    if st.button("Listeye Ekle", key=f"add_{i}"):
                        st.session_state.kitap_listesi.append({
                            "title": b['title'], "author": b['author'], 
                            "cover": b['cover'], "status": durum
                        })
                        st.success("Eklendi!")
            st.divider()

with tab_liste:
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
