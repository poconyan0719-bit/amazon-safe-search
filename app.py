import streamlit as st
import urllib.parse
import streamlit.components.v1 as components

# ページ設定
st.set_page_config(
    page_title="Amazon安心検索",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# セッション状態の初期化
if 'last_redirected_query' not in st.session_state:
    st.session_state.last_redirected_query = ""

# カスタムCSSの適用
st.markdown("""
<style>
/* ボタンのスタイル調整 */
.custom-btn {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin-bottom: 15px;
    padding: 12px 24px;
    text-align: center;
    text-decoration: none;
    font-size: 16px;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.custom-btn:hover {
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}

.btn-amazon {
    background-color: #FF9900;
    color: white !important;
}

.btn-sakura {
    background-color: #0088CC;
    color: white !important;
}

.btn-google {
    background-color: #DB4437;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# タイトル
st.title("🛒 Amazon安心検索")
st.markdown("Amazonでの商品検索から、「怪しい中国メーカー・出品者」を排除し、信頼できる「Amazon.co.jp（直販）」の商品のみを素早く検索するためのツールです。")

st.markdown("---")

# 検索入力フォーム
search_query = st.text_input("検索キーワード", placeholder="例：モバイルバッテリー")

if search_query:
    # URLエンコード (スペースを+に変換)
    encoded_query = urllib.parse.quote_plus(search_query)
    
    # ---------------------------------------------------------
    # Amazon検索用URLパラメータ (＆emi=AN1VRQENFRJN5)
    # ---------------------------------------------------------
    amazon_url = f"https://www.amazon.co.jp/s?k={encoded_query}&emi=AN1VRQENFRJN5"
    
    # ---------------------------------------------------------
    # サクラチェッカーURL
    # ---------------------------------------------------------
    sakura_url = f"https://sakura-checker.jp/itemsearch/?word={encoded_query}"
    
    # ---------------------------------------------------------
    # Google検索URL (公式サイト 価格)
    # ---------------------------------------------------------
    # 「キーワード + 公式サイト + 価格」 でGoogle検索するURLを生成
    google_query = urllib.parse.quote_plus(search_query + " 公式サイト 価格")
    google_url = f"https://www.google.com/search?q={google_query}"
    
    st.markdown("### 🔍 検索を実行")
    st.markdown("以下のボタンをクリックすると、それぞれの検索結果が開きます。")
    st.info("💡 **Google検索ボタンについて**：Amazonで見つけた具体的な「メーカー名＋正式な商品名」を入力して検索すると、公式サイトの正確な価格がヒットしやすくなります。")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<a href="{amazon_url}" target="_blank" class="custom-btn btn-amazon">🛒 Amazon(直販)</a>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<a href="{sakura_url}" target="_blank" class="custom-btn btn-sakura">🌸 サクラチェッカー</a>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<a href="{google_url}" target="_blank" class="custom-btn btn-google">🔍 Googleで価格検索</a>', unsafe_allow_html=True)

else:
    st.info("上に検索キーワードを入力すると、検索ボタンが表示されます。")

st.markdown("---")
st.markdown("""
**💡 使い方のヒント**
- 【安心検索（Amazon）】ボタンは、Amazon検索機能に独自のパラメータ（`&emi=AN1VRQENFRJN5`）を付与することで、販売元を「Amazon.co.jp」直販のみに絞り込みます。
""")
