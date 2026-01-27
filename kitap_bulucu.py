import streamlit as st
import requests

# --- 1. AYARLAR & MODERN TASARIM ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; height: 3.2em; font-weight: bold; }
    .book-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

if 'liste' not in st.session_state: st.session_state.liste = []
if 'ara_sonuc' not in st.session_state: st.session_state.ara_sonuc = []

# --- 2. KESİN ÇÖZÜM: ÇAPRAZ ARAMA (Google + OpenLibrary) ---
def kitap_ara_kesin(sorgu):
    results = []
    q = sorgu.replace(' ', '+')
    
    # ADIM 1: OpenLibrary Denemesi (Kısıtlama yoktur, en güvenilir yoldur)
    try:
        ol_url = f"https://openlibrary.org/search.json?q={q}&limit=10"
        ol_res = requests.get(ol_url, timeout=10).json()
        for doc in ol_res.get("docs", []):
            cover_id = doc.get("cover_i")
            if cover_id:
                results.append({
                    "ad": doc.get("title", "Bilinmiyor"),
                    "yazar": doc.get("author_name", ["Bilinmiyor"])[0],
                    "kapak": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                })
    except: pass

    # ADIM 2: Eğer hala sonuç yoksa, Google'ı en sade (engellenemeyen) haliyle dene
    if not results:
        try:
            g_url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=10"
            headers = {"User-Agent": "Mozilla/5.0"}
            g_res = requests.get(g_url, headers=headers, timeout=10).json()
            for item in g_res.get("items", []):
                inf = item.get("volumeInfo", {})
                img = inf.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
                if img:
                    results.append({
                        "ad": inf.get("title", "Bilinmiyor"),
                        "yazar": inf.get("authors", ["Bilinmiyor"])[0],
                        "kapak": img
                    })
        except: pass
    return results

# --- 3. ARAYÜZ ---
st.title("📚 Dijital Kütüphanem")
t1, t2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Listem"])

with t1:
    s = st.text_input("Kitap veya Yazar Adı", placeholder="Örn: Simyacı, Şehit...")
    if st.button("Sistemde Derin Ara"):
        if s:
            with st.spinner('Kütüphaneler taranıyor...'):
                st.session_state.ara_sonuc = kitap_ara_kesin(s)
    
    if st.session_state.ara_sonuc:
        for i, k in enumerate(st.session_state.ara_sonuc):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], width=110)
                with c2:
                    st.markdown(f"**{k['ad']}**")
                    st.caption(f"Yazar: {k['yazar']}")
                    d = st.selectbox("Durum", ["Okuyacağım", "Okuyorum", "Okudum"], key=f"d_{i}")
                    if st.button("Ekle", key=f"b_{i}"):
                        st.session_state.liste.append({"ad": k['ad'], "yazar": k['yazar'], "kapak": k['kapak'], "durum": d})
                        st.success("Eklendi!")
            st.divider()

with t2:
    if not st.session_state.liste:
        st.info("Kütüphaneniz boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.liste)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1: st.image(ktp['kapak'], width=70)
            with c2:
                renk = "#28a745" if ktp['durum'] == "Okudum" else "#ffc107"
                st.markdown(f'<div class="book-card"><b>{ktp["ad"]}</b><br><small>{ktp["yazar"]}</small><br><span style="color:{renk};">● {ktp["durum"]}</span></div>', unsafe_allow_html=True)
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.liste.pop(len(st.session_state.liste)-1-idx)
                    st.rerun()
