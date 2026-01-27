import streamlit as st
import requests

# 1. Uygulama Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# Sizin istediğiniz o modern mavi tasarım
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; height: 3.5em; font-weight: bold; }
    .book-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

if 'kutuphane' not in st.session_state: st.session_state.kutuphane = []
if 'bulunanlar' not in st.session_state: st.session_state.bulunanlar = []

# 2. ASLA TAKILMAYAN HİBRİT ARAMA MOTORU
def kitap_ara_sinirsiz(sorgu):
    results = []
    q = sorgu.replace(' ', '+')
    
    # KANAL A: Open Library (Google engellese bile burası her zaman çalışır)
    try:
        url_ol = f"https://openlibrary.org/search.json?q={q}&limit=12"
        res_ol = requests.get(url_ol, timeout=15).json()
        for doc in res_ol.get("docs", []):
            c_id = doc.get("cover_i")
            if c_id:
                results.append({
                    "ad": doc.get("title", "Bilinmiyor"),
                    "yazar": doc.get("author_name", ["Bilinmiyor"])[0],
                    "kapak": f"https://covers.openlibrary.org/b/id/{c_id}-L.jpg"
                })
    except: pass

    # KANAL B: Google (Yedek olarak, User-Agent maskesi ile)
    if not results:
        try:
            url_g = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=10"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"}
            res_g = requests.get(url_g, headers=headers, timeout=10).json()
            for item in res_g.get("items", []):
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

# 3. ARAYÜZ
st.title("📚 Dijital Kütüphanem")
t1, t2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Listem"])

with t1:
    s_input = st.text_input("Kitap, Yazar veya ISBN Yazın", placeholder="Örn: Simyacı veya 9786053755456")
    if st.button("Sistemde Derin Ara"):
        if s_input:
            with st.spinner('Kütüphaneler taranıyor...'):
                st.session_state.bulunanlar = kitap_ara_sinirsiz(s_input)

    if st.session_state.bulunanlar:
        for i, k in enumerate(st.session_state.bulunanlar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], use_container_width=True)
                with c2:
                    st.markdown(f"**{k['ad']}**")
                    st.caption(f"Yazar: {k['yazar']}")
                    d = st.selectbox("Okuma Durumu", ["Okuyacağım", "Okuyorum", "Okudum"], key=f"sel_{i}")
                    if st.button("Listeme Kaydet", key=f"btn_{i}"):
                        st.session_state.kutuphane.append({"ad": k['ad'], "yazar": k['yazar'], "kapak": k['kapak'], "durum": d})
                        st.success("Listeye eklendi!")
            st.divider()

with t2:
    if not st.session_state.kutuphane:
        st.info("Kütüphaneniz boş. Kitap ekleyerek başlayın!")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.kutuphane)):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1: st.image(ktp['kapak'], width=70)
            with col2:
                renk = "#28a745" if ktp['durum'] == "Okudum" else "#ffc107"
                st.markdown(f'<div class="book-card"><b>{ktp["ad"]}</b><br>{ktp["yazar"]}<br><span style="color:{renk}; font-weight:bold;">● {ktp["durum"]}</span></div>', unsafe_allow_html=True)
            with col3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.kutuphane.pop(len(st.session_state.kutuphane)-1-idx)
                    st.rerun()
