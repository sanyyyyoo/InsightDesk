"""
L1 "Krisha-corrected" case-level labels for the synthetic ground truth.

Krisha's manual audit (upstream data-recalibration 8801740,
data/ground_truth_corrections.csv) relabelled 5 calibration pairs as
NOT duplicates because one issue_id mixes different specific failures:
  invoice_missing_details  billing address vs tax breakdown ("different invoice fields")
  sync_not_updating        stale teammate updates vs cross-device sync
  mfa_setup_fails          enrollment timeout vs authenticator pairing

L1 splits ONLY these three issue ids into sub-issues. Every other issue id
is unchanged. Each core sentence's sub-issue and who decided it is written
to results/l1_label_map.csv for review. Krisha's data file is not modified;
output goes to experiments/dedup/labels/synthetic_l1.csv.

  python experiments/dedup/build_l1_labels.py
"""

import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(__file__))
from replay_lab import GROUND_TRUTH_PATH, strip_generator_templates  # noqa: E402

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "labels", "synthetic_l1.csv")
MAP_OUT = os.path.join(HERE, "results", "l1_label_map.csv")

# core sentence -> (sub-issue, decided_by)
K, S = "Krisha (ground_truth_corrections.csv)", "Sanyogita/Claude, applying Krisha's rule"
SPLITS = {
    "invoice_missing_details": {
        "Generated invoices are missing the company billing address.": ("invoice_missing_billing_address", K),
        "The invoice doesn't show a proper tax breakdown for accounting purposes.": ("invoice_missing_tax_breakdown", K),
        "Tax ID isn't showing up anywhere on the downloaded invoice.": ("invoice_missing_tax_id", S),
        "Invoice PDF is incomplete, some line items are blank.": ("invoice_blank_line_items", S),
    },
    "sync_not_updating": {
        "Records updated by a teammate don't reflect on my screen without a manual refresh.": ("sync_teammate_updates_stale", K),
        "Changes I make aren't syncing across devices.": ("sync_cross_device", K),
        "Cross-device sync just isn't happening anymore.": ("sync_cross_device", S),
        "Sync between the web app and mobile app is broken.": ("sync_cross_device", K),
        "Data updated on desktop doesn't show up on mobile until much later.": ("sync_cross_device", S),
    },
    "mfa_setup_fails": {
        "MFA enrollment keeps timing out before I can finish setup.": ("mfa_enrollment_timeout", K),
        "The authenticator app won't pair no matter how many times I scan the code.": ("mfa_authenticator_pairing", K),
        "Setting up two-factor authentication fails at the QR code step.": ("mfa_authenticator_pairing", S),
    },
}


def main():
    df = pd.read_csv(GROUND_TRUTH_PATH)
    core = df["complaint_text"].map(strip_generator_templates)
    new, rows = [], []
    for issue, c in zip(df["issue_id"], core):
        if issue in SPLITS:
            if c not in SPLITS[issue]:
                raise ValueError(f"unmapped sentence in {issue}: {c}")
            new.append(SPLITS[issue][c][0])
        else:
            new.append(issue)
    for issue, m in SPLITS.items():
        for sentence, (sub, who) in m.items():
            rows.append({"issue_id": issue, "core_sentence": sentence, "l1_sub_issue": sub, "decided_by": who,
                         "complaints": int(((df["issue_id"] == issue) & (core == sentence)).sum())})

    out = df.assign(issue_id=new)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.to_csv(OUT, index=False)
    pd.DataFrame(rows).to_csv(MAP_OUT, index=False)
    print(f"issues: {df.issue_id.nunique()} -> {out.issue_id.nunique()} (complaints unchanged: {len(out)})")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
