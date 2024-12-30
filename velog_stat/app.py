import altair as alt
import streamlit as st
import pandas as pd
from crawler import HitsCrawler

# [1] 전역 스타일 & 페이지 설정
st.set_page_config(page_title="velog stat", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #f0f4ff 0%, #ffffff 100%);
        font-family: 'Helvetica Neue', sans-serif;
        margin: 0; padding: 0; color: #333;
    }
    section.main > div {
        padding: 2rem 3rem;
        background-color: #fff;
        border-radius: 10px;
        max-width: 1100px;
        margin: 2rem auto;
        box-shadow: 0 3px 8px rgba(0,0,0,0.05);
    }
    h1 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem;
        color: #2c2c2c !important;
    }
    /* metric 카드 글씨 크기 */
    .css-1ht1j8u, .css-1r6slb0, .css-h5rgaw {
        font-size: 1.1rem !important;
    }
    .css-1ht1j8u .css-2vgkg4 {
        font-size: 1.3rem !important;
        color: #3E7BFA !important;
    }
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stHeader"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# [2] 세션 상태 초기화
if "username" not in st.session_state:
    st.session_state["username"] = None
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "post_infos" not in st.session_state:
    st.session_state["post_infos"] = None

# ─────────────────────────────────────────────────────────────────────────────
# 보조 함수: Velog 데이터 가져오기
# ─────────────────────────────────────────────────────────────────────────────
def fetch_velog_data():
    username = st.session_state["username"]
    access_token = st.session_state["access_token"]
    hits_crawler = HitsCrawler(username, access_token)

    if not hits_crawler.is_exist_user():
        st.error("존재하지 않는 사용자입니다.")
        return

    with st.spinner("데이터 가져오는 중..."):
        post_infos = hits_crawler.get_post_infos()
        if post_infos is not None:
            st.success("데이터가 성공적으로 로드되었습니다!", icon="✅")
            st.session_state["post_infos"] = post_infos
        else:
            st.error("데이터를 불러오지 못했습니다.")


# ─────────────────────────────────────────────────────────────────────────────
# 도넛 차트 생성 함수
# ─────────────────────────────────────────────────────────────────────────────
def create_donut_chart(df, val_col, title_col, color_scheme):
    df = df.copy()
    if "url_slug" in df.columns:
        df["url"] = df["url_slug"].apply(
            lambda s: f"https://velog.io/@{st.session_state['username']}/{s}"
        )
    else:
        df["url"] = ""

    donut_chart = alt.Chart(df).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(f"{val_col}:Q"),
        color=alt.Color(f"{title_col}:N", sort=None, scale=alt.Scale(scheme=color_scheme)),
        tooltip=[
            alt.Tooltip(f"{title_col}:N", title="제목"),
            alt.Tooltip(f"{val_col}:Q", title=val_col, format=","),
            alt.Tooltip("url:N", title="URL")
        ],
        href="url:N"  # 동일 탭 이동
    ).properties(width=500, height=400)
    return donut_chart


# ─────────────────────────────────────────────────────────────────────────────
# [3] 로그인 화면
# ─────────────────────────────────────────────────────────────────────────────
def show_login_screen():
    """아이디/토큰 입력 → 버튼 한 번 누르면 즉시 메인화면 진입"""
    st.title("velog stat 📊")
    st.markdown("""
        **Velog 블로그**의 조회수, 댓글 수, 좋아요 수를
        확인할 수 있는 미니 대시보드
    """)

    with st.expander("아이디 & 토큰 입력 방법"):
        st.markdown("""
            1. velog 로그인  
            2. 개발자도구(F12) → Application → Cookies → `https://velog.io`  
            3. `access_token` 복사  
            4. 아이디: URL의 `@` 뒤
        """)

    # 텍스트 입력
    username = st.text_input("사용자 이름 (ex: sin_0)", value="", key="input_username")
    access_token = st.text_input("Access Token", value="", type="password", key="input_access_token")

    # 일반 버튼
    if st.button("데이터 가져오기"):
        if not username or not access_token:
            st.error("아이디와 토큰을 모두 입력하세요.")
            return
        if len(access_token.split(".")) != 3:
            st.error("잘못된 Access Token 형식입니다.")
            return

        # 세션에 저장
        st.session_state["username"] = username
        st.session_state["access_token"] = access_token

        # 로그인 후 곧바로 메인화면 보여주기
        show_main_app()
        return  # 함수 종료, 아래 코드는 실행 안 됨


