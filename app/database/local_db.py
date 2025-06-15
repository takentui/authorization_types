from typing import Any, Dict, Optional


class LocalDatabase:
    """Simple in-memory database for development."""

    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {
            "users": {},
            "sessions": {},
            "blacklist": {},
        }

    def get(self, table: str, key: str) -> Optional[Dict[str, Any]]:
        """Get a record from the specified table."""
        return self._data.get(table, {}).get(key)

    def set(self, table: str, key: str, value: Dict[str, Any]) -> None:
        """Set a record in the specified table."""
        if table not in self._data:
            self._data[table] = {}
        self._data[table][key] = value

    def delete(self, table: str, key: str) -> bool:
        """Delete a record from the specified table."""
        if table in self._data and key in self._data[table]:
            del self._data[table][key]
            return True
        return False

    def exists(self, table: str, key: str) -> bool:
        """Check if a record exists in the specified table."""
        return table in self._data and key in self._data[table]

    def get_all(self, table: str) -> Dict[str, Any]:
        """Get all records from the specified table."""
        return self._data.get(table, {}).copy()

    def clear(self) -> None:
        """Clear all data (useful for testing)."""
        self._data = {"users": {}, "sessions": {}, "blacklist": {}}
