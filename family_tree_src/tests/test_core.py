from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "family_tree_src"
sys.path.insert(0, str(SRC_ROOT))

from family_tree.export_html import export_html_document
from family_tree.model import SCHEMA_VERSION, FamilyTree
from family_tree.storage import load, validate_data


class FamilyTreeModelTests(unittest.TestCase):
    def test_current_tree_json_loads(self):
        tree = load(ROOT / "family_tree_src" / "data" / "tree.json")
        self.assertGreater(len(tree.people), 0)
        self.assertGreater(len(tree.relationships), 0)

    def test_schema_version_is_stable(self):
        self.assertEqual(SCHEMA_VERSION, 1)

    def test_share_html_includes_relationship_lines_and_ui(self):
        tree = FamilyTree()
        parent = tree.add_person("Parent")
        child = tree.add_person("Child")
        spouse = tree.add_person("Spouse")
        sibling = tree.add_person("Sibling")
        tree.add_relationship("parent", parent.id, child.id)
        tree.add_relationship("spouse", parent.id, spouse.id)
        tree.add_relationship("sibling", child.id, sibling.id)

        html = export_html_document(tree)

        self.assertIn("<svg", html)
        self.assertIn('class="tree-link"', html)
        self.assertIn('class="tree-link spouse"', html)
        self.assertIn('data-person-id="', html)
        self.assertIn('data-type="parent"', html)
        self.assertIn('id="zoom-in"', html)
        self.assertIn('id="people-search"', html)
        self.assertIn("function applySelection", html)
        self.assertIn("function renderSearch", html)
        self.assertNotIn("sample-line sibling", html)

    def test_repair_adds_missing_spouse_between_coparents(self):
        tree = FamilyTree()
        child = tree.add_person("Child")
        father = tree.add_person("Father")
        mother = tree.add_person("Mother")
        tree.link_parent_child(father.id, child.id)
        tree.link_parent_child(mother.id, child.id)

        repair = tree.repair_relationship_consistency()

        self.assertEqual(repair["spouses_added"], 1)
        spouse_ids = {person.id for person in tree.spouses_of(father.id)}
        self.assertIn(mother.id, spouse_ids)

    def test_repair_adds_missing_coparent_from_only_spouse(self):
        tree = FamilyTree()
        child = tree.add_person("Child")
        father = tree.add_person("Father")
        mother = tree.add_person("Mother")
        tree.link_spouse(father.id, mother.id)
        tree.link_parent_child(father.id, child.id)
        tree.relationships = [
            rel
            for rel in tree.relationships
            if not (
                rel.type == "parent"
                and rel.person_a == mother.id
                and rel.person_b == child.id
            )
        ]

        repair = tree.repair_relationship_consistency()

        self.assertEqual(repair["parents_added"], 1)
        parent_ids = {person.id for person in tree.parents_of(child.id)}
        self.assertIn(father.id, parent_ids)
        self.assertIn(mother.id, parent_ids)

    def test_validate_rejects_parent_cycles(self):
        bad_data = {
            "people": [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}],
            "relationships": [
                {"type": "parent", "person_a": "a", "person_b": "b"},
                {"type": "parent", "person_a": "b", "person_b": "a"},
            ],
            "sibling_groups": [],
        }

        with self.assertRaisesRegex(ValueError, "cycle"):
            validate_data(bad_data)


if __name__ == "__main__":
    unittest.main()
