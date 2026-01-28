import streamlit as st
import requests

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; height: 3.5em; font-weight: bold; }
    .book-card { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

if 'kutuphane' not in st.session_state: st.session_state.kutuphane = []
if 'ara_sonuclar' not in st.session_state: st.session_state.ara_sonuclar = []

# --- 2. HİBRİT ARAMA MOTORU (Stabil Versiyon) ---
def kitap_ara_stabil(sorgu):
    results = []
    q = sorgu.replace(' ', '+')
    
    # KANAL 1: Google Books (Geniş Arama)
    try:
        # Headers ekleyerek sunucuyu gerçek bir kullanıcı gibi tanıtıyoruz
        headers = {"User-Agent": "Mozilla/5.0"}
        url_g = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=15"
        res_g = requests.get(url_g, headers=headers, timeout=10).json()
        
        if "items" in res_g:
            for item in res_g["items"]:
                inf = item.get("volumeInfo", {})
                img = inf.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
                if img:
                    results.append({
                        "ad": inf.get("title", "Bilinmiyor"),
                        "yazar": inf.get("authors", ["Bilinmiyor"])[0],
                        "kapak": img
                    })
    except: pass

    # KANAL 2: Open Library (Google'ın bulamadığı veya engellediği durumlar için)
    if len(results) < 3:
        try:
            url_ol = f"https://openlibrary.org/search.json?q={q}&limit=10"
            res_ol = requests.get(url_ol, timeout=10).json()
            for doc in res_ol.get("docs", []):
                c_id = doc.get("cover_i")
                if c_id:
                    results.append({
                        "ad": doc.get("title", "Bilinmiyor"),
                        "yazar": doc.get("author_name", ["Bilinmiyor"])[0],
                        "kapak": f"https://covers.openlibrary.org/b/id/{c_id}-M.jpg"
                    })
        except: pass
    
    return results

# --- 3. ARAYÜZ ---
st.title("📚 Koray Bey'in Kitaplığı")
tab1, tab2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Okuma Listem"])

with tab1:
    s_input = st.text_input("Kitap, Yazar veya Barkod Yazın", placeholder="Örn: Radley Ailesi")
    
    if st.button("Sistemde Ara"):
        if s_input:
            with st.spinner('Kitaplar taranıyor...'):
                st.session_state.ara_sonuclar = kitap_ara_stabil(s_input)

    # Arama Sonuçlarını Listele
    if st.session_state.ara_sonuclar:
        for i, k in enumerate(st.session_state.ara_sonuclar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], use_container_width=True)
                with c2:
                    st.markdown(f"**{k['ad']}**")
                    st.caption(f"✍️ {k['yazar']}")
                    d = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"d_{i}")
                    if st.button("Listeye Ekle", key=f"b_{i}"):
                        st.session_state.kutuphane.append({"ad": k['ad'], "yazar": k['yazar'], "kapak": k['kapak'], "durum": d})
                        st.success(f"'{k['ad']}' eklendi!")
            st.divider()

with tab2:
    if not st.session_state.kutuphane:
        st.info("Kütüphaneniz boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.kutuphane)):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1: st.image(ktp['kapak'], width=70)
            with col2:
                r_renk = "#28a745" if ktp['durum'] == "Okundu" else "#ffc107"
                st.markdown(f'<div class="book-card"><b>{ktp["ad"]}</b><br>{ktp["yazar"]}<br><span style="color:{r_renk}; font-weight:bold;">● {ktp["durum"]}</span></div>', unsafe_allow_html=True)
            with col3:
                if st.button("Sil", key=f"sil_{idx}"):
                    # Tersten siliyoruz
                    st.session_state.kutuphane.pop(len(st.session_state.koleksiyon)-1-idx if 'koleksiyon' in dir() else len(st.session_state.kutuphane)-1-idx)
                    st.rerun()
