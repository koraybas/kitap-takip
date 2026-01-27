import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Hafıza (Oturum kapansa da veriler burada tutulur)
if 'kitaplar' not in st.session_state:
    st.session_state.kitaplar = []

# 3. Akıllı Arama Motoru
def kitap_getir(sorgu):
    results = []
    # Google'ın her şeyi gören genel arama parametreleri
    url = f"https://www.googleapis.com/books/v1/volumes?q={sorgu.replace(' ', '+')}&maxResults=10"
    try:
        res = requests.get(url, timeout=10).json()
        if "items" in res:
            for item in res["items"]:
                info = item.get("volumeInfo", {})
                img = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
                if img:
                    results.append({
                        "title": info.get("title", "Bilinmiyor"),
                        "author": info.get("authors", ["Bilinmiyor"])[0],
                        "cover": img
                    })
    except:
        pass
    return results

# 4. Arayüz Tasarımı
st.title("📚 Dijital Kütüphanem")

tab_ara, tab_liste = st.tabs(["🔍 Kitap Ara & Ekle", "📋 Kütüphanem"])

with tab_ara:
    sorgu = st.text_input("Kitap veya Yazar Yazın", placeholder="Örn: Simyacı")
    
    if st.button("Sistemde Ara"):
        if sorgu:
            with st.spinner('Kitaplar aranıyor...'):
                bulunanlar = kitap_getir(sorgu)
                if not bulunanlar:
                    st.error("Aradığınız kitap teknik bir kısıtlamaya takıldı.")
                else:
                    for i, b in enumerate(bulunanlar):
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.image(b['cover'], width=100)
                        with c2:
                            st.markdown(f"**{b['title']}**")
                            st.caption(f"Yazar: {b['author']}")
                            durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"sel_{i}")
                            if st.button("Ekle", key=f"add_{i}"):
                                st.session_state.kitaplar.append({
                                    "title": b['title'], "author": b['author'], 
                                    "cover": b['cover'], "status": durum
                                })
                                st.success("Eklendi!")
                        st.divider()

    # CAN SİMİDİ: Manuel Ekleme (Eğer arama bulamazsa burası hayat kurtarır)
    st.write("---")
    with st.expander("➕ Aradığınız Kitabı Bulamadınız mı? Kendiniz Yazın"):
        m_ad = st.text_input("Kitap Adı")
        m_yazar = st.text_input("Yazar")
        m_durum = st.selectbox("Okuma Durumu", ["Okunacak", "Okunuyor", "Okundu"], key="m_durum")
        if st.button("Manuel Olarak Ekle"):
            if m_ad and m_yazar:
                st.session_state.kitaplar.append({
                    "title": m_ad, "author": m_yazar, 
                    "cover": "https://via.placeholder.com/150x220?text=Manuel+Kayit", 
                    "status": m_durum
                })
                st.success("Kitap kütüphanenize eklendi!")

with tab_liste:
    if not st.session_state.kitaplar:
        st.info("Kütüphaneniz şu an boş.")
    else:
        for idx, k in enumerate(reversed(st.session_state.kitaplar)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.image(k['cover'], width=70)
            with c2:
                st.markdown(f"**{k['title']}**")
                st.caption(f"{k['author']} | {k['status']}")
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.kitaplar.pop(len(st.session_state.kitaplar)-1-idx)
                    st.rerun()
            st.divider()
