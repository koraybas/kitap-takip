import streamlit as st
import pandas as pd

# Sayfa Ayarları
st.set_page_config(page_title="Koray'ın Kütüphanesi", page_icon="📚")

# Başlık
st.title("📚 Kitap Takip Sistemi")

# Veri girişi için basit bir yapı (Şimdilik hafızada, birazdan Sheets'e bağlayacağız)
if 'kitaplar' not in st.session_state:
    st.session_state.kitaplar = [
        {"isim": "Simyacı", "yazar": "Paulo Coelho", "durum": "Okundu"},
        {"isim": "1984", "yazar": "George Orwell", "durum": "Okunuyor"}
    ]

# YENİ KİTAP EKLEME FORMU (Manuel ve Kesin)
with st.expander("➕ Yeni Kitap Ekle"):
    yeni_ad = st.text_input("Kitap Adı")
    yeni_yazar = st.text_input("Yazar")
    yeni_durum = st.selectbox("Durum", ["Okunacak", "Okunuyor", "Okundu"])
    if st.button("Listeye Ekle"):
        if yeni_ad and yeni_yazar:
            st.session_state.kitaplar.append({"isim": yeni_ad, "yazar": yeni_yazar, "durum": yeni_durum})
            st.success("Kitap başarıyla eklendi!")
            st.rerun()

# LİSTELEME
st.subheader("📋 Kütüphanem")
df = pd.DataFrame(st.session_state.kitaplar)

for index, row in df.iterrows():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{row['isim']}** \n*{row['yazar']}*")
    with col2:
        # Renkli etiketler
        color = "green" if row['durum'] == "Okundu" else "orange" if row['durum'] == "Okunuyor" else "gray"
        st.markdown(f":{color}[{row['durum']}]")
    st.divider()
