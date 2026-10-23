from sqlalchemy.orm import Session

from app.mysql_models import Inventory
from core.item import Item


class MySQLRepository:
    """Repository for MySQL-backed inventory storage."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_pid(self, pid: str) -> Inventory | None:
        normalized_pid = self._normalize_pid(pid)
        return (
            self.db.query(Inventory)
            .filter(Inventory.pid == normalized_pid)
            .first()
        )

    def create_item(
        self,
        pid: str,
        name: str,
        qty: int,
        receiver: str = "",
        shipper: str = "",
    ) -> Item:
        db_item = Inventory(
            pid=self._normalize_pid(pid),
            item_name=name,
            qty=qty,
            receiver=receiver,
            shipper=shipper,
        )

        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)

        return self.to_item(db_item)

    def update_item(
        self,
        db_item: Inventory,
        qty: int,
        receiver: str = "",
        shipper: str = "",
    ) -> Item:
        db_item.qty = qty
        db_item.receiver = receiver
        db_item.shipper = shipper

        self.db.commit()
        self.db.refresh(db_item)

        return self.to_item(db_item)

    def rollback(self) -> None:
        self.db.rollback()

    @staticmethod
    def to_item(db_item: Inventory) -> Item:
        return Item(
            pid=db_item.pid,
            name=db_item.item_name,
            current_qty=db_item.qty,
            buyer=db_item.receiver,
            shipper=db_item.shipper,
        )

    @staticmethod
    def _normalize_pid(pid: str) -> str:
        return pid.strip().upper()
