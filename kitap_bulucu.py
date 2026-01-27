import streamlit as st
import pandas as pd
import sqlite3
import requests

# Sayfa Ayarları
st.set_page_config(page_title="Dijital Kitaplığım", page_icon="📚", layout="centered")

# --- MODERN STİL (Gelişmiş Kart Görünümü) ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .book-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        display: flex;
        flex-direction: row;
        align-items: center;
    }
    .book-info { margin-left: 20px; flex-grow: 1; }
    .book-cover { border-radius: 8px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- VERİTABANI VE API FONKSİYONLARI ---
def init_db():
    conn = sqlite3.connect('kutuphanem.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kitaplar 
                 (isim TEXT, yazar TEXT, tur TEXT, durum TEXT, kapak_url TEXT)''')
    conn.commit()
    return conn

def get_book_details(kitap_adi):
    # Google Books API'den kapak ve yazar bilgisi çeker
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={kitap_adi}"
        response = requests.get(url).json()
        if "items" in response:
            item = response["items"][0]["volumeInfo"]
            kapak = item.get("imageLinks", {}).get("thumbnail", "https://via.placeholder.com/128x192?text=Kapak+Yok")
            yazar = item.get("authors", ["Bilinmiyor"])[0]
            return yazar, kapak
    except:
        pass
    return "Bilinmiyor", "https://via.placeholder.com/128x192?text=Kapak+Yok"

conn = init_db()

# --- ARAYÜZ ---
st.title("📚 Dijital Kitaplığım")
tab1, tab2 = st.tabs(["➕ Yeni Kitap", "📖 Kütüphaneyi Gez"])

with tab1:
    with st.form("ekleme_formu"):
        isim = st.text_input("Kitap Adı")
        submit = st.form_submit_button("Bilgileri Getir ve Kaydet")
        
        if submit and isim:
            yazar, kapak = get_book_details(isim)
            c = conn.cursor()
            c.execute("INSERT INTO kitaplar VALUES (?,?,?,?,?)", (isim, yazar, "Genel", "Okunacak", kapak))
            conn.commit()
            st.success(f"'{isim}' kütüphaneye eklendi!")

with tab2:
    c = conn.cursor()
    c.execute("SELECT * FROM kitaplar")
    kitaplar = c.fetchall()
    
    for k in kitaplar:
        # Kart Tasarımı
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(k[4], width=100) # Kapak resmi
        with col2:
            st.subheader(k[0]) # Kitap adı
            st.write(f"**Yazar:** {k[1]}")
            st.write(f"**Durum:** {k[3]}")
        st.divider()
