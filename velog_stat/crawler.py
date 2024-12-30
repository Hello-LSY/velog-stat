import asyncio
import json
import aiohttp
import pandas as pd
import requests
import streamlit as st
from graphql import graphql_posts, graphql_get_status

LIMIT = 50
VELOG_URL = "https://velog.io/"
POST_GRAPHQL_URL = "https://v3.velog.io/graphql"
VIEW_GRAPHQL_URL = "https://v2cdn.velog.io/graphql"


@st.cache_data(ttl=3600)
def fetch_post_infos(username: str, access_token: str) -> pd.DataFrame:
    """게시물 정보와 조회수 데이터를 통합하여 반환합니다."""
    crawler = HitsCrawler(username, access_token)
    posts = crawler.get_posts()
    hits = asyncio.run(crawler.get_hits(posts))

    df_posts = pd.DataFrame(posts)
    df_hits = pd.DataFrame(hits)
    
    # 날짜 형식 변환
    df_posts['released_at'] = pd.to_datetime(df_posts['released_at'])
    df_posts['updated_at'] = pd.to_datetime(df_posts['updated_at'])
    
    post_infos = pd.merge(left=df_posts, right=df_hits, how="inner", on="id")
    
    # total 컬럼이 실제 조회수를 나타내도록 통합
    if 'total' in post_infos.columns:
        post_infos = post_infos.rename(columns={'total': 'views'})
        post_infos['total'] = post_infos['views']
    
    return post_infos


class HitsCrawler:
    def __init__(self, username: str, access_token: str) -> None:
        self.username = username
        self.url = f"{VELOG_URL}@{username}/"
        self.access_token = access_token
        self.headers = {"Authorization": f"Bearer {access_token}"}

    def is_exist_user(self) -> bool:
        """사용자가 존재하는지 확인합니다."""
        response = requests.get(self.url)
        return response.status_code != 404

    def get_post_infos(self) -> pd.DataFrame:
        """캐시된 함수를 호출하여 데이터를 가져옵니다."""
        return fetch_post_infos(self.username, self.access_token)

    def get_posts(self) -> list:
        """사용자의 게시물 목록을 GraphQL API를 통해 가져옵니다."""
        posts = []
        cursor = None

        while True:
            query = self._build_post_query(cursor)
            response_data = self._execute_graphql_query(POST_GRAPHQL_URL, query)

            # 혹시나 data가 없거나 에러가 있으면 break
            if "data" not in response_data or "posts" not in response_data["data"]:
                break

            posts_chunk = response_data["data"]["posts"]
            posts.extend(posts_chunk)

            if len(posts_chunk) < LIMIT:
                break

            cursor = posts[-1]["id"]

        return posts

    async def get_hits(self, posts: list) -> list:
        """모든 게시물의 조회수를 비동기적으로 가져옵니다."""
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_view_by_post(session, post) for post in posts]
            hits = await asyncio.gather(*tasks)
        return hits

    async def get_view_by_post(self, session: aiohttp.ClientSession, post: dict) -> dict:
        """게시물의 조회수를 GraphQL API를 통해 가져옵니다."""
        try:
            query = graphql_get_status(post["id"])
            response_data = await self._execute_graphql_query_async(session, VIEW_GRAPHQL_URL, query)
            
            # GraphQL Error 체크 (optionally)
            if "data" not in response_data or "getStats" not in response_data["data"]:
                return {"id": post["id"], "total": 0}

            return {
                "id": post["id"],
                "total": response_data["data"]["getStats"]["total"],
            }
        except Exception as e:
            st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {str(e)}")
            st.stop()

    def _build_post_query(self, cursor: str = None) -> dict:
        """게시물 목록을 가져오기 위한 GraphQL 쿼리를 생성합니다."""
        return graphql_posts(self.username, LIMIT, cursor)

    def _execute_graphql_query(self, url: str, query: dict) -> dict:
        """GraphQL 쿼리를 동기적으로 실행합니다."""
        response = requests.post(url=url, json=query, headers=self.headers)
        response.raise_for_status()  # 오류 발생 시 예외 처리
        result = response.json()
        # GraphQL 에러가 있으면 예외 처리 (옵션)
        if "errors" in result:
            st.error(f"GraphQL Error: {result['errors']}")
        return result

    async def _execute_graphql_query_async(self, session: aiohttp.ClientSession, url: str, query: dict) -> dict:
        """GraphQL 쿼리를 비동기적으로 실행합니다."""
        async with session.post(url=url, json=query, headers=self.headers, ssl=False) as response:
            response.raise_for_status()  # 오류 발생 시 예외 처리
            result = await response.json()
            # GraphQL 에러 체크 (옵션)
            if "errors" in result:
                st.error(f"GraphQL Error: {result['errors']}")
            return result
