import pytest
from sqlalchemy.orm import Session

from app.ingestion.demo.seed import count_domain_rows, seed_demo_league

pytestmark = pytest.mark.postgres


def test_seed_is_idempotent(db_session: Session) -> None:
    seed_demo_league(db_session)
    first_counts = count_domain_rows(db_session)

    seed_demo_league(db_session)
    second_counts = count_domain_rows(db_session)

    assert first_counts == second_counts
    assert first_counts["leagues"] == 1
    assert first_counts["teams"] == 4
    assert first_counts["matches"] == 3
