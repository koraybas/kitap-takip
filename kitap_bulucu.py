import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Veri Saklama Alanı (Hata vermeyen hafıza yöntemi)
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []

# 3. Google Books API (Gelişmiş Hata Ayıklamalı)
def kitap_ara(kitap_adi):
    default_img = "https://via.placeholder.com/150x220?text=Resim+Yok"
    try:
        query = kitap_adi.replace(' ', '+')
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        response = requests.get(url, timeout=10).json()
        
        # Eğer sonuç yoksa hata vermek yerine boş dön
        if "items" not in response:
            return "Bilinmiyor", default_img
            
        info = response["items"][0]["volumeInfo"]
        yazar = info.get("authors", ["Bilinmiyor"])[0]
        kapak = info.get("imageLinks", {}).get("thumbnail", default_img).replace("http://", "https://")
        return yazar, kapak
    except Exception:
        return "Bilinmiyor", default_img

# 4. Arayüz Tasarımı
st.title("📚 Dijital Kitaplığım")

# Menü Sekmeleri
sekme_liste, sekme_ekle = st.tabs(["📋 Listem", "➕ Kitap Ekle"])

with sekme_ekle:
    st.subheader("Yeni Kitap Kaydı")
    with st.form("ekleme_formu", clear_on_submit=True):
        input_isim = st.text_input("Kitap İsmi")
        submit_btn = st.form_submit_button("Kütüphaneye Ekle")
        
        if submit_btn and input_isim:
            yazar, kapak = kitap_ara(input_isim)
            # Veriyi hafızaya ekle
            st.session_state.kitap_listesi.append({
                "isim": input_isim,
                "yazar": yazar,
                "kapak": kapak
            })
            st.success(f"'{input_isim}' başarıyla listeye alındı!")

with sekme_liste:
    if not st.session_state.kitap_listesi:
        st.info("Listeniz şu an boş. Kitap ekleyerek başlayabilirsiniz.")
    else:
        # Kitapları listele
        for index, kitap in enumerate(reversed(st.session_state.kitap_listesi)):
            col_img, col_text, col_del = st.columns([1, 3, 1])
            
            with col_img:
                st.image(kitap["kapak"], width=80)
            
            with col_text:
                st.subheader(kitap["isim"])
                st.caption(f"Yazar: {kitap['yazar']}")
            
            with col_del:
                # Silme butonu ekledik
                if st.button("Sil", key=f"del_{index}"):
                    # Tersten dizdiğimiz için gerçek indexi hesapla
                    real_index = len(st.session_state.kitap_listesi) - 1 - index
                    st.session_state.kitap_listesi.pop(real_index)
                    st.rerun()
            st.divider()
