def graphql_posts(username, limit, cursor=None) -> dict:
    """블로그 게시물 목록 가져오는 GraphQL 쿼리"""
    return {
        "query": """
        query velogPosts($input: GetPostsInput!) {
          posts(input: $input) {
            id
            title
            url_slug
            released_at
            updated_at
            comments_count
            tags
            likes
          }
        }
        """,
        "variables": {
            "input": {
                "cursor": cursor if cursor else None,
                "username": username,
                "limit": limit,
                "tag": ""
            }
        }
    }


def graphql_get_status(post_id):
    """통계 정보(조회수 등) 가져오는 GraphQL 쿼리"""
    return {
        "query": """
        query GetStats($post_id: ID!) {
          getStats(post_id: $post_id) {
            total
            count_by_day {
              count
              day
            }
          }
        }
        """,
        "variables": {"post_id": post_id}
    }
