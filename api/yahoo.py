from yahoo_fantasy_api import game, league, team
from yahoo_oauth import OAuth2

oauth = OAuth2(None, None, from_file="yahooAuth.json")


def main():
    league_ids = game.Game(oauth, "nba").league_ids()
    print(league_ids)
    current_league = league.League(oauth, "402.l.35721")
    print(current_league.matchups())
    return 0


if __name__ == "__main__":
    main()