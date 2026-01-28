from anthropic import beta_tool
from nba_api.stats.endpoints import ScoreboardV2
from nba_api.stats.static import teams
from datetime import datetime


def get_team_id(team_nickname: str) -> int | None:
    """Convert team nickname string to team_id from nba.com"""

    # Search through all NBA teams
    all_teams = teams.get_teams()
    for team in all_teams:
        if team_nickname in team["nickname"]:
            return team["id"]

    return None


@beta_tool
def game_finder(team_name: str) -> str:
    """Find the nba.com game_id for a specific team's ongoing NBA game
    Args:
        team_name: NBA team name e.g. Lakers, Warriors, etc.
    """
    try:
        # Convert team name to team ID
        team_id = get_team_id(team_nickname=team_name)
        if team_id is None:
            print(f"\nTeam '{team_name}' not found.\n")
            return f"\nTeam '{team_name}' not found.\n"

        # Get today's games
        today = datetime.now().strftime("%Y-%m-%d")
        scoreboard = ScoreboardV2(day_offset=0, game_date=today, league_id="00")

        # Get game header data which contains game IDs and status
        games = scoreboard.game_header.get_data_frame()

        # Filter for ongoing/live games (GAME_STATUS_ID indicates live status)
        ongoing_games = games[games["GAME_STATUS_ID"].isin([2])]

        # Filter for games where the team is playing
        requested_game = ongoing_games[
            (ongoing_games["HOME_TEAM_ID"] == team_id)
            | (ongoing_games["VISITOR_TEAM_ID"] == team_id)
        ]

        if requested_game.empty:
            print(f"\nNo live game found for {team_name}.\n")
            return f"\nNo live game found for {team_name}.\n"

        # Return the game ID
        return requested_game["GAME_ID"].iloc[0]

    except Exception as e:
        print(f"Error fetching NBA games: {str(e)}")
        return f"Error fetching NBA games: {str(e)}"
