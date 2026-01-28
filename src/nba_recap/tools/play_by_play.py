import json

from anthropic import beta_tool
from nba_api.live.nba.endpoints import PlayByPlay


@beta_tool
def play_by_play(game_id: str) -> str:
    """Get live play-by-play data for NBA game specified by game_id.

    Args:
        game_id: nba.com game ID (e.g. 0022500670)

    Returns:
        JSON array of play objects with keys: actionNumber, clock, period,
        teamTricode, actionType, subType, descriptor, playerName, description,
        scoreHome, scoreAway, isFieldGoal, x, y.
        Returns JSON with error key on failure.
    """
    try:
        # Fetch live play by play for NBA game denoted by game_id
        pbp = PlayByPlay(game_id=game_id)
        data = pbp.get_dict()

        actions = data.get("game", {}).get("actions", [])

        if not actions:
            return json.dumps(
                {"error": f"No play-by-play data found for game {game_id}"}
            )

        # Format play by play data into a list of dictionaries
        # Adds data for each play
        plays = []
        for action in actions:
            play = {
                "actionNumber": action.get("actionNumber"),
                "clock": action.get("clock"),
                "period": action.get("period"),
                "teamTricode": action.get("teamTricode"),
                "actionType": action.get("actionType"),
                "subType": action.get("subType"),
                "descriptor": action.get("descriptor"),
                "playerName": action.get("playerNameI"),
                "description": action.get("description"),
                "scoreHome": action.get("scoreHome"),
                "scoreAway": action.get("scoreAway"),
                "isFieldGoal": action.get("isFieldGoal"),
                "x": action.get("x"),
                "y": action.get("y"),
            }
            plays.append(play)

        return json.dumps(plays)

    except Exception as e:
        return json.dumps({"error": f"Error fetching play-by-play data: {str(e)}"})
