import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Hafıza (Listeyi tutmak için)
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []

# 3. KESİN ÇÖZÜM: Kısıtlamaya Takılmayan Arama Fonksiyonu
def kitap_ara_kesin(sorgu):
    results = []
    # Google Books kısıtlamasını aşmak için parametreleri sadeleştiriyoruz
    url = f"https://www.googleapis.com/books/v1/volumes?q={sorgu.replace(' ', '+')}&maxResults=8"
    
    try:
        # Tarayıcı gibi davranarak engellenmeyi önlüyoruz
        res = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}).json()
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
    
    # Eğer Google sonuç vermezse OpenLibrary yedek olarak devreye girer
    if not results:
        try:
            ol_url = f"https://openlibrary.org/search.json?q={sorgu.replace(' ', '+')}&limit=5"
            ol_res = requests.get(ol_url, timeout=10).json()
            for doc in ol_res.get("docs", []):
                cover_id = doc.get("cover_i")
                if cover_id:
                    results.append({
                        "title": doc.get("title", "Bilinmiyor"),
                        "author": doc.get("author_name", ["Bilinmiyor"])[0],
                        "cover": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                    })
        except:
            pass
    return results

# 4. Arayüz Tasarımı
st.title("📚 Dijital Kütüphanem")

tab_ekle, tab_liste = st.tabs(["🔍 Kitap Ara & Ekle", "📋 Kütüphanem"])

with tab_ekle:
    st.subheader("Kitap İsmi Yazın")
    sorgu = st.text_input("", placeholder="Örn: Simyacı, Radley Ailesi...")
    
    if st.button("Sistemde Ara", use_container_width=True):
        if sorgu:
            with st.spinner('Arama yapılıyor...'):
                st.session_state.bulunanlar = kitap_ara_kesin(sorgu)
    
    # Arama sonuçlarını göster
    if 'bulunanlar' in st.session_state and st.session_state.bulunanlar:
        st.write("---")
        for i, b in enumerate(st.session_state.bulunanlar):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(b['cover'], width=100)
            with col2:
                st.markdown(f"**{b['title']}**")
                st.caption(f"Yazar: {b['author']}")
                durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"], key=f"sel_{i}")
                if st.button("Kütüphaneye Ekle", key=f"add_{i}"):
                    st.session_state.kitap_listesi.append({
                        "title": b['title'], "author": b['author'], 
                        "cover": b['cover'], "status": durum
                    })
                    st.success(f"'{b['title']}' eklendi!")
            st.divider()

with tab_liste:
    if not st.session_state.kitap_listesi:
        st.info("Kütüphaneniz şu an boş.")
    else:
        for idx, k in enumerate(reversed(st.session_state.kitap_listesi)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.image(k['cover'], width=70)
            with c2:
                st.markdown(f"**{k['title']}**")
                st.caption(f"{k['author']} | {k['status']}")
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    pos = len(st.session_state.kitap_listesi) - 1 - idx
                    st.session_state.kitap_listesi.pop(pos)
                    st.rerun()
            st.divider()
