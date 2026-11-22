import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

function App() {
  const [rows, setRows] = useState([]);
  const [reason, setReason] = useState("All");
  const [org, setOrg] = useState("");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("record_id");
  const [msg, setMsg] = useState("Loading supplied CSVs…");

  async function run(files = {}, chosenOrg = org) {
    setMsg("Comparing…");

    const fd = new FormData();

    if (chosenOrg) {
      fd.append("org_id", chosenOrg);
    }

    Object.entries(files).forEach(([key, file]) => {
      if (file) {
        fd.append(key, file);
      }
    });

    try {
      const response = await fetch("/api/compare/", {
        method: "POST",
        body: fd,
      });

      const text = await response.text();

      let data;

      try {
        data = JSON.parse(text);
      } catch {
        throw new Error(
          ` Check the API connection.`
        );
      }

      if (!response.ok) {
        throw new Error(
          data.error || data.detail || `Request failed (HTTP ${response.status})`
        );
      }

      setRows(data.records || []);
      setMsg(
        `${data.count ?? data.records?.length ?? 0} reconciliation rows`
      );
    } catch (error) {
      setMsg(error.message || "Could not connect to the backend.");
    }
  }

  React.useEffect(() => {
    run();
  }, []);

  const reasons = ["All", ...new Set(rows.map((row) => row.reason))];

  const visible = useMemo(
    () =>
      rows
        .filter(
          (row) =>
            (reason === "All" || row.reason === reason) &&
            JSON.stringify(row).toLowerCase().includes(query.toLowerCase())
        )
        .sort((a, b) =>
          String(a[sort] || "").localeCompare(String(b[sort] || ""))
        ),
    [rows, reason, query, sort]
  );

  const counts = rows.reduce(
    (output, row) => {
      output[row.reason] = (output[row.reason] || 0) + 1;
      return output;
    },
    {}
  );

  function handleUpload() {
    const files = Object.fromEntries(
      ["system_a", "system_b", "locations"].map((key) => [
        key,
        document.getElementById(key).files[0],
      ])
    );

    run(files);
  }

  return (
    <main>
      <header>
        <div>
          <small>ADOSX · DEALEROS</small>
          <h1>Reconciliation workspace</h1>
          <p>Compare source records with a traceable reason for every result.</p>
        </div>
        <span className="status">● {msg}</span>
      </header>

      <section className="controls">
        <label>
          Organization
          <select
            value={org}
            onChange={(event) => {
              const selectedOrg = event.target.value;
              setOrg(selectedOrg);
              run({}, selectedOrg);
            }}
          >
            <option value="">All organizations</option>
            <option value="ORG-A">ORG-A</option>
            <option value="ORG-B">ORG-B</option>
          </select>
        </label>

        {["system_a", "system_b", "locations"].map((name, index) => (
          <label key={name}>
            {["System A CSV", "System B CSV", "Locations CSV"][index]}
            <input type="file" accept=".csv" id={name} />
          </label>
        ))}

        <button onClick={handleUpload}>Upload &amp; compare</button>
      </section>

      <section className="stats">
        <div>
          <b>{rows.length}</b>
          <span>Total results</span>
        </div>
        <div>
          <b>{counts.Matched || 0}</b>
          <span>Matched</span>
        </div>
        <div>
          <b>{rows.length - (counts.Matched || 0)}</b>
          <span>Needs review</span>
        </div>
      </section>

      <section className="tablewrap">
        <div className="tablehead">
          <h2>Reconciliation results</h2>

          <input
            placeholder="Search record, location, reason…"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />

          <select
            value={reason}
            onChange={(event) => setReason(event.target.value)}
          >
            {reasons.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>

          <select
            value={sort}
            onChange={(event) => setSort(event.target.value)}
          >
            <option value="record_id">Sort: record</option>
            <option value="reason">Sort: reason</option>
            <option value="system_a_amount">Sort: amount</option>
          </select>
        </div>

        <div className="scroll">
          <table>
            <thead>
              <tr>
                {[
                  "Reason",
                  "Record",
                  "System A location",
                  "System B location",
                  "A date",
                  "B date",
                  "A amount",
                  "B amount",
                  "Details",
                ].map((heading) => (
                  <th key={heading}>{heading}</th>
                ))}
              </tr>
            </thead>

            <tbody>
              {visible.map((row, index) => (
                <tr key={index}>
                  <td>
                    <span
                      className={
                        "pill " + (row.reason === "Matched" ? "ok" : "warn")
                      }
                    >
                      {row.reason}
                    </span>
                  </td>
                  <td>{row.record_id}</td>
                  <td>{row.system_a_location || "—"}</td>
                  <td>{row.system_b_location || "—"}</td>
                  <td>{row.system_a_date || "—"}</td>
                  <td>{row.system_b_date || "—"}</td>
                  <td>{row.system_a_amount || "—"}</td>
                  <td>{row.system_b_amount || "—"}</td>
                  <td>{row.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {!visible.length && (
            <p className="empty">No records match these filters.</p>
          )}
        </div>
      </section>

      <footer>
        Source data is compared within the selected organization scope. Confirm
        exceptions before taking operational action.
      </footer>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);