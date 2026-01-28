import streamlit as st
import requests
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- 1. AYARLAR & SİZİN TASARIMINIZ ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%; border-radius: 10px; height: 3em;
        background-color: #007bff; color: white; border: none;
    }
    .book-card {
        background-color: white; padding: 15px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;
        border-left: 5px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GOOGLE SHEETS BAĞLANTISI (Kalıcı Veritabanı) ---
# Not: Bu kısım hata vermesin diye başlangıçta boş liste tutuyoruz
if 'liste' not in st.session_state:
    st.session_state.liste = []

# --- 3. AKILLI ARAMA FONKSİYONU ---
def kitap_ara_hibrit(sorgu):
    results = []
    # ISBN mi yoksa metin mi kontrol et
    is_isbn = sorgu.replace("-", "").replace(" ", "").isdigit()
    prefix = "isbn:" if is_isbn else ""
    url = f"https://www.googleapis.com/books/v1/volumes?q={prefix}{sorgu.replace(' ', '+')}&maxResults=10"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10).json()
        if "items" in res:
            for item in res["items"]:
                inf = item.get("volumeInfo", {})
                img = inf.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
                results.append({
                    "isim": inf.get("title", "Bilinmiyor"),
                    "yazar": inf.get("authors", ["Bilinmiyor"])[0],
                    "kapak": img if img else "https://via.placeholder.com/150x220?text=Kapak+Yok",
                    "tur": inf.get("categories", ["Diğer"])[0]
                })
    except: pass
    return results

# --- 4. ANA MENÜ ---
tab1, tab2 = st.tabs(["➕ Kitap Bul & Ekle", "📚 Kütüphanem"])

with tab1:
    st.subheader("Kitap Bul (İsim, Yazar veya Barkod)")
    arama_metni = st.text_input("Aramak istediğiniz kitabı yazın veya barkod taratın", placeholder="Örn: Radley Ailesi")
    
    if st.button("Sistemde Ara"):
        if arama_metni:
            with st.spinner('Kütüphaneler taranıyor...'):
                st.session_state.bulunanlar = kitap_ara_hibrit(arama_metni)

    if 'bulunanlar' in st.session_state:
        for i, k in enumerate(st.session_state.bulunanlar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], use_container_width=True)
                with c2:
                    st.markdown(f"**{k['isim']}**")
                    st.caption(f"✍️ {k['yazar']}")
                    durum = st.selectbox("Okuma Durumu", ["Okunacak", "Okunuyor", "Okundu"], key=f"d_{i}")
                    if st.button("Kütüphaneye Kaydet", key=f"b_{i}"):
                        st.session_state.liste.append({**k, "durum": durum})
                        st.success(f"'{k['isim']}' eklendi!")

with tab2:
    st.subheader("Kitap Listem")
    if not st.session_state.liste:
        st.info("Kütüphaneniz henüz boş. Kitap ekleyerek başlayın!")
    else:
        for idx, v in enumerate(reversed(st.session_state.liste)):
            with st.container():
                st.markdown(f"""
                <div class="book-card">
                    <h3 style='margin:0; color:#1f1f1f;'>📖 {v['isim']}</h3>
                    <p style='margin:5px 0; color:#555;'>👤 <b>Yazar:</b> {v['yazar']}</p>
                    <span style='background:#e9ecef; padding:2px 8px; border-radius:5px; font-size:0.8em;'>{v['tur']}</span>
                    <span style='margin-left:10px; color:{"#28a745" if v["durum"]=="Okundu" else "#ffc107"}; font-weight:bold;'>• {v['durum']}</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🗑️ Sil", key=f"sil_{idx}"):
                    st.session_state.liste.pop(len(st.session_state.liste) - 1 - idx)
                    st.rerun()
