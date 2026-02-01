from __future__ import annotations
from src.domain.entities.child import Child

class User:
    def __init__(self, user_id: int):
        self.id = user_id
        self.children: list[Child] = []

    def add_child(self, child: Child):
        self.children.append(child)