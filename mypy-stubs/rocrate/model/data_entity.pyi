from .entity import Entity as Entity

class DataEntity(Entity):
    def write(self, base_path: str) -> None: ...
