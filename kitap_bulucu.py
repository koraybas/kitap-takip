import streamlit as st
import requests
import sqlite3
import pandas as pd
import uuid

# Sayfa ayarları
st.set_page_config(page_title="BookPulse Ultra", page_icon="📚", layout="wide")

# --- BELLEK VE VERİTABANI ---
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

def init_db():
    conn = sqlite3.connect('kutuphanem.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS kitaplar 
                 (id TEXT PRIMARY KEY, title TEXT, author TEXT, date TEXT, durum TEXT, image_url TEXT)''')
    conn.commit()
    conn.close()

def add_to_library(bid, title, author, status, img):
    conn = sqlite3.connect('kutuphanem.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO kitaplar VALUES (?,?,?,?,?,?)", 
              (bid, title, author, "2026", status, img))
    conn.commit()
    conn.close()
    st.toast(f"✅ {title} -> {status} olarak eklendi!")
    st.rerun()

def update_status(bid, new_status):
    conn = sqlite3.connect('kutuphanem.db')
    c = conn.cursor()
    c.execute("UPDATE kitaplar SET durum = ? WHERE id = ?", (new_status, bid))
    conn.commit()
    conn.close()
    st.rerun()

init_db()

# --- HİBRİT ARAMA MOTORU ---
def master_search(q):
    results = []
    # 1. Kaynak: Kitapyurdu
    try:
        ky_res = requests.get(f"https://www.kitapyurdu.com/index.php?route=product/search&filter_name={q}", headers={"User-Agent": "Mozilla/5.0"}, timeout=5, verify=False)
        items = ky_res.text.split('class="product-cr"')[1:6]
        for item in items:
            results.append({
                "id": f"KY_{uuid.uuid4().hex[:5]}", "title": item.split('alt="')[1].split('"')[0],
                "author": item.split('class="author"')[1].split('</span>')[0].split('>')[-1].strip(),
                "img": item.split('src="')[1].split('"')[0], "src": "Kitapyurdu"
            })
    except: pass

    # 2. Kaynak: Amazon/Global
    try:
        amz_url = f"https://www.googleapis.com/books/v1/volumes?q={q.replace(' ','+')}+amazon&maxResults=5"
        amz_res = requests.get(amz_url, verify=False, timeout=5).json()
        for item in amz_res.get('items', []):
            inf = item['volumeInfo']
            results.append({
                "id": f"AMZ_{item['id']}", "title": inf.get('title'),
                "author": ", ".join(inf.get('authors', ['Bilinmiyor'])),
                "img": inf.get('imageLinks', {}).get('thumbnail', ""), "src": "Amazon / Global"
            })
    except: pass
    return results

# --- ARAYÜZ ---
st.title("📚 BookPulse Ultra")

# SIDEBAR
with st.sidebar:
    st.header("📋 Kütüphanem")
    conn = sqlite3.connect('kutuphanem.db')
    df = pd.read_sql_query("SELECT * FROM kitaplar", conn)
    conn.close()
    
    if not df.empty:
        okundu = len(df[df['durum'] == 'Okudum'])
        st.metric("İlerleme", f"{okundu}/{len(df)} Kitap")
        st.progress(okundu/len(df))
        
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Listeyi İndir", data=csv, file_name="kutuphanem.csv")
        st.divider()
        
        for _, row in df.iterrows():
            with st.expander(f"📖 {row['title']}"):
                if row['image_url']: st.image(row['image_url'], width=80)
                # Kütüphanedeki durum değiştirici
                durum_opsiyonlari = ["Okuyacağım", "Okuyorum", "Okudum"]
                mevcut_idx = durum_opsiyonlari.index(row['durum']) if row['durum'] in durum_opsiyonlari else 0
                yeni_durum = st.selectbox("Durum:", durum_opsiyonlari, index=mevcut_idx, key=f"s_{row['id']}")
                
                if yeni_durum != row['durum']:
                    update_status(row['id'], yeni_durum)
                
                if st.button("🗑️ Sil", key=f"d_{row['id']}", use_container_width=True):
                    conn = sqlite3.connect('kutuphanem.db')
                    conn.cursor().execute("DELETE FROM kitaplar WHERE id=?", (row['id'],))
                    conn.commit()
                    conn.close()
                    st.rerun()

# ANA EKRAN
q = st.text_input("Kitap veya Yazar:", placeholder="Aramak istediğiniz kitabı yazın...")
if st.button("🔍 Ara"):
    if q:
        with st.spinner('Taranıyor...'):
            st.session_state.search_results = master_search(q)

if st.session_state.search_results:
    for k in st.session_state.search_results:
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])
            with c1: 
                if k['img']: st.image(k['img'])
            with c2:
                st.subheader(k['title'])
                st.caption(f"Yazar: {k['author']} | 📍 Kaynak: {k['src']}")
                
                # ARAMA BÖLÜMÜNDEKİ YENİ BUTONLAR
                btns = st.columns(3)
                if btns[0].button("⏳ Okuyacağım", key=f"w_{k['id']}", use_container_width=True): 
                    add_to_library(k['id'], k['title'], k['author'], "Okuyacağım", k['img'])
                if btns[1].button("📖 Okuyorum", key=f"r_{k['id']}", use_container_width=True): 
                    add_to_library(k['id'], k['title'], k['author'], "Okuyorum", k['img'])
                if btns[2].button("✅ Okudum", key=f"f_{k['id']}", use_container_width=True): 
                    add_to_library(k['id'], k['title'], k['author'], "Okudum", k['img'])