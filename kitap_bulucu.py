import streamlit as st
import requests

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; height: 3.5em; font-weight: bold; }
    .book-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

if 'koleksiyon' not in st.session_state: st.session_state.koleksiyon = []
if 'ara_sonuclar' not in st.session_state: st.session_state.ara_sonuclar = []

# --- 2. AKILLI HİBRİT ARAMA MOTORU ---
def kitap_ara_derin(sorgu):
    results = []
    q = sorgu.replace(' ', '+')
    
    # KANAL 1: Google Books (Genişletilmiş Filtre)
    try:
        url_g = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=15&printType=books"
        headers = {"User-Agent": "Mozilla/5.0"}
        res_g = requests.get(url_g, headers=headers, timeout=10).json()
        
        if "items" in res_g:
            for item in res_g["items"]:
                inf = item.get("volumeInfo", {})
                img_data = inf.get("imageLinks", {})
                img = img_data.get("thumbnail") or img_data.get("smallThumbnail")
                if img:
                    img = img.replace("http://", "https://")
                    results.append({
                        "ad": inf.get("title", "Bilinmiyor"),
                        "yazar": inf.get("authors", ["Bilinmiyor"])[0],
                        "kapak": img
                    })
    except: pass

    # KANAL 2: Open Library (Yedek)
    if len(results) < 5:
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
st.title("📚 Koray'ın Dijital Kütüphanesi")
t1, t2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Okuma Listem"])

with t1:
    s_in = st.text_input("Kitap, Yazar veya Karakter Adı", placeholder="Örn: Radley Ailesi veya Matt Haig")
    if st.button("Sistemde Derin Ara"):
        if s_in:
            with st.spinner('Tüm raflar taranıyor...'):
                st.session_state.ara_sonuclar = kitap_ara_derin(s_in)

    if st.session_state.ara_sonuclar:
        for i, k in enumerate(st.session_state.ara_sonuclar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], use_container_width=True)
                with c2:
                    st.markdown(f"**{k['ad']}**")
                    st.caption(f"Yazar: {k['yazar']}")
                    durum_sec = st.selectbox("Durum Seçin", ["Okuyacağım", "Okuyorum", "Okudum"], key=f"d_{i}")
                    if st.button("Listeye Ekle", key=f"b_{i}"):
                        st.session_state.koleksiyon.append({"ad": k['ad'], "yazar": k['yazar'], "kapak": k['kapak'], "durum": durum_sec})
                        st.success("Listenize eklendi!")
            st.divider()

with t2:
    if not st.session_state.koleksiyon:
        st.info("Listeniz henüz boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.koleksiyon)):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1: st.image(ktp['kapak'], width=70)
            with col2:
                durum_renk = "#28a745" if ktp['durum'] == "Okudum" else "#ffc107" if ktp['durum'] == "Okuyorum" else "#6c757d"
                st.markdown(f"""
                    <div class="book-card">
                        <b>{ktp["ad"]}</b><br>
                        <small>{ktp["yazar"]}</small><br>
                        <span style="color:{durum_renk}; font-weight:bold;">● {ktp["durum"]}</span>
                    </div>
                """, unsafe_allow_html=True)
            with col3:
                if st.button("Sil", key=f"del_{idx}"):
                    # Listeden silme işlemi
                    pos = len(st.session_state.koleksiyon) - 1 - idx
                    st.session_state.koleksiyon.pop(pos)
                    st.rerun()
