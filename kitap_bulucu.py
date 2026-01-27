import streamlit as st
import sqlite3
import requests

# 1. Sayfa Konfigürasyonu
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Veritabanı Fonksiyonları (OperationalError ve Kayıp Veri Engelleyici)
def get_db():
    conn = sqlite3.connect('kutuphanem.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row # Verileri isimle çekebilmek için
    return conn

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS kitaplar (isim TEXT, yazar TEXT, kapak TEXT)')
    conn.commit()
    conn.close()

init_db()

# 3. Google Books API (Görseli Kesin Getirme Ayarlı)
def fetch_book(title):
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={title}"
        res = requests.get(url, timeout=5).json()
        if "items" in res:
            info = res["items"][0]["volumeInfo"]
            author = info.get("authors", ["Bilinmiyor"])[0]
            # Resim yoksa standart bir kapak koy
            cover = info.get("imageLinks", {}).get("thumbnail", "https://via.placeholder.com/150x220?text=Kapak+Yok")
            # Güvenlik için https dönüşümü
            cover = cover.replace("http://", "https://")
            return author, cover
    except:
        pass
    return "Bilinmiyor", "https://via.placeholder.com/150x220?text=Kapak+Yok"

# 4. Arayüz
st.title("📚 Dijital Kütüphanem")

tab1, tab2 = st.tabs(["📖 Kütüphanem", "➕ Yeni Kitap"])

with tab2:
    st.subheader("Kitap Ekle")
    with st.form("add_form", clear_on_submit=True):
        kitap_adi = st.text_input("Kitap İsmi")
        submit = st.form_submit_button("Sisteme Kaydet")
        
        if submit and kitap_adi:
            yazar, kapak = fetch_book(kitap_adi)
            conn = get_db()
            conn.execute("INSERT INTO kitaplar (isim, yazar, kapak) VALUES (?, ?, ?)", (kitap_adi, yazar, kapak))
            conn.commit()
            conn.close()
            st.success(f"'{kitap_adi}' başarıyla kütüphanenize eklendi!")
            st.image(kapak, width=100)

with tab1:
    conn = get_db()
    books = conn.execute("SELECT * FROM kitaplar ORDER BY rowid DESC").fetchall()
    conn.close()

    if not books:
        st.info("Kütüphaneniz henüz boş.")
    else:
        for book in books:
            # HTML Kart Yapısı (Daha stabil görsel gösterimi)
            st.markdown(f"""
                <div style="display: flex; align-items: center; border: 1px solid #e6e6e6; padding: 10px; border-radius: 12px; margin-bottom: 10px; background-color: #ffffff; box-shadow: 2px 2px 8px rgba(0,0,0,0.05);">
                    <img src="{book['kapak']}" style="width: 70px; height: 100px; object-fit: cover; border-radius: 5px; margin-right: 15px;">
                    <div style="flex-grow: 1;">
                        <h4 style="margin: 0; font-size: 16px; color: #333;">{book['isim']}</h4>
                        <p style="margin: 5px 0 0 0; font-size: 14px; color: #666;">{book['yazar']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
