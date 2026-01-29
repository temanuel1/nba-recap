import json

from anthropic import beta_tool
from nba_api.live.nba.endpoints import PlayByPlay


@beta_tool
def play_by_play(game_id: str) -> str:
    """Get live play-by-play data for NBA game specified by game_id.

    Args:
        game_id: nba.com game ID (e.g. 0022500670)

    Returns:
        JSON array of raw action objects from the NBA live API.
        Returns JSON with error key on failure.
    """
    try:
        # Fetch live play by play for NBA game denoted by game_id
        pbp = PlayByPlay(game_id=game_id)
        data = pbp.get_dict()
        actions = data.get("game", {}).get("actions", [])

        return json.dumps(actions)

    except Exception as e:
        return json.dumps({"error": f"Error fetching play-by-play data: {str(e)}"})
