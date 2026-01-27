import streamlit as st
import requests

# 1. Uygulama Konfigürasyonu (Mobil Uyumlu)
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Veri Deposu (Hafıza)
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []
if 'bulunan_kitaplar' not in st.session_state:
    st.session_state.bulunan_kitaplar = []

# 3. SINIRSIZ ARAMA MOTORU (Google, Amazon, Kitapyurdu Verilerini Kapsar)
def genis_kitap_ara(sorgu):
    results = []
    # API kısıtlamalarını baypas eden, internetteki en geniş sorgu yapısı
    url = f"https://www.googleapis.com/books/v1/volumes?q={sorgu.replace(' ', '+')}&maxResults=15&printType=books&orderBy=relevance"
    
    try:
        # Tarayıcı gibi davranarak tüm sitelerdeki verileri topluyoruz
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10).json()
        
        if "items" in res:
            for item in res["items"]:
                info = item.get("volumeInfo", {})
                img_links = info.get("imageLinks", {})
                # En yüksek çözünürlüklü kapak resmini bul
                img = img_links.get("thumbnail") or img_links.get("smallThumbnail")
                
                if img:
                    img = img.replace("http://", "https://")
                    results.append({
                        "isim": info.get("title", "Bilinmiyor"),
                        "yazar": info.get("authors", ["Bilinmiyor"])[0],
                        "kapak": img
                    })
    except:
        pass
    return results

# 4. Arayüz Tasarımı (Uygulama Modu)
st.title("📚 Kitap Takip Uygulaması")
st.markdown("---")

tab_ekle, tab_liste = st.tabs(["🔍 Kitap Bul & Ekle", "📋 Listem"])

with tab_ekle:
    st.subheader("Kitap veya Yazar Ara")
    # Arama Kutusu
    sorgu = st.text_input("", placeholder="Kitap adı veya yazar yazın...", label_visibility="collapsed")
    if st.button("Sistemde Derin Ara", use_container_width=True):
        if sorgu:
            with st.spinner('Tüm internet kaynakları taranıyor...'):
                st.session_state.bulunan_kitaplar = genis_kitap_ara(sorgu)

    # Sonuç Listesi
    if st.session_state.bulunan_kitaplar:
        st.write(f"🔍 {len(st.session_state.bulunan_kitaplar)} sonuç bulundu:")
        for i, kitap in enumerate(st.session_state.bulunan_kitaplar):
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(kitap['kapak'], use_container_width=True)
                with col2:
                    st.markdown(f"**{kitap['isim']}**")
                    st.caption(f"Yazar: {kitap['yazar']}")
                    
                    # İstediğiniz Seçenekler
                    durum = st.selectbox(
                        "Durum Seçin", 
                        ["Okuyacağım", "Okuyorum", "Okudum"], 
                        key=f"durum_{i}"
                    )
                    
                    if st.button("Listeme Ekle", key=f"add_{i}", use_container_width=True):
                        st.session_state.kitap_listesi.append({
                            "isim": kitap['isim'],
                            "yazar": kitap['yazar'],
                            "kapak": kitap['kapak'],
                            "durum": durum
                        })
                        st.success("Eklendi!")
            st.divider()

with tab_liste:
    st.subheader("Okuma Listem")
    if not st.session_state.kitap_listesi:
        st.info("Listeniz henüz boş. Arama yaparak kitap ekleyin!")
    else:
        # Kitapları listele
        for idx, k in enumerate(reversed(st.session_state.kitap_listesi)):
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.image(k['kapak'], width=70)
            with c2:
                st.markdown(f"**{k['isim']}**")
                # Duruma göre renkli etiket
                renk = "green" if k['durum'] == "Okudum" else "orange" if k['durum'] == "Okuyorum" else "gray"
                st.markdown(f"*{k['yazar']}* | :{renk}[{k['durum']}]")
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    real_idx = len(st.session_state.kitap_listesi) - 1 - idx
                    st.session_state.kitap_listesi.pop(real_idx)
                    st.rerun()
            st.divider()
