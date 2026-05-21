from __future__ import annotations

import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from typing import Literal

SCHEMA_VERSION = 1

RelationshipType = Literal[
    "parent", "spouse", "sibling", "brother", "sister"
]

SYMMETRIC_TYPES = frozenset({"spouse", "sibling", "brother", "sister"})

RELATIONSHIP_LABELS = {
    "spouse": "Spouse",
    "parent": "Parent",
    "child": "Child",
    "sibling": "Sibling",
    "brother": "Brother",
    "sister": "Sister",
}

SIBLING_EDGE_TYPES = frozenset({"sibling", "brother", "sister"})


def birth_order_label(position: int, total: int) -> str:
    """position is 0-based, 0 = eldest."""
    if total <= 1:
        return "Only child"
    if total == 2:
        return "Eldest" if position == 0 else "Youngest"
    if position == 0:
        return "Eldest"
    if position == total - 1:
        return "Youngest"
    if total == 3 and position == 1:
        return "Middle"
    return f"{position + 1}{_ordinal_suffix(position + 1)} (of {total})"


def _ordinal_suffix(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


@dataclass
class Person:
    name: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    birth: str | None = None
    death: str | None = None
    birth_place: str | None = None
    death_place: str | None = None
    gender: str | None = None
    occupation: str | None = None
    photo: str | None = None
    sources: str = ""
    notes: str = ""

    def label(self) -> str:
        years = ""
        if self.birth and self.death:
            years = f" ({self.birth}-{self.death})"
        elif self.birth:
            years = f" (b. {self.birth})"
        elif self.death:
            years = f" (d. {self.death})"
        return f"{self.name}{years}"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Person:
        payload = dict(data)
        allowed = {
            "id",
            "name",
            "birth",
            "death",
            "birth_place",
            "death_place",
            "gender",
            "occupation",
            "photo",
            "sources",
            "notes",
        }
        return cls(**{key: value for key, value in payload.items() if key in allowed})


@dataclass
class Relationship:
    type: RelationshipType
    person_a: str
    person_b: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Relationship:
        payload = dict(data)
        payload.setdefault("id", uuid.uuid4().hex[:8])
        allowed = {"id", "type", "person_a", "person_b"}
        return cls(**{key: value for key, value in payload.items() if key in allowed})

    def involves(self, person_id: str) -> bool:
        return person_id in (self.person_a, self.person_b)

    def other(self, person_id: str) -> str:
        return self.person_b if self.person_a == person_id else self.person_a


@dataclass
class SiblingGroup:
    """Ordered eldest → youngest. order[0] is the eldest sibling."""
    id: str
    order: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> SiblingGroup:
        payload = dict(data)
        payload.setdefault("id", uuid.uuid4().hex[:8])
        allowed = {"id", "order"}
        return cls(**{key: value for key, value in payload.items() if key in allowed})


class FamilyTree:
    def __init__(self) -> None:
        self.people: dict[str, Person] = {}
        self.relationships: list[Relationship] = []
        self.sibling_groups: dict[str, SiblingGroup] = {}

    def add_person(
        self,
        name: str,
        *,
        birth: str | None = None,
        death: str | None = None,
        gender: str | None = None,
        birth_place: str | None = None,
        death_place: str | None = None,
        occupation: str | None = None,
        photo: str | None = None,
        sources: str = "",
        notes: str = "",
        person_id: str | None = None,
    ) -> Person:
        name = name.strip()
        if not name:
            raise ValueError("Name is required")
        person = Person(
            id=person_id or uuid.uuid4().hex[:8],
            name=name,
            birth=birth or None,
            death=death or None,
            birth_place=birth_place or None,
            death_place=death_place or None,
            gender=gender or None,
            occupation=occupation or None,
            photo=photo or None,
            sources=sources or "",
            notes=notes or "",
        )
        self.people[person.id] = person
        return person

    def update_person(
        self,
        person_id: str,
        *,
        name: str,
        birth: str | None = None,
        death: str | None = None,
        gender: str | None = None,
        birth_place: str | None = None,
        death_place: str | None = None,
        occupation: str | None = None,
        photo: str | None = None,
        sources: str = "",
        notes: str = "",
    ) -> Person:
        person = self.get_person(person_id)
        if not name.strip():
            raise ValueError("Name is required")
        person.name = name.strip()
        person.birth = birth or None
        person.death = death or None
        person.birth_place = birth_place or None
        person.death_place = death_place or None
        person.gender = gender or None
        person.occupation = occupation or None
        person.photo = photo or None
        person.sources = sources or ""
        person.notes = notes or ""
        self.sync_sibling_groups()
        return person

    def remove_person(self, person_id: str) -> None:
        self.get_person(person_id)
        del self.people[person_id]
        self.relationships = [
            r for r in self.relationships if not r.involves(person_id)
        ]
        self.sync_sibling_groups()

    def get_person(self, person_id: str) -> Person:
        if person_id not in self.people:
            raise KeyError(f"No person with id '{person_id}'")
        return self.people[person_id]

    def find_by_name(self, name: str) -> list[Person]:
        needle = name.lower()
        return [p for p in self.people.values() if needle in p.name.lower()]

    def add_relationship(
        self, rel_type: str, person_a_id: str, person_b_id: str
    ) -> Relationship:
        if person_a_id == person_b_id:
            raise ValueError("Cannot relate a person to themselves")

        rel_type = rel_type.lower()
        if rel_type == "child":
            rel_type = "parent"
            person_a_id, person_b_id = person_b_id, person_a_id

        if rel_type not in RELATIONSHIP_LABELS and rel_type != "child":
            raise ValueError(f"Unknown relationship type: {rel_type}")

        if rel_type == "parent":
            rel = self._add_parent(person_a_id, person_b_id)
            self.repair_relationship_consistency()
            self.sync_sibling_groups()
            return rel

        if rel_type in SYMMETRIC_TYPES:
            rel = self._add_symmetric(rel_type, person_a_id, person_b_id)
            self.repair_relationship_consistency()
            self.sync_sibling_groups()
            return rel

        raise ValueError(f"Unknown relationship type: {rel_type}")

    def remove_relationship(self, relationship_id: str) -> None:
        before = len(self.relationships)
        self.relationships = [
            r for r in self.relationships if r.id != relationship_id
        ]
        if len(self.relationships) == before:
            raise KeyError(f"No relationship with id '{relationship_id}'")
        self.sync_sibling_groups()

    def sibling_group_for(self, person_id: str) -> SiblingGroup | None:
        for group in self.sibling_groups.values():
            if person_id in group.order:
                return group if len(group.order) >= 2 else None
        return None

    def ordered_siblings(self, person_id: str) -> list[Person]:
        group = self.sibling_group_for(person_id)
        if not group:
            return []
        return [self.people[pid] for pid in group.order if pid in self.people]

    def sibling_order_info(self, person_id: str) -> dict | None:
        group = self.sibling_group_for(person_id)
        if not group:
            return None
        total = len(group.order)
        members = []
        for index, pid in enumerate(group.order):
            person = self.people.get(pid)
            if not person:
                continue
            members.append(
                {
                    "id": pid,
                    "name": person.name,
                    "birth": person.birth,
                    "label": birth_order_label(index, total),
                    "position": index,
                }
            )
        position = group.order.index(person_id) if person_id in group.order else -1
        return {
            "group_id": group.id,
            "members": members,
            "your_label": birth_order_label(position, total) if position >= 0 else None,
        }

    def set_sibling_order(self, group_id: str, ordered_ids: list[str]) -> SiblingGroup:
        if group_id not in self.sibling_groups:
            raise KeyError(f"No sibling group with id '{group_id}'")
        group = self.sibling_groups[group_id]
        expected = set(group.order)
        if len(ordered_ids) != len(set(ordered_ids)):
            raise ValueError("Order must include each sibling exactly once")
        if set(ordered_ids) != expected:
            raise ValueError("Order must include exactly the same siblings")
        group.order = list(ordered_ids)
        return group

    def sync_sibling_groups(self) -> None:
        clusters = self._sibling_clusters()
        old_groups = list(self.sibling_groups.values())
        self.sibling_groups = {}

        for members in clusters:
            if len(members) < 2:
                continue
            preserved = self._best_preserved_order(members, old_groups)
            group_id = self._best_preserved_group_id(members, old_groups)
            self.sibling_groups[group_id] = SiblingGroup(
                id=group_id, order=preserved
            )

    def repair_relationship_consistency(self) -> dict[str, int]:
        """
        Fill obvious missing links implied by the existing tree structure.

        Current rules:
        - If a child has exactly two parents, ensure those co-parents are linked
          as spouses.
        - If a child has exactly one known parent, and that parent has exactly
          one spouse, add the spouse as the missing co-parent.
        """
        added_spouses = 0
        added_parents = 0
        changed = True

        while changed:
            changed = False

            # Two known co-parents should appear as spouses.
            for person in list(self.people.values()):
                parents = self.parents_of(person.id)
                if len(parents) != 2:
                    continue
                a, b = parents
                if self._find_symmetric("spouse", a.id, b.id):
                    continue
                self._add_symmetric("spouse", a.id, b.id)
                added_spouses += 1
                changed = True

            # A sole known parent with exactly one spouse implies the spouse is
            # the missing co-parent, unless the child already has two parents.
            for person in list(self.people.values()):
                parents = self.parents_of(person.id)
                if len(parents) != 1:
                    continue
                sole_parent = parents[0]
                spouses = self.spouses_of(sole_parent.id)
                if len(spouses) != 1:
                    continue
                spouse = spouses[0]
                if spouse.id == person.id:
                    continue
                if self._find_relationship("parent", spouse.id, person.id):
                    continue
                if len(self.parents_of(person.id)) >= 2:
                    continue
                if self._is_ancestor(person.id, spouse.id):
                    continue
                self._add_parent(spouse.id, person.id)
                added_parents += 1
                changed = True

        return {"spouses_added": added_spouses, "parents_added": added_parents}

    def _best_preserved_group_id(
        self, members: set[str], old_groups: list[SiblingGroup]
    ) -> str:
        for group in old_groups:
            if set(group.order) == members:
                return group.id
        return uuid.uuid4().hex[:8]

    def _best_preserved_order(
        self, members: set[str], old_groups: list[SiblingGroup]
    ) -> list[str]:
        for group in old_groups:
            if set(group.order) == members:
                return list(group.order)
        for group in old_groups:
            overlap = [pid for pid in group.order if pid in members]
            if len(overlap) >= 2:
                rest = [pid for pid in members if pid not in overlap]
                return overlap + sorted(
                    rest,
                    key=lambda pid: self._default_sort_key(self.people[pid]),
                )
        return sorted(
            members, key=lambda pid: self._default_sort_key(self.people[pid])
        )

    def _default_sort_key(self, person: Person) -> tuple:
        birth = int(person.birth) if person.birth and person.birth.isdigit() else 9999
        return (birth, person.name.lower())

    def _sibling_clusters(self) -> list[set[str]]:
        parent = {pid: pid for pid in self.people}

        def find(x: str) -> str:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: str, b: str) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        children_by_parent: dict[str, list[str]] = defaultdict(list)
        for rel in self.relationships:
            if rel.type == "parent":
                children_by_parent[rel.person_a].append(rel.person_b)

        for children in children_by_parent.values():
            for i, child_a in enumerate(children):
                for child_b in children[i + 1 :]:
                    if child_a in parent and child_b in parent:
                        union(child_a, child_b)

        for rel in self.relationships:
            if rel.type in SIBLING_EDGE_TYPES:
                if rel.person_a in parent and rel.person_b in parent:
                    union(rel.person_a, rel.person_b)

        clusters: dict[str, set[str]] = defaultdict(set)
        for pid in self.people:
            clusters[find(pid)].add(pid)
        return [members for members in clusters.values() if len(members) >= 2]

    def connections_for(self, person_id: str) -> list[dict]:
        self.get_person(person_id)
        result: list[dict] = []
        for rel in self.relationships:
            if not rel.involves(person_id):
                continue
            other_id = rel.other(person_id)
            other = self.people[other_id]
            result.append(
                {
                    "id": rel.id,
                    "type": rel.type,
                    "label": self._connection_label(rel, person_id),
                    "other": other.to_dict(),
                }
            )
        result.sort(key=lambda item: (item["label"], item["other"]["name"]))
        return result

    def link_parent_child(self, parent_id: str, child_id: str) -> Relationship:
        return self._add_parent(parent_id, child_id)

    def link_spouse(self, person_a_id: str, person_b_id: str) -> Relationship:
        return self._add_symmetric("spouse", person_a_id, person_b_id)

    def parents_of(self, person_id: str) -> list[Person]:
        return [
            self.people[r.person_a]
            for r in self.relationships
            if r.type == "parent" and r.person_b == person_id
        ]

    def children_of(self, person_id: str) -> list[Person]:
        return [
            self.people[r.person_b]
            for r in self.relationships
            if r.type == "parent" and r.person_a == person_id
        ]

    def spouses_of(self, person_id: str) -> list[Person]:
        return self._symmetric_partners(person_id, "spouse")

    def siblings_of(self, person_id: str) -> list[Person]:
        partners: list[Person] = []
        for rel_type in ("sibling", "brother", "sister"):
            partners.extend(self._symmetric_partners(person_id, rel_type))
        seen: set[str] = set()
        unique: list[Person] = []
        for person in partners:
            if person.id not in seen:
                seen.add(person.id)
                unique.append(person)
        return unique

    def roots(self) -> list[Person]:
        has_parent = {r.person_b for r in self.relationships if r.type == "parent"}
        if not has_parent:
            return list(self.people.values())
        return [p for pid, p in self.people.items() if pid not in has_parent]

    def generations(self) -> list[list[Person]]:
        if not self.people:
            return []
        if self.has_parent_cycle():
            raise ValueError("Parent relationships contain an ancestry cycle")

        assigned = {person.id: 0 for person in self.roots()}
        changed = True
        while changed:
            changed = False
            for rel in self.relationships:
                if rel.type != "parent":
                    continue
                parent_gen = assigned.get(rel.person_a, 0)
                child_gen = parent_gen + 1
                if assigned.get(rel.person_b, -1) < child_gen:
                    assigned[rel.person_b] = child_gen
                    changed = True
                if assigned.get(rel.person_a, 0) < assigned[rel.person_b] - 1:
                    assigned[rel.person_a] = assigned[rel.person_b] - 1
                    changed = True
            for rel in self.relationships:
                if rel.type != "spouse":
                    continue
                gen_a = assigned.get(rel.person_a, 0)
                gen_b = assigned.get(rel.person_b, 0)
                target = max(gen_a, gen_b)
                if assigned.get(rel.person_a, 0) != target:
                    assigned[rel.person_a] = target
                    changed = True
                if assigned.get(rel.person_b, 0) != target:
                    assigned[rel.person_b] = target
                    changed = True

        for person_id in self.people:
            assigned.setdefault(person_id, 0)

        by_gen: dict[int, list[Person]] = {}
        for person in self.people.values():
            by_gen.setdefault(assigned[person.id], []).append(person)

        return [by_gen[i] for i in sorted(by_gen)]

    def to_dict(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "people": [p.to_dict() for p in self.people.values()],
            "relationships": [r.to_dict() for r in self.relationships],
            "sibling_groups": [g.to_dict() for g in self.sibling_groups.values()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> FamilyTree:
        tree = cls()
        for raw in data.get("people", []):
            person = Person.from_dict(raw)
            tree.people[person.id] = person
        tree.relationships = [
            Relationship.from_dict(r) for r in data.get("relationships", [])
        ]
        for raw in data.get("sibling_groups", []):
            group = SiblingGroup.from_dict(raw)
            tree.sibling_groups[group.id] = group
        tree.repair_relationship_consistency()
        tree.sync_sibling_groups()
        return tree

    def _add_parent(self, parent_id: str, child_id: str) -> Relationship:
        self._ensure_exists(parent_id, child_id)
        existing = self._find_relationship("parent", parent_id, child_id)
        if existing:
            return existing
        if len(self.parents_of(child_id)) >= 2:
            raise ValueError("A person cannot have more than two parents")
        if self._find_symmetric("spouse", parent_id, child_id):
            raise ValueError("A person cannot be both spouse and parent/child")
        if self._find_symmetric("sibling", parent_id, child_id):
            raise ValueError("A person cannot be both sibling and parent/child")
        if self._find_symmetric("brother", parent_id, child_id):
            raise ValueError("A person cannot be both sibling and parent/child")
        if self._find_symmetric("sister", parent_id, child_id):
            raise ValueError("A person cannot be both sibling and parent/child")
        if self._is_ancestor(child_id, parent_id):
            raise ValueError("Parent relationship would create an ancestry cycle")
        rel = Relationship("parent", parent_id, child_id)
        self.relationships.append(rel)
        return rel

    def _add_symmetric(
        self, rel_type: RelationshipType, person_a_id: str, person_b_id: str
    ) -> Relationship:
        self._ensure_exists(person_a_id, person_b_id)
        if rel_type in SIBLING_EDGE_TYPES:
            for sibling_type in SIBLING_EDGE_TYPES:
                existing = self._find_symmetric(
                    sibling_type, person_a_id, person_b_id
                )
                if existing:
                    if existing.type == rel_type:
                        return existing
                    raise ValueError(
                        "A sibling relationship already exists between these people"
                    )
        else:
            existing = self._find_symmetric(rel_type, person_a_id, person_b_id)
            if existing:
                return existing
        if rel_type == "spouse" and self._are_parent_child(person_a_id, person_b_id):
            raise ValueError("A person cannot be both spouse and parent/child")
        if rel_type in SIBLING_EDGE_TYPES and (
            self._are_parent_child(person_a_id, person_b_id)
            or self._find_symmetric("spouse", person_a_id, person_b_id)
        ):
            raise ValueError(
                "A person cannot be both sibling and spouse or parent/child"
            )
        a, b = sorted((person_a_id, person_b_id))
        rel = Relationship(rel_type, a, b)
        self.relationships.append(rel)
        return rel

    def _find_relationship(
        self, rel_type: str, person_a_id: str, person_b_id: str
    ) -> Relationship | None:
        for rel in self.relationships:
            if (
                rel.type == rel_type
                and rel.person_a == person_a_id
                and rel.person_b == person_b_id
            ):
                return rel
        return None

    def _find_symmetric(
        self, rel_type: str, person_a_id: str, person_b_id: str
    ) -> Relationship | None:
        pair = {person_a_id, person_b_id}
        for rel in self.relationships:
            if rel.type == rel_type and {rel.person_a, rel.person_b} == pair:
                return rel
        return None

    def _symmetric_partners(
        self, person_id: str, rel_type: str
    ) -> list[Person]:
        result = []
        for rel in self.relationships:
            if rel.type == rel_type and rel.involves(person_id):
                result.append(self.people[rel.other(person_id)])
        return result

    def _connection_label(self, rel: Relationship, viewer_id: str) -> str:
        other_id = rel.other(viewer_id)
        other = self.people[other_id]
        if rel.type == "parent":
            if rel.person_a == viewer_id:
                return f"Parent of {other.name}"
            return f"Child of {other.name}"
        return f"{RELATIONSHIP_LABELS[rel.type]} of {other.name}"

    def _ensure_exists(self, *ids: str) -> None:
        for person_id in ids:
            if person_id not in self.people:
                raise KeyError(f"No person with id '{person_id}'")

    def _are_parent_child(self, person_a_id: str, person_b_id: str) -> bool:
        return any(
            rel.type == "parent"
            and {rel.person_a, rel.person_b} == {person_a_id, person_b_id}
            for rel in self.relationships
        )

    def _is_ancestor(self, ancestor_id: str, descendant_id: str) -> bool:
        frontier = [ancestor_id]
        seen: set[str] = set()
        while frontier:
            current = frontier.pop()
            if current in seen:
                continue
            seen.add(current)
            for child in self.children_of(current):
                if child.id == descendant_id:
                    return True
                frontier.append(child.id)
        return False

    def has_parent_cycle(self) -> bool:
        children_by_parent: dict[str, list[str]] = defaultdict(list)
        for rel in self.relationships:
            if (
                rel.type == "parent"
                and rel.person_a in self.people
                and rel.person_b in self.people
            ):
                children_by_parent[rel.person_a].append(rel.person_b)

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(person_id: str) -> bool:
            if person_id in visiting:
                return True
            if person_id in visited:
                return False
            visiting.add(person_id)
            for child_id in children_by_parent.get(person_id, []):
                if visit(child_id):
                    return True
            visiting.remove(person_id)
            visited.add(person_id)
            return False

        return any(visit(person_id) for person_id in self.people)
