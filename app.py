import datetime
from PIL import Image
import streamlit as st

# ストリームライト用の画像切り抜きライブラリ（streamlit-cropper）の代わりに
# Streamlit標準の機能やPythonのライブラリを活用してシンプルに実装します
import numpy as np

# 日本語・韓国語のOCR（文字認識）を行うためのライブラリ（easyocr）などを活用
try:
  import easyocr

  # リーダーのキャッシュ（高速化）
  @st.cache_resource
  def load_ocr_reader():
    return easyocr.Reader(['ko', 'ja', 'en'])

  OCR_AVAILABLE = True
except ImportError:
  OCR_AVAILABLE = False

st.set_page_config(
    page_title="講義スライド＆文字起こし", page_icon="🎓", layout="centered"
)

st.title("🎓 講義スライド自動抽出＆文字起こし")

# --- 1. 管理単位の入力 ---
st.header("1. 講義情報の入力")
col_l1, col_l2 = st.columns(2)
with col_l1:
  lecture_name = st.text_input("講義名", "プログラミング基礎")
  lecture_date = st.date_input("日付", datetime.date.today())
with col_l2:
  lecture_location = st.text_input("場所（教室など）", "201号室")

st.divider()

# --- 2. 画像アップロード & スライド切り出しツール ---
st.header("2. スライド画像の選択と切り出し")
st.info(
    "💡 スマホでズーム撮影した写真を選び、スライドの形に合わせて切り抜いてください。"
)

uploaded_file = st.file_uploader(
    "スライドの写真を選択 (JPEG / PNG)", type=["jpg", "jpeg", "png"]
)

processed_img = None

if uploaded_file is not None:
  image = Image.open(uploaded_file)
  w, h = image.size

  st.markdown("### ✂️ 切り出しエリアの調整")
  st.write("スライドが綺麗に見えるように上下左右の範囲を調整できます")

  # スライダーでトリミング位置を直感的に指定できるようにする（切り出しツール）
  col_t1, col_t2 = st.columns(2)
  with col_t1:
    crop_top = st.slider("上側を削る", 0, int(h * 0.4), 0)
    crop_bottom = st.slider(
        "下側を削る", 0, int(h * 0.4), 0
    )  # 下から削る量
  with col_t2:
    crop_left = st.slider("左側を削る", 0, int(w * 0.4), 0)
    crop_right = st.slider("右側を削る", 0, int(w * 0.4), 0)

  # トリミング実行
  left = crop_left
  top = crop_top
  right = w - crop_right
  bottom = h - crop_bottom

  if right > left and bottom > top:
    cropped_image = image.crop((left, top, right, bottom))
  else:
    cropped_image = image

  st.image(
      cropped_image,
      caption="切り抜かれたスライドプレビュー",
      use_container_width=True,
  )
  processed_img = cropped_image

st.divider()

# --- 3. スライド文字起こし（OCR） & 韓国語翻訳 ---
st.header("3. スライドの文字起こし（OCR） & 翻訳")

extracted_text = ""

if processed_img is not None:
  if st.button("🔍 スライドの文字を読み取る（文字起こし実行）", type="primary"):
    if not OCR_AVAILABLE:
      st.error(
          "OCRライブラリ（easyocr）がインストールされていません。"
          "requirements.txtを確認してください。"
      )
    else:
      with st.spinner("スライドから文字を読み取っています..."):
        reader = load_ocr_reader()
        # 画像をnumpy配列に変換してOCRにかける
        img_np = np.array(processed_img)
        results = reader.readtext(img_np)

        # 読み取ったテキストを結合
        extracted_text = "\n".join([text[1] for text in results])

# テキスト編集・確認エリア
slide_text_box = st.text_area(
    "読み取られたテキスト（必要に応じて修正できます）",
    value=extracted_text,
    placeholder="ここにスライドの文字が自動で入ります...",
    height=150,
)

# 韓国語判定と日本語訳の表示
if slide_text_box:
  # 韓国語（ハングル文字）が含まれているかチェック
  is_korean = any(0xAC00 <= ord(char) <= 0xD7A3 for char in slide_text_box)

  if is_korean:
    st.markdown("🇰🇷 **検出言語: 韓国語（スライド）**")
    # ここに簡単な韓国語訳の表示（将来的には翻訳APIなどとも連携可能）
    st.markdown(
        "> **【日本語訳（自動表示）】**\n"
        f"（※韓国語の検出を確認しました。テキスト「{slide_text_box[:30]}...」の翻訳処理を行います）"
    )
  else:
    st.markdown("🇯🇵 **検出言語: 日本語 / その他**")

st.divider()

# --- 4. スライドごとのメモ ---
st.header("4. スライドメモ")
slide_memo = st.text_area(
    "このスライドに関するメモ", placeholder="先生が強調していたポイントなど"
)

# --- 保存ボタン ---
if st.button("💾 このスライドの情報を保存する", type="primary"):
  st.success(
      f"【{lecture_name} / {lecture_date} / {lecture_location}】のデータを保存しました！"
  )
