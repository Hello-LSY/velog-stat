import altair as alt
import streamlit as st
from crawler import HitsCrawler

# Streamlit 페이지 설정
st.set_page_config(page_title="velog stat", page_icon="📊", layout="wide")

# 헤더와 설명 추가
st.title("velog stat 📊")
st.markdown(
    """
    **당신의 velog 통계는?**
    """
    
    """
    velog 블로그의 조회수, 댓글 수, 좋아요 수를 쉽게 분석할 수 있습니다!.
    """
)

# 사용자 입력 및 검증을 위한 함수
def get_user_input():
    with st.sidebar:
        with st.form(key='form', clear_on_submit=True):
            username = st.text_input(
                label="사용자 이름을 입력해주세요 !",
                placeholder="username",
                help="velog에서 사용 중인 사용자 이름을 입력하세요. ex) sin_0"
            )
            access_token = st.text_input(
                label="Access Token 값을 입력해주세요 !",
                placeholder="access token",
                type="password",
                help="velog에서 발급받은 Access Token을 입력하세요."
            )
            submit = st.form_submit_button(label="데이터 가져오기")

            if submit:
                if not username or not access_token:
                    st.error("사용자 이름 또는 Access Token을 입력해주세요.")
                    return None, None
                # Access Token 형식 검증 추가
                if len(access_token.split('.')) != 3:
                    st.error("잘못된 Access Token 형식입니다.")
                    return None, None
                return username, access_token

        st.markdown("---")
        st.subheader("💡 Access Token 가져오는 방법")
        st.markdown(
            """
            1. velog에 로그인합니다.
            2. 브라우저 개발자 도구를 엽니다 (F12를 누르거나 우클릭 > 검사 선택).
            3. `Application` 탭에서 `Storage` > `Cookies` > `https://velog.io`로 이동합니다.
            4. `access_token`을 찾아 값을 복사합니다.
            """
        )
    return None, None

# 사용자 입력 받기
username, access_token = get_user_input()

# 데이터 수집 및 시각화는 입력이 있을 때만 실행
if username and access_token:
    # Velog 데이터 수집 함수
    def fetch_velog_data(username, access_token):
        hits_crawler = HitsCrawler(username, access_token)
        if hits_crawler.is_exist_user() is False:
            st.error("존재하지 않는 사용자입니다.")
            return None

        with st.spinner('🍀 데이터를 가져오는 중입니다. 잠시만 기다려 주세요 !'):
            post_infos = hits_crawler.get_post_infos()
            st.info("데이터가 성공적으로 로드되었습니다!", icon="✅")

        return post_infos

    # 데이터 시각화 함수
    def create_chart(data, x, y, title, color, tooltip_title):
        chart = alt.Chart(data).mark_bar().encode(
            x=alt.X(x, title=title),
            y=alt.Y(y, title="제목", sort="-x"),
            color=alt.Color(color, scale=alt.Scale(scheme="reds"), legend=None),
            tooltip=[alt.Tooltip("title", title="제목"), alt.Tooltip(x, title=tooltip_title, format="d")]
        ).interactive()
        return chart

    # Velog 데이터 가져오기
    post_infos = fetch_velog_data(username, access_token)

    if post_infos is not None:
        # 요약 통계 출력
        st.header("📑 통계 요약")
        col1, col2, col3 = st.columns(3)
        col1.metric("총 조회수", f"{post_infos['total'].sum()}")
        col2.metric("총 댓글 수", f"{post_infos['comments_count'].sum()}")
        col3.metric("총 좋아요 수", f"{post_infos['likes'].sum()}")
        # 추가 통계 정보
        avg_views = post_infos['total'].mean()
        avg_comments = post_infos['comments_count'].mean()
        avg_likes = post_infos['likes'].mean()
        col1.metric("평균 조회수", f"{avg_views:.2f}")
        col2.metric("평균 댓글 수", f"{avg_comments:.2f}")
        col3.metric("평균 좋아요 수", f"{avg_likes:.2f}")

        # 탭 구성 및 시각화
        tab_views, tab_comments, tab_likes = st.tabs(["📈 조회수 순위", "💬 댓글 순위", "♥️ 좋아요 순위"])

        with tab_views:
            st.subheader("포스트 조회수 순위")
            st.altair_chart(create_chart(post_infos, "total", "title", "조회수", "total", "조회수"), use_container_width=True)

        with tab_comments:
            st.subheader("포스트 댓글 순위")
            st.altair_chart(create_chart(post_infos, "comments_count", "title", "댓글", "comments_count", "댓글"), use_container_width=True)

        with tab_likes:
            st.subheader("포스트 좋아요 순위")
            st.altair_chart(create_chart(post_infos, "likes", "title", "좋아요", "likes", "좋아요"), use_container_width=True)
