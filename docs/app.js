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

const catalogObjects = [
  { name: "ASTROCAST-0401", norad: 55110, missKm: 52.157, tcaMin: 75, inc: 97.5559, mm: 15.28412847, raanDelta: 1.808, incDelta: 0.328 },
  { name: "LEMUR-2-JK0903EM1407", norad: 58336, missKm: 586.747, tcaMin: 165, inc: 97.3917, mm: 15.52862811, raanDelta: 3.105, incDelta: 0.164 },
  { name: "OUTPOST MISSION 2", norad: 58334, missKm: 970.002, tcaMin: 0, inc: 97.3961, mm: 15.59484684, raanDelta: 0.19, incDelta: 0.168 },
  { name: "2024-016A", norad: 58820, missKm: 1196.562, tcaMin: 186.533, inc: 97.4479, mm: 15.56411123, raanDelta: 1.692, incDelta: 0.22 },
  { name: "FLOCK 4Q-7", norad: 58318, missKm: 1941.092, tcaMin: 186.533, inc: 97.3904, mm: 15.57050195, raanDelta: 2.814, incDelta: 0.162 },
  { name: "2024-110B", norad: 60013, missKm: 2205.642, tcaMin: 0, inc: 97.573, mm: 15.22777191, raanDelta: 2.103, incDelta: 0.345 },
  { name: "IPERDRONE.0", norad: 60520, missKm: 2513.07, tcaMin: 0, inc: 97.3764, mm: 15.70168447, raanDelta: 0.727, incDelta: 0.148 },
  { name: "ICEYE-X34", norad: 58294, missKm: 5040.429, tcaMin: 186.533, inc: 97.3861, mm: 15.6975075, raanDelta: 2.808, incDelta: 0.158 },
  { name: "BRO-6", norad: 52422, missKm: 5268.402, tcaMin: 186.533, inc: 97.3389, mm: 15.52257261, raanDelta: 2.51, incDelta: 0.111 },
  { name: "TRANSPORTER-12 OBJECT M", norad: 62620, missKm: 6639.611, tcaMin: 0, inc: 97.3909, mm: 15.66842659, raanDelta: 3.803, incDelta: 0.163 },
  { name: "AE1D", norad: 62618, missKm: 7344.069, tcaMin: 0, inc: 97.3932, mm: 15.66542373, raanDelta: 3.271, incDelta: 0.165 },
  { name: "ASTROCAST-0402", norad: 55109, missKm: 8024.224, tcaMin: 186.533, inc: 97.5575, mm: 15.28925204, raanDelta: 1.567, incDelta: 0.329 },
  { name: "ION SCV-008", norad: 55051, missKm: 8435.101, tcaMin: 186.533, inc: 97.5711, mm: 15.28840099, raanDelta: 2.653, incDelta: 0.343 },
  { name: "FLOCK 4Q-27", norad: 58282, missKm: 9380.325, tcaMin: 0, inc: 97.3807, mm: 15.5669026, raanDelta: 3.475, incDelta: 0.153 },
  { name: "JILIN-1 KUANFU 02A", norad: 57696, missKm: 9937.537, tcaMin: 0, inc: 97.5567, mm: 15.10787288, raanDelta: 0.482, incDelta: 0.329 },
  { name: "EAGLEEYE", norad: 60508, missKm: 10031.883, tcaMin: 0, inc: 97.3703, mm: 15.75536199, raanDelta: 0.469, incDelta: 0.142 },
  { name: "JILIN-1 09", norad: 43943, missKm: 10140.731, tcaMin: 186.533, inc: 97.4742, mm: 15.20712233, raanDelta: 0.721, incDelta: 0.246 },
  { name: "FLOCK 4Q-28", norad: 58280, missKm: 10494.242, tcaMin: 0, inc: 97.388, mm: 15.5653002, raanDelta: 2.223, incDelta: 0.16 },
  { name: "ASTROCAST-0404", norad: 55112, missKm: 10689.494, tcaMin: 0, inc: 97.5664, mm: 15.287651, raanDelta: 0.208, incDelta: 0.338 },
  { name: "2024-016D", norad: 58823, missKm: 11241.341, tcaMin: 186.533, inc: 97.4311, mm: 15.54125338, raanDelta: 3.81, incDelta: 0.203 },
  { name: "BUGSAT-1 (TITA)", norad: 40014, missKm: 11975.597, tcaMin: 186.533, inc: 98.0422, mm: 15.15844396, raanDelta: 0.18, incDelta: 0.814 },
  { name: "ANSER FOLLOWER 1", norad: 58019, missKm: 12253.531, tcaMin: 186.533, inc: 97.5515, mm: 15.50026787, raanDelta: 3.233, incDelta: 0.323 },
  { name: "ARCSAT-1", norad: 52161, missKm: 12337.97, tcaMin: 186.533, inc: 97.2751, mm: 15.54174259, raanDelta: 1.588, incDelta: 0.047 },
  { name: "ASTROCAST-0403", norad: 55111, missKm: 13527.798, tcaMin: 0, inc: 97.5615, mm: 15.32174242, raanDelta: 0.031, incDelta: 0.333 },
  { name: "2024-110A", norad: 60012, missKm: 13674.996, tcaMin: 186.533, inc: 97.5695, mm: 15.13571889, raanDelta: 2.473, incDelta: 0.341 },
];

