from dataclasses import dataclass
from datetime import UTC, date, datetime


@dataclass(frozen=True)
class DemoLeagueFixture:
    name: str
    slug: str


@dataclass(frozen=True)
class DemoSeasonFixture:
    name: str
    start_date: date
    end_date: date


@dataclass(frozen=True)
class DemoTeamFixture:
    name: str
    slug: str
    logo_url: str | None = None


@dataclass(frozen=True)
class DemoPlayerFixture:
    demo_slug: str
    first_name: str
    last_name: str
    display_name: str
    position: str | None


@dataclass(frozen=True)
class DemoRosterFixture:
    team_slug: str
    player_demo_slug: str
    jersey_number: int | None


@dataclass(frozen=True)
class DemoSetFixture:
    set_number: int
    home_score: int
    away_score: int


@dataclass(frozen=True)
class DemoMatchFixture:
    key: str
    home_team_slug: str
    away_team_slug: str
    scheduled_at: datetime
    status: str
    venue: str | None
    sets: tuple[DemoSetFixture, ...]


DEMO_LEAGUE = DemoLeagueFixture(
    name="Демо-лига любительского волейбола",
    slug="demo-amateur-league",
)

DEMO_SEASON = DemoSeasonFixture(
    name="Сезон 2025–2026",
    start_date=date(2025, 9, 1),
    end_date=date(2026, 6, 30),
)

DEMO_TEAMS: tuple[DemoTeamFixture, ...] = (
    DemoTeamFixture(name="Северный ветер", slug="severny-veter"),
    DemoTeamFixture(name="Пляжные коты", slug="plyazhnye-koty"),
    DemoTeamFixture(name="Городские барсы", slug="gorodskie-barsy"),
    DemoTeamFixture(name="Речные дельфины", slug="rechnye-delfiny"),
)

DEMO_PLAYERS: tuple[DemoPlayerFixture, ...] = (
    DemoPlayerFixture("alina-orlova", "Алина", "Орлова", "Алина Орлова", "Связующая"),
    DemoPlayerFixture("ivan-petrov", "Иван", "Петров", "Иван Петров", "Доигровщик"),
    DemoPlayerFixture("maria-sokolova", "Мария", "Соколова", "Мария Соколова", "Либеро"),
    DemoPlayerFixture(
        "dmitry-volkov",
        "Дмитрий",
        "Волков",
        "Дмитрий Волков",
        "Центральный блокирующий",
    ),
    DemoPlayerFixture("elena-zhukova", "Елена", "Жукова", "Елена Жукова", "Диагональная"),
    DemoPlayerFixture("pavel-novikov", "Павел", "Новиков", "Павел Новиков", "Связующий"),
    DemoPlayerFixture("olga-belova", "Ольга", "Белова", "Ольга Белова", "Доигровщица"),
    DemoPlayerFixture("sergey-kuznetsov", "Сергей", "Кузнецов", "Сергей Кузнецов", "Либеро"),
)

DEMO_ROSTERS: tuple[DemoRosterFixture, ...] = (
    DemoRosterFixture("severny-veter", "alina-orlova", 7),
    DemoRosterFixture("severny-veter", "ivan-petrov", 11),
    DemoRosterFixture("severny-veter", "maria-sokolova", 1),
    DemoRosterFixture("plyazhnye-koty", "dmitry-volkov", 9),
    DemoRosterFixture("plyazhnye-koty", "elena-zhukova", 4),
    DemoRosterFixture("plyazhnye-koty", "pavel-novikov", 3),
    DemoRosterFixture("gorodskie-barsy", "olga-belova", 10),
    DemoRosterFixture("gorodskie-barsy", "sergey-kuznetsov", 2),
    DemoRosterFixture("rechnye-delfiny", "ivan-petrov", 5),
    DemoRosterFixture("rechnye-delfiny", "alina-orlova", 8),
)

DEMO_MATCHES: tuple[DemoMatchFixture, ...] = (
    DemoMatchFixture(
        key="m1",
        home_team_slug="severny-veter",
        away_team_slug="plyazhnye-koty",
        scheduled_at=datetime(2025, 10, 12, 18, 0, tzinfo=UTC),
        status="completed",
        venue="Спорткомплекс «Север»",
        sets=(
            DemoSetFixture(1, 25, 21),
            DemoSetFixture(2, 23, 25),
            DemoSetFixture(3, 25, 18),
        ),
    ),
    DemoMatchFixture(
        key="m2",
        home_team_slug="gorodskie-barsy",
        away_team_slug="rechnye-delfiny",
        scheduled_at=datetime(2025, 10, 19, 17, 30, tzinfo=UTC),
        status="completed",
        venue=None,
        sets=(
            DemoSetFixture(1, 25, 20),
            DemoSetFixture(2, 22, 25),
            DemoSetFixture(3, 25, 23),
            DemoSetFixture(4, 21, 25),
        ),
    ),
    DemoMatchFixture(
        key="m3",
        home_team_slug="plyazhnye-koty",
        away_team_slug="gorodskie-barsy",
        scheduled_at=datetime(2025, 11, 2, 19, 0, tzinfo=UTC),
        status="scheduled",
        venue="Дворец спорта",
        sets=(),
    ),
)