# ─────────────────────────────────────────────────────────────────────────────
# [4] 메인 화면
# ─────────────────────────────────────────────────────────────────────────────
def show_main_app():
    """로그인 후 메인 화면"""
    st.title("velog stat 📊")

    # "다른 아이디 검색하기" 버튼
    if st.button("다른 아이디 검색하기"):
        # 세션 초기화
        st.session_state["username"] = None
        st.session_state["access_token"] = None
        st.session_state["post_infos"] = None

        # 곧바로 로그인 화면 호출
        show_login_screen()
        return  # 함수를 즉시 종료 -> 아래 코드 실행 안 함

    # 아직 데이터가 없으면 불러오기
    if st.session_state["post_infos"] is None:
        fetch_velog_data()

    # 통계 출력
    if st.session_state["post_infos"] is not None:
        post_infos = st.session_state["post_infos"]
        total_posts = len(post_infos)

        st.header("📑 통계 요약")
        st.caption(f"총 게시물 수: {total_posts}개")

        col1, col2, col3 = st.columns(3)
        col1.metric(
            "총 조회수 👀",
            f"{post_infos['total'].sum():,}",
            f"평균 {post_infos['total'].mean():.1f}"
        )
        col2.metric(
            "총 댓글 수 💬",
            f"{post_infos['comments_count'].sum():,}",
            f"평균 {post_infos['comments_count'].mean():.1f}"
        )
        col3.metric(
            "총 좋아요 수 ❤️",
            f"{post_infos['likes'].sum():,}",
            f"평균 {post_infos['likes'].mean():.1f}"
        )

        # 조회수/댓글/좋아요 탭
        tab_views, tab_comments, tab_likes = st.tabs(["조회수 순위", "댓글 순위", "좋아요 순위"])

        with tab_views:
            st.subheader("조회수 Top 10")
            top10_views = post_infos.sort_values(by="total", ascending=False).head(10)
            donut_views = create_donut_chart(top10_views, "total", "title", "set2")
            st.altair_chart(donut_views, use_container_width=True)

        with tab_comments:
            st.subheader("댓글 Top 10")
            top10_comments = post_infos.sort_values(by="comments_count", ascending=False).head(10)
            donut_comments = create_donut_chart(top10_comments, "comments_count", "title", "tableau20")
            st.altair_chart(donut_comments, use_container_width=True)

        with tab_likes:
            st.subheader("좋아요 Top 10")
            top10_likes = post_infos.sort_values(by="likes", ascending=False).head(10)
            donut_likes = create_donut_chart(top10_likes, "likes", "title", "category20")
            st.altair_chart(donut_likes, use_container_width=True)

        # 일자별 조회수
        st.header("일자별 조회수 추이")
        df_daily = post_infos.copy()
        df_daily["date"] = df_daily["released_at"].dt.date
        df_daily = df_daily.groupby("date", as_index=False)["total"].sum()

        area_chart = alt.Chart(df_daily).mark_area(opacity=0.6).encode(
            x=alt.X('date:T', title='작성일'),
            y=alt.Y('total:Q', title='조회수'),
            tooltip=[
                alt.Tooltip('date:T', title='작성일'),
                alt.Tooltip('total:Q', title='조회수')
            ],
            color=alt.value("#5ac")
        ).properties(height=300)
        st.altair_chart(area_chart.interactive(), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# [5] 메인 실행
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # 세션에 username 없으면 → 로그인 화면
    if st.session_state["username"] is None or st.session_state["access_token"] is None:
        show_login_screen()
    else:
        # 로그인된 상태면 메인 화면
        show_main_app()

if __name__ == "__main__":
    main()
