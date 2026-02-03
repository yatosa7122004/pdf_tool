import streamlit as st
from pypdf import PdfReader, PdfWriter
from PIL import Image
import io

# ページ設定
st.set_page_config(page_title="万能PDFツール", layout="centered")
st.title("📄 万能PDFツール")

# タブで機能を切り替え
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📂 結合", 
    "✂️ 抽出", 
    "🗑️ 削除", 
    "🖼️ 画像PDF化",
    "🔒 ロック"
])

# --- 1. 結合 (Merge) ---
with tab1:
    st.header("複数のPDFを1つにまとめる")
    uploaded_files = st.file_uploader("PDFを選択（複数可）", type="pdf", accept_multiple_files=True, key="merge")
    if uploaded_files:
        if st.button("結合する", key="btn_merge"):
            merger = PdfWriter()
            for pdf in uploaded_files:
                reader = PdfReader(pdf)
                for page in reader.pages:
                    merger.add_page(page)
            
            output = io.BytesIO()
            merger.write(output)
            output.seek(0)
            st.download_button("ダウンロード", output, "merged.pdf", "application/pdf")

# --- 2. 抽出 (Extract) ---
with tab2:
    st.header("必要なページだけ取り出す")
    target_file = st.file_uploader("PDFを選択", type="pdf", key="extract")
    if target_file:
        reader = PdfReader(target_file)
        total = len(reader.pages)
        st.info(f"全 {total} ページあります")
        
        selected = st.multiselect("残したいページを選択", range(1, total + 1), key="sel_ext")
        
        if st.button("抽出する", key="btn_ext"):
            if selected:
                writer = PdfWriter()
                for p in selected:
                    writer.add_page(reader.pages[p-1])
                
                output = io.BytesIO()
                writer.write(output)
                output.seek(0)
                st.download_button("ダウンロード", output, "extracted.pdf", "application/pdf")
            else:
                st.error("ページを選んでください")

# --- 3. 削除 (Delete) ---
with tab3:
    st.header("不要なページを削除する")
    target_del = st.file_uploader("PDFを選択", type="pdf", key="delete")
    if target_del:
        reader = PdfReader(target_del)
        total = len(reader.pages)
        st.info(f"全 {total} ページあります")
        
        # 削除したいページを選択
        delete_pages = st.multiselect("削除したいページを選択", range(1, total + 1), key="sel_del")
        
        if st.button("削除して保存", key="btn_del"):
            if delete_pages:
                writer = PdfWriter()
                # 選ばれていないページだけを追加する
                for i in range(total):
                    if (i + 1) not in delete_pages:
                        writer.add_page(reader.pages[i])
                
                output = io.BytesIO()
                writer.write(output)
                output.seek(0)
                st.download_button("ダウンロード", output, "deleted.pdf", "application/pdf")
            else:
                st.error("削除するページを選んでください")

# --- 4. 画像PDF化 (Image to PDF) ---
with tab4:
    st.header("画像をPDFに変換")
    st.write("スマホで撮った写真やスクショをまとめてPDFにします。")
    img_files = st.file_uploader("画像を選択（複数可）", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img")
    
    if img_files:
        if st.button("PDFに変換", key="btn_img"):
            # 画像を開いてリストにする
            images = []
            for img_file in img_files:
                img = Image.open(img_file)
                # 色モードをRGBに変換（PNGの透過対策など）
                if img.mode != "RGB":
                    img = img.convert("RGB")
                images.append(img)
            
            output = io.BytesIO()
            # 1枚目をベースに残りを追加して保存
            images[0].save(output, format="PDF", save_all=True, append_images=images[1:])
            output.seek(0)
            st.download_button("ダウンロード", output, "images.pdf", "application/pdf")

# --- 5. パスワード設定 (Security) ---
with tab5:
    st.header("パスワードをかける")
    target_lock = st.file_uploader("PDFを選択", type="pdf", key="lock")
    password = st.text_input("設定するパスワード", type="password")
    
    if target_lock and password:
        if st.button("ロックする", key="btn_lock"):
            reader = PdfReader(target_lock)
            writer = PdfWriter()
            
            # 全ページをコピー
            for page in reader.pages:
                writer.add_page(page)
            
            # パスワード設定
            writer.encrypt(password)
            
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            st.success("ロック完了！")
            st.download_button("ダウンロード", output, "locked.pdf", "application/pdf")