const selectedCandidates = [
  { id: "out30_delay1800_rec900", outage: 30, ballisticMin: 30.5, recoveryMin: 15, terminalKm: 0.00143, velocityMps: 0.00278, deltaV: 0.00567, baseCandidateMissKm: 185.767, nearest: "ASTROCAST-0401" },
  { id: "out300_delay1800_rec900", outage: 300, ballisticMin: 35, recoveryMin: 15, terminalKm: 0.01482, velocityMps: 0.00913, deltaV: 0.00567, baseCandidateMissKm: 175.152, nearest: "ASTROCAST-0401" },
  { id: "out600_delay1800_rec900", outage: 600, ballisticMin: 40, recoveryMin: 15, terminalKm: 0.03437, velocityMps: 0.02025, deltaV: 0.00567, baseCandidateMissKm: 158.152, nearest: "ASTROCAST-0401" },
];

const searchSpace = [
  { id: "out30_delay0_rec900", outage: 30, ballisticMin: 0.5, terminalKm: 0.00058467, deltaV: 0.00566967, recoverable: true },
  { id: "out30_delay600_rec900", outage: 30, ballisticMin: 10.5, terminalKm: 0.00057291, deltaV: 0.00566967, recoverable: true },
  { id: "out30_delay1800_rec900", outage: 30, ballisticMin: 30.5, terminalKm: 0.00143054, deltaV: 0.00566967, recoverable: true },
  { id: "out30_delay0_rec2100", outage: 30, ballisticMin: 0.5, terminalKm: 0.00487053, deltaV: 0.01322924, recoverable: true },
  { id: "out30_delay600_rec2100", outage: 30, ballisticMin: 10.5, terminalKm: 0.00554981, deltaV: 0.01322924, recoverable: true },
  { id: "out30_delay1800_rec2100", outage: 30, ballisticMin: 30.5, terminalKm: 0.00657832, deltaV: 0.01322924, recoverable: true },
  { id: "out30_delay0_rec4200", outage: 30, ballisticMin: 0.5, terminalKm: 0.03508387, deltaV: 0.02645847, recoverable: false },
  { id: "out30_delay600_rec4200", outage: 30, ballisticMin: 10.5, terminalKm: 0.03513765, deltaV: 0.02645847, recoverable: false },
  { id: "out30_delay1800_rec4200", outage: 30, ballisticMin: 30.5, terminalKm: 0.0352776, deltaV: 0.02645847, recoverable: false },
  { id: "out300_delay0_rec900", outage: 300, ballisticMin: 5, terminalKm: 0.0006746, deltaV: 0.00566967, recoverable: true },
  { id: "out300_delay600_rec900", outage: 300, ballisticMin: 15, terminalKm: 0.00409594, deltaV: 0.00566967, recoverable: true },
  { id: "out300_delay600_rec2100", outage: 300, ballisticMin: 15, terminalKm: 0.00126414, deltaV: 0.01322924, recoverable: true },
  { id: "out300_delay0_rec2100", outage: 300, ballisticMin: 5, terminalKm: 0.0073962, deltaV: 0.01322924, recoverable: true },
  { id: "out300_delay1800_rec900", outage: 300, ballisticMin: 35, terminalKm: 0.01481614, deltaV: 0.00566967, recoverable: true },
  { id: "out300_delay1800_rec2100", outage: 300, ballisticMin: 35, terminalKm: 0.01312465, deltaV: 0.01322924, recoverable: true },
  { id: "out300_delay0_rec4200", outage: 300, ballisticMin: 5, terminalKm: 0.02644014, deltaV: 0.02645847, recoverable: false },
  { id: "out300_delay600_rec4200", outage: 300, ballisticMin: 15, terminalKm: 0.02841226, deltaV: 0.02645847, recoverable: false },
  { id: "out300_delay1800_rec4200", outage: 300, ballisticMin: 35, terminalKm: 0.02833463, deltaV: 0.02645847, recoverable: false },
  { id: "out600_delay0_rec900", outage: 600, ballisticMin: 10, terminalKm: 0.00310367, deltaV: 0.00566967, recoverable: true },
  { id: "out600_delay600_rec900", outage: 600, ballisticMin: 20, terminalKm: 0.0111552, deltaV: 0.00566967, recoverable: true },
  { id: "out600_delay0_rec2100", outage: 600, ballisticMin: 10, terminalKm: 0.00732256, deltaV: 0.01322924, recoverable: true },
  { id: "out600_delay600_rec2100", outage: 600, ballisticMin: 20, terminalKm: 0.02021379, deltaV: 0.01322924, recoverable: true },
  { id: "out600_delay600_rec4200", outage: 600, ballisticMin: 20, terminalKm: 0.00419244, deltaV: 0.02645847, recoverable: true },
  { id: "out600_delay0_rec4200", outage: 600, ballisticMin: 10, terminalKm: 0.00721085, deltaV: 0.02645847, recoverable: true },
  { id: "out600_delay1800_rec4200", outage: 600, ballisticMin: 40, terminalKm: 0.00671034, deltaV: 0.02645847, recoverable: true },
  { id: "out600_delay1800_rec900", outage: 600, ballisticMin: 40, terminalKm: 0.03436887, deltaV: 0.00566967, recoverable: true },
  { id: "out600_delay1800_rec2100", outage: 600, ballisticMin: 40, terminalKm: 0.04129369, deltaV: 0.01322924, recoverable: true },
];

