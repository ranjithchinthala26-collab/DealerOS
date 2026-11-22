import csv
from pathlib import Path
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .engine import reconcile, read_csv_bytes
DATA=Path(__file__).resolve().parent.parent/"data"
def load_default(name):
    with open(DATA/name,newline="",encoding="utf-8-sig") as f: return list(csv.DictReader(f))
@api_view(["GET"])
def health(request): return Response({"status":"ok","service":"DealerOS reconciliation API"})
@api_view(["GET"])
def reference_data(request): return Response({"locations":load_default("locations.csv")})
@api_view(["POST"])
@parser_classes([MultiPartParser,FormParser])
def compare(request):
    try:
        def rows(field,default):
            return read_csv_bytes(request.FILES[field]) if field in request.FILES else load_default(default)
        a=rows("system_a","system_a.csv"); b=rows("system_b","system_b.csv"); locations=rows("locations","locations.csv")
        org=request.data.get("org_id") or None
        records=reconcile(a,b,locations,org)
        return Response({"records":records,"count":len(records),"org_id":org or "ALL"})
    except (ValueError,KeyError) as exc:
        return Response({"error":str(exc)},status=status.HTTP_400_BAD_REQUEST)
