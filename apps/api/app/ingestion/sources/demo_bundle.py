"""Read-only adapter: demo fixtures as ImportBundleV1 (does not write to DB)."""

from app.ingestion.demo.fixtures import (
    DEMO_LEAGUE,
    DEMO_MATCHES,
    DEMO_PLAYERS,
    DEMO_ROSTERS,
    DEMO_SEASON,
    DEMO_TEAMS,
)
from app.ingestion.schemas.file_v1 import (
    ImportBundleV1,
    LeaguePayloadV1,
    MatchPayloadV1,
    PlayerPayloadV1,
    RosterPayloadV1,
    SeasonPayloadV1,
    SetPayloadV1,
    TeamPayloadV1,
)


class DemoFixturesImportSource:
    """Exposes built-in demo data through the same bundle schema as file import."""

    def load_bundle(self) -> ImportBundleV1:
        league_ref = "demo-league"
        season_ref = "demo-season"
        return ImportBundleV1(
            schema_version=1,
            source_label="demo-fixtures-readonly",
            league=LeaguePayloadV1(
                ref=league_ref,
                name=DEMO_LEAGUE.name,
                slug=DEMO_LEAGUE.slug,
            ),
            seasons=[
                SeasonPayloadV1(
                    ref=season_ref,
                    name=DEMO_SEASON.name,
                    start_date=DEMO_SEASON.start_date,
                    end_date=DEMO_SEASON.end_date,
                    league_ref=league_ref,
                )
            ],
            teams=[
                TeamPayloadV1(
                    ref=team.slug,
                    name=team.name,
                    slug=team.slug,
                    logo_url=team.logo_url,
                )
                for team in DEMO_TEAMS
            ],
            players=[
                PlayerPayloadV1(
                    ref=player.demo_slug,
                    first_name=player.first_name,
                    last_name=player.last_name,
                    display_name=player.display_name,
                    position=player.position,
                )
                for player in DEMO_PLAYERS
            ],
            rosters=[
                RosterPayloadV1(
                    team_ref=roster.team_slug,
                    player_ref=roster.player_demo_slug,
                    season_ref=season_ref,
                    jersey_number=roster.jersey_number,
                )
                for roster in DEMO_ROSTERS
            ],
            matches=[
                MatchPayloadV1(
                    ref=match.key,
                    season_ref=season_ref,
                    home_team_ref=match.home_team_slug,
                    away_team_ref=match.away_team_slug,
                    scheduled_at=match.scheduled_at,
                    status=match.status,
                    venue=match.venue,
                    sets=[
                        SetPayloadV1(
                            set_number=set_row.set_number,
                            home_score=set_row.home_score,
                            away_score=set_row.away_score,
                        )
                        for set_row in match.sets
                    ],
                )
                for match in DEMO_MATCHES
            ],
        )
