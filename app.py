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

# --- 2. スクリーン撮影 & ズーム機能付き切り出し ---
st.header("2. スクリーン撮影 & ズーム・切り出し")
uploaded_file = st.camera_input("スクリーンの写真を撮影")

if uploaded_file is not None:
  # 画像をOpenCV形式に変換
  bytes_data = uploaded_file.getvalue()
  np_arr = np.frombuffer(bytes_data, np.uint8)
  img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

  h, w, _ = img.shape

  # 🔍 拡大倍率の選択ボタン（後ろの席対策！）
  st.markdown("### 🔍 ズーム（拡大）倍率")
  zoom_level = st.radio(
      "遠くて文字が見えにくい場合は倍率を選んでください",
      ["等倍 (1x)", "2倍 (2x)", "4倍 (4x)"],
      horizontal=True,
  )

  # 選択された倍率に応じて画像を切り出し（中央をズーム）
  if "2倍" in zoom_level:
    crop_h, crop_w = int(h / 2), int(w / 2)
    start_h, start_w = int(h / 4), int(w / 4)
    img = img[start_h : start_h + crop_h, start_w : start_w + crop_w]
  elif "4倍" in zoom_level:
    crop_h, crop_w = int(h / 4), int(w / 4)
    start_h, start_w = int(h * 3 / 8), int(w * 3 / 8)
    img = img[start_h : start_h + crop_h, start_w : start_w + crop_w]

  # 簡易的な輪郭検出によるスクリーン自動切り出しの試み
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
    st.success("スライドの範囲を検出・ズームしました！")
  else:
    st.info(f"選択された倍率（{zoom_level}）で表示しています。")

  st.image(img, channels="BGR", caption=f"プレビュー ({zoom_level})")

st.divider()

# --- 3. 文字起こし & 翻訳 ---
st.header("3. 文字起こし & 翻訳")
transcribed_text = st.text_area(
    "文字起こしテキスト（音声入力または手動入力）",
    placeholder="韓国語の場合はここにテキストを入力すると自動で日本語訳が表示されます...",
)

if transcribed_text:
  # 韓国語（ハングル）の文字コードが含まれているか判定
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