const events = [
  ["request", "CelesTrak GP query for TANAGER-1 TLE by NORAD catalog ID 60507"],
  ["catalog", "Active catalog CSV parsed and normalized into orbital-element features"],
  ["filter", "Local catalog filtered using altitude, inclination, RAAN, and mean-motion gates"],
  ["propagate", "Operator and selected local objects propagated with SGP4"],
  ["rank", "Objects ranked by minimum baseline miss distance and TCA offset"],
];

const fmt = new Intl.NumberFormat("en-US", { maximumFractionDigits: 3 });
const state = {
  catalogSize: 15,
  windowOrbits: 2,
  closeThreshold: 250,
};

const presets = {
  fast: { catalogSize: 10, windowOrbits: 1, closeThreshold: 100 },
  balanced: { catalogSize: 15, windowOrbits: 2, closeThreshold: 250 },
  conservative: { catalogSize: 25, windowOrbits: 3, closeThreshold: 2500 },
};

function setText(id, text) {
  document.getElementById(id).textContent = text;
}

function screeningWindowMin() {
  return state.windowOrbits * summary.operator.periodMin;
}

function scoredObjects() {
  const windowMin = screeningWindowMin();
  return catalogObjects
    .slice(0, state.catalogSize)
    .map((object) => {
      const inWindow = object.tcaMin <= windowMin;
      const thresholdRatio = object.missKm / state.closeThreshold;
      const priorityScore = object.missKm + (inWindow ? 0 : state.closeThreshold * 1.4);
      return {
        ...object,
        inWindow,
        underThreshold: inWindow && object.missKm <= state.closeThreshold,
        thresholdRatio,
        priorityScore,
      };
    })
    .sort((a, b) => a.priorityScore - b.priorityScore);
}

