import streamlit as st
import sqlite3
import requests

# 1. Sayfa Ayarları
st.set_page_config(page_title="Kitaplığım", page_icon="📚", layout="centered")

# 2. Veritabanı Fonksiyonu
def get_db_connection():
    conn = sqlite3.connect('kutuphanem.db', check_same_thread=False)
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS kitaplar (isim TEXT, yazar TEXT, kapak_url TEXT)')
        conn.commit()

init_db()

# 3. Google Books API (Görsel hatasını önlemek için güvenli link çekme)
def get_book_data(book_name):
    try:
        # Sorguyu temizleyip API'ye gönderiyoruz
        url = f"https://www.googleapis.com/books/v1/volumes?q={book_name.replace(' ', '+')}"
        res = requests.get(url, timeout=5).json()
        if "items" in res:
            info = res["items"][0]["volumeInfo"]
            # HTTP yerine HTTPS linkini zorluyoruz (Güvenlik ve hata önleme için)
            cover = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
            if not cover:
                cover = "https://via.placeholder.com/150x200?text=Kapak+Yok"
            author = info.get("authors", ["Bilinmiyor"])[0]
            return author, cover
    except:
        pass
    return "Bilinmiyor", "https://via.placeholder.com/150x200?text=Kapak+Yok"

# 4. Arayüz
st.title("📱 Mobil Kitaplığım")

menu = st.tabs(["📚 Listem", "➕ Ekle"])

# --- EKLEME SEKMESİ ---
with menu[1]:
    st.subheader("Yeni Kitap")
    isim_input = st.text_input("Kitap ismini tam yazın")
    if st.button("Sorgula ve Kaydet"):
        if isim_input:
            yazar, kapak = get_book_data(isim_input)
            with get_db_connection() as conn:
                conn.execute("INSERT INTO kitaplar VALUES (?,?,?)", (isim_input, yazar, kapak))
                conn.commit()
            st.success(f"'{isim_input}' eklendi!")
            st.image(kapak, width=100)

# --- LİSTELEME SEKMESİ ---
with menu[0]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM kitaplar")
        kitaplar = cursor.fetchall()

    if not kitaplar:
        st.info("Henüz kitap eklenmemiş.")
    else:
        for k in kitaplar:
            # st.image yerine HTML kullanarak storage hatasını tamamen eziyoruz
            st.markdown(f"""
            <div style="display: flex; align-items: center; background: white; padding: 10px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #ddd;">
                <img src="{k[2]}" style="width: 70px; border-radius: 5px; margin-right: 15px;">
                <div>
                    <b style="font-size: 16px;">{k[0]}</b><br>
                    <span style="color: gray; font-size: 14px;">{k[1]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
