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

const runSettings = {
  catalogSize: 15,
  windowOrbits: 2,
  closeThresholdKm: 250,
  altitudeGateKm: 100,
  inclinationGateDeg: 5,
  raanGateDeg: 30,
  meanMotionGateRevDay: 0.35,
};

const tle = [
  "TANAGER-1",
  "1 60507U 24149AR  26190.70477619  .00000245  00000+0  72329-5 0  9995",
  "2 60507  97.2281 284.8679 0002763 147.2432 212.8988 15.43935842106519",
];

const nearestObjects = [
  { name: "ASTROCAST-0401", norad: 55110, missKm: 52.157, tcaMin: 75, inc: 97.5559, mm: 15.28412847 },
  { name: "LEMUR-2-JK0903EM1407", norad: 58336, missKm: 586.747, tcaMin: 165, inc: 97.3917, mm: 15.52862811 },
  { name: "OUTPOST MISSION 2", norad: 58334, missKm: 970.002, tcaMin: 0, inc: 97.3961, mm: 15.59484684 },
  { name: "2024-016A", norad: 58820, missKm: 1196.562, tcaMin: 186.533, inc: 97.4479, mm: 15.56411123 },
  { name: "FLOCK 4Q-7", norad: 58318, missKm: 1941.092, tcaMin: 186.533, inc: 97.3904, mm: 15.57050195 },
  { name: "2024-110B", norad: 60013, missKm: 2205.642, tcaMin: 0, inc: 97.573, mm: 15.22777191 },
  { name: "IPERDRONE.0", norad: 60520, missKm: 2513.07, tcaMin: 0, inc: 97.3764, mm: 15.70168447 },
  { name: "ICEYE-X34", norad: 58294, missKm: 5040.429, tcaMin: 186.533, inc: 97.3861, mm: 15.6975075 },
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

const events = [
  ["request", "CelesTrak GP query for TANAGER-1 TLE by NORAD catalog ID 60507"],
  ["catalog", "Active catalog CSV parsed and normalized into orbital-element features"],
  ["filter", "Local catalog filtered using altitude, inclination, RAAN, and mean-motion gates"],
  ["propagate", "Operator and selected local objects propagated with SGP4"],
  ["rank", "Objects ranked by minimum baseline miss distance and TCA offset"],
];

const fmt = new Intl.NumberFormat("en-US", { maximumFractionDigits: 3 });

function setText(id, text) {
  const element = document.getElementById(id);
  if (element) element.textContent = text;
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
  setText("runtimeEstimate", "< 2 min");
}

function renderRunSettings() {
  setText("catalogSizeValue", `${runSettings.catalogSize} objects`);
  setText("windowOrbitsValue", `${runSettings.windowOrbits} orbits`);
  setText("closeThresholdValue", `${runSettings.closeThresholdKm} km`);
  setText("altitudeGate", `${runSettings.altitudeGateKm} km`);
  setText("inclinationGate", `${runSettings.inclinationGateDeg} deg`);
  setText("raanGate", `${runSettings.raanGateDeg} deg`);
  setText("meanMotionGate", `${runSettings.meanMotionGateRevDay} rev/day`);
}

function renderNearestObjects() {
  const windowMin = runSettings.windowOrbits * summary.operator.periodMin;
  document.getElementById("nearestRows").innerHTML = nearestObjects
    .map((row) => {
      const inWindow = row.tcaMin <= windowMin;
      const underThreshold = inWindow && row.missKm <= runSettings.closeThresholdKm;
      const status = underThreshold ? "watch" : inWindow ? "screened" : "outside window";
      return `
        <tr class="${underThreshold ? "watch-row" : ""}">
          <td>${row.name}</td>
          <td>${row.norad}</td>
          <td>${row.missKm.toFixed(2)}</td>
          <td>${row.tcaMin.toFixed(2)}</td>
          <td>${row.inc.toFixed(4)}</td>
          <td>${row.mm.toFixed(5)}</td>
          <td><span class="status-pill ${underThreshold ? "watch" : ""}">${status}</span></td>
        </tr>
      `;
    })
    .join("");
  setText(
    "nearestCaption",
    `${runSettings.catalogSize} objects, ${runSettings.windowOrbits} orbit window, ${runSettings.closeThresholdKm} km threshold`,
  );
}

function renderEvents() {
  document.getElementById("eventList").innerHTML = events
    .map(([label, text]) => `<li><span>${label}</span><strong>${text}</strong></li>`)
    .join("");
}

function renderCandidates() {
  const bestTerminal = Math.min(...selectedCandidates.map((candidate) => candidate.terminalKm));
  const lowestDv = Math.min(...selectedCandidates.map((candidate) => candidate.deltaV));
  setText("recoverableCount", `${summary.recoverableCandidateCount} recoverable from 27`);
  setText("phaseGrid", "3 outages x 3 delays x 3 horizons");
  setText("bestTerminal", `${bestTerminal.toFixed(5)} km`);
  setText("lowestDv", `${lowestDv.toFixed(5)} m/s`);
  setText("ssaChoices", `${selectedCandidates.length} SSA-screened`);

  document.getElementById("candidateList").innerHTML = selectedCandidates
    .map(
      (candidate, index) => `
        <article class="candidate-card ${index === 0 ? "best" : ""}">
          <header>
            <strong>${candidate.id}</strong>
            <span class="pill">${candidate.outage} s outage</span>
          </header>
          <dl>
            <div><dt>Ballistic</dt><dd>${candidate.ballisticMin.toFixed(1)} min</dd></div>
            <div><dt>Recovery</dt><dd>${candidate.recoveryMin.toFixed(1)} min</dd></div>
            <div><dt>Terminal error</dt><dd>${candidate.terminalKm.toFixed(5)} km</dd></div>
            <div><dt>Extra delta-v</dt><dd>${candidate.deltaV.toFixed(5)} m/s</dd></div>
            <div><dt>Candidate miss</dt><dd>${candidate.missKm.toFixed(2)} km</dd></div>
            <div><dt>New close approaches</dt><dd>${candidate.newClose}</dd></div>
          </dl>
        </article>
      `,
    )
    .join("");
}

function wireCopy() {
  document.getElementById("copyTle").addEventListener("click", async () => {
    await navigator.clipboard.writeText(tle.join("\n"));
  });
}

renderSteps();
renderSummary();
renderRunSettings();
renderNearestObjects();
renderEvents();
renderCandidates();
wireCopy();