function dynamicCandidateMetrics() {
  const objects = scoredObjects();
  const activeObjects = objects.filter((object) => object.inWindow);
  const nearestMiss = activeObjects[0]?.missKm ?? objects[0]?.missKm ?? 0;
  const closeCount = activeObjects.filter((object) => object.missKm <= state.closeThreshold).length;
  const loadFactor = Math.sqrt(Math.max(activeObjects.length, 1) / 10);
  const thresholdFactor = Math.max(state.closeThreshold / 250, 0.2);

  return selectedCandidates
    .map((candidate, index) => {
      const outageFactor = candidate.outage / 600;
      const candidateMissKm = Math.max(
        1,
        candidate.baseCandidateMissKm - closeCount * 1.8 - outageFactor * thresholdFactor * 8 + nearestMiss * 0.0008,
      );
      const riskProxy = Math.exp(-0.5 * (candidateMissKm / Math.max(state.closeThreshold, 1)) ** 2) * loadFactor;
      const newClose = candidateMissKm < state.closeThreshold && closeCount > index ? 1 : 0;
      const score =
        candidate.terminalKm * 42 +
        candidate.deltaV * 12 +
        riskProxy * 2.5 +
        newClose * 0.4 -
        candidate.ballisticMin * 0.002;
      return {
        ...candidate,
        candidateMissKm,
        riskProxy,
        newClose,
        score,
      };
    })
    .sort((a, b) => a.score - b.score);
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
}

function renderHyperparams() {
  const controls = [
    ["catalogSize", "catalogSizeValue", " objects", "catalogSize"],
    ["windowOrbits", "windowOrbitsValue", " orbits", "windowOrbits"],
    ["closeThreshold", "closeThresholdValue", " km", "closeThreshold"],
  ];
  controls.forEach(([inputId, outputId, suffix, key]) => {
    const input = document.getElementById(inputId);
    input.value = state[key];
    const update = () => {
      state[key] = Number(input.value);
      document.getElementById(outputId).textContent = `${state[key]}${suffix}`;
      syncPresetButtons();
      renderDynamicViews();
    };
    input.addEventListener("input", update);
    update();
  });
  document.querySelectorAll(".preset-button").forEach((button) => {
    button.addEventListener("click", () => {
      Object.assign(state, presets[button.dataset.preset]);
      syncHyperparamControls();
      renderDynamicViews();
    });
  });
}

function syncHyperparamControls() {
  [
    ["catalogSize", "catalogSizeValue", " objects", "catalogSize"],
    ["windowOrbits", "windowOrbitsValue", " orbits", "windowOrbits"],
    ["closeThreshold", "closeThresholdValue", " km", "closeThreshold"],
  ].forEach(([inputId, outputId, suffix, key]) => {
    document.getElementById(inputId).value = state[key];
    document.getElementById(outputId).textContent = `${state[key]}${suffix}`;
  });
  syncPresetButtons();
}

function syncPresetButtons() {
  const activePreset = Object.entries(presets).find(([, values]) =>
    Object.keys(values).every((key) => values[key] === state[key]),
  )?.[0];
  document.querySelectorAll(".preset-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.preset === activePreset);
  });
}

function renderNearestObjects() {
  const objects = scoredObjects();
  const visibleRows = objects.slice(0, Math.min(8, objects.length));
  document.getElementById("nearestRows").innerHTML = visibleRows
    .map((row) => {
      const status = row.underThreshold ? "watch" : row.inWindow ? "screened" : "outside window";
      return `
        <tr class="${row.underThreshold ? "watch-row" : ""}">
          <td>${row.name}</td>
          <td>${row.norad}</td>
          <td>${row.missKm.toFixed(2)}</td>
          <td>${row.tcaMin.toFixed(2)}</td>
          <td>${row.inc.toFixed(4)}</td>
          <td>${row.mm.toFixed(5)}</td>
          <td><span class="status-pill ${row.underThreshold ? "watch" : ""}">${status}</span></td>
        </tr>
      `;
    })
    .join("");
}

function renderEvents() {
  document.getElementById("eventList").innerHTML = events
    .map(([label, text]) => `<li><span>${label}</span><strong>${text}</strong></li>`)
    .join("");
}

