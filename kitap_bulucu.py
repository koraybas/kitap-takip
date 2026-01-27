import streamlit as st
import requests

# --- 1. AYARLAR & MODERN TASARIM ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; height: 3.2em; font-weight: bold; }
    .book-card { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

if 'liste' not in st.session_state: st.session_state.liste = []
if 'ara_sonuc' not in st.session_state: st.session_state.ara_sonuc = []

# --- 2. ASLA KAÇIRMAYAN ARAMA MOTORU ---
def kitap_ara_pro(sorgu):
    results = []
    q = sorgu.replace(' ', '+')
    
    # ISBN veya İsim ile Google'ın en derin katmanına iniyoruz
    url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=15&printType=books"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10).json()
        
        for item in res.get("items", []):
            info = item.get("volumeInfo", {})
            img = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
            results.append({
                "ad": info.get("title", "Bilinmiyor"),
                "yazar": info.get("authors", ["Bilinmiyor"])[0],
                "kapak": img if img else "https://via.placeholder.com/150x220?text=Kapak+Yok"
            })
    except: pass
    return results

# --- 3. ARAYÜZ ---
st.title("📚 Dijital Kütüphanem")
t1, t2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Listem"])

with t1:
    st.subheader("İsim, Yazar veya Barkod (ISBN) Yazın")
    s = st.text_input("", placeholder="Örn: 9786256029132 (Barkod) veya Radley Ailesi", label_visibility="collapsed")
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        if st.button("Sistemde Ara"):
            if s:
                with st.spinner('Derin tarama yapılıyor...'):
                    st.session_state.ara_sonuc = kitap_ara_pro(s)
    with col_b:
        if st.button("Temizle"):
            st.session_state.ara_sonuc = []
            st.rerun()

    if st.session_state.ara_sonuc:
        for i, k in enumerate(st.session_state.ara_sonuc):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], width=110)
                with c2:
                    st.markdown(f"**{k['ad']}**")
                    st.caption(f"Yazar: {k['yazar']}")
                    d = st.selectbox("Durum", ["Okuyacağım", "Okuyorum", "Okudum"], key=f"d_{i}")
                    if st.button("Listeye Ekle", key=f"b_{i}"):
                        st.session_state.liste.append({"ad": k['ad'], "yazar": k['yazar'], "kapak": k['kapak'], "durum": d})
                        st.success("Eklendi!")
            st.divider()
    
    # MANUEL CAN SİMİDİ (Hiçbir şey bulamazsa)
    st.markdown("---")
    with st.expander("➕ Aradığım Kitabı Sistem Bulamadı (Manuel Ekle)"):
        m_ad = st.text_input("Kitap Adı")
        m_yazar = st.text_input("Yazar")
        m_durum = st.selectbox("Durum", ["Okuyacağım", "Okuyorum", "Okudum"], key="m_d")
        if st.button("Hemen Ekle"):
            if m_ad and m_yazar:
                st.session_state.liste.append({"ad": m_ad, "yazar": m_yazar, "kapak": "https://via.placeholder.com/150x220?text=Ozel+Kayit", "durum": m_durum})
                st.success("Manuel olarak eklendi!")

with t2:
    if not st.session_state.liste:
        st.info("Listeniz henüz boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.liste)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1: st.image(ktp['kapak'], width=70)
            with c2:
                r = "#28a745" if ktp['durum'] == "Okudum" else "#ffc107"
                st.markdown(f'<div class="book-card"><b>{ktp["ad"]}</b><br>{ktp["yazar"]}<br><span style="color:{r};">● {ktp["durum"]}</span></div>', unsafe_allow_html=True)
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.liste.pop(len(st.session_state.liste)-1-idx)
                    st.rerun()
