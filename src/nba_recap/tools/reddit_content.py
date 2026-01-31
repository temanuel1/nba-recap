import json, requests
from anthropic import beta_tool
from nba_recap.urls import NBA_MOD_POSTS_URL, NBA_COMMENT_URL


def extract_comments(children: list) -> list[str]:
    """Recursively extract all comments including replies."""
    comments = []
    for c in children:
        if c["kind"] != "t1":
            continue
        if body := c["data"].get("body"):
            comments.append(body)
        replies = c["data"].get("replies")
        if replies and isinstance(replies, dict):
            comments.extend(extract_comments(replies["data"]["children"]))
    return comments


@beta_tool
def reddit_content(team_name: str) -> str:
    """
    Fetches fan comments from the r/nba game thread for contextual color.

    Returns real-time fan reactions, hot takes, and commentary that capture
    the emotional pulse of the game. Use these to add flavor and atmosphere
    to the recap - quote particularly funny, insightful, or representative
    comments to show how fans are experiencing key moments.

    Args:
        team_name: Team nickname (e.g., "Thunder", "Warriors")

    Returns:
        JSON string with comments on success,
        or JSON string with error key on failure.
    """
    headers = {"User-Agent": "nba-recap/0.1"}

    try:
        feed_resp = requests.get(
            NBA_MOD_POSTS_URL, params={"sort": "new", "limit": 100}, headers=headers
        )
        feed_resp.raise_for_status()

        post_id = None
        for post in feed_resp.json()["data"]["children"]:
            title = post["data"]["title"]
            if "GAME THREAD" in title and team_name.lower() in title.lower():
                post_id = post["data"]["id"]
                break

        if not post_id:
            return json.dumps({"error": f"No game thread found for {team_name}"})

        comments_resp = requests.get(
            NBA_COMMENT_URL.format(post_id=post_id),
            params={"sort": "new", "limit": 100},
            headers=headers,
        )
        comments_resp.raise_for_status()

        data = comments_resp.json()
        comments = extract_comments(data[1]["data"]["children"])

        return json.dumps(comments)
    except Exception as e:
        return json.dumps({"error": f"Error fetching live comments: {str(e)}"})
