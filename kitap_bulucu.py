import streamlit as st
import requests

# --- 1. AYARLAR ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# Sizin istediğiniz modern mavi stil
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; height: 3em; }
    .book-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 5px solid #007bff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'liste' not in st.session_state: st.session_state.liste = []
if 'sonuclar' not in st.session_state: st.session_state.sonuclar = []

# --- 2. ASLA ENGELLENMEYEN ARAMA MOTORU ---
def kitap_ara_derin(sorgu):
    all_results = []
    q = sorgu.replace(' ', '+')
    
    # Kaynak 1: Open Library (Dünya Arşivi - Hiçbir kısıtlama yoktur)
    try:
        url_ol = f"https://openlibrary.org/search.json?q={q}&limit=10"
        res_ol = requests.get(url_ol, timeout=10).json()
        for doc in res_ol.get("docs", []):
            c_id = doc.get("cover_i")
            if c_id:
                all_results.append({
                    "ad": doc.get("title", "Bilinmiyor"),
                    "yazar": doc.get("author_name", ["Bilinmiyor"])[0],
                    "kapak": f"https://covers.openlibrary.org/b/id/{c_id}-L.jpg"
                })
    except: pass

    # Kaynak 2: Google Books (Sadece kısıtlama yoksa sonuçları ekler)
    try:
        url_g = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=10"
        headers = {"User-Agent": "Mozilla/5.0"}
        res_g = requests.get(url_g, headers=headers, timeout=10).json()
        for item in res_g.get("items", []):
            inf = item.get("volumeInfo", {})
            img = inf.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
            if img:
                all_results.append({
                    "ad": inf.get("title", "Bilinmiyor"),
                    "yazar": inf.get("authors", ["Bilinmiyor"])[0],
                    "kapak": img
                })
    except: pass
    
    return all_results

# --- 3. ARAYÜZ ---
t1, t2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Listem"])

with t1:
    s = st.text_input("Kitap veya Yazar Yazın", placeholder="Örn: Simyacı, Şehit...")
    if st.button("Sistemde Derin Ara"):
        if s:
            with st.spinner('Kütüphaneler taranıyor...'):
                st.session_state.sonuclar = kitap_ara_derin(s)

    if st.session_state.sonuclar:
        for i, k in enumerate(st.session_state.sonuclar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], width=100)
                with c2:
                    st.markdown(f"**{k['ad']}**")
                    st.caption(f"Yazar: {k['yazar']}")
                    d = st.selectbox("Durum", ["Okuyacağım", "Okuyorum", "Okudum"], key=f"d_{i}")
                    if st.button("Ekle", key=f"b_{i}"):
                        st.session_state.liste.append({"ad": k['ad'], "yazar": k['yazar'], "kapak": k['kapak'], "durum": d})
                        st.success("Listeye Eklendi!")
            st.divider()

with t2:
    if not st.session_state.liste:
        st.info("Listeniz henüz boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.liste)):
            with st.container():
                c1, c2, c3 = st.columns([1, 3, 1])
                with c1: st.image(ktp['kapak'], width=70)
                with c2:
                    r_renk = "#28a745" if ktp['durum'] == "Okudum" else "#ffc107"
                    st.markdown(f'<div class="book-card"><b>{ktp["ad"]}</b><br><small>{ktp["yazar"]}</small><br><span style="color:{r_renk};">● {ktp["durum"]}</span></div>', unsafe_allow_html=True)
                with c3:
                    if st.button("🗑️", key=f"del_{idx}"):
                        st.session_state.liste.pop(len(st.session_state.liste)-1-idx)
                        st.rerun()