function renderScreeningMetrics() {
  const objects = scoredObjects();
  const activeObjects = objects.filter((object) => object.inWindow);
  const closeObjects = activeObjects.filter((object) => object.underThreshold);
  const nearest = activeObjects[0] ?? objects[0];
  const estimatedSeconds = 20 + state.catalogSize * state.windowOrbits * 1.9 + summary.phaseGuessCandidateCount * 1.8;

  setText("previewCount", `${objects.length} / 25`);
  setText("windowCount", `${activeObjects.length}`);
  setText("thresholdCount", `${closeObjects.length}`);
  setText("dynamicNearest", nearest ? `${nearest.missKm.toFixed(2)} km` : "-");
  setText("nearestCaption", `${objects.length} objects, ${activeObjects.length} inside ${state.windowOrbits} orbit window`);
  setText("screened", fmt.format(objects.length));
  setText("nearestMiss", nearest ? `${nearest.missKm.toFixed(2)} km` : "-");
  setText("runtimeEstimate", `< ${Math.max(1, Math.ceil(estimatedSeconds / 60))} min`);
}

function renderCandidates() {
  const candidates = dynamicCandidateMetrics();
  const bestTerminal = Math.min(...candidates.map((candidate) => candidate.terminalKm));
  const lowestDv = Math.min(...candidates.map((candidate) => candidate.deltaV));
  setText("recoverableCount", `${summary.recoverableCandidateCount} recoverable from 27`);
  setText("phaseGrid", "3 outages x 3 delays x 3 horizons");
  setText("bestTerminal", `${bestTerminal.toFixed(5)} km`);
  setText("lowestDv", `${lowestDv.toFixed(5)} m/s`);
  setText("ssaChoices", `${candidates.length} ranked`);

  document.getElementById("candidateList").innerHTML = candidates
    .map(
      (candidate, index) => `
        <article class="candidate-card ${index === 0 ? "best" : ""}">
          <header>
            <strong>${candidate.id}</strong>
            <span class="pill">${index === 0 ? "best current" : `${candidate.outage} s outage`}</span>
          </header>
          <dl>
            <div><dt>Ballistic</dt><dd>${candidate.ballisticMin.toFixed(1)} min</dd></div>
            <div><dt>Recovery</dt><dd>${candidate.recoveryMin.toFixed(1)} min</dd></div>
            <div><dt>Terminal error</dt><dd>${candidate.terminalKm.toFixed(5)} km</dd></div>
            <div><dt>Extra delta-v</dt><dd>${candidate.deltaV.toFixed(5)} m/s</dd></div>
            <div><dt>Candidate miss</dt><dd>${candidate.candidateMissKm.toFixed(2)} km</dd></div>
            <div><dt>Risk proxy</dt><dd>${candidate.riskProxy.toFixed(3)}</dd></div>
          </dl>
        </article>
      `,
    )
    .join("");
}

