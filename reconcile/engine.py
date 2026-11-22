import csv, io
from collections import defaultdict
from decimal import Decimal, InvalidOperation

REASONS=("Matched","Missing in System B","Missing in System A","Amount mismatch","Date mismatch","Location mismatch","Duplicate in System B","Invalid reference")

def read_csv_bytes(upload):
    raw=upload.read()
    for encoding in ("utf-8-sig","utf-8"):
        try: return list(csv.DictReader(io.StringIO(raw.decode(encoding))))
        except UnicodeDecodeError: continue
    raise ValueError("CSV must be UTF-8 encoded.")

def norm_ref(value):
    value=(value or "").strip().upper()
    return value[4:] if value.startswith("REC-") else value

def money(value):
    try: return Decimal(str(value).strip()).quantize(Decimal("0.01"))
    except (InvalidOperation,ValueError,TypeError): return None

def reconcile(system_a,system_b,locations,org_id=None):
    loc_org={str(x["location_id"]).strip():str(x["org_id"]).strip().upper() for x in locations}
    org=(org_id or "").strip().upper()
    def in_scope(row):
        loc=str(row.get("location_id","")).strip()
        return bool(loc) and (not org or loc_org.get(loc)==org)
    a_rows=[dict(r) for r in system_a if in_scope(r)]
    b_rows=[dict(r) for r in system_b if in_scope(r)]
    a_by,b_by=defaultdict(list),defaultdict(list)
    for row in a_rows:
        key=norm_ref(row.get("record_id"))
        if key: a_by[key].append(row)
    for row in b_rows:
        key=norm_ref(row.get("record_ref"))
        if key: b_by[key].append(row)
    out,used_b=[],set()
    def result(reason,a=None,b=None,detail=""):
        a,b=a or {},b or {}
        return {"reason":reason,"record_id":a.get("record_id") or b.get("record_ref") or "",
        "system_a_location":a.get("location_id",""),"system_b_location":b.get("location_id",""),
        "system_a_date":a.get("event_date",""),"system_b_date":b.get("recorded_on",""),
        "system_a_amount":str(money(a.get("total_value")) or ""),
        "system_b_amount":str(money(b.get("value")) or ""),
        "system_a_state":a.get("state",""),"system_b_entry":b.get("entry_id",""),"detail":detail}
    for key,group_a in a_by.items():
        group_b=b_by.get(key,[])
        if not group_b:
            for a in group_a: out.append(result("Missing in System B",a=a,detail="No System B entry references this record."))
            continue
        if len(group_a)>1 or len(group_b)>1:
            # Explicitly labelled part entries are legitimate only when they form a complete set.
            marked_parts = [x for x in group_b if "part" in str(x.get("label","")).lower()]
            # The brief's split example labels only the continuation row ("part 2 of 2").
            # Accept it only when the stated total equals the number of entries in this group.
            import re
            expected = []
            for x in marked_parts:
                match = re.search(r"part\s+\d+\s+of\s+(\d+)", str(x.get("label","")).lower())
                if match: expected.append(int(match.group(1)))
            valid_split = bool(marked_parts) and len(expected)==len(marked_parts) and len(set(expected))==1 and expected[0]==len(group_b)
            if len(group_a)==1 and valid_split and len(group_b)>1:
                parts=group_b
                a=group_a[0]
                totals=[money(x.get("value")) for x in parts]
                part_sum=sum((v for v in totals if v is not None),Decimal("0.00"))
                first=parts[0]
                used_b.update(id(x) for x in group_b)
                if any(x.get("location_id")!=first.get("location_id") or x.get("recorded_on")!=first.get("recorded_on") for x in parts):
                    reason,detail="Location mismatch","Split entries disagree on location or date; manual review required."
                elif part_sum!=money(a.get("total_value")):
                    reason,detail="Amount mismatch",f"Split entry sum ({part_sum}) differs from System A total."
                else:
                    reason,detail="Matched",f"Explicitly labelled split entries sum to {part_sum} and match System A."
                row=result(reason,a,first,detail)
                row["system_b_entry"]=", ".join(x.get("entry_id","") for x in parts)
                row["system_b_amount"]=str(part_sum)
                out.append(row)
            else:
                for a in group_a:
                    out.append(result("Duplicate in System B" if len(group_b)>1 else "Invalid reference",a=a,b=group_b[0],
                    detail=f"Reference occurs {len(group_a)} time(s) in A and {len(group_b)} time(s) in B; needs review."))
                used_b.update(id(x) for x in group_b)
            continue
        a,b=group_a[0],group_b[0]; used_b.add(id(b))
        if str(a.get("location_id","")).strip()!=str(b.get("location_id","")).strip():
            reason,detail="Location mismatch","Locations differ; verify both locations belong to the selected organization."
        elif str(a.get("event_date","")).strip()!=str(b.get("recorded_on","")).strip():
            reason,detail="Date mismatch","Event date and recorded date differ."
        elif money(a.get("total_value"))!=money(b.get("value")):
            reason,detail="Amount mismatch","Normalized amounts differ."
        else: reason,detail="Matched","Reference, location, date, and amount agree."
        out.append(result(reason,a,b,detail))
    for b in b_rows:
        key=norm_ref(b.get("record_ref"))
        if id(b) in used_b: continue
        if not key: out.append(result("Invalid reference",b=b,detail="System B reference is blank or cannot be normalized."))
        elif key not in a_by: out.append(result("Missing in System A",b=b,detail="No System A record references this entry."))
    return sorted(out,key=lambda r:(r["reason"],r["record_id"],r["system_b_entry"]))
