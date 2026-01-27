import streamlit as st
import requests

# --- 1. SAYFA AYARLARI (Mobil Uyumluluk) ---
st.set_page_config(
    page_title="Kitaplığım",
    page_icon="📚",
    layout="centered"
)

# --- 2. MODERN STİL (Paylaştığınız CSS Tasarımı) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
        border: none;
    }
    .book-card {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 5px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HAFIZA YÖNETİMİ ---
if 'kutuphane' not in st.session_state:
    st.session_state.kutuphane = []

# --- 4. OTOMATİK ARAMA MOTORU (Google & Amazon Verileri) ---
def kitap_ara_otomatik(sorgu):
    url = f"https://www.googleapis.com/books/v1/volumes?q={sorgu.replace(' ', '+')}&maxResults=10"
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10).json()
        results = []
        if "items" in res:
            for item in res["items"]:
                info = item.get("volumeInfo", {})
                img = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
                if img:
                    results.append({
                        "isim": info.get("title", "Bilinmiyor"),
                        "yazar": info.get("authors", ["Bilinmiyor"])[0],
                        "kapak": img
                    })
        return results
    except:
        return []

# --- 5. ANA MENÜ (SEKMELER) ---
tab1, tab2 = st.tabs(["➕ Kitap Bul & Ekle", "📚 Kütüphanem"])

# --- TAB 1: KİTAP BUL & EKLE ---
with tab1:
    st.subheader("Kitap Ara ve Listene Ekle")
    arama_sorgusu = st.text_input("Kitap adı veya yazar yazın", placeholder="Örn: Simyacı")
    
    if st.button("Sistemde Derin Ara"):
        if arama_sorgusu:
            with st.spinner('Taranıyor...'):
                sonuclar = kitap_ara_otomatik(arama_sorgusu)
                if not sonuclar:
                    st.error("Üzgünüm, kitap bulunamadı.")
                else:
                    for i, k in enumerate(sonuclar):
                        with st.container():
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                st.image(k['kapak'], width=100)
                            with col2:
                                st.markdown(f"**{k['isim']}**")
                                st.caption(f"Yazar: {k['yazar']}")
                                durum = st.selectbox("Durum", ["Okuyacağım", "Okuyorum", "Okudum"], key=f"d_{i}")
                                if st.button("Listeme Ekle", key=f"b_{i}"):
                                    st.session_state.kutuphane.append({
                                        "isim": k['isim'],
                                        "yazar": k['yazar'],
                                        "kapak": k['kapak'],
                                        "durum": durum
                                    })
                                    st.success(f"'{k['isim']}' eklendi!")
                        st.divider()

# --- TAB 2: KÜTÜPHANEM ---
with tab2:
    st.subheader("Okuma Listem")
    if not st.session_state.kutuphane:
        st.info("Kütüphaneniz henüz boş.")
    else:
        for idx, kitap in enumerate(reversed(st.session_state.kutuphane)):
            with st.container():
                c1, c2, c3 = st.columns([1, 3, 1])
                with c1:
                    st.image(kitap['kapak'], width=70)
                with c2:
                    # Sizin paylaştığınız kart tasarımı
                    renk = "#28a745" if kitap['durum'] == "Okudum" else "#ffc107"
                    st.markdown(f"""
                        <div class="book-card">
                            <h3 style='margin:0; font-size:1.1em;'>📖 {kitap['isim']}</h3>
                            <p style='margin:5px 0; color:#555;'>👤 {kitap['yazar']}</p>
                            <span style='color:{renk}; font-weight:bold;'>• {kitap['durum']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                with c3:
                    if st.button("🗑️", key=f"sil_{idx}"):
                        gercek_idx = len(st.session_state.kutuphane) - 1 - idx
                        st.session_state.kutuphane.pop(gercek_idx)
                        st.rerun()
