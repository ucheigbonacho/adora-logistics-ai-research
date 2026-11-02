"""Read-only provenance and schema audit of 30 user-supplied logistics records."""
import collections
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

REQUIRED=("case_id","timestamp","scenario","expected","signal_metric","kind",
          "utterance","telemetry_checksum_sha256","reviewer_id","approval_ref")
LABELS={"routine","exception","escalate"}

def audit(path, as_of="2026-11-02T23:59:59Z"):
    data=Path(path).read_bytes()
    rows=[json.loads(line) for line in data.decode("utf-8").splitlines() if line.strip()]
    cutoff=dt.datetime.fromisoformat(as_of.replace("Z","+00:00"))
    seen=set()
    issues=[]
    groups=collections.Counter()
    for i,row in enumerate(rows,1):
        if not isinstance(row,dict):
            issues.append({"row":i,"issue":"not_object"})
            continue
        missing=[k for k in REQUIRED if k not in row]
        if missing:
            issues.append({"row":i,"issue":"missing_fields","fields":missing})
            continue
        ident=row["case_id"]
        if ident in seen:
            issues.append({"row":i,"issue":"duplicate_id","case_id":ident})
        seen.add(ident)
        try:
            stamp=dt.datetime.fromisoformat(row["timestamp"].replace("Z","+00:00"))
            if stamp.tzinfo is None:
                raise ValueError("missing timezone")
            actual_quarter=f"Q{(stamp.month-1)//3+1}"
            groups[actual_quarter]+=1
            if stamp>cutoff:
                issues.append({"row":i,"issue":"future_timestamp","case_id":ident})
            label=re.search(r"-Q([1-4])-",ident)
            if label and f"Q{label.group(1)}"!=actual_quarter:
                issues.append({"row":i,"issue":"id_quarter_mismatch","case_id":ident})
        except (TypeError,ValueError,AttributeError):
            issues.append({"row":i,"issue":"invalid_timestamp","case_id":ident})
        if row["expected"] not in LABELS:
            issues.append({"row":i,"issue":"unknown_label","case_id":ident})
        metric=row["signal_metric"]
        if isinstance(metric,bool) or not isinstance(metric,(int,float)) or not 0<=metric<=1:
            issues.append({"row":i,"issue":"invalid_metric","case_id":ident})
        checksum=row["telemetry_checksum_sha256"]
        if not isinstance(checksum,str) or re.fullmatch("[0-9a-fA-F]{64}",checksum) is None:
            issues.append({"row":i,"issue":"unverifiable_truncated_checksum","case_id":ident})
    return {"basis":"USER_SUPPLIED_RECORDS_PROVENANCE_NOT_AUTHENTICATED",
            "input_sha256":hashlib.sha256(data).hexdigest(),
            "total":len(rows),"by_actual_quarter":dict(groups),"issues":issues}

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("jsonl")
    parser.add_argument("--as-of",default="2026-11-02T23:59:59Z")
    args=parser.parse_args()
    print(json.dumps(audit(args.jsonl,args.as_of),indent=2))
