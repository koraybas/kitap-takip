import streamlit as st
import requests

st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

if 'kitaplar' not in st.session_state:
    st.session_state.kitaplar = []

# ARAMA FONKSİYONU - DÜNYA ARŞİVİ (OpenLibrary)
def kitap_ara(sorgu):
    results = []
    try:
        # Sorguyu dünya kütüphane arşivine gönderiyoruz
        url = f"https://openlibrary.org/search.json?q={sorgu.replace(' ', '+')}&limit=10"
        response = requests.get(url, timeout=15)
        data = response.json()
        
        for doc in data.get("docs", []):
            # Kapak resmi id'si varsa al, yoksa boş bırak
            cover_id = doc.get("cover_i")
            if cover_id:
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                results.append({
                    "title": doc.get("title", "Bilinmiyor"),
                    "author": doc.get("author_name", ["Bilinmiyor"])[0],
                    "cover": cover_url
                })
        
        # Eğer yukarıdan sonuç gelmezse (veya az gelirse) Google'ı yedek olarak tara
        if len(results) < 3:
            g_url = f"https://www.googleapis.com/books/v1/volumes?q={sorgu.replace(' ', '+')}"
            g_data = requests.get(g_url, timeout=10).json()
            for item in g_data.get("items", []):
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

st.title("📚 Dijital Kitaplığım")

t1, t2 = st.tabs(["🔍 Kitap Bul", "📋 Listem"])

with t1:
    sorgu = st.text_input("Kitap adını veya yazarını yazın")
    if st.button("Sistemde Ara"):
        if sorgu:
            with st.spinner('Kitaplar aranıyor...'):
                sonuclar = kitap_ara(sorgu)
                if not sonuclar:
                    st.warning("Hiçbir kaynakta bulunamadı. Lütfen ismi kontrol edin.")
                else:
                    for i, b in enumerate(sonuclar):
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.image(b['cover'], width=100)
                        with c2:
                            st.write(f"**{b['title']}**")
                            st.caption(f"Yazar: {b['author']}")
                            durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"d_{i}")
                            if st.button("Ekle", key=f"b_{i}"):
                                st.session_state.kitaplar.append({
                                    "title": b['title'], "author": b['author'], 
                                    "cover": b['cover'], "status": durum
                                })
                                st.success("Eklendi!")
                        st.divider()

with t2:
    if not st.session_state.kitaplar:
        st.info("Listeniz henüz boş.")
    else:
        for idx, k in enumerate(reversed(st.session_state.kitaplar)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.image(k['cover'], width=80)
            with c2:
                st.write(f"**{k['title']}**")
                st.caption(f"{k['author']} | {k['status']}")
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.kitaplar.pop(len(st.session_state.kitaplar)-1-idx)
                    st.rerun()
            st.divider()
