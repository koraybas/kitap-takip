import streamlit as st
import pandas as pd
import sqlite3
import requests

# Sayfa Konfigürasyonu (Mobil Uyumluluk İçin)
st.set_page_config(
    page_title="Kitaplığım",
    page_icon="📚",
    layout="centered", # Mobilde daha iyi ortalar
    initial_sidebar_state="collapsed"
)

# --- MODERN STİL (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
        border: none;
    }
    .book-card {
        background-color: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 5px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VERİTABANI FONKSİYONLARI ---
def init_db():
    conn = sqlite3.connect('kutuphanem.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kitaplar 
                 (isim TEXT, yazar TEXT, tur TEXT, durum TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- ANA MENÜ (MOBİL UYUMLU SEKME) ---
tab1, tab2 = st.tabs(["➕ Kitap Ekle", "📚 Kütüphanem"])

# --- TAB 1: KİTAP EKLE ---
with tab1:
    st.subheader("Yeni Kitap Kaydı")
    with st.container():
        kitap_adi = st.text_input("Kitap Adı", placeholder="Örn: Nutuk")
        yazar_adi = st.text_input("Yazar", placeholder="Örn: Mustafa Kemal Atatürk")
        tur = st.selectbox("Tür", ["Roman", "Tarih", "Kişisel Gelişim", "Bilim", "Diğer"])
        durum = st.radio("Okuma Durumu", ["Okundu", "Okunuyor", "Okunacak"], horizontal=True)
        
        if st.button("Kütüphaneye Kaydet"):
            if kitap_adi and yazar_adi:
                c = conn.cursor()
                c.execute("INSERT INTO kitaplar VALUES (?,?,?,?)", (kitap_adi, yazar_adi, tur, durum))
                conn.commit()
                st.success(f"'{kitap_adi}' başarıyla eklendi! 🎉")
            else:
                st.warning("Lütfen kitap ve yazar adını boş bırakmayın.")

# --- TAB 2: KÜTÜPHANEM ---
with tab2:
    st.subheader("Kitap Listem")
    c = conn.cursor()
    c.execute("SELECT * FROM kitaplar")
    veriler = c.fetchall()
    
    if not veriler:
        st.info("Kütüphaneniz henüz boş. Kitap ekleyerek başlayın!")
    else:
        for v in veriler:
            # Her kitap için bir "kart" tasarımı
            with st.container():
                st.markdown(f"""
                <div class="book-card">
                    <h3 style='margin:0; color:#1f1f1f;'>📖 {v[0]}</h3>
                    <p style='margin:5px 0; color:#555;'>👤 <b>Yazar:</b> {v[1]}</p>
                    <span style='background:#e9ecef; padding:2px 8px; border-radius:5px; font-size:0.8em;'>{v[2]}</span>
                    <span style='margin-left:10px; color:{"#28a745" if v[3]=="Okundu" else "#ffc107"}; font-weight:bold;'>• {v[3]}</span>
                </div>
                """, unsafe_allow_html=True)
