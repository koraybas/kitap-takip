import streamlit as st
import sqlite3
import requests
from contextlib import contextmanager

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Güvenli Veritabanı Bağlantısı (OperationalError Çözümü)
@contextmanager
def db_connection():
    # 'timeout' ekleyerek dosya kilitlenmelerini (OperationalError) engelliyoruz
    conn = sqlite3.connect('kutuphanem.db', timeout=10, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS kitaplar 
                        (isim TEXT, yazar TEXT, kapak_url TEXT)''')
        conn.commit()

init_db()

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
            yazar, kapak = get_book_info(yeni_kitap)
            with db_connection() as conn:
                conn.execute("INSERT INTO kitaplar VALUES (?,?,?)", (yeni_kitap, yazar, kapak))
                conn.commit()
            st.success(f"'{yeni_kitap}' eklendi!")
        else:
            st.warning("Lütfen bir isim yazın.")

with tab1:
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kitaplar")
        kitaplar = cursor.fetchall()

    if not kitaplar:
        st.info("Kütüphaneniz boş. Kitap ekleyerek başlayın!")
    else:
        for k in kitaplar:
            st.markdown(f"""
                <div style="display: flex; align-items: center; border: 1px solid #ddd; padding: 12px; border-radius: 15px; margin-bottom: 12px; background-color: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                    <img src="{k[2]}" style="width: 75px; border-radius: 8px; margin-right: 15px;">
                    <div style="flex-grow: 1;">
                        <h4 style="margin: 0; font-size: 16px; color: #1f1f1f;">{k[0]}</h4>
                        <p style="margin: 4px 0 0 0; font-size: 14px; color: #666;">{k[1]}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
