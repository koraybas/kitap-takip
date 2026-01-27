import streamlit as st
import sqlite3
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Veritabanı Yönetimi
def get_db():
    conn = sqlite3.connect('kutuphanem.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS kitaplar (isim TEXT, yazar TEXT, kapak TEXT)')
    conn.commit()
    conn.close()

init_db()

# 3. Gelişmiş Google Books API (Index Error Engelleyici)
def fetch_book(title):
    no_cover = "https://via.placeholder.com/150x220?text=Kapak+Yok"
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={title}"
        res = requests.get(url, timeout=5).json()
        
        # Eğer sonuç listesi boşsa (Index Error'un sebebi burasıdır)
        if "items" not in res or len(res["items"]) == 0:
            return "Bilinmiyor", no_cover
            
        info = res["items"][0]["volumeInfo"]
        author = info.get("authors", ["Bilinmiyor"])[0]
        cover = info.get("imageLinks", {}).get("thumbnail", no_cover)
        return author, cover.replace("http://", "https://")
    except Exception as e:
        return "Hata", no_cover

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
            st.success(f"'{kitap_adi}' kaydedildi!")

with tab1:
    conn = get_db()
    books = conn.execute("SELECT * FROM kitaplar ORDER BY rowid DESC").fetchall()
    conn.close()

    if not books:
        st.info("Kütüphaneniz henüz boş.")
    else:
        for book in books:
            st.markdown(f"""
                <div style="display: flex; align-items: center; border: 1px solid #eee; padding: 12px; border-radius: 12px; margin-bottom: 12px; background-color: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <img src="{book['kapak']}" style="width: 70px; height: 100px; object-fit: cover; border-radius: 6px; margin-right: 15px;">
                    <div style="flex-grow: 1;">
                        <h4 style="margin: 0; font-size: 16px;">{book['isim']}</h4>
                        <p style="margin: 5px 0 0 0; font-size: 14px; color: #777;">{book['yazar']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
