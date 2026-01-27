import streamlit as st
import sqlite3
import requests

# 1. Sayfa Ayarları (Hata riskini en aza indirir)
st.set_page_config(page_title="Kitaplığım", page_icon="📚")

# 2. Veritabanı ve Bağlantı (Her seferinde taze bağlantı)
def init_db():
    conn = sqlite3.connect('kutuphanem.db', check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS kitaplar (isim TEXT, yazar TEXT, kapak_url TEXT)')
    conn.commit()
    conn.close()

init_db()

# 3. Google API (Görsel hatasını önleyen en temiz URL çekici)
def get_book_info(book_name):
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={book_name}"
        res = requests.get(url, timeout=5).json()
        if "items" in res:
            volume = res["items"][0]["volumeInfo"]
            author = volume.get("authors", ["Bilinmiyor"])[0]
            # Resim yoksa standart bir görsel
            cover = volume.get("imageLinks", {}).get("thumbnail", "https://via.placeholder.com/150x200?text=No+Cover")
            # En kritik nokta: http'yi https'e çeviriyoruz
            cover = cover.replace("http://", "https://")
            return author, cover
    except:
        pass
    return "Bilinmiyor", "https://via.placeholder.com/150x200?text=No+Cover"

# 4. Arayüz
st.title("📚 Dijital Kitaplığım")

tab1, tab2 = st.tabs(["📋 Listem", "➕ Kitap Ekle"])

with tab2:
    st.subheader("Yeni Kitap Ekle")
    yeni_kitap = st.text_input("Kitap İsmi")
    if st.button("Kaydet"):
        if yeni_kitap:
            yazar, kapak = get_book_info(yeni_kitap)
            conn = sqlite3.connect('kutuphanem.db')
            conn.execute("INSERT INTO kitaplar VALUES (?,?,?)", (yeni_kitap, yazar, kapak))
            conn.commit()
            conn.close()
            st.success(f"{yeni_kitap} başarıyla listeye eklendi!")
        else:
            st.error("Lütfen bir isim yazın.")

with tab1:
    conn = sqlite3.connect('kutuphanem.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kitaplar")
    kitaplar = cursor.fetchall()
    conn.close()

    if not kitaplar:
        st.info("Kütüphaneniz şu an boş. Bir kitap ekleyin!")
    else:
        for k in kitaplar:
            # DİKKAT: st.image kullanmıyoruz! 
            # Doğrudan HTML kullanarak Streamlit'in depolama hatasını baypas ediyoruz.
            st.markdown(f"""
                <div style="display: flex; align-items: center; border: 1px solid #ddd; padding: 10px; border-radius: 12px; margin-bottom: 10px; background-color: white;">
                    <img src="{k[2]}" style="width: 70px; border-radius: 8px; margin-right: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                    <div style="flex-grow: 1;">
                        <h4 style="margin: 0; font-size: 16px; color: #333;">{k[0]}</h4>
                        <p style="margin: 5px 0 0 0; font-size: 14px; color: #666;">{k[1]}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
