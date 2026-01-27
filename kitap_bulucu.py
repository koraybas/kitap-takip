import streamlit as st
import sqlite3
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚")

# Veritabanı
def get_db():
    conn = sqlite3.connect('kutuphanem.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Tablo oluşturma
with get_db() as conn:
    conn.execute('CREATE TABLE IF NOT EXISTS kitaplar (isim TEXT, yazar TEXT, kapak TEXT)')
    conn.commit()

# --- GÜVENLİ VERİ ÇEKME ---
def fetch_book(title):
    default_cover = "https://via.placeholder.com/150x220?text=Kapak+Yok"
    if not title: return None
    
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={title.strip()}"
        res = requests.get(url, timeout=10).json()
        
        # EĞER HİÇBİR ŞEY BULUNAMAZSA (Index Error Engelleyici)
        if "items" not in res or not res["items"]:
            return "Bilinmiyor", default_cover
            
        # İlk sonucu güvenli bir şekilde al
        volume_info = res.get("items", [{}])[0].get("volumeInfo", {})
        author = volume_info.get("authors", ["Bilinmiyor"])[0]
        cover = volume_info.get("imageLinks", {}).get("thumbnail", default_cover)
        
        return author, cover.replace("http://", "https://")
    except Exception:
        return "Bilinmiyor", default_cover

# Arayüz
st.title("📚 Dijital Kütüphanem")
t1, t2 = st.tabs(["📋 Listem", "➕ Ekle"])

with t2:
    with st.form("ekle_form", clear_on_submit=True):
        kitap = st.text_input("Kitap İsmi")
        submit = st.form_submit_button("Kaydet")
        
        if submit and kitap:
            data = fetch_book(kitap)
            if data:
                yazar, kapak = data
                with get_db() as conn:
                    conn.execute("INSERT INTO kitaplar VALUES (?, ?, ?)", (kitap, yazar, kapak))
                    conn.commit()
                st.success(f"{kitap} eklendi!")

with t1:
    with get_db() as conn:
        books = conn.execute("SELECT * FROM kitaplar ORDER BY rowid DESC").fetchall()
    
    if not books:
        st.info("Kütüphane boş.")
    else:
        for b in books:
            st.markdown(f"""
                <div style="display: flex; align-items: center; border: 1px solid #ddd; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                    <img src="{b['kapak']}" style="width: 60px; height: 90px; border-radius: 5px; margin-right: 15px;">
                    <div>
                        <h4 style="margin:0;">{b['isim']}</h4>
                        <p style="margin:0; color: gray;">{b['yazar']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
