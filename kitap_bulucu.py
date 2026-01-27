import streamlit as st
import requests

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; height: 3em; font-weight: bold; }
    .book-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'liste' not in st.session_state: st.session_state.liste = []
if 'ara_sonuc' not in st.session_state: st.session_state.ara_sonuc = []

# --- 2. GÜNCEL KİTAP MOTORU (Deep Search) ---
def guncel_kitap_ara(sorgu):
    results = []
    q = sorgu.replace(' ', '+')
    
    # 1. Kanal: Google Books (Genişletilmiş Filtresiz Sorgu)
    try:
        # 'langRestrict' kaldırıldı, 'orderBy=relevance' eklendi
        g_url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=20&printType=books&orderBy=relevance"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(g_url, headers=headers, timeout=10).json()
        
        for item in res.get("items", []):
            info = item.get("volumeInfo", {})
            img = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
            if img:
                results.append({
                    "ad": info.get("title", "Bilinmiyor"),
                    "yazar": info.get("authors", ["Bilinmiyor"])[0],
                    "kapak": img
                })
    except: pass

    # 2. Kanal: OpenLibrary (Google'ın bulamadığı güncel küresel baskılar için)
    if len(results) < 5:
        try:
            ol_url = f"https://openlibrary.org/search.json?q={q}&limit=10"
            ol_res = requests.get(ol_url, timeout=10).json()
            for doc in ol_res.get("docs", []):
                c_id = doc.get("cover_i")
                if c_id:
                    results.append({
                        "ad": doc.get("title", "Bilinmiyor"),
                        "yazar": doc.get("author_name", ["Bilinmiyor"])[0],
                        "kapak": f"https://covers.openlibrary.org/b/id/{c_id}-L.jpg"
                    })
        except: pass
    
    return results

# --- 3. ARAYÜZ ---
t1, t2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Okuma Listem"])

with t1:
    s = st.text_input("Kitap veya Yazar Yazın", placeholder="Örn: Şehit Kaveh Akbar")
    if st.button("Derin Ara"):
        if s:
            with st.spinner('En güncel veriler taranıyor...'):
                st.session_state.ara_sonuc = guncel_kitap_ara(s)
    
    if st.session_state.ara_sonuc:
        for i, k in enumerate(st.session_state.ara_sonuc):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], width=110)
                with c2:
                    st.markdown(f"**{k['ad']}**")
                    st.caption(f"Yazar: {k['yazar']}")
                    d = st.selectbox("Durum", ["Okuyacağım", "Okuyorum", "Okudum"], key=f"d_{i}")
                    if st.button("Listeme Ekle", key=f"b_{i}"):
                        st.session_state.liste.append({"ad": k['ad'], "yazar": k['yazar'], "kapak": k['kapak'], "durum": d})
                        st.success("Eklendi!")
            st.divider()

with t2:
    if not st.session_state.liste:
        st.info("Kütüphaneniz henüz boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.liste)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1: st.image(ktp['kapak'], width=70)
            with c2:
                r_renk = "#28a745" if ktp['durum'] == "Okudum" else "#ffc107"
                st.markdown(f'<div class="book-card"><b>{ktp["ad"]}</b><br><small>{ktp["yazar"]}</small><br><span style="color:{r_renk}; font-weight:bold;">● {ktp["durum"]}</span></div>', unsafe_allow_html=True)
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.liste.pop(len(st.session_state.liste)-1-idx)
                    st.rerun()
