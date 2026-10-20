"""Protect consultation evidence, version separation and safe public comments."""
import csv
import hashlib
import importlib.util
import json
import math
import re
import unittest
import zipfile
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from lxml import html


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "consultation_under_test", ROOT / "scripts/consultation_portal.py"
)
PORTAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PORTAL)
DATA = ROOT / PORTAL.DATA.lstrip("/")
EMAIL = re.compile(r"[^\s<>\"@]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=";"))


class ConsultationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = read_json(DATA / "profil-37.json")
        cls.model = cls.profile["model_id"]
        cls.version = cls.profile["package_version"]
        cls.indicators = {item["code"]: item for item in cls.profile["indicators"]}
        cls.doc = html.parse(str(ROOT / PORTAL.PAGE))

    def test_page_and_csv_preserve_all_37_values_and_units(self):
        self.assertEqual(len(self.profile["indicators"]), 37)
        self.assertEqual(len(self.indicators), 37)
        roots = self.doc.xpath("//*[@data-consultation]")
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].get("data-model-id"), self.model)
        self.assertEqual(roots[0].get("data-package-version"), self.version)
        rows = self.doc.xpath("//tr[@data-code]")
        self.assertEqual(len(rows), 37)
        self.assertEqual({row.get("data-code") for row in rows}, set(self.indicators))
        for row in rows:
            item = self.indicators[row.get("data-code")]
            with self.subTest(indicator=item["code"]):
                self.assertEqual(Decimal(row.get("data-value")), item["value_per_kWh"])
                self.assertEqual(row.get("data-unit"), item["impact_unit"])
                visible = row.xpath("./td[contains(@class,'consult-result-value')]")[0].text
                self.assertEqual(
                    Decimal(visible.replace(",", ".")),
                    Decimal(format(float(item["value_per_kWh"]), ".6g")),
                )
        metric = self.doc.xpath("//*[@data-consultation-gwp]")[0]
        self.assertEqual(
            Decimal(metric.get("data-consultation-gwp")),
            self.indicators["GWP-total"]["value_per_kWh"],
        )
        exported = read_csv(DATA / "wskazniki-37.csv")
        self.assertEqual(len(exported), 37)
        self.assertEqual({row["code"] for row in exported}, set(self.indicators))
        for row in exported:
            item = self.indicators[row["code"]]
            self.assertEqual(row["model_id"], self.model)
            self.assertEqual(row["package_version"], self.version)
            self.assertEqual(row["status"], "consultation_candidate")
            self.assertEqual(Decimal(row["value_per_kWh"]), item["value_per_kWh"])
            self.assertEqual(row["impact_unit"], item["impact_unit"])
            self.assertEqual(row["denominator_unit"], "kWh")

    def test_candidate_is_separate_from_datasets_and_calculator_default(self):
        self.assertIs(self.profile["is_default"], False)
        for flag in (
            "production_approved",
            "formal_EN15804_qualification",
            "operator_decision_signed",
            "human_verification_recorded",
            "internal_checks_are_external_expert_review",
        ):
            self.assertIs(self.profile["status"][flag], False, flag)
        self.assertIs(self.profile["provenance"]["previous_profile_is_replaced"], False)
        catalog = read_json(ROOT / "data/portal-catalog.json")
        self.assertNotIn(self.model, str(catalog["datasets"]))
        self.assertFalse(
            any("/konsultacje/" in str(row) for row in catalog["datasets"]),
            "A consultation must remain a resource rather than a production dataset.",
        )
        regular_files = [
            ROOT / "data/datasets.json",
            ROOT / "data/default-methodology.json",
            *sorted((ROOT / "data/datasets").glob("*.json")),
        ]
        for path in regular_files:
            with self.subTest(path=path.name):
                self.assertNotIn(self.model, path.read_text())
                self.assertNotIn(PORTAL.DATA, path.read_text())
        calculator = html.parse(str(ROOT / "oblicz-energie-2025.html"))
        embedded = json.loads(
            calculator.xpath('//*[@id="energy-profile-data"]')[0].text,
            parse_float=Decimal,
        )
        previous = ROOT / self.profile["provenance"]["previous_public_profile"].lstrip("/")
        self.assertEqual(embedded, read_json(previous))
        self.assertNotEqual(embedded["model_id"], self.model)

    def test_quality_coverage_is_complete_and_not_presented_as_good_data(self):
        quality = read_json(DATA / "jakosc-danych.json")
        self.assertEqual(quality["model_id"], self.model)
        self.assertEqual(quality["package_version"], self.version)
        self.assertEqual(quality["recorded_decisions"], 73)
        self.assertEqual(quality["required_indicator_count"], 15)
        assessed = quality["indicators"]
        self.assertEqual(len(assessed), 15)
        self.assertEqual(len({row["indicator"] for row in assessed}), 15)
        self.assertEqual(sum(row["scope"] == "core_normative" for row in assessed), 13)
        self.assertEqual(
            {row["indicator"] for row in assessed if row["scope"] != "core_normative"},
            {"IRP", "RWD"},
        )
        for row in assessed:
            with self.subTest(indicator=row["indicator"]):
                self.assertIn(row["indicator"], self.indicators)
                coverage = float(row["assessed_absolute_coverage"])
                unassessed = float(row["unassessed_absolute_share"])
                self.assertGreaterEqual(coverage, 0)
                self.assertLessEqual(coverage, 1)
                self.assertTrue(math.isclose(coverage + unassessed, 1, abs_tol=1e-12))
                for dimension in ("time", "geography", "technology"):
                    shares = row["quality_shares"][dimension]
                    self.assertEqual(set(shares), {"1", "2", "3", "4", "5"})
                    self.assertTrue(all(0 <= share <= 1 for share in shares.values()))
                    self.assertTrue(math.isclose(
                        sum(float(share) for share in shares.values()), coverage,
                        abs_tol=1e-12,
                    ))
        checks = read_json(DATA / "kontrola-techniczna.json")["calculation_checks"]
        self.assertIs(checks["coverage_is_not_good_quality_share"], True)
        self.assertEqual(checks["required_quality_indicators_checked"], 15)
        self.assertEqual(
            checks["minimum_required_assessed_absolute_coverage"],
            min(row["assessed_absolute_coverage"] for row in assessed),
        )

    def test_sensitivity_contains_17_complete_scenarios_with_correct_central_values(self):
        rows = read_csv(DATA / "wrazliwosc-37.csv")
        self.assertEqual(len(rows), 17 * 37)
        scenarios = defaultdict(list)
        for row in rows:
            scenarios[row["scenario"]].append(row)
            self.assertEqual(row["model_id"], self.model)
            self.assertEqual(row["package_version"], self.version)
            item = self.indicators[row["indicator"]]
            self.assertEqual(Decimal(row["central"]), item["value_per_kWh"])
            self.assertEqual(row["unit"], item["impact_unit"] + "/kWh")
            value, central = float(row["value"]), float(row["central"])
            self.assertTrue(math.isfinite(value))
            self.assertTrue(math.isclose(
                float(row["difference"]), value - central, rel_tol=1e-11, abs_tol=1e-15
            ))
            if central:
                self.assertTrue(math.isclose(
                    float(row["difference_percent"]),
                    (value - central) / central * 100,
                    rel_tol=1e-10, abs_tol=1e-10,
                ))
        self.assertEqual(len(scenarios), 17)
        central_scenarios = []
        pairs = set()
        for scenario, values in scenarios.items():
            with self.subTest(scenario=scenario):
                self.assertEqual(len(values), 37)
                self.assertEqual({row["indicator"] for row in values}, set(self.indicators))
                pair = {(Decimal(row["q_hardcoal"]), Decimal(row["q_lignite"])) for row in values}
                self.assertEqual(len(pair), 1)
                pairs.update(pair)
                if pair == {(Decimal("0.35"), Decimal("0.35"))}:
                    central_scenarios.append(scenario)
                    for row in values:
                        self.assertEqual(Decimal(row["value"]), Decimal(row["central"]))
        self.assertEqual(len(pairs), 17)
        self.assertEqual(len(central_scenarios), 1)

    def test_manifest_and_zip_match_exact_payload_excluding_live_register(self):
        manifest = read_json(DATA / "manifest.json")
        self.assertEqual(manifest["model_id"], self.model)
        self.assertEqual(manifest["package_version"], self.version)
        self.assertEqual(manifest["hash_algorithm"], "SHA-256")
        self.assertEqual(manifest["live_register_excluded"], "uwagi.json")
        files = manifest["files"]
        self.assertNotIn("uwagi.json", files)
        self.assertNotIn("manifest.json", files)
        archives = list(DATA.glob("*.zip"))
        self.assertEqual(len(archives), 1)
        with zipfile.ZipFile(archives[0]) as archive:
            names = archive.namelist()
            self.assertEqual(len(names), len(set(names)))
            self.assertEqual(set(names), set(files) | {"manifest.json"})
            self.assertIsNone(archive.testzip())
            for name in names:
                with self.subTest(filename=name):
                    self.assertEqual(Path(name).name, name)
                    payload = (DATA / name).read_bytes()
                    self.assertEqual(archive.read(name), payload)
                    if name in files:
                        self.assertEqual(len(payload), files[name]["bytes"])
                        self.assertEqual(hashlib.sha256(payload).hexdigest(), files[name]["sha256"])

    def test_public_register_has_no_contact_data_and_matches_its_version(self):
        register = read_json(DATA / "uwagi.json")
        self.assertEqual(register["model_id"], self.model)
        self.assertEqual(register["package_version"], self.version)
        self.assertNotRegex((DATA / "uwagi.json").read_text(), EMAIL)
        for entry in register["entries"]:
            self.assertEqual(entry["package_version"], self.version)
            self.assertFalse(
                any("email" in key.lower().replace("-", "").replace("_", "") for key in entry)
            )
        rendered = html.fragment_fromstring(
            PORTAL.registry(register["entries"], self.version), create_parent="div"
        )
        self.assertEqual(
            len(rendered.xpath(".//article[contains(@class,'consult-comment')]")),
            len(register["entries"]),
        )
        self.assertEqual(
            int(self.doc.xpath("//*[@data-consultation-registry]")[0].get("data-entry-count")),
            len(register["entries"]),
        )

    def sample_entry(self):
        return {
            "id": "TEST-001",
            "package_version": self.version,
            "status": "received",
            "submitted_at": "2026-10-20",
            "author_label": "Czytelnik",
            "topic": "Alokacja",
            "section": "Sekcja 3",
            "comment": "Proszę sprawdzić założenie.",
            "source": "Źródło publiczne",
            "proposal": "Porównać wariant.",
        }

    def test_registry_renders_topic_version_and_escapes_all_text(self):
        entry = self.sample_entry()
        payload = '<img src=x onerror="alert(1)"><script>alert(2)</script> & "tekst"'
        fields = ("topic", "author_label", "section", "comment", "source", "proposal",
                  "response", "resolution", "changed_in_version")
        for field in fields:
            entry[field] = field + ": " + payload
        fragment = html.fragment_fromstring(
            PORTAL.registry([entry], self.version), create_parent="div"
        )
        self.assertEqual(fragment.xpath(".//h3")[0].text_content(), entry["topic"])
        self.assertIn(self.version, fragment.text_content())
        for field in fields:
            self.assertIn(entry[field], fragment.text_content(), field)
        self.assertFalse(fragment.xpath(".//script|.//img|.//@onerror|.//@onclick"))

    def test_registry_rejects_wrong_version_private_email_and_unresolved_resolution(self):
        entry = self.sample_entry()
        with self.assertRaises(ValueError):
            PORTAL.registry([dict(entry, package_version="1999-01-01.1")], self.version)
        for field in ("comment", "source", "author_label", "email"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                PORTAL.registry([dict(entry, **{field: "private.person@example.org"})], self.version)
        with self.assertRaises(ValueError):
            PORTAL.registry([dict(entry, status="resolved")], self.version)
        PORTAL.registry([dict(entry, status="resolved", resolution="Uwzględniono.")], self.version)
        with self.assertRaises(ValueError):
            PORTAL.registry([entry, entry], self.version)

    def test_all_six_steps_and_submission_fallback_are_available_without_javascript(self):
        copy = read_json(ROOT / "content/consultation-energy.json")
        steps = self.doc.xpath("//*[@data-step]")
        self.assertEqual(len(steps), 6)
        self.assertEqual(
            [step.get("id") for step in steps],
            ["krok-" + item["id"] for item in copy["steps"]],
        )
        self.assertEqual(
            [item["state"] for item in copy["steps"]],
            ["completed", "completed", "completed", "completed", "planned", "open"],
        )
        for step, expected in zip(steps, copy["steps"]):
            self.assertFalse(step.xpath("ancestor-or-self::*[@hidden or @aria-hidden='true']"))
            self.assertIn(expected["text"], step.text_content())
            self.assertEqual(step.xpath(".//a/@href"), [expected["evidence_href"]])
        self.assertEqual(len(copy["questions"]), 4)
        self.assertEqual(len(self.doc.xpath("//*[contains(@class,'consult-question')][@id]")), 4)
        self.assertTrue(self.doc.xpath("//*[@id='consult-form-fields'][@disabled]"))
        self.assertFalse(self.doc.xpath("//*[@id='consultation-form']//*[@name]"))
        fallback = self.doc.xpath("//*[@id='zglos-uwage']//noscript")[0]
        self.assertIn(self.version, fallback.text_content())
        self.assertTrue(fallback.xpath(".//a[starts-with(@href,'mailto:')]"))


if __name__ == "__main__":
    unittest.main()
