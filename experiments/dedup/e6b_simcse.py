"""
E6b: unsupervised domain adaptation of MiniLM with SimCSE (no labels).

Trains all-MiniLM-L6-v2 on the 1,432 complaint texts of
data/master_complaints_v2.csv only (944 real + 488 synthetic; issue labels
are never read). Each text is encoded twice with dropout; the two views are
positives, the other texts in the batch are negatives (in-batch contrastive
loss, temperature 0.05). The text is exactly what the pipeline embeds:
boilerplate-suppressed, then clean_text.

This is transductive: the synthetic test complaints' TEXT is in the
unlabelled training corpus (as it would be in production, where the model
adapts on incoming complaints), but no label, pair or threshold is used.

CPU only, 4 threads (laptop heat). Saves to experiments/dedup/models/minilm-simcse
(git-excluded). Evaluate with:
  python experiments/dedup/compare_pipelines.py --model experiments/dedup/models/minilm-simcse ...

  python experiments/dedup/e6b_simcse.py [--epochs 1]
"""

import argparse
import os
import random
import sys

import numpy as np
import torch

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.preprocess import clean_text  # noqa: E402
from normalize import boilerplate_suppress  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "models", "minilm-simcse")
BASE = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    import pandas as pd
    from sentence_transformers import SentenceTransformer

    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--lr", type=float, default=3e-5)
    parser.add_argument("--temp", type=float, default=0.05)
    args = parser.parse_args()

    torch.set_num_threads(4)
    random.seed(0)
    np.random.seed(0)
    torch.manual_seed(0)

    texts = pd.read_csv("data/master_complaints_v2.csv")["complaint_text"].astype(str).tolist()
    model = SentenceTransformer(BASE, device="cpu")
    texts = [clean_text(t) for t in boilerplate_suppress(texts, model)]
    texts = [t for t in dict.fromkeys(texts) if t.strip()]          # unique, non-empty
    print(f"training texts: {len(texts)}", flush=True)

    model.train()
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr)
    step = 0
    for epoch in range(args.epochs):
        random.shuffle(texts)
        for k in range(0, len(texts) - 1, args.batch):
            batch = texts[k:k + args.batch]
            if len(batch) < 2:
                continue
            feats = model.tokenize(batch)
            z1 = model(dict(feats))["sentence_embedding"]            # dropout view 1
            z2 = model(dict(feats))["sentence_embedding"]            # dropout view 2
            z1, z2 = torch.nn.functional.normalize(z1, dim=-1), torch.nn.functional.normalize(z2, dim=-1)
            logits = z1 @ z2.T / args.temp
            loss = torch.nn.functional.cross_entropy(logits, torch.arange(len(batch)))
            opt.zero_grad()
            loss.backward()
            opt.step()
            step += 1
            if step % 10 == 0:
                print(f"epoch {epoch} step {step} loss {loss.item():.4f}", flush=True)
    model.eval()
    os.makedirs(OUT, exist_ok=True)
    model.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
