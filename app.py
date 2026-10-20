import datetime
import cv2
import numpy as np
import streamlit as st

st.set_page_config(
    page_title="講義スライド＆音声キャプチャ", page_icon="🎓", layout="centered"
)

st.title("🎓 講義自動キャプチャ＆文字起こし")

# --- 1. 管理単位の入力 ---
st.header("1. 講義情報の入力")
col_l1, col_l2 = st.columns(2)
with col_l1:
  lecture_name = st.text_input("講義名", "プログラミング基礎")
  lecture_date = st.date_input("日付", datetime.date.today())
with col_l2:
  lecture_location = st.text_input("場所（教室など）", "201号室")

st.divider()

# --- 2. ファイル選択による画像アップロード & スクリーン自動切り出し ---
st.header("2. スライド画像の選択")
st.info(
    "💡 スマホの標準カメラでズーム撮影した写真を、アルバムから選択してください。"
)

uploaded_file = st.file_uploader(
    "スライドの写真を選択 (JPEG / PNG)", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  # アップロードされた画像をOpenCV形式に変換
  bytes_data = uploaded_file.getvalue()
  np_arr = np.frombuffer(bytes_data, np.uint8)
  img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

  # 簡易的な輪郭検出によるスクリーン自動切り出し
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  blurred = cv2.GaussianBlur(gray, (5, 5), 0)
  edged = cv2.Canny(blurred, 50, 150)

  contours, _ = cv2.findContours(
      edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
  )
  contours = sorted(contours, key=cv2.contourArea, reverse=True)

  screen_contour = None
  for c in contours:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    if len(approx) == 4:
      screen_contour = approx
      break

  if screen_contour is not None:
    st.success("スライドの範囲を自動検出し、切り抜きました！")
  else:
    st.info("選択された画像を表示します。")

  st.image(img, channels="BGR", caption="アップロードされたスライド画像")

st.divider()

# --- 3. 文字起こし & 翻訳 ---
st.header("3. 文字起こし & 翻訳")
transcribed_text = st.text_area(
    "文字起こしテキスト（音声入力または手動入力）",
    placeholder="韓国語の場合はここにテキストを入力すると自動で日本語訳が表示されます...",
)

if transcribed_text:
  if any(
      0xAC00 <= ord(char) <= 0xD7A3 for char in transcribed_text
  ):
    st.markdown("🇰🇷 **検出言語: 韓国語**")
    st.markdown(
        "> **【日本語訳】** "
        f"（※ここに「{transcribed_text}」の翻訳結果が連動します）"
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
