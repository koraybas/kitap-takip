import streamlit as st
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Veri Saklama (Hafıza Yöntemi - SQLite hatalarını engeller)
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []

# 3. Gelişmiş Google Books API
def kitap_verisi_cek(kitap_adi):
    no_cover = "https://via.placeholder.com/150x220?text=Kapak+Yok"
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={kitap_adi.replace(' ', '+')}"
        res = requests.get(url, timeout=10).json()
        
        if "items" in res:
            info = res["items"][0]["volumeInfo"]
            yazar = info.get("authors", ["Bilinmiyor"])[0]
            kapak = info.get("imageLinks", {}).get("thumbnail", no_cover).replace("http://", "https://")
            return yazar, kapak
    except:
        pass
    return "Bilinmiyor", no_cover

# 4. Arayüz
st.title("📚 Dijital Kütüphanem")

tab_liste, tab_ekle = st.tabs(["📋 Kitap Listem", "➕ Yeni Kitap Ekle"])

with tab_ekle:
    st.subheader("Yeni Kayıt Oluştur")
    with st.form("yeni_kitap_formu", clear_on_submit=True):
        isim = st.text_input("Kitap Adı")
        durum = st.selectbox("Okuma Durumu", ["Okunacak", "Okunuyor", "Okundu"])
        submit = st.form_submit_button("Kütüphaneye Kaydet")
        
        if submit and isim:
            with st.spinner('Bilgiler getiriliyor...'):
                yazar, kapak = kitap_verisi_cek(isim)
                # Veriyi listeye ekle
                st.session_state.kitap_listesi.append({
                    "isim": isim,
                    "yazar": yazar,
                    "kapak": kapak,
                    "durum": durum
                })
                st.success(f"'{isim}' başarıyla eklendi!")
                # Eklendiğinde kapağı hemen göster
                st.image(kapak, width=100, caption="Bulunan Kapak")

with tab_liste:
    if not st.session_state.kitap_listesi:
        st.info("Kütüphaneniz boş. Kitap ekleyerek başlayın!")
    else:
        # Kitapları listele (Son eklenen en üstte)
        for idx, kitap in enumerate(reversed(st.session_state.kitap_listesi)):
            # Statüye göre renk belirle
            renk = "#28a745" if kitap['durum'] == "Okundu" else "#ffc107" if kitap['durum'] == "Okunuyor" else "#6c757d"
            
            st.markdown(f"""
                <div style="display: flex; align-items: center; border: 1px solid #ddd; padding: 12px; border-radius: 15px; margin-bottom: 12px; background-color: white;">
                    <img src="{kitap['kapak']}" style="width: 70px; border-radius: 8px; margin-right: 15px;">
                    <div style="flex-grow: 1;">
                        <h4 style="margin: 0; color: #333;">{kitap['isim']}</h4>
                        <p style="margin: 3px 0; color: #666; font-size: 14px;">{kitap['yazar']}</p>
                        <span style="background: {renk}; color: white; padding: 2px 8px; border-radius: 5px; font-size: 12px;">{kitap['durum']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Silme butonu
            if st.button("Bu Kitabı Sil", key=f"btn_{idx}"):
                real_idx = len(st.session_state.kitap_listesi) - 1 - idx
                st.session_state.kitap_listesi.pop(real_idx)
                st.rerun()
            st.divider()
