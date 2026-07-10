const steps = [
  { id: "target", title: "Choose Target Spacecraft" },
  { id: "tle", title: "Show TLEs" },
  { id: "hyperparams", title: "Choose Conjunction Hyperparameters" },
  { id: "nearest", title: "Preview Nearest Objects" },
  { id: "propagation", title: "Fetch CelesTrak Records + SGP4" },
  { id: "search", title: "Post-MTE Phase Guess Search" },
  { id: "pareto", title: "Pareto Front Plot" },
];

const summary = {
  operator: {
    name: "TANAGER-1",
    catnr: 60507,
    epoch: "2026-07-09T16:54:52.662816+00:00",
    inclinationDeg: 97.2281,
    meanMotionRevDay: 15.43935842,
    periodMin: 93.26812428517998,
    perigeeAltKm: 432.62435218671453,
    apogeeAltKm: 436.38901908739626,
  },
  rawCatalogRows: 15985,
  prefilterCatalogRows: 663,
  screenedCatalogRows: 25,
  phaseGuessCandidateCount: 27,
  recoverableCandidateCount: 21,
  selectedCandidateCount: 3,
};

const tle = [
  "TANAGER-1",
  "1 60507U 24149AR  26190.70477619  .00000245  00000+0  72329-5 0  9995",
  "2 60507  97.2281 284.8679 0002763 147.2432 212.8988 15.43935842106519",
];

const nearestObjects = [
  { name: "ASTROCAST-0401", norad: 55110, missKm: 52.157, tcaMin: 75.0, inc: 97.5559, mm: 15.28412847 },
  { name: "LEMUR-2-JK0903EM1407", norad: 58336, missKm: 586.747, tcaMin: 165.0, inc: 97.3917, mm: 15.52862811 },
  { name: "OUTPOST MISSION 2", norad: 58334, missKm: 970.002, tcaMin: 0.0, inc: 97.3961, mm: 15.59484684 },
  { name: "2024-016A", norad: 58820, missKm: 1196.562, tcaMin: 186.53, inc: 97.4479, mm: 15.56411123 },
  { name: "FLOCK 4Q-7", norad: 58318, missKm: 1941.092, tcaMin: 186.53, inc: 97.3904, mm: 15.57050195 },
  { name: "2024-110B", norad: 60013, missKm: 2205.642, tcaMin: 0.0, inc: 97.573, mm: 15.22777191 },
  { name: "IPERDRONE.0", norad: 60520, missKm: 2513.07, tcaMin: 0.0, inc: 97.3764, mm: 15.70168447 },
];

const selectedCandidates = [
  {
    id: "out30_delay1800_rec900",
    outage: 30,
    ballisticMin: 30.5,
    recoveryMin: 15,
    terminalKm: 0.00143,
    deltaV: 0.00567,
    newClose: 0,
    nearest: "ASTROCAST-0401",
    missKm: 185.767,
  },
  {
    id: "out300_delay1800_rec900",
    outage: 300,
    ballisticMin: 35,
    recoveryMin: 15,
    terminalKm: 0.01482,
    deltaV: 0.00567,
    newClose: 0,
    nearest: "ASTROCAST-0401",
    missKm: 175.152,
  },
  {
    id: "out600_delay1800_rec900",
    outage: 600,
    ballisticMin: 40,
    recoveryMin: 15,
    terminalKm: 0.03437,
    deltaV: 0.00567,
    newClose: 0,
    nearest: "ASTROCAST-0401",
    missKm: 158.152,
  },
];

const searchPoints = [
  [0.5, 0.00058, 0.00567],
  [10.5, 0.00057, 0.00567],
  [30.5, 0.00143, 0.00567],
  [0.5, 0.00487, 0.01323],
  [10.5, 0.00551, 0.01323],
  [30.5, 0.00657, 0.01323],
  [0.5, 0.03514, 0.02646],
  [35.0, 0.01482, 0.00567],
  [40.0, 0.03437, 0.00567],
];

const events = [
  ["request", "CelesTrak GP query for TANAGER-1 TLE by NORAD catalog ID 60507"],
  ["catalog", "Active catalog CSV parsed and normalized into orbital-element features"],
  ["filter", "Local catalog filtered using altitude, inclination, RAAN, and mean-motion gates"],
  ["propagate", "Operator and local objects propagated with SGP4 over the screening window"],
  ["rank", "Objects ranked by minimum baseline miss distance and TCA offset"],
];

const fmt = new Intl.NumberFormat("en-US", { maximumFractionDigits: 3 });

function setText(id, text) {
  document.getElementById(id).textContent = text;
}

function renderSteps() {
  const list = document.getElementById("stepList");
  list.innerHTML = steps
    .map(
      (step, index) => `
        <button class="step-button ${index === 0 ? "active" : ""}" data-step="${step.id}">
          <span>${index + 1}</span>
          <strong>${step.title}</strong>
        </button>
      `,
    )
    .join("");

  list.addEventListener("click", (event) => {
    const button = event.target.closest(".step-button");
    if (!button) return;
    activateStep(button.dataset.step);
  });
}

function activateStep(stepId) {
  document.querySelectorAll(".step-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.step === stepId);
  });
  document.querySelectorAll(".panel").forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.panel === stepId);
  });
  setText("stepTitle", steps.find((step) => step.id === stepId).title);
}

