import json
import os
import re
import tempfile
from datetime import datetime
from pathlib import Path

from .model import SCHEMA_VERSION, SIBLING_EDGE_TYPES, SYMMETRIC_TYPES, FamilyTree

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "tree.json"
BACKUP_LIMIT = 30
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def raw_data(path: Path = DEFAULT_PATH) -> dict:
    path = Path(path)
    if not path.exists():
        return FamilyTree().to_dict()
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Tree data must be a JSON object")
    data.setdefault("schema_version", SCHEMA_VERSION)
    return data


def validate_data(data: dict) -> FamilyTree:
    if not isinstance(data, dict):
        raise ValueError("Tree data must be a JSON object")
    if "people" not in data or "relationships" not in data:
        raise ValueError("Tree data must include people and relationships")
    if not isinstance(data["people"], list):
        raise ValueError("people must be a list")
    if not isinstance(data["relationships"], list):
        raise ValueError("relationships must be a list")
    if "sibling_groups" in data and not isinstance(data["sibling_groups"], list):
        raise ValueError("sibling_groups must be a list")
    people_ids = set()
    for person in data["people"]:
        if not isinstance(person, dict):
            raise ValueError("Each person must be an object")
        person_id = person.get("id")
        name = str(person.get("name", "")).strip()
        if not isinstance(person_id, str) or not name:
            raise ValueError("Each person must include id and name")
        _validate_safe_id(person_id, "person id")
        if person_id in people_ids:
            raise ValueError(f"Duplicate person id: {person_id}")
        people_ids.add(person_id)

    allowed_relationships = set(SYMMETRIC_TYPES) | {"parent"}
    seen_relationships = set()
    relationship_ids = set()
    pair_types: dict[tuple[str, str], set[str]] = {}
    parent_counts: dict[str, int] = {}
    for relationship in data["relationships"]:
        if not isinstance(relationship, dict):
            raise ValueError("Each relationship must be an object")
        rel_type = relationship.get("type")
        if rel_type not in allowed_relationships:
            raise ValueError(f"Unknown relationship type: {rel_type}")
        rel_id = relationship.get("id")
        if rel_id is not None:
            if not isinstance(rel_id, str):
                raise ValueError("Relationship id must be a string")
            _validate_safe_id(rel_id, "relationship id")
            if rel_id in relationship_ids:
                raise ValueError(f"Duplicate relationship id: {rel_id}")
            relationship_ids.add(rel_id)
        person_a = relationship.get("person_a")
        person_b = relationship.get("person_b")
        if person_a not in people_ids:
            raise ValueError("Relationship references an unknown person")
        if person_b not in people_ids:
            raise ValueError("Relationship references an unknown person")
        if person_a == person_b:
            raise ValueError("Cannot relate a person to themselves")

        relationship_key = (
            (rel_type, person_a, person_b)
            if rel_type == "parent"
            else (rel_type, *sorted((person_a, person_b)))
        )
        if relationship_key in seen_relationships:
            raise ValueError("Duplicate relationship")
        seen_relationships.add(relationship_key)

        pair_key = tuple(sorted((person_a, person_b)))
        pair_types.setdefault(pair_key, set()).add(rel_type)
        if rel_type == "parent":
            parent_counts[person_b] = parent_counts.get(person_b, 0) + 1

    for child_id, count in parent_counts.items():
        if count > 2:
            raise ValueError(
                f"Person '{child_id}' has more than two parent relationships"
            )

    for types in pair_types.values():
        sibling_types = types & set(SIBLING_EDGE_TYPES)
        if len(sibling_types) > 1:
            raise ValueError("Only one sibling relationship type is allowed per pair")
        if "parent" in types and "spouse" in types:
            raise ValueError("A person cannot be both spouse and parent/child")
        if "parent" in types and sibling_types:
            raise ValueError("A person cannot be both sibling and parent/child")
        if "spouse" in types and sibling_types:
            raise ValueError("A person cannot be both sibling and spouse")

    sibling_group_ids = set()
    for group in data.get("sibling_groups", []):
        if not isinstance(group, dict):
            raise ValueError("Each sibling group must be an object")
        group_id = group.get("id")
        if group_id is not None:
            if not isinstance(group_id, str):
                raise ValueError("Sibling group id must be a string")
            _validate_safe_id(group_id, "sibling group id")
            if group_id in sibling_group_ids:
                raise ValueError(f"Duplicate sibling group id: {group_id}")
            sibling_group_ids.add(group_id)
        order = group.get("order", [])
        if not isinstance(order, list):
            raise ValueError("Sibling group order must be a list")
        if any(not isinstance(person_id, str) for person_id in order):
            raise ValueError("Sibling group order ids must be strings")
        if len(order) != len(set(order)):
            raise ValueError("Sibling group order includes a duplicate person")
        if any(person_id not in people_ids for person_id in order):
            raise ValueError("Sibling group references an unknown person")

    tree = FamilyTree.from_dict(data)
    if tree.has_parent_cycle():
        raise ValueError("Parent relationships contain an ancestry cycle")
    return tree


def _validate_safe_id(value: str, label: str) -> None:
    if not SAFE_ID_RE.fullmatch(value):
        raise ValueError(f"Invalid {label}: {value!r}")


def load(path: Path = DEFAULT_PATH) -> FamilyTree:
    path = Path(path)
    if not path.exists():
        return FamilyTree()
    return validate_data(raw_data(path))


def save(tree: FamilyTree, path: Path = DEFAULT_PATH, *, backup: bool = True) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if backup and path.exists():
        create_backup(path)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    tmp_path = Path(tmp_name)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(tree.to_dict(), f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp_path.replace(path)
    return path


def backup_dir(path: Path = DEFAULT_PATH) -> Path:
    return Path(path).parent / "backups"


def create_backup(path: Path = DEFAULT_PATH) -> Path | None:
    path = Path(path)
    if not path.exists():
        return None
    target_dir = backup_dir(path)
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    target = target_dir / f"{path.stem}-{stamp}{path.suffix}"
    target.write_bytes(path.read_bytes())
    prune_backups(path)
    return target


def list_backups(path: Path = DEFAULT_PATH) -> list[dict]:
    entries = []
    for backup in sorted(backup_dir(path).glob("*.json"), reverse=True):
        stat = backup.stat()
        entries.append(
            {
                "name": backup.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(
                    timespec="seconds"
                ),
            }
        )
    return entries


def prune_backups(path: Path = DEFAULT_PATH, keep: int = BACKUP_LIMIT) -> None:
    backups = sorted(
        backup_dir(path).glob("*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for backup in backups[keep:]:
        backup.unlink(missing_ok=True)


def restore_backup(name: str, path: Path = DEFAULT_PATH) -> FamilyTree:
    source = _safe_backup_path(name, path)
    data = raw_data(source)
    tree = validate_data(data)
    save(tree, path)
    return tree


def import_data(data: dict, path: Path = DEFAULT_PATH) -> FamilyTree:
    tree = validate_data(data)
    save(tree, path)
    return tree


def _safe_backup_path(name: str, path: Path = DEFAULT_PATH) -> Path:
    root = backup_dir(path).resolve()
    source = (root / name).resolve()
    if source == root or root not in source.parents or not source.is_file():
        raise ValueError("Backup not found")
    return source
