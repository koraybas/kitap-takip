import streamlit as st
import requests

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Kitap Barkod Tarayıcı", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; background-color: #28a745; color: white; height: 3.5em; font-weight: bold; }
    .isbn-box { background-color: #f0f2f6; padding: 20px; border-radius: 15px; border: 2px dashed #28a745; text-align: center; }
    .book-card { background: white; padding: 15px; border-radius: 15px; shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 6px solid #28a745; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

if 'koleksiyon' not in st.session_state: st.session_state.koleksiyon = []

# --- 2. BARKOD / ISBN ARAMA MOTORU ---
def isbn_sorgula(kod):
    # ISBN numaralarındaki tireleri kaldır
    temiz_kod = kod.replace("-", "").replace(" ", "")
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{temiz_kod}"
    
    try:
        res = requests.get(url, timeout=10).json()
        if "items" in res:
            info = res["items"][0]["volumeInfo"]
            img = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
            return {
                "ad": info.get("title", "Bilinmiyor"),
                "yazar": info.get("authors", ["Bilinmiyor"])[0],
                "kapak": img if img else "https://via.placeholder.com/150x220?text=Kapak+Yok"
            }
    except:
        return None
    return None

# --- 3. ARAYÜZ ---
st.title("📚 Kitap Barkod Sistemi")

tab1, tab2 = st.tabs(["🔍 Barkod Tara / Yaz", "📋 Kütüphanem"])

with tab1:
    st.markdown('<div class="isbn-box">', unsafe_allow_html=True)
    isbn_input = st.text_input("Kitabın arkasındaki 13 haneli ISBN numarasını yazın veya yapıştırın", placeholder="Örn: 9786053755456")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Kitabı Barkoddan Bul"):
        if isbn_input:
            with st.spinner('Barkod sorgulanıyor...'):
                kitap = isbn_sorgula(isbn_input)
                if kitap:
                    st.session_state.son_bulunan = kitap
                else:
                    st.error("Bu barkod ile eşleşen kitap bulunamadı. Lütfen numarayı kontrol edin.")

    # Kitap Bulunduysa Göster
    if 'son_bulunan' in st.session_state:
        k = st.session_state.son_bulunan
        st.divider()
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(k['kapak'], use_container_width=True)
        with c2:
            st.subheader(k['ad'])
            st.write(f"✍️ **Yazar:** {k['yazar']}")
            durum = st.selectbox("Durum", ["Okuyacağım", "Okuyorum", "Okudum"])
            if st.button("Kütüphaneme Ekle"):
                st.session_state.koleksiyon.append({**k, "durum": durum})
                st.success("Kitap başarıyla eklendi!")
                del st.session_state.son_bulunan # Ekrandan temizle

with tab2:
    if not st.session_state.koleksiyon:
        st.info("Kütüphaneniz henüz boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.koleksiyon)):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1: st.image(ktp['kapak'], width=80)
            with col2:
                st.markdown(f"**{ktp['ad']}**")
                st.caption(f"{ktp['yazar']} | {ktp['durum']}")
            with col3:
                if st.button("Sil", key=f"del_{idx}"):
                    pos = len(st.session_state.koleksiyon) - 1 - idx
                    st.session_state.koleksiyon.pop(pos)
                    st.rerun()
