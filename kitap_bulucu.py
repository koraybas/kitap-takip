import streamlit as st
import requests

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; height: 3.2em; font-weight: bold; }
    .book-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

if 'koleksiyon' not in st.session_state: st.session_state.koleksiyon = []
if 'ara_sonuclar' not in st.session_state: st.session_state.ara_sonuclar = []

# --- 2. GÜNCEL KİTAP BULUCU (Hibrit Model) ---
def kitap_ara_derin(sorgu):
    results = []
    q = sorgu.replace(' ', '+')
    
    # GOOGLE BOOKS - Güncel kitaplar için en geniş parametreler
    # orderBy=relevance ve maxResults=20 yaparak yeni baskıları yakalama ihtimalini artırıyoruz
    url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=20&printType=books&orderBy=relevance"
    
    try:
        # Sunucuyu 'yabancı' görmemesi için tarayıcı kimliği (headers) ekliyoruz
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        res = requests.get(url, headers=headers, timeout=12).json()
        
        if "items" in res:
            for item in res["items"]:
                info = item.get("volumeInfo", {})
                img_data = info.get("imageLinks", {})
                # En iyi çözünürlüklü kapağı seç
                img = img_data.get("thumbnail") or img_data.get("smallThumbnail")
                if img:
                    img = img.replace("http://", "https://")
                    results.append({
                        "ad": info.get("title", "Bilinmiyor"),
                        "yazar": info.get("authors", ["Bilinmiyor"])[0],
                        "kapak": img
                    })
    except:
        pass
    return results

# --- 3. ARAYÜZ ---
st.title("📚 Koray Bey'in Kitaplığı")
tab1, tab2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Okuma Listem"])

with tab1:
    s = st.text_input("Kitap, Yazar veya Karakter Adı", placeholder="Örn: Şehit Kaveh Akbar")
    if st.button("Tüm Kaynaklarda Derin Ara"):
        if s:
            with st.spinner('En yeni kitaplar taranıyor...'):
                st.session_state.ara_sonuclar = kitap_ara_derin(s)

    if st.session_state.ara_sonuclar:
        st.write(f"🔍 {len(st.session_state.ara_sonuclar)} sonuç listeleniyor:")
        for i, k in enumerate(st.session_state.ara_sonuclar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], use_container_width=True)
                with c2:
                    st.markdown(f"### {k['ad']}")
                    st.caption(f"✍️ {k['yazar']}")
                    d = st.selectbox("Durum", ["Okuyacağım", "Okuyorum", "Okudum"], key=f"sel_{i}")
                    if st.button("Koleksiyona Ekle", key=f"add_{i}"):
                        st.session_state.koleksiyon.append({
                            "ad": k['ad'], "yazar": k['yazar'], 
                            "kapak": k['kapak'], "durum": d
                        })
                        st.success(f"'{k['ad']}' eklendi!")
            st.divider()

with tab2:
    if not st.session_state.koleksiyon:
        st.info("Kütüphaneniz şu an boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.koleksiyon)):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1: st.image(ktp['kapak'], width=75)
            with col2:
                renk = "#28a745" if ktp['durum'] == "Okudum" else "#ffc107" if ktp['durum'] == "Okuyorum" else "#6c757d"
                st.markdown(f"""<div class="book-card"><b>{ktp["ad"]}</b><br><small>{ktp["yazar"]}</small><br><span style="color:{renk}; font-weight:bold;">● {ktp["durum"]}</span></div>""", unsafe_allow_html=True)
            with col3:
                if st.button("Sil", key=f"del_{idx}"):
                    st.session_state.koleksiyon.pop(len(st.session_state.koleksiyon)-1-idx)
                    st.rerun()
