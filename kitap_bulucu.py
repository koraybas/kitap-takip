import streamlit as st
import requests

# --- 1. AYARLAR & TASARIM ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; background-color: #007bff; color: white; height: 3.5em; font-weight: bold; }
    .book-card { background: white; padding: 12px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'koleksiyon' not in st.session_state: st.session_state.koleksiyon = []
if 'ara_sonuclar' not in st.session_state: st.session_state.ara_sonuclar = []

# --- 2. TÜRKİYE ODAKLI ARAMA MOTORU ---
def kitap_ara_turkiye(sorgu):
    results = []
    # Türkçe sonuçları ve Türkiye baskılarını zorlayan parametreler
    q = sorgu.replace(' ', '+')
    # country=TR ve langRestrict=tr ekleyerek yerel baskılara öncelik veriyoruz
    url = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=15&country=TR&langRestrict=tr&orderBy=relevance"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10).json()
        
        if "items" in res:
            for item in res["items"]:
                inf = item.get("volumeInfo", {})
                img_data = inf.get("imageLinks", {})
                # Resim yoksa standart bir kitap görseli koy
                img = img_data.get("thumbnail") or img_data.get("smallThumbnail")
                if not img:
                    img = "https://via.placeholder.com/150x220?text=Kapak+Bulunamadi"
                
                img = img.replace("http://", "https://")
                results.append({
                    "ad": inf.get("title", "Bilinmiyor"),
                    "yazar": inf.get("authors", ["Bilinmiyor"])[0],
                    "kapak": img
                })
        
        # Eğer Türkçe sonuç azsa, global aramayı da altına ekle (Hiçbir şey kaçmasın)
        if len(results) < 5:
            url_global = f"https://www.googleapis.com/books/v1/volumes?q={q}&maxResults=5"
            res_g = requests.get(url_global, timeout=10).json()
            for item in res_g.get("items", []):
                inf = item.get("volumeInfo", {})
                img = inf.get("imageLinks", {}).get("thumbnail", "https://via.placeholder.com/150x220?text=Kapak+Yok").replace("http://", "https://")
                results.append({"ad": inf.get("title"), "yazar": inf.get("authors", [""])[0], "kapak": img})
                
    except: pass
    return results

# --- 3. ARAYÜZ ---
st.title("📚 Koray Bey'in Kitaplığı")
tab1, tab2 = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Okuma Listem"])

with tab1:
    s_in = st.text_input("Kitap veya Yazar Adı", placeholder="Örn: Radley Ailesi")
    if st.button("Türkiye Veritabanında Ara"):
        if s_in:
            with st.spinner('Türkiye rafları taranıyor...'):
                st.session_state.ara_sonuclar = kitap_ara_turkiye(s_in)

    if st.session_state.ara_sonuclar:
        for i, k in enumerate(st.session_state.ara_sonuclar):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], use_container_width=True)
                with c2:
                    st.markdown(f"**{k['ad']}**")
                    st.caption(f"Yazar: {k['yazar']}")
                    d_sec = st.selectbox("Durum", ["Okuyacağım", "Okuyorum", "Okudum"], key=f"d_{i}")
                    if st.button("Listeye Ekle", key=f"b_{i}"):
                        st.session_state.koleksiyon.append({"ad": k['ad'], "yazar": k['yazar'], "kapak": k['kapak'], "durum": d_sec})
                        st.success(f"'{k['ad']}' eklendi!")
            st.divider()

with tab2:
    if not st.session_state.koleksiyon:
        st.info("Listeniz henüz boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.koleksiyon)):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1: st.image(ktp['kapak'], width=70)
            with col2:
                renk = "#28a745" if ktp['durum'] == "Okudum" else "#ffc107" if ktp['durum'] == "Okuyorum" else "#6c757d"
                st.markdown(f"""
                    <div class="book-card">
                        <b>{ktp["ad"]}</b><br>
                        <small>{ktp["yazar"]}</small><br>
                        <span style="color:{renk}; font-weight:bold;">● {ktp["durum"]}</span>
                    </div>
                """, unsafe_allow_html=True)
            with col3:
                if st.button("Sil", key=f"del_{idx}"):
                    pos = len(st.session_state.koleksiyon) - 1 - idx
                    st.session_state.koleksiyon.pop(pos)
                    st.rerun()
