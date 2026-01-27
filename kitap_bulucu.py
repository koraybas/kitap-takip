import streamlit as st
import sqlite3
import requests

# 1. Sayfa Ayarları (Hata riskini azaltmak için en başa)
st.set_page_config(page_title="Kitaplığım", page_icon="📚")

# 2. Veritabanı Bağlantısı (Bulut uyumlu)
def get_connection():
    return sqlite3.connect('kutuphanem.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kitaplar 
                 (isim TEXT, yazar TEXT, kapak_url TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. Google'dan Kapak Bulma Fonksiyonu
def get_book_info(book_name):
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={book_name}"
        res = requests.get(url).json()
        if "items" in res:
            info = res["items"][0]["volumeInfo"]
            cover = info.get("imageLinks", {}).get("thumbnail", "https://via.placeholder.com/150x200?text=Kapak+Yok")
            author = info.get("authors", ["Bilinmiyor"])[0]
            return author, cover
    except:
        pass
    return "Bilinmiyor", "https://via.placeholder.com/150x200?text=Kapak+Yok"

# 4. Arayüz Tasarımı
st.title("📚 Dijital Kitaplığım")

menu = st.sidebar.selectbox("Menü", ["Kitaplarımı Gör", "Yeni Kitap Ekle"])

if menu == "Yeni Kitap Ekle":
    st.subheader("Yeni Bir Kitap Ara ve Ekle")
    kitap_adi = st.text_input("Kitap Adı Yazın")
    
    if st.button("Kütüphaneme Ekle"):
        if kitap_adi:
            yazar, kapak = get_book_info(kitap_adi)
            conn = get_connection()
            c = conn.cursor()
            c.execute("INSERT INTO kitaplar VALUES (?,?,?)", (kitap_adi, yazar, kapak))
            conn.commit()
            conn.close()
            st.success(f"'{kitap_adi}' başarıyla eklendi!")
            st.image(kapak, width=150)
        else:
            st.error("Lütfen bir isim yazın.")

else:
    st.subheader("Kütüphanem")
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM kitaplar")
    kitaplar = c.fetchall()
    conn.close()

    if not kitaplar:
        st.info("Kütüphaneniz şu an boş.")
    else:
        # Kitapları mobilde güzel görünen bir ızgara (grid) yapısında göster
        for k in kitaplar:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(k[2], width=120)
            with col2:
                st.markdown(f"### {k[0]}")
                st.markdown(f"**Yazar:** {k[1]}")
            st.divider()
