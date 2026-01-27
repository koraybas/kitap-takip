import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Veri Yönetimi (SQLite yerine Streamlit Session State - Hata Riski Sıfır)
if 'kitaplik' not in st.session_state:
    st.session_state.kitaplik = []

# 3. Google API (Kapak Bulucu)
def get_book_info(book_name):
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={book_name}"
        res = requests.get(url, timeout=5).json()
        if "items" in res:
            volume = res["items"][0]["volumeInfo"]
            author = volume.get("authors", ["Bilinmiyor"])[0]
            cover = volume.get("imageLinks", {}).get("thumbnail", "https://via.placeholder.com/150x200?text=No+Cover")
            return author, cover.replace("http://", "https://")
    except:
        pass
    return "Bilinmiyor", "https://via.placeholder.com/150x200?text=No+Cover"

# 4. Arayüz Tasarımı
st.title("📚 Dijital Kitaplığım")

tab1, tab2 = st.tabs(["📋 Listem", "➕ Kitap Ekle"])

with tab2:
    st.subheader("Yeni Kitap Ekle")
    yeni_kitap = st.text_input("Kitap İsmi", key="input_kitap")
    if st.button("Kaydet"):
        if yeni_kitap:
            with st.spinner('Kitap bilgileri aranıyor...'):
                yazar, kapak = get_book_info(yeni_kitap)
                # Veriyi listeye ekle
                yeni_veri = {"isim": yeni_kitap, "yazar": yazar, "kapak": kapak}
                st.session_state.kitaplik.append(yeni_veri)
                st.success(f"'{yeni_kitap}' listeye eklendi!")
        else:
            st.warning("Lütfen bir isim yazın.")

with tab1:
    if not st.session_state.kitaplik:
        st.info("Kütüphaneniz boş. Kitap ekleyerek başlayın!")
    else:
        # Son ekleneni en üstte göster
        for k in reversed(st.session_state.kitaplik):
            st.markdown(f"""
                <div style="display: flex; align-items: center; border: 1px solid #ddd; padding: 12px; border-radius: 15px; margin-bottom: 12px; background-color: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                    <img src="{k['kapak']}" style="width: 75px; border-radius: 8px; margin-right: 15px;">
                    <div style="flex-grow: 1;">
                        <h4 style="margin: 0; font-size: 16px; color: #1f1f1f;">{k['isim']}</h4>
                        <p style="margin: 4px 0 0 0; font-size: 14px; color: #666;">{k['yazar']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
