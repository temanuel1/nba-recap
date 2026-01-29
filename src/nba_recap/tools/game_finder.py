import json
from datetime import datetime

from anthropic import beta_tool
from nba_api.stats.endpoints import ScoreboardV2
from nba_api.stats.static import teams


def get_team_id(team_nickname: str) -> int | None:
    """Convert team nickname string to team_id from nba.com"""
    # Fetches all NBA teams and returns the team_id from nba.com corresponding to team_nickname
    all_teams = teams.get_teams()
    for team in all_teams:
        if team_nickname == team["nickname"]:
            return team["id"]
    return None


@beta_tool
def game_finder(team_name: str) -> str:
    """Find the nba.com game_id for a specific team's ongoing NBA game.

    Args:
        team_name: NBA team nickname (case-sensitive), e.g. Lakers, Warriors, Celtics

    Returns:
        JSON string with game_id on success,
        or JSON string with error key on failure.
    """
    try:
        # Uses helper to fetch team_id from team_nickname
        team_id = get_team_id(team_nickname=team_name)
        if team_id is None:
            return json.dumps({"error": f"Team '{team_name}' not found"})

        # Fetches live NBA scoreboard for today's games
        today = datetime.now().strftime("%Y-%m-%d")
        scoreboard = ScoreboardV2(day_offset=0, game_date=today, league_id="00")
        ongoing_games = scoreboard.game_header.get_data_frame()

        # Filters games to only include game where specified team is playing
        requested_game = ongoing_games[
            (ongoing_games["HOME_TEAM_ID"] == team_id)
            | (ongoing_games["VISITOR_TEAM_ID"] == team_id)
        ]

        if requested_game.empty:
            return json.dumps({"error": f"No live game found for {team_name}"})

        game = requested_game.iloc[0]

        return json.dumps(
            {
                "game_id": game["GAME_ID"],
            }
        )

    except Exception as e:
        return json.dumps({"error": f"Error fetching NBA games: {str(e)}"})
