import streamlit as st
from pypdf import PdfReader, PdfWriter
from PIL import Image
import io

# --- 設定: スマホで見やすくするおまじない ---
st.set_page_config(page_title="PDFツール", layout="centered")

# CSSで余白を削り、見た目をスマホアプリ風にする
st.markdown("""
    <style>
        /* 全体の余白を減らす */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        /* ヘッダーとフッターを消す */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        /* ボタンを少し大きくして押しやすく */
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            height: 3em;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📱 万能PDFツール")

# --- メニュー選択（スマホ最適化） ---
# タブではなく「セレクトボックス」にすることで、親指で操作しやすくする
menu = st.selectbox(
    "機能を選んでください",
    ["📂 PDF結合", "✂️ ページ抽出", "🗑️ ページ削除", "🖼️ 画像PDF化", "🔒 パスワード設定"]
)

st.divider() # 区切り線

# --- 1. 結合 (Merge) ---
if menu == "📂 PDF結合":
    st.header("複数のPDFを結合")
    uploaded_files = st.file_uploader("結合したいファイルを順番に選択", type="pdf", accept_multiple_files=True, key="merge")
    
    if uploaded_files:
        st.write(f"現在 {len(uploaded_files)} 個のファイルを選択中")
        if st.button("結合してダウンロード"):
            merger = PdfWriter()
            for pdf in uploaded_files:
                reader = PdfReader(pdf)
                for page in reader.pages:
                    merger.add_page(page)
            
            output = io.BytesIO()
            merger.write(output)
            output.seek(0)
            st.success("完了しました！")
            st.download_button("PDFを保存", output, "merged.pdf", "application/pdf")

# --- 2. 抽出 (Extract) ---
elif menu == "✂️ ページ抽出":
    st.header("必要なページを抽出")
    target_file = st.file_uploader("PDFを選択", type="pdf", key="extract")
    
    if target_file:
        reader = PdfReader(target_file)
        total = len(reader.pages)
        st.info(f"全 {total} ページ")
        
        selected = st.multiselect("残すページを選択", range(1, total + 1), key="sel_ext")
        
        if st.button("抽出してダウンロード"):
            if selected:
                writer = PdfWriter()
                for p in selected:
                    writer.add_page(reader.pages[p-1])
                output = io.BytesIO()
                writer.write(output)
                output.seek(0)
                st.download_button("PDFを保存", output, "extracted.pdf", "application/pdf")
            else:
                st.error("ページを選んでね")

# --- 3. 削除 (Delete) ---
elif menu == "🗑️ ページ削除":
    st.header("不要なページを削除")
    target_del = st.file_uploader("PDFを選択", type="pdf", key="delete")
    
    if target_del:
        reader = PdfReader(target_del)
        total = len(reader.pages)
        st.info(f"全 {total} ページ")
        
        delete_pages = st.multiselect("消すページを選択", range(1, total + 1), key="sel_del")
        
        if st.button("削除してダウンロード"):
            if delete_pages:
                writer = PdfWriter()
                for i in range(total):
                    if (i + 1) not in delete_pages:
                        writer.add_page(reader.pages[i])
                output = io.BytesIO()
                writer.write(output)
                output.seek(0)
                st.download_button("PDFを保存", output, "deleted.pdf", "application/pdf")
            else:
                st.error("ページを選んでね")

# --- 4. 画像PDF化 ---
elif menu == "🖼️ 画像PDF化":
    st.header("画像をPDFに変換")
    img_files = st.file_uploader("画像を選択（複数可）", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="img")
    
    if img_files:
        st.write(f"{len(img_files)} 枚の画像を選択中")
        if st.button("PDFに変換して保存"):
            images = []
            for img_file in img_files:
                img = Image.open(img_file)
                if img.mode != "RGB":
                    img = img.convert("RGB")
                images.append(img)
            
            output = io.BytesIO()
            images[0].save(output, format="PDF", save_all=True, append_images=images[1:])
            output.seek(0)
            st.success("変換完了！")
            st.download_button("PDFを保存", output, "images.pdf", "application/pdf")

# --- 5. ロック (Security) ---
elif menu == "🔒 パスワード設定":
    st.header("パスワード設定")
    target_lock = st.file_uploader("PDFを選択", type="pdf", key="lock")
    password = st.text_input("パスワードを入力", type="password")
    
    if target_lock and password:
        if st.button("ロックして保存"):
            reader = PdfReader(target_lock)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(password)
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            st.success("ロックしました！")
            st.download_button("PDFを保存", output, "locked.pdf", "application/pdf")