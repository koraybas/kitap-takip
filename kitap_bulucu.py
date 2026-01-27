import streamlit as st

# 1. Sayfa Ayarları
st.set_page_config(page_title="Koray'ın Kitaplığı", page_icon="📚", layout="centered")

# 2. Veri Deposu (Hafıza)
if 'kitap_listesi' not in st.session_state:
    st.session_state.kitap_listesi = []

# 3. Arayüz Tasarımı
st.title("📚 Dijital Kütüphanem")
st.markdown("---")

# 4. Kitap Ekleme Bölümü (Engellenme Riski Sıfır)
with st.container():
    st.subheader("➕ Yeni Kitap Ekle")
    col1, col2 = st.columns(2)
    
    with col1:
        kitap_adi = st.text_input("Kitap Adı", placeholder="Örn: Simyacı")
        yazar_adi = st.text_input("Yazar", placeholder="Örn: Paulo Coelho")
    
    with col2:
        durum = st.selectbox("Okuma Durumu", ["Okunacak", "Okunuyor", "Okundu"])
        kapak_link = st.text_input("Kapak Resim Linki (Opsiyonel)", placeholder="https://...")

    if st.button("Kütüphaneye Kaydet", use_container_width=True):
        if kitap_adi and yazar_adi:
            # Resim linki boşsa varsayılan bir görsel koy
            resim = kapak_link if kapak_link else "https://via.placeholder.com/150x220?text=Kitap+Kapak"
            
            st.session_state.kitap_listesi.append({
                "title": kitap_adi,
                "author": yazar_adi,
                "status": durum,
                "cover": resim
            })
            st.success(f"'{kitap_adi}' listeye eklendi!")
            st.rerun()
        else:
            st.error("Lütfen Kitap ve Yazar adını doldurun.")

st.markdown("---")

# 5. Kütüphane Listesi
st.subheader("📋 Kütüphanem")

if not st.session_state.kitap_listesi:
    st.info("Henüz kitap eklemediniz.")
else:
    # Kitapları kartlar halinde göster
    for idx, kitap in enumerate(reversed(st.session_state.kitap_listesi)):
        with st.container():
            c1, c2, c3 = st.columns([1, 3, 1])
            with c1:
                st.image(kitap['cover'], width=80)
            with c2:
                st.markdown(f"### {kitap['title']}")
                st.write(f"**Yazar:** {kitap['author']}")
                
                # Duruma göre renkli etiket
                renk = "green" if kitap['status'] == "Okundu" else "orange" if kitap['status'] == "Okunuyor" else "gray"
                st.markdown(f"**Durum:** :{renk}[{kitap['status']}]")
            
            with c3:
                if st.button("Sil", key=f"del_{idx}"):
                    # Listeden silme
                    gercek_index = len(st.session_state.kitap_listesi) - 1 - idx
                    st.session_state.kitap_listesi.pop(gercek_index)
                    st.rerun()
        st.divider()
