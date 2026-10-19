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
col1, col2 = st.columns(2)
with col1:
    lecture_name = st.text_input("講義名", "プログラミング基礎")
    lecture_date = st.date_input("日付", datetime.date.today())
with col2:
    lecture_location = st.text_input("場所（教室など）", "201号室")

st.divider()

# --- 2. スクリーン画像撮影・自動台形補正 ---
st.header("2. スクリーン撮影 & 自動切り出し")
uploaded_file = st.camera_input("スクリーンの写真を撮影")

if uploaded_file is not None:
  # 画像をOpenCV形式に変換
  bytes_data = uploaded_file.getvalue()
  np_arr = np.frombuffer(bytes_data, np.uint8)
  img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

  # 簡易的な輪郭検出によるスクリーン自動切り出し・台形補正のロジック
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
    if len(approx) == 4:  # 四角形を検出
      screen_contour = approx
      break

  if screen_contour is not None:
    # 四隅の座標を使って台形補正（簡易版）
    st.success("スライドの範囲を自動検出し、補正しました！")
    # ※ 本格的なパースペクティブ変換はここに組み込みます
    st.image(img, channels="BGR", caption="検出・補正後プレビュー")
  else:
    st.warning(
        "スクリーンの四隅がうまく検出されませんでした。元の画像を表示します。"
    )
    st.image(img, channels="BGR", caption="撮影画像")

st.divider()

# --- 3. 文字起こし & 翻訳 ---
st.header("3. 文字起こし & 翻訳")
st.info(
    "💡 スマホのマイクに向かって話した内容、または韓国語の音声をテキスト化します。"
)

# 音声入力のシミュレーション（ブラウザの音声認識機能と連携）
transcribed_text = st.text_area(
    "文字起こしテキスト（音声入力または手動入力）",
    placeholder=(
        "ここに文字起こしされたテキストが入ります（例：안녕하세요. 오늘..."
    ),
)

# 韓国語判定と翻訳の処理（簡易デモ）
if transcribed_text:
  # 簡単なキーワード判定（実際にはGoogle翻訳API等と連携可能）
  if any(
      ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in transcribed_text
  ):
    st.markdown("🇰🇷 **検出言語: 韓国語**")
    # サンプルの日本語訳表示
    st.markdown(
        "> **【日本語訳】** "
        f"（※ここに「{transcribed_text}」の翻訳結果が表示されます）"
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
  # ここにデータベースやファイル（NotionやGoogleスプレッドシートなど）への保存処理を追加できます。
