import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Hafıza
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []
if 'bulunan_kitaplar' not in st.session_state:
    st.session_state.bulunan_kitaplar = []

# 3. MEGA Arama Fonksiyonu (Google + Open Library + Cross Check)
def mega_kitap_ara(sorgu):
    results = []
    # Arama terimini hem orijinal hem de normalize ederek temizle
    q = sorgu.strip().replace(' ', '+')
    
    # Kaynak 1: Google Books (Genişletilmiş Sorgu)
    try:
        # langRestrict'i kaldırdım çünkü 'Şehit' gibi kitaplar farklı dillerde de olabilir
        g_url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=8&printType=books"
        g_res = requests.get(g_url, timeout=10).json()
        for item in g_res.get("items", []):
            info = item.get("volumeInfo", {})
            img = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
            if img:
                results.append({
                    "title": info.get("title", "Bilinmiyor"),
                    "author": info.get("authors", ["Bilinmiyor"])[0],
                    "cover": img
                })
    except: pass

    # Kaynak 2: Open Library (Google'ın bulamadığı nadir/yeni kitaplar için)
    if len(results) < 3:
        try:
            ol_url = f"https://openlibrary.org/search.json?q={q}&limit=5"
            ol_res = requests.get(ol_url, timeout=10).json()
            for doc in ol_res.get("docs", []):
                cover_id = doc.get("cover_i")
                if cover_id:
                    results.append({
                        "title": doc.get("title", "Bilinmiyor"),
                        "author": doc.get("author_name", ["Bilinmiyor"])[0],
                        "cover": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                    })
        except: pass
    
    # Aynı kitapları listeden temizle (Duplicate check)
    unique_results = []
    seen_titles = set()
    for r in results:
        if r['title'].lower() not in seen_titles:
            unique_results.append(r)
            seen_titles.add(r['title'].lower())
            
    return unique_results

# 4. Arayüz
st.title("📚 Dijital Kütüphanem")

tab_ekle, tab_liste = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Kütüphanem"])

with tab_ekle:
    st.subheader("Kitap, Yazar veya Karakter Yazın")
    col_in, col_btn = st.columns([4, 1])
    with col_in:
        sorgu = st.text_input("Arama yapın...", placeholder="Örn: Şehit Kaveh Akbar", key="s_input", label_visibility="collapsed")
    with col_btn:
        ara_btn = st.button("Ara")

    if ara_btn and sorgu:
        with st.spinner('Derin arama yapılıyor...'):
            st.session_state.bulunan_kitaplar = mega_kitap_ara(sorgu)

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
                    if st.button("Listeye Ekle", key=f"add_{i}"):
                        st.session_state.kitap_listesi.append({
                            "title": b['title'], "author": b['author'], 
                            "cover": b['cover'], "status": durum
                        })
                        st.success("Kütüphaneye eklendi!")
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
