import streamlit as st
import requests

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Koray'ın Kitaplığı", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; background-color: #007bff; color: white; height: 3.5em; font-weight: bold; }
    .book-card { background: white; padding: 15px; border-radius: 15px; border-left: 6px solid #007bff; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 10px; }
    .search-box { background-color: #f1f3f6; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

if 'liste' not in st.session_state: st.session_state.liste = []
if 'ara_sonuclar' not in st.session_state: st.session_state.ara_sonuclar = []

# --- 2. AKILLI ARAMA MOTORU (Barkod, İsim ve Yazar) ---
def kitap_ara_derin(sorgu):
    results = []
    # Eğer sadece rakamlardan oluşuyorsa Barkod (ISBN) araması yap
    is_isbn = sorgu.replace("-", "").replace(" ", "").isdigit()
    prefix = "isbn:" if is_isbn else ""
    
    # Arama terimini temizle ve hazırla
    q = f"{prefix}{sorgu.replace(' ', '+')}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=12&orderBy=relevance"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10).json()
        
        if "items" in res:
            for item in res["items"]:
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
    return results

# --- 3. ARAYÜZ ---
st.title("📚 Profesyonel Kitap Takip")

tab1, tab2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Benim Listem"])

with tab1:
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    st.subheader("Arama Yapın")
    s_input = st.text_input("Barkod (978...), Kitap Adı veya Yazar Adı girin", placeholder="Örn: Radley Ailesi veya Matt Haig")
    
    if st.button("Kütüphaneleri Tara"):
        if s_input:
            with st.spinner('Derin arama yapılıyor...'):
                st.session_state.ara_sonuclar = kitap_ara_derin(s_input)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.ara_sonuclar:
        st.write(f"🔍 {len(st.session_state.ara_sonuclar)} kitap bulundu:")
        for i, k in enumerate(st.session_state.ara_sonuclar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(k['kapak'], use_container_width=True)
                with c2:
                    st.markdown(f"### {k['ad']}")
                    st.write(f"👤 **Yazar:** {k['yazar']}")
                    d = st.selectbox("Okuma Durumu", ["Okuyacağım", "Okuyorum", "Okudum"], key=f"d_{i}")
                    if st.button("Listeme Kaydet", key=f"b_{i}"):
                        st.session_state.liste.append({**k, "durum": d})
                        st.toast(f"'{k['ad']}' başarıyla eklendi!")
            st.divider()

with tab2:
    if not st.session_state.liste:
        st.info("Listeniz henüz boş. Birkaç kitap ekleyerek başlayın!")
    else:
        # En son eklenen en üstte görünsün
        for idx, ktp in enumerate(reversed(st.session_state.liste)):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.image(ktp['kapak'], width=70)
            with col2:
                renk = "#28a745" if ktp['durum'] == "Okudum" else "#ffc107" if ktp['durum'] == "Okuyorum" else "#6c757d"
                st.markdown(f"""
                    <div class="book-card">
                        <b style='font-size:16px;'>📖 {ktp["ad"]}</b><br>
                        <small>✍️ {ktp["yazar"]}</small><br>
                        <span style='color:{renk}; font-weight:bold;'>● {ktp["durum"]}</span>
                    </div>
                """, unsafe_allow_html=True)
            with col3:
                if st.button("🗑️", key=f"del_{idx}"):
                    pos = len(st.session_state.liste) - 1 - idx
                    st.session_state.liste.pop(pos)
                    st.rerun()
