import streamlit as st
import requests

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Koray'ın Kitaplığı", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; background-color: #007bff; color: white; height: 3.5em; font-weight: bold; }
    .book-card { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border-left: 6px solid #007bff; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

if 'liste' not in st.session_state: st.session_state.liste = []
if 'ara_sonuc' not in st.session_state: st.session_state.ara_sonuc = []

# --- 2. TÜRKİYE ODAKLI ARAMA MOTORU ---
def kitap_ara_yerel(sorgu):
    results = []
    q = sorgu.replace(' ', '+')
    
    # Google'ı Türkiye sonuçlarına zorlayan özel URL
    # 'langRestrict=tr' ve 'lr=lang_tr' parametrelerini ekledik
    url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=20&country=TR&langRestrict=tr&lr=lang_tr&orderBy=relevance"
    
    try:
        # Sunucuyu gerçek bir Chrome tarayıcı gibi tanıtıyoruz
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        res = requests.get(url, headers=headers, timeout=10).json()
        
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
        
        # Eğer Türkçe sonuç çıkmazsa (Radley Ailesi gibi spesifik durumlar için) 
        # yazar adıyla global bir arama daha ekle
        if len(results) < 3:
            url_global = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=10"
            res_global = requests.get(url_global, headers=headers, timeout=10).json()
            if "items" in res_global:
                for item in res_global["items"]:
                    inf = item.get("volumeInfo", {})
                    img = inf.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
                    if img:
                        results.append({"isim": inf.get("title"), "yazar": inf.get("authors", [""])[0], "kapak": img})
                        
    except: pass
    return results

# --- 3. ARAYÜZ ---
st.title("📚 Koray Bey'in Kitaplığı")
tab1, tab2 = st.tabs(["🔍 Kitap Bul", "📋 Okuma Listem"])

with tab1:
    s = st.text_input("Kitap veya Yazar Adı Yazın", placeholder="Örn: Radley Ailesi")
    if st.button("Derin Ara"):
        if s:
            with st.spinner('Türkiye rafları taranıyor...'):
                st.session_state.ara_sonuc = kitap_ara_yerel(s)
    
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
                        st.toast(f"'{k['isim']}' listeye eklendi!")

with tab2:
    if not st.session_state.liste:
        st.info("Kütüphaneniz henüz boş.")
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
                    pos = len(st.session_state.liste) - 1 - idx
                    st.session_state.liste.pop(pos)
                    st.rerun()