function renderParetoPlot() {
  const dynamicCandidates = dynamicCandidateMetrics();
  const pareto = dynamicCandidates.slice().sort((a, b) => a.ballisticMin - b.ballisticMin);
  const width = 980;
  const height = 620;
  const plot = { left: 92, top: 70, right: 785, bottom: 505 };
  const colorbar = { x: 825, y: plot.top, width: 28, height: plot.bottom - plot.top };
  const xMin = 0;
  const xMax = 42;
  const yMin = 0;
  const yMax = 0.043;
  const dvMin = Math.min(...searchSpace.map((point) => point.deltaV));
  const dvMax = Math.max(...searchSpace.map((point) => point.deltaV));
  const sx = (x) => plot.left + ((x - xMin) / (xMax - xMin)) * (plot.right - plot.left);
  const sy = (y) => plot.bottom - ((y - yMin) / (yMax - yMin)) * (plot.bottom - plot.top);
  const palette = [
    [68, 1, 84],
    [72, 40, 120],
    [62, 73, 137],
    [49, 104, 142],
    [38, 130, 142],
    [31, 158, 137],
    [53, 183, 121],
    [109, 205, 89],
    [180, 222, 44],
    [253, 231, 37],
  ];
  const colorForDv = (value) => {
    const t = Math.max(0, Math.min(1, (value - dvMin) / (dvMax - dvMin || 1)));
    const scaled = t * (palette.length - 1);
    const low = Math.floor(scaled);
    const high = Math.min(palette.length - 1, low + 1);
    const mix = scaled - low;
    const rgb = palette[low].map((channel, index) => Math.round(channel + (palette[high][index] - channel) * mix));
    return `rgb(${rgb.join(",")})`;
  };
  const interpolatedDv = (x, y) => {
    let numerator = 0;
    let denominator = 0;
    for (const point of searchSpace) {
      const dx = (x - point.ballisticMin) / 9;
      const dy = (y - point.terminalKm) / 0.009;
      const distance = Math.sqrt(dx * dx + dy * dy);
      const weight = 1 / Math.max(distance ** 2.2, 0.025);
      numerator += point.deltaV * weight;
      denominator += weight;
    }
    return numerator / denominator;
  };
  const cells = [];
  const xSteps = 44;
  const ySteps = 30;
  const cellWidth = (plot.right - plot.left) / xSteps + 0.4;
  const cellHeight = (plot.bottom - plot.top) / ySteps + 0.4;
  for (let ix = 0; ix < xSteps; ix += 1) {
    for (let iy = 0; iy < ySteps; iy += 1) {
      const x = xMin + ((ix + 0.5) / xSteps) * (xMax - xMin);
      const y = yMin + ((iy + 0.5) / ySteps) * (yMax - yMin);
      const rectX = plot.left + ix * ((plot.right - plot.left) / xSteps);
      const rectY = plot.bottom - (iy + 1) * ((plot.bottom - plot.top) / ySteps);
      cells.push(
        `<rect x="${rectX}" y="${rectY}" width="${cellWidth}" height="${cellHeight}" fill="${colorForDv(interpolatedDv(x, y))}" opacity="0.92" />`,
      );
    }
  }
  const contourLines = [0.007, 0.011, 0.015, 0.019, 0.023, 0.026]
    .map((level) => {
      const near = searchSpace.filter((point) => Math.abs(point.deltaV - level) < 0.005);
      const path = near
        .sort((a, b) => a.ballisticMin - b.ballisticMin)
        .map((point, index) => `${index === 0 ? "M" : "L"} ${sx(point.ballisticMin)} ${sy(point.terminalKm)}`)
        .join(" ");
      return path ? `<path d="${path}" fill="none" stroke="#f3d86a" stroke-width="0.8" opacity="0.28" />` : "";
    })
    .join("");
  const searchDots = searchSpace
    .map((point) => `<circle cx="${sx(point.ballisticMin)}" cy="${sy(point.terminalKm)}" r="3" fill="#b7e7d9" opacity="${point.recoverable ? 0.28 : 0.16}" />`)
    .join("");
  const paretoPath = pareto.map((candidate, index) => `${index === 0 ? "M" : "L"} ${sx(candidate.ballisticMin)} ${sy(candidate.terminalKm)}`).join(" ");
  const paretoNodes = pareto
    .map((candidate) => {
      const x = sx(candidate.ballisticMin);
      const y = sy(candidate.terminalKm);
      const riskHalo = Math.min(10, candidate.riskProxy * 5);
      return `
        <g>
          <circle cx="${x}" cy="${y}" r="${15 + riskHalo}" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.96" />
          <circle cx="${x}" cy="${y}" r="9" fill="#0b1117" stroke="#ffffff" stroke-width="1.4" opacity="0.9" />
          <text x="${x + (candidate.outage === 600 ? -8 : 12)}" y="${y - 10}" fill="#ffffff" font-size="13" text-anchor="${candidate.outage === 600 ? "end" : "start"}">${candidate.outage} s</text>
        </g>
      `;
    })
    .join("");
  const colorbarStops = palette
    .map((rgb, index) => `<stop offset="${(index / (palette.length - 1)) * 100}%" stop-color="rgb(${rgb.join(",")})" />`)
    .join("");
  const colorTicks = [dvMin, (dvMin + dvMax) / 2, dvMax]
    .map((value) => {
      const y = colorbar.y + colorbar.height - ((value - dvMin) / (dvMax - dvMin || 1)) * colorbar.height;
      return `
        <line x1="${colorbar.x + colorbar.width}" y1="${y}" x2="${colorbar.x + colorbar.width + 7}" y2="${y}" stroke="#d7e4e8" />
        <text x="${colorbar.x + colorbar.width + 12}" y="${y + 4}" fill="#d7e4e8" font-size="12">${value.toFixed(3)}</text>
      `;
    })
    .join("");
  const yTicks = [0.005, 0.015, 0.025, 0.035]
    .map((value) => {
      const y = sy(value);
      return `
        <line x1="${plot.left}" y1="${y}" x2="${plot.right}" y2="${y}" stroke="#ffffff" opacity="0.12" />
        <text x="${plot.left - 12}" y="${y + 4}" fill="#d7e4e8" text-anchor="end" font-size="12">${value.toFixed(3)}</text>
      `;
    })
    .join("");
  const xTicks = [0, 10, 20, 30, 40]
    .map((value) => {
      const x = sx(value);
      return `
        <line x1="${x}" y1="${plot.top}" x2="${x}" y2="${plot.bottom}" stroke="#ffffff" opacity="0.12" />
        <text x="${x}" y="${plot.bottom + 24}" fill="#d7e4e8" text-anchor="middle" font-size="12">${value}</text>
      `;
    })
    .join("");

  document.getElementById("paretoCaption").textContent =
    `${state.catalogSize} objects, ${state.windowOrbits} orbit window, ${state.closeThreshold} km threshold`;
  document.getElementById("paretoPlot").innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img">
      <defs>
        <linearGradient id="deltaVScale" x1="0" x2="0" y1="1" y2="0">${colorbarStops}</linearGradient>
        <clipPath id="plotClip"><rect x="${plot.left}" y="${plot.top}" width="${plot.right - plot.left}" height="${plot.bottom - plot.top}" /></clipPath>
      </defs>
      <rect x="0" y="0" width="${width}" height="${height}" fill="#03070a" />
      <text x="${plot.left}" y="40" fill="#ffffff" font-size="18">Real-Time SSA Data based LEO Sat Missed-Thrust Recovery Search</text>
      <g clip-path="url(#plotClip)">
        ${cells.join("")}
        ${contourLines}
        ${searchDots}
        <path d="${paretoPath}" fill="none" stroke="#ffffff" stroke-width="3.2" opacity="0.95" />
        ${paretoNodes}
      </g>
      ${xTicks}
      ${yTicks}
      <rect x="${plot.left}" y="${plot.top}" width="${plot.right - plot.left}" height="${plot.bottom - plot.top}" fill="none" stroke="#d8e6eb" stroke-width="1" opacity="0.7" />
      <text x="${(plot.left + plot.right) / 2}" y="${height - 40}" fill="#d7e4e8" text-anchor="middle" font-size="16">Ballistic time (min)</text>
      <text x="28" y="${(plot.top + plot.bottom) / 2}" fill="#d7e4e8" transform="rotate(-90 28 ${(plot.top + plot.bottom) / 2})" text-anchor="middle" font-size="16">Distance from Nominal Trajectory (km)</text>
      <rect x="${colorbar.x}" y="${colorbar.y}" width="${colorbar.width}" height="${colorbar.height}" fill="url(#deltaVScale)" stroke="#d8e6eb" opacity="0.96" />
      ${colorTicks}
      <text x="${colorbar.x + 78}" y="${(colorbar.y + colorbar.y + colorbar.height) / 2}" fill="#d7e4e8" transform="rotate(-90 ${colorbar.x + 78} ${(colorbar.y + colorbar.y + colorbar.height) / 2})" text-anchor="middle" font-size="14">Fuel Proxy: Extra delta-v (m/s)</text>
      <g>
        <circle cx="${plot.right - 180}" cy="${plot.top + 24}" r="9" fill="none" stroke="#ffffff" stroke-width="2.5" />
        <text x="${plot.right - 160}" y="${plot.top + 29}" fill="#ffffff" font-size="13">Pareto front (SSA-aware)</text>
      </g>
    </svg>
  `;
}

function renderDynamicViews() {
  renderScreeningMetrics();
  renderNearestObjects();
  renderCandidates();
  renderParetoPlot();
}

function wireCopy() {
  document.getElementById("copyTle").addEventListener("click", async () => {
    await navigator.clipboard.writeText(tle.join("\n"));
  });
}

renderSteps();
renderSummary();
renderEvents();
renderHyperparams();
wireCopy();
