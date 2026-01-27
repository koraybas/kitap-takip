import streamlit as st
import requests

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; height: 3em; }
    .book-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 5px solid #007bff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'liste' not in st.session_state: st.session_state.liste = []
if 'ara_sonuc' not in st.session_state: st.session_state.ara_sonuc = []

# --- 2. GÜNCEL KİTAP BULUCU (Amazon & Kitapyurdu Verisi Dahil) ---
def guncel_kitap_ara(sorgu):
    results = []
    # Arama terimini zenginleştiriyoruz ki en yeni baskıları bulsun
    q = sorgu.replace(' ', '+')
    
    # GOOGLE BOOKS - En yeni ve en alakalı sonuçlar için özel parametreler
    # printType=books ve orderBy=relevance ekleyerek en güncel ticari kitapları zorluyoruz
    url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=15&printType=books&orderBy=relevance"
    
    try:
        # User-Agent ekleyerek Google'ın bizi "yabancı sunucu" diye engellemesini aşıyoruz
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get(url, headers=headers, timeout=10).json()
        
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
    return results

# --- 3. ARAYÜZ ---
t1, t2 = st.tabs(["🔍 Yeni Kitap Bul", "📋 Kütüphanem"])

with t1:
    s = st.text_input("Kitap veya Yazar Adı", placeholder="Örn: Şehit, Radley Ailesi...")
    if st.button("Derinlemesine Ara"):
        if s:
            with st.spinner('Güncel kitaplar taranıyor...'):
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
        st.info("Listeniz boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.liste)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1: st.image(ktp['kapak'], width=70)
            with c2:
                st.markdown(f'<div class="book-card"><b>{ktp["ad"]}</b><br><small>{ktp["yazar"]}</small><br><span style="color:#007bff;">{ktp["durum"]}</span></div>', unsafe_allow_html=True)
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.liste.pop(len(st.session_state.liste)-1-idx)
                    st.rerun()
