from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session


class Repository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def count(self, statement: Select[tuple[object]]) -> int:
        count_stmt = select(func.count()).select_from(statement.subquery())
        return int(self.session.scalar(count_stmt) or 0)
