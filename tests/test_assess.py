"""Mutation test for scripts/assess_san_francisco.py. Run: python3 -I tests/test_assess.py -v

Copies the real San Francisco ledger into a temp root, symlinks the real archives, damages three
claims, and checks that the assessor demotes exactly those to speculative and nothing else.
Skipped when the archives are not present.
"""
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import assess_san_francisco as assess  # noqa: E402

DAMAGED = {"sf-pci-citywide-2023", "sf-blocks-resurfaced-as-of-2025-11", "sf-avg-cost-per-paved-block-2025-11", "sf-blocks-paved-2025",
           "sf311-pavement-defect-cases-2020", "sf-pothole-service-orders-2025", "sf-pothole-response-72h-mean-2023"}


@unittest.skipUnless((REPO / "cities/san-francisco/claims.yaml").exists() and (REPO / "sources").is_dir(), "no San Francisco data")
class AssessMutation(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "cities").mkdir()
        shutil.copytree(REPO / "cities/san-francisco", self.root / "cities/san-francisco")
        (self.root / "sources").symlink_to(REPO / "sources")
        self.path = self.root / "cities/san-francisco/claims.yaml"

    def tearDown(self):
        shutil.rmtree(self.root)

    def confidence(self):
        return {c["id"]: c["confidence"] for c in yaml.safe_load(self.path.read_text())}

    def test_undamaged_ledger_has_no_demotions(self):
        self.assertEqual(assess.main(["--root", str(self.root)]), 0)
        self.assertNotIn("speculative", self.confidence().values())

    def test_damaged_claims_are_demoted_and_others_are_not(self):
        claims = yaml.safe_load(self.path.read_text())
        for c in claims:
            if c["id"] == "sf-blocks-resurfaced-as-of-2025-11":
                c["value"] = 9149
                c["statement"] = c["statement"].replace("9,148", "9,149")
            if c["id"] == "sf-pci-citywide-2023":
                c["period"] = "2022"
            if c["id"] == "sf-blocks-paved-2025":
                c["value"] = 582
                c["statement"] = c["statement"].replace("581", "582")
            if c["id"] == "sf311-pavement-defect-cases-2020":  # off by one: inside the suppression tolerance, caught by the exact path
                c["value"] = 4583
                c["statement"] = c["statement"].replace("4,582", "4,583")
            if c["id"] == "sf-pothole-service-orders-2025":
                c["value"] = 848
                c["statement"] = c["statement"].replace("847", "848")
            if c["id"] == "sf-pothole-response-72h-mean-2023":  # the old float rounding answer
                c["value"] = 89.2
                c["statement"] = c["statement"].replace("89.3", "89.2")
            if c["id"] == "sf-avg-cost-per-paved-block-2025-11":
                c["archive"] = c["archive"].replace("5", "6", 1)
        self.path.write_text(yaml.safe_dump(claims, sort_keys=False))
        assess.main(["--root", str(self.root)])
        demoted = {k for k, v in self.confidence().items() if v == "speculative"}
        self.assertEqual(demoted, DAMAGED)


    def test_every_claim_in_the_ledger_has_a_derivation(self):
        ids = {c["id"] for c in yaml.safe_load(self.path.read_text())}
        self.assertEqual(sorted(ids - set(assess.DERIVE)), [], "claims added without an Assess derivation")

    def test_unassessed_claim_is_capped_at_provisional_not_demoted(self):
        claims = yaml.safe_load(self.path.read_text())
        extra = dict(next(c for c in claims if c["id"] == "sf-pci-citywide-2023"))
        extra["id"] = "sf-new-claim-without-derivation"
        extra["confidence"] = "supported"
        claims.append(extra)
        self.path.write_text(yaml.safe_dump(claims, sort_keys=False))
        assess.main(["--root", str(self.root)])
        self.assertEqual(self.confidence()["sf-new-claim-without-derivation"], "provisional")


if __name__ == "__main__":
    unittest.main()
