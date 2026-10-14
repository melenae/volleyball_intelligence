from collections import Counter

from app.ingestion.errors import IngestionIssue
from app.ingestion.schemas.file_v1 import ImportBundleV1


def _check_unique_refs(
    items: list[object],
    entity_type: str,
    attr: str = "ref",
) -> list[IngestionIssue]:
    issues: list[IngestionIssue] = []
    refs = [getattr(item, attr) for item in items]
    counts = Counter(refs)
    for ref, count in counts.items():
        if count > 1:
            issues.append(
                IngestionIssue(
                    code="duplicate_ref",
                    message=f"Дублирующийся ref «{ref}» ({count} раз).",
                    entity_type=entity_type,
                    entity_ref=ref,
                    field=attr,
                )
            )
    return issues


def validate_bundle_structure(bundle: ImportBundleV1) -> list[IngestionIssue]:
    issues: list[IngestionIssue] = []

    issues.extend(_check_unique_refs([bundle.league], "league"))
    issues.extend(_check_unique_refs(bundle.seasons, "season"))
    issues.extend(_check_unique_refs(bundle.teams, "team"))
    issues.extend(_check_unique_refs(bundle.players, "player"))
    issues.extend(_check_unique_refs(bundle.matches, "match"))

    season_refs = {season.ref for season in bundle.seasons}
    team_refs = {team.ref for team in bundle.teams}
    player_refs = {player.ref for player in bundle.players}

    for season in bundle.seasons:
        if season.league_ref != bundle.league.ref:
            issues.append(
                IngestionIssue(
                    code="unknown_reference",
                    message=(
                        f"season.league_ref «{season.league_ref}» не совпадает "
                        f"с league.ref «{bundle.league.ref}»."
                    ),
                    entity_type="season",
                    entity_ref=season.ref,
                    field="league_ref",
                )
            )

    for roster in bundle.rosters:
        if roster.team_ref not in team_refs:
            issues.append(
                IngestionIssue(
                    code="unknown_reference",
                    message=f"Неизвестный team_ref «{roster.team_ref}».",
                    entity_type="roster",
                    entity_ref=f"{roster.team_ref}/{roster.player_ref}/{roster.season_ref}",
                    field="team_ref",
                )
            )
        if roster.player_ref not in player_refs:
            issues.append(
                IngestionIssue(
                    code="unknown_reference",
                    message=f"Неизвестный player_ref «{roster.player_ref}».",
                    entity_type="roster",
                    entity_ref=f"{roster.team_ref}/{roster.player_ref}/{roster.season_ref}",
                    field="player_ref",
                )
            )
        if roster.season_ref not in season_refs:
            issues.append(
                IngestionIssue(
                    code="unknown_reference",
                    message=f"Неизвестный season_ref «{roster.season_ref}».",
                    entity_type="roster",
                    entity_ref=f"{roster.team_ref}/{roster.player_ref}/{roster.season_ref}",
                    field="season_ref",
                )
            )

    roster_keys = [f"{r.team_ref}|{r.player_ref}|{r.season_ref}" for r in bundle.rosters]
    for key, count in Counter(roster_keys).items():
        if count > 1:
            issues.append(
                IngestionIssue(
                    code="duplicate_ref",
                    message=f"Дублирующаяся заявка «{key}».",
                    entity_type="roster",
                    entity_ref=key,
                )
            )

    for match in bundle.matches:
        if match.season_ref not in season_refs:
            issues.append(
                IngestionIssue(
                    code="unknown_reference",
                    message=f"Неизвестный season_ref «{match.season_ref}».",
                    entity_type="match",
                    entity_ref=match.ref,
                    field="season_ref",
                )
            )
        if match.home_team_ref not in team_refs:
            issues.append(
                IngestionIssue(
                    code="unknown_reference",
                    message=f"Неизвестный home_team_ref «{match.home_team_ref}».",
                    entity_type="match",
                    entity_ref=match.ref,
                    field="home_team_ref",
                )
            )
        if match.away_team_ref not in team_refs:
            issues.append(
                IngestionIssue(
                    code="unknown_reference",
                    message=f"Неизвестный away_team_ref «{match.away_team_ref}».",
                    entity_type="match",
                    entity_ref=match.ref,
                    field="away_team_ref",
                )
            )
        set_numbers = [set_row.set_number for set_row in match.sets]
        for set_number, count in Counter(set_numbers).items():
            if count > 1:
                issues.append(
                    IngestionIssue(
                        code="duplicate_set_number",
                        message=f"Повтор номера сета {set_number}.",
                        entity_type="match",
                        entity_ref=match.ref,
                        field="sets",
                    )
                )

    return issues
