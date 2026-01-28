import streamlit as st
import requests

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Koray'ın Kitaplığı", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; background-color: #007bff; color: white; height: 3.5em; font-weight: bold; }
    .book-card { background: white; padding: 15px; border-radius: 15px; border-left: 6px solid #007bff; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 10px; }
    #barcode-scanner { width: 100%; border-radius: 15px; overflow: hidden; border: 2px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

if 'koleksiyon' not in st.session_state: st.session_state.koleksiyon = []
if 'ara_sonuclar' not in st.session_state: st.session_state.ara_sonuclar = []

# --- 2. HİBRİT ARAMA MOTORU ---
def kitap_ara(q, mod="text"):
    results = []
    prefix = "isbn:" if mod == "isbn" else ""
    url = f"https://www.googleapis.com/books/v1/volumes?q={prefix}{q.replace(' ', '+')}&maxResults=15"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10).json()
        if "items" in res:
            for item in res["items"]:
                inf = item.get("volumeInfo", {})
                img = inf.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
                results.append({
                    "ad": inf.get("title", "Bilinmiyor"),
                    "yazar": inf.get("authors", ["Bilinmiyor"])[0],
                    "kapak": img if img else "https://via.placeholder.com/150x220?text=Kapak+Yok"
                })
    except: pass
    return results

# --- 3. ARAYÜZ ---
st.title("📚 Akıllı Kitap Takip Sistemi")

tab1, tab2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Listem"])

with tab1:
    # --- BARKOD & İSİM GİRİŞİ ---
    search_val = st.text_input("Kitap Adı, Yazar veya Barkod Yazın", placeholder="Örn: Radley Ailesi veya 978...")
    
    col_a, col_b = st.columns(2)
    with col_a:
        search_mode = st.selectbox("Arama Türü", ["İsim/Yazar", "Barkod (ISBN)"])
    with col_b:
        search_btn = st.button("Sistemde Bul")

    if search_btn and search_val:
        mod = "isbn" if search_mode == "Barkod (ISBN)" else "text"
        with st.spinner('Kitap aranıyor...'):
            st.session_state.ara_sonuclar = kitap_ara(search_val, mod)

    # Sonuçlar
    if st.session_state.ara_sonuclar:
        st.divider()
        for i, k in enumerate(st.session_state.ara_sonuclar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], use_container_width=True)
                with c2:
                    st.markdown(f"**{k['ad']}**")
                    st.caption(f"✍️ {k['yazar']}")
                    d = st.selectbox("Okuma Durumu", ["Okuyacağım", "Okuyorum", "Okudum"], key=f"sel_{i}")
                    if st.button("Kütüphaneye Ekle", key=f"btn_{i}"):
                        st.session_state.koleksiyon.append({**k, "durum": d})
                        st.success("Listeye Eklendi!")

with tab2:
    if not st.session_state.koleksiyon:
        st.info("Kütüphaneniz şu an boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.koleksiyon)):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1: st.image(ktp['kapak'], width=70)
            with col2:
                renk = "#28a745" if ktp['durum'] == "Okudum" else "#ffc107"
                st.markdown(f'<div class="book-card"><b>{ktp["ad"]}</b><br>{ktp["yazar"]}<br><span style="color:{renk};">● {ktp["durum"]}</span></div>', unsafe_allow_html=True)
            with col3:
                if st.button("Sil", key=f"del_{idx}"):
                    st.session_state.koleksiyon.pop(len(st.session_state.koleksiyon)-1-idx)
                    st.rerun()
