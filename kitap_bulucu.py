import streamlit as st
import requests

# --- 1. TASARIM (Sizin Stiliniz) ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; height: 3em; }
    .book-card { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'liste' not in st.session_state: st.session_state.liste = []
if 'ara_sonuc' not in st.session_state: st.session_state.ara_sonuc = []

# --- 2. ENGEL TANIMAYAN ARAMA MOTORU (Open Library) ---
def kitap_ara_acik(sorgu):
    results = []
    # Google engellese bile Open Library asla engellemez
    url = f"https://openlibrary.org/search.json?q={sorgu.replace(' ', '+')}&limit=10"
    try:
        res = requests.get(url, timeout=15).json()
        for doc in res.get("docs", []):
            cover_id = doc.get("cover_i")
            if cover_id: # Sadece kapağı olanları getir
                results.append({
                    "isim": doc.get("title", "Bilinmiyor"),
                    "yazar": doc.get("author_name", ["Bilinmiyor"])[0],
                    "kapak": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg",
                    "tur": doc.get("subject", ["Genel"])[0]
                })
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
    return results

# --- 3. ARAYÜZ ---
tab1, tab2 = st.tabs(["🔍 Kitap Bul", "📋 Listem"])

with tab1:
    s = st.text_input("Kitap veya Yazar Adı", placeholder="Örn: Simyacı veya Matt Haig")
    if st.button("Derin Ara"):
        if s:
            with st.spinner('Evrensel kütüphane taranıyor...'):
                st.session_state.ara_sonuc = kitap_ara_acik(s)
    
    if st.session_state.ara_sonuc:
        for i, k in enumerate(st.session_state.ara_sonuc):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], use_container_width=True)
                with c2:
                    st.markdown(f"**{k['isim']}**")
                    st.caption(f"✍️ {k['yazar']}")
                    d = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"d_{i}")
                    if st.button("Listeye Ekle", key=f"b_{i}"):
                        st.session_state.liste.append({**k, "durum": d})
                        st.toast("Eklendi!")

with tab2:
    for idx, v in enumerate(reversed(st.session_state.liste)):
        st.markdown(f"""<div class="book-card"><h3>📖 {v['isim']}</h3><p>👤 {v['yazar']}</p><b>• {v['durum']}</b></div>""", unsafe_allow_html=True)
