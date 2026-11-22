# Implementation decisions

1. **Keep source files unchanged.** CSV rows are read into memory and reconciliation output is a separate derived view.
2. **Normalize only record-reference format.** Trim, uppercase, and remove a leading `REC-` to handle the variation shown in the brief without fuzzy matching unrelated records.
3. **Use decimal arithmetic for currency.** Amounts are quantized to cents to avoid binary floating-point comparison errors.
4. **Resolve tenant scope before matching.** Each source is filtered through `locations.csv` first. A match in another organization's location cannot resolve a record in the selected organization.
5. **Treat split entries conservatively.** Multiple System B rows are aggregated only when every row is explicitly labelled as a part. Unmarked repeats remain review exceptions, not silently deduplicated.
6. **Expose exceptions, not silent guesses.** Each result contains a reason and explanatory detail. The UI supports reason filtering, searching, and sorting.
7. **Use a lightweight API/UI split.** Django provides the API and CSV parsing; React renders the comparison table. Reconciliation logic lives in a testable pure-Python module.
8. **Security boundary.** Organization filtering is implemented in the comparison service, but this prototype has no authentication. Do not deploy as a multi-tenant production service without authorization and request-level tenant enforcement.
