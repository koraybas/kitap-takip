import streamlit as st
import requests

# --- 1. TASARIM & AYARLAR ---
st.set_page_config(page_title="Koray'ın Kitaplığı", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; background-color: #007bff; color: white; height: 3.5em; font-weight: bold; }
    .book-card { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-left: 6px solid #007bff; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

if 'liste' not in st.session_state: st.session_state.liste = []
if 'ara_sonuc' not in st.session_state: st.session_state.ara_sonuc = []

# --- 2. ÇİFT KANAL ARAMA MOTORU (Türkiye Odaklı) ---
def kitap_ara_super(sorgu):
    results = []
    q = sorgu.replace(' ', '+')
    
    # KANAL 1: Google Books (Türkiye Marketini Zorla)
    try:
        # User-Agent ekleyerek Google'ın bizi "bot" sanmasını engelliyoruz
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        # country=TR ekleyerek Türkiye baskılarını (Radley Ailesi gibi) öne çıkarıyoruz
        g_url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=15&country=TR&orderBy=relevance"
        res = requests.get(g_url, headers=headers, timeout=10).json()
        
        if "items" in res:
            for item in res["items"]:
                inf = item.get("volumeInfo", {})
                img_links = inf.get("imageLinks", {})
                img = img_links.get("thumbnail") or img_links.get("smallThumbnail")
                if img:
                    img = img.replace("http://", "https://")
                    results.append({
                        "isim": inf.get("title", "Bilinmiyor"),
                        "yazar": inf.get("authors", ["Bilinmiyor"])[0],
                        "kapak": img
                    })
    except: pass

    # KANAL 2: Open Library (Yedek Kanal)
    if not results:
        try:
            ol_url = f"https://openlibrary.org/search.json?q={q}&limit=10"
            ol_res = requests.get(ol_url, timeout=10).json()
            for doc in ol_res.get("docs", []):
                c_id = doc.get("cover_i")
                if c_id:
                    results.append({
                        "isim": doc.get("title", "Bilinmiyor"),
                        "yazar": doc.get("author_name", ["Bilinmiyor"])[0],
                        "kapak": f"https://covers.openlibrary.org/b/id/{c_id}-L.jpg"
                    })
        except: pass
    
    return results

# --- 3. ARAYÜZ ---
st.title("📚 Koray'ın Akıllı Kitaplığı")
tab1, tab2 = st.tabs(["🔍 Kitap Bul", "📋 Okuma Listem"])

with tab1:
    s = st.text_input("Kitap, Yazar veya Barkod Yazın", placeholder="Örn: Radley Ailesi veya Simyacı")
    if st.button("Derin Ara"):
        if s:
            with st.spinner('Tüm dünya kütüphaneleri taranıyor...'):
                st.session_state.ara_sonuc = kitap_ara_super(s)
    
    # HATA DÜZELTİLDİ: := operatörü yerine standart kontrol
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
                        st.toast(f"'{k['isim']}' eklendi!")

with tab2:
    if not st.session_state.liste:
        st.info("Listeniz henüz boş.")
    else:
        for idx, v in enumerate(reversed(st.session_state.liste)):
            with st.container():
                st.markdown(f"""
                <div class="book-card">
                    <h3>📖 {v['isim']}</h3>
                    <p>👤 {v['yazar']}</p>
                    <b>• {v['durum']}</b>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️ Sil", key=f"sil_{idx}"):
                    # Tersten dizdiğimiz için silme indeksini ayarlıyoruz
                    pos = len(st.session_state.liste) - 1 - idx
                    st.session_state.liste.pop(pos)
                    st.rerun()
