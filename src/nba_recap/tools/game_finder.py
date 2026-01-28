import json
from datetime import datetime

from anthropic import beta_tool
from nba_api.stats.endpoints import ScoreboardV2
from nba_api.stats.static import teams


def get_team_id(team_nickname: str) -> int | None:
    """Convert team nickname string to team_id from nba.com"""
    all_teams = teams.get_teams()
    for team in all_teams:
        if team_nickname in team["nickname"]:
            return team["id"]
    return None


@beta_tool
def game_finder(team_name: str) -> str:
    """Find the nba.com game_id for a specific team's ongoing NBA game
    Args:
        team_name: NBA team nickname with proper capitalization (e.g. Lakers, Warriors, Celtics)
    """
    try:
        team_id = get_team_id(team_nickname=team_name)
        if team_id is None:
            return json.dumps({"error": f"Team '{team_name}' not found"})

        today = datetime.now().strftime("%Y-%m-%d")
        scoreboard = ScoreboardV2(day_offset=0, game_date=today, league_id="00")

        games = scoreboard.game_header.get_data_frame()
        ongoing_games = games[games["GAME_STATUS_ID"].isin([2])]

        requested_game = ongoing_games[
            (ongoing_games["HOME_TEAM_ID"] == team_id)
            | (ongoing_games["VISITOR_TEAM_ID"] == team_id)
        ]

        if requested_game.empty:
            return json.dumps({"error": f"No live game found for {team_name}"})

        return requested_game["GAME_ID"].iloc[0]

    except Exception as e:
        return json.dumps({"error": f"Error fetching NBA games: {str(e)}"})
