import streamlit as st
import requests

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# --- 2. MODERN STİL (Sizin Tasarımınız) ---
st.markdown("""
    <style>
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

if 'kutuphane' not in st.session_state:
    st.session_state.kutuphane = []

# --- 3. ENGEL TANIMAYAN ARAMA MOTORU (OpenLibrary & Google Hibrit) ---
def kitap_ara_sorgusuz_sualsiz(sorgu):
    results = []
    q = sorgu.replace(' ', '+')
    
    # İLK DENEME: OpenLibrary (Kısıtlama yoktur, her şeyi bulur)
    try:
        ol_url = f"https://openlibrary.org/search.json?q={q}&limit=10"
        ol_res = requests.get(ol_url, timeout=10).json()
        for doc in ol_res.get("docs", []):
            cover_id = doc.get("cover_i")
            if cover_id:
                results.append({
                    "isim": doc.get("title", "Bilinmiyor"),
                    "yazar": doc.get("author_name", ["Bilinmiyor"])[0],
                    "kapak": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                })
    except: pass

    # İKİNCİ DENEME (EĞER OLMAYAN VARSA): Google Books (Sadeleştirilmiş Sorgu)
    if len(results) < 3:
        try:
            g_url = f"https://www.googleapis.com/books/v1/volumes?q={q}"
            g_res = requests.get(g_url, timeout=10).json()
            for item in g_res.get("items", []):
                info = item.get("volumeInfo", {})
                img = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
                if img:
                    results.append({
                        "isim": info.get("title", "Bilinmiyor"),
                        "yazar": info.get("authors", ["Bilinmiyor"])[0],
                        "kapak": img
                    })
        except: pass
    return results

# --- 4. ARAYÜZ ---
tab1, tab2 = st.tabs(["🔍 Kitap Bul", "📚 Listem"])

with tab1:
    st.subheader("Kitap veya Yazar Ara")
    s_input = st.text_input("Örn: Simyacı", key="main_search")
    
    if st.button("Derin Ara"):
        if s_input:
            with st.spinner('Kütüphaneler taranıyor...'):
                st.session_state.temp_results = kitap_ara_sorgusuz_sualsiz(s_input)
    
    if 'temp_results' in st.session_state and st.session_state.temp_results:
        for i, k in enumerate(st.session_state.temp_results):
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1: st.image(k['kapak'], width=100)
                with c2:
                    st.markdown(f"**{k['isim']}**")
                    st.caption(f"Yazar: {k['yazar']}")
                    durum = st.selectbox("Durum", ["Okuyacağım", "Okuyorum", "Okundun"], key=f"sel_{i}")
                    if st.button("Ekle", key=f"btn_{i}"):
                        st.session_state.kutuphane.append({"isim": k['isim'], "yazar": k['yazar'], "kapak": k['kapak'], "durum": durum})
                        st.success("Eklendi!")
            st.divider()

with tab2:
    if not st.session_state.kutuphane:
        st.info("Listeniz boş.")
    else:
        for idx, ktp in enumerate(reversed(st.session_state.kutuphane)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1: st.image(ktp['kapak'], width=70)
            with c2:
                renk = "#28a745" if ktp['durum'] == "Okundun" else "#ffc107"
                st.markdown(f"""<div class="book-card"><h3>📖 {ktp['isim']}</h3><p>{ktp['yazar']}</p><span style='color:{renk};'>• {ktp['durum']}</span></div>""", unsafe_allow_html=True)
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.kutuphane.pop(len(st.session_state.kutuphane)-1-idx)
                    st.rerun()
