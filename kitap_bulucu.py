import streamlit as st
import requests

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Kitap Takip", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; background-color: #007bff; color: white; height: 3.5em; font-weight: bold; }
    .book-card { background: white; padding: 15px; border-radius: 15px; border-left: 6px solid #007bff; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'koleksiyon' not in st.session_state: st.session_state.koleksiyon = []

# --- 2. BARKOD SORGULAMA MOTORU ---
def kitap_getir_isbn(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    try:
        res = requests.get(url, timeout=10).json()
        if "items" in res:
            inf = res["items"][0]["volumeInfo"]
            img = inf.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
            return {
                "ad": inf.get("title", "Bilinmiyor"),
                "yazar": inf.get("authors", ["Bilinmiyor"])[0],
                "kapak": img if img else "https://via.placeholder.com/150x220?text=Kapak+Yok"
            }
    except: pass
    return None

# --- 3. ARAYÜZ ---
st.title("📚 Akıllı Kitap Takip")

tab1, tab2 = st.tabs(["📷 Barkod Tara / Bul", "📋 Kütüphanem"])

with tab1:
    # KAMERA İLE FOTOĞRAF ÇEKME
    st.subheader("Barkodun Fotoğrafını Çek")
    foto = st.camera_input("Kitabın arkasındaki barkodu ortalayarak fotoğraf çekin")
    
    if foto:
        st.warning("Not: Görselden barkod okuma işlemi için telefonunuzun klavye üzerindeki 'Tarama' özelliğini de kullanabilirsiniz.")
    
    st.divider()
    
    # MANUEL GİRİŞ (Barkodu fotoğraftan okuyup buraya yazmak için)
    isbn_input = st.text_input("Veya Barkod Numarasını Buraya Yazın (978...)", placeholder="Örn: 9786256029132")
    
    if st.button("Kitabı Bul ve Getir"):
        if isbn_input:
            with st.spinner('Kitap bilgileri çekiliyor...'):
                k = kitap_getir_isbn(isbn_input)
                if k:
                    c1, c2 = st.columns([1, 2])
                    with c1: st.image(k['kapak'], use_container_width=True)
                    with c2:
                        st.markdown(f"**{k['ad']}**")
                        st.caption(f"Yazar: {k['yazar']}")
                        d = st.selectbox("Durum", ["Okuyacağım", "Okuyorum", "Okudum"])
                        if st.button("Listeye Ekle"):
                            st.session_state.koleksiyon.append({**k, "durum": d})
                            st.success("Kitap eklendi!")
                else:
                    st.error("Bu barkod ile kayıt bulunamadı.")

with tab2:
    if not st.session_state.koleksiyon:
        st.info("Kütüphaneniz boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.koleksiyon)):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1: st.image(ktp['kapak'], width=70)
            with col2:
                renk = "#28a745" if ktp['durum'] == "Okudum" else "#ffc107"
                st.markdown(f'<div class="book-card"><b>{ktp["ad"]}</b><br>{ktp["yazar"]}<br><span style="color:{renk}; font-weight:bold;">● {ktp["durum"]}</span></div>', unsafe_allow_html=True)
            with col3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.koleksiyon.pop(len(st.session_state.koleksiyon)-1-idx)
                    st.rerun()
