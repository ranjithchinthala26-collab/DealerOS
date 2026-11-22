from django.test import SimpleTestCase
from .engine import reconcile, norm_ref, money
class ReconciliationTests(SimpleTestCase):
    def setUp(self):
        self.locations=[{"location_id":"L-A","org_id":"ORG-A"},{"location_id":"L-B","org_id":"ORG-B"}]
        self.a=[{"record_id":"REC-1","location_id":"L-A","event_date":"2026-01-01","total_value":"10.00","state":"OK"}]
        self.b=[{"record_ref":"1","location_id":"L-A","recorded_on":"2026-01-01","value":"10","entry_id":"E1"}]
    def test_normalized_reference_and_money_match(self):
        self.assertEqual(norm_ref(" rec-1 "), "1")
        self.assertEqual(money("10"), money("10.00"))
        self.assertEqual(reconcile(self.a,self.b,self.locations)[0]["reason"],"Matched")
    def test_amount_difference(self):
        self.b[0]["value"]="11"
        self.assertEqual(reconcile(self.a,self.b,self.locations)[0]["reason"],"Amount mismatch")
    def test_date_difference(self):
        self.b[0]["recorded_on"]="2026-01-02"
        self.assertEqual(reconcile(self.a,self.b,self.locations)[0]["reason"],"Date mismatch")
    def test_missing_system_b(self):
        self.assertEqual(reconcile(self.a,[],self.locations)[0]["reason"],"Missing in System B")
    def test_missing_system_a(self):
        self.assertEqual(reconcile([],self.b,self.locations)[0]["reason"],"Missing in System A")
    def test_org_scope_excludes_other_tenant(self):
        self.b[0]["location_id"]="L-B"
        rows=reconcile(self.a,self.b,self.locations,"ORG-A")
        self.assertEqual([r["reason"] for r in rows],["Missing in System B"])
        self.assertNotIn("L-B",str(rows))
    def test_duplicate_system_b(self):
        self.assertEqual(reconcile(self.a,self.b+self.b,self.locations)[0]["reason"],"Duplicate in System B")
