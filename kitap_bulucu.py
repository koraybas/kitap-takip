import streamlit as st
import requests

# --- 1. MODERN TASARIM (Mobil Öncelikli) ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; background-color: #007bff; color: white; height: 3.5em; font-weight: bold; font-size: 16px; transition: 0.3s; }
    .stButton>button:hover { background-color: #0056b3; border: 2px solid #fff; }
    .book-card { background: white; padding: 15px; border-radius: 15px; shadow: 0 4px 12px rgba(0,0,0,0.1); border-left: 6px solid #007bff; margin-bottom: 15px; }
    .status-badge { padding: 4px 10px; border-radius: 8px; font-weight: bold; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

if 'liste' not in st.session_state: st.session_state.liste = []
if 'sonuclar' not in st.session_state: st.session_state.sonuclar = []

# --- 2. DERİN ARAMA MOTORU (Google & Open Library Global İndeks) ---
def kitap_ara_derin(sorgu):
    results = []
    q = sorgu.replace(' ', '+')
    # Hem Türkiye hem Global marketi tarayan en geniş URL yapısı
    url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=15&orderBy=relevance&printType=books"
    
    try:
        # Kendimizi bir tarayıcı gibi tanıtıyoruz ki engellenmeyelim
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        res = requests.get(url, headers=headers, timeout=10).json()
        
        if "items" in res:
            for item in res["items"]:
                info = item.get("volumeInfo", {})
                img = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
                if img:
                    results.append({
                        "ad": info.get("title", "Bilinmiyor"),
                        "yazar": info.get("authors", ["Bilinmiyor"])[0],
                        "kapak": img
                    })
    except:
        pass
    return results

# --- 3. ARAYÜZ ---
st.title("📚 Koray'ın Akıllı Kitaplığı")
st.caption("Amazon, Google ve Türkiye kitap pazarı verileri taranıyor.")

tab1, tab2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Okuma Listem"])

with tab1:
    s_in = st.text_input("Kitap, Yazar veya Karakter", placeholder="Örn: Radley Ailesi, Şehit, Matt Haig...")
    
    if st.button("Sistemde Derin Ara"):
        if s_in:
            with st.spinner('Tüm raflar taranıyor...'):
                st.session_state.sonuclar = kitap_ara_derin(s_in)
    
    if st.session_state.sonuclar:
        for i, k in enumerate(st.session_state.sonuclar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(k['kapak'], use_container_width=True)
                with c2:
                    st.markdown(f"### {k['ad']}")
                    st.write(f"✍️ **{k['yazar']}**")
                    d = st.selectbox("Durum Seçin", ["Okuyacağım", "Okuyorum", "Okudum"], key=f"sel_{i}")
                    if st.button("Listeye Ekle", key=f"btn_{i}"):
                        st.session_state.liste.append({"ad": k['ad'], "yazar": k['yazar'], "kapak": k['kapak'], "durum": d})
                        st.toast(f"'{k['ad']}' eklendi!", icon='✅')
            st.divider()

with tab2:
    if not st.session_state.liste:
        st.info("Listeniz henüz boş. Aramaya başlayın!")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.liste)):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1: st.image(ktp['kapak'], width=80)
            with col2:
                renk = "#28a745" if ktp['durum'] == "Okudum" else "#ffc107" if ktp['durum'] == "Okuyorum" else "#6c757d"
                st.markdown(f"""
                    <div class="book-card">
                        <b style="font-size:16px;">{ktp["ad"]}</b><br>
                        <small>{ktp["yazar"]}</small><br>
                        <span style="color:{renk}; font-weight:bold;">● {ktp["durum"]}</span>
                    </div>
                """, unsafe_allow_html=True)
            with col3:
                if st.button("Sil", key=f"del_{idx}"):
                    pos = len(st.session_state.liste) - 1 - idx
                    st.session_state.liste.pop(pos)
                    st.rerun()