function renderSummary() {
  const op = summary.operator;
  setText("runEpoch", new Date(op.epoch).toLocaleString());
  setText("catalogRows", fmt.format(summary.screenedCatalogRows));
  setText("candidateCount", fmt.format(summary.phaseGuessCandidateCount));
  setText("selectedCount", fmt.format(summary.selectedCandidateCount));
  setText("meanMotion", `${op.meanMotionRevDay.toFixed(5)} rev/day`);
  setText("inclination", `${op.inclinationDeg.toFixed(4)} deg`);
  setText("period", `${op.periodMin.toFixed(2)} min`);
  setText("altitudeBand", `${op.perigeeAltKm.toFixed(1)}-${op.apogeeAltKm.toFixed(1)} km`);
  setText("tleBlock", tle.join("\n"));
  setText("rawCatalog", fmt.format(summary.rawCatalogRows));
  setText("prefiltered", fmt.format(summary.prefilterCatalogRows));
  setText("screened", fmt.format(summary.screenedCatalogRows));
  setText("nearestMiss", `${nearestObjects[0].missKm.toFixed(2)} km`);
  setText("recoverableCount", `${summary.recoverableCandidateCount} recoverable`);
}

function renderHyperparams() {
  const controls = [
    ["catalogSize", "catalogSizeValue", " objects"],
    ["windowOrbits", "windowOrbitsValue", " orbits"],
    ["closeThreshold", "closeThresholdValue", " km"],
  ];
  controls.forEach(([inputId, outputId, suffix]) => {
    const input = document.getElementById(inputId);
    const output = document.getElementById(outputId);
    const update = () => {
      output.value = `${input.value}${suffix}`;
    };
    input.addEventListener("input", update);
    update();
  });
}

function renderNearestObjects() {
  document.getElementById("nearestRows").innerHTML = nearestObjects
    .map(
      (row) => `
        <tr>
          <td>${row.name}</td>
          <td>${row.norad}</td>
          <td>${row.missKm.toFixed(2)}</td>
          <td>${row.tcaMin.toFixed(2)}</td>
          <td>${row.inc.toFixed(4)}</td>
          <td>${row.mm.toFixed(5)}</td>
        </tr>
      `,
    )
    .join("");
}

function renderEvents() {
  document.getElementById("eventList").innerHTML = events
    .map(([label, text]) => `<li><span>${label}</span><strong>${text}</strong></li>`)
    .join("");
}

function renderCandidates() {
  document.getElementById("candidateList").innerHTML = selectedCandidates
    .map(
      (c) => `
        <article class="candidate-card">
          <header>
            <strong>${c.id}</strong>
            <span class="pill">${c.outage} s outage</span>
          </header>
          <dl>
            <div><dt>Ballistic</dt><dd>${c.ballisticMin.toFixed(1)} min</dd></div>
            <div><dt>Recovery</dt><dd>${c.recoveryMin.toFixed(1)} min</dd></div>
            <div><dt>Terminal error</dt><dd>${c.terminalKm.toFixed(5)} km</dd></div>
            <div><dt>Extra delta-v</dt><dd>${c.deltaV.toFixed(5)} m/s</dd></div>
            <div><dt>New close approaches</dt><dd>${c.newClose}</dd></div>
            <div><dt>Nearest object</dt><dd>${c.nearest}</dd></div>
          </dl>
        </article>
      `,
    )
    .join("");
}

function renderSearchChart() {
  const chart = document.getElementById("searchChart");
  const width = 720;
  const height = 360;
  const pad = 48;
  const xs = searchPoints.map((p) => p[0]);
  const ys = searchPoints.map((p) => p[1]);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const sx = (x) => pad + ((x - minX) / (maxX - minX)) * (width - pad * 2);
  const sy = (y) => height - pad - ((y - minY) / (maxY - minY)) * (height - pad * 2);
  const points = searchPoints
    .map(([x, y, dv]) => {
      const r = 5 + dv * 220;
      const color = dv > 0.02 ? "#f5c85b" : dv > 0.01 ? "#62d2c6" : "#7aa7ff";
      return `<circle cx="${sx(x)}" cy="${sy(y)}" r="${r.toFixed(1)}" fill="${color}" opacity="0.82" />`;
    })
    .join("");
  const paretoPath = selectedCandidates.map((c, i) => `${i === 0 ? "M" : "L"} ${sx(c.ballisticMin)} ${sy(c.terminalKm)}`).join(" ");

  chart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img">
      <line x1="${pad}" y1="${height - pad}" x2="${width - pad}" y2="${height - pad}" stroke="#36505f" />
      <line x1="${pad}" y1="${pad}" x2="${pad}" y2="${height - pad}" stroke="#36505f" />
      <text x="${width / 2}" y="${height - 10}" fill="#9fb2bd" text-anchor="middle">Ballistic time (min)</text>
      <text x="18" y="${height / 2}" fill="#9fb2bd" transform="rotate(-90 18 ${height / 2})" text-anchor="middle">Terminal error (km)</text>
      ${points}
      <path d="${paretoPath}" fill="none" stroke="#ffffff" stroke-width="3" />
      ${selectedCandidates.map((c) => `<circle cx="${sx(c.ballisticMin)}" cy="${sy(c.terminalKm)}" r="9" fill="none" stroke="#ffffff" stroke-width="3" />`).join("")}
    </svg>
  `;
}

function wireCopy() {
  document.getElementById("copyTle").addEventListener("click", async () => {
    await navigator.clipboard.writeText(tle.join("\n"));
  });
}

renderSteps();
renderSummary();
renderHyperparams();
renderNearestObjects();
renderEvents();
renderCandidates();
renderSearchChart();
wireCopy();
