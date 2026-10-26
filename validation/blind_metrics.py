"""Read-only classification report for genuinely reviewed blind cases.

Reports descriptive metrics only; does not create labels or authenticate
reviewer identity. All calculations use the supplied case outcomes.
"""
from collections import Counter

def classification_report(evaluation):
    if evaluation.get("status") != "STRUCTURALLY_ACCEPTED_NOT_AUTHENTICATED":
        raise ValueError("blind intake did not pass")
    rows = evaluation["evaluation"]["cases"]
    if not rows:
        raise ValueError("no evaluated cases")
    counts = Counter((r["expected"], r["actual"]) for r in rows)
    labels = sorted({r["expected"] for r in rows} | {r["actual"] for r in rows if r["actual"] is not None})
    metrics = {}
    for label in labels:
        tp = counts[(label, label)]
        support = sum(v for (expected, _), v in counts.items() if expected == label)
        predicted = sum(v for (_, actual), v in counts.items() if actual == label)
        precision = tp / predicted if predicted else None
        recall = tp / support if support else None
        metrics[label] = {"support": support, "predicted": predicted,
                          "true_positive": tp, "precision": precision,
                          "recall": recall}
    return {"status": "DESCRIPTIVE_METRICS_NOT_AUTHENTICATED_ACCURACY",
            "total": len(rows), "correct": sum(r["pass"] for r in rows),
            "accuracy": sum(r["pass"] for r in rows) / len(rows),
            "labels": labels,
            "confusion_matrix": [
                {"expected": expected, "actual": actual, "count": count}
                for (expected, actual), count in sorted(counts.items(), key=lambda x: (str(x[0][0]), str(x[0][1])))
            ],
            "per_category": metrics}
