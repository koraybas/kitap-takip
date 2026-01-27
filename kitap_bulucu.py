import streamlit as st
import sqlite3
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚")

# 2. Veritabanı (Bağlantıyı her işlemde taze açalım)
def init_db():
    conn = sqlite3.connect('kutuphanem.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS kitaplar (isim TEXT, yazar TEXT, kapak_url TEXT)')
    conn.commit()
    conn.close()

init_db()

# 3. Google API (Kapak bulucu)
def get_book_info(book_name):
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={book_name}"
        res = requests.get(url, timeout=5).json()
        if "items" in res:
            volume = res["items"][0]["volumeInfo"]
            author = volume.get("authors", ["Bilinmiyor"])[0]
            # Resim yoksa standart bir ikon koyalım
            cover = volume.get("imageLinks", {}).get("thumbnail", "https://via.placeholder.com/150x200?text=Kapak+Yok")
            # Güvenli bağlantı (https) zorlaması
            cover = cover.replace("http://", "https://")
            return author, cover
    except:
        pass
    return "Bilinmiyor", "https://via.placeholder.com/150x200?text=Kapak+Yok"

# 4. Arayüz
st.title("📚 Dijital Kitaplığım")

# Üst menü (Sekmeler)
sekme1, sekme2 = st.tabs(["📋 Listem", "➕ Kitap Ekle"])

with sekme2:
    st.subheader("Yeni Kayıt")
    yeni_isim = st.text_input("Kitap Adı")
    if st.button("Kaydet"):
        if yeni_isim:
            yazar, kapak = get_book_info(yeni_isim)
            conn = sqlite3.connect('kutuphanem.db')
            conn.execute("INSERT INTO kitaplar VALUES (?,?,?)", (yeni_isim, yazar, kapak))
            conn.commit()
            conn.close()
            st.success(f"{yeni_isim} eklendi!")
        else:
            st.error("Bir isim yazmalısınız.")

with sekme1:
    conn = sqlite3.connect('kutuphanem.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kitaplar")
    kitaplar = cursor.fetchall()
    conn.close()

    if not kitaplar:
        st.info("Kütüphane şu an boş.")
    else:
        for k in kitaplar:
            # En sağlam mobil yerleşim: İki sütun
            col1, col2 = st.columns([1, 3])
            with col1:
                # Use_container_width=True mobilde daha iyi sonuç verir
                st.image(k[2], width=80) 
            with col2:
                st.subheader(k[0]) # Kitap Adı
                st.caption(f"Yazar: {k[1]}") # Yazar Adı
            st.divider()
