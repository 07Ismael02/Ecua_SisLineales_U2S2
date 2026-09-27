"use strict";

const OFFICIAL = {
  A: [[10, -2, -1, 0], [-1, 8, 0, -2], [-2, 0, 12, -3], [0, -1, -2, 9]],
  b: [15, 18, 25, 20],
  x0: [0, 0, 0, 0],
  epsilon: 0.0001,
  max_iteraciones: 100,
};

const state = { n: 4, analysis: null, result: null };
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

function formatNumber(value, digits = 10) {
  if (value === null || value === undefined) return "—";
  if (!Number.isFinite(Number(value))) return String(value);
  const number = Number(value);
  if (number === 0) return "0";
  const absolute = Math.abs(number);
  if (absolute >= 1e7 || absolute < 1e-6) return number.toExponential(digits - 1).replace(/\.0+e/, "e");
  return Number(number.toPrecision(digits)).toString();
}

function vectorText(vector) {
  return `[${vector.map((value) => formatNumber(value)).join(", ")}]`;
}

function equationText(row, rightSide) {
  const terms = [];
  row.forEach((coefficient, index) => {
    if (coefficient === 0) return;
    const magnitude = Math.abs(coefficient);
    const factor = magnitude === 1 ? "" : formatNumber(magnitude);
    const variable = `${factor}x${index + 1}`;
    if (!terms.length) terms.push(`${coefficient < 0 ? "-" : ""}${variable}`);
    else terms.push(`${coefficient < 0 ? "-" : "+"} ${variable}`);
  });
  return `${terms.join(" ") || "0"} = ${formatNumber(rightSide)}`;
}

function showMessage(text, type = "error") {
  const element = $("#message");
  element.textContent = text;
  element.className = `message${type === "success" ? " success" : ""}`;
  element.hidden = false;
  element.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function hideMessage() {
  $("#message").hidden = true;
}

function setBusy(button, busy, busyText) {
  if (!button.dataset.label) button.dataset.label = button.textContent;
  button.disabled = busy;
  button.textContent = busy ? busyText : button.dataset.label;
}

function hideSections(selector) {
  $$(selector).forEach((section) => { section.hidden = true; });
}

function invalidateAnalysis() {
  state.analysis = null;
  state.result = null;
  hideSections(".result-section");
  $("#copy-status").textContent = "";
}

function invalidateSolution() {
  state.result = null;
  hideSections(".solution-section");
  $("#copy-status").textContent = "";
}

function buildEditor(n, values = null) {
  state.n = n;
  $("#size-select").value = String(n);
  const matrix = $("#matrix-a");
  const vectorB = $("#vector-b");
  const vectorX = $("#vector-x-symbol");
  const vectorX0 = $("#vector-x0");
  matrix.innerHTML = "";
  vectorB.innerHTML = "";
  vectorX.innerHTML = "";
  vectorX0.innerHTML = "";
  matrix.style.gridTemplateColumns = `repeat(${n}, 72px)`;

  for (let i = 0; i < n; i += 1) {
    for (let j = 0; j < n; j += 1) {
      const input = document.createElement("input");
      input.type = "number";
      input.step = "any";
      input.className = "matrix-input";
      input.dataset.row = i;
      input.dataset.col = j;
      input.setAttribute("aria-label", `A fila ${i + 1}, columna ${j + 1}`);
      input.value = values ? values.A[i][j] : "";
      matrix.append(input);
    }

    const bInput = document.createElement("input");
    bInput.type = "number";
    bInput.step = "any";
    bInput.className = "b-input";
    bInput.dataset.row = i;
    bInput.setAttribute("aria-label", `b fila ${i + 1}`);
    bInput.value = values ? values.b[i] : "";
    vectorB.append(bInput);

    const symbol = document.createElement("span");
    symbol.innerHTML = `x<sub>${i + 1}</sub>`;
    vectorX.append(symbol);

    const label = document.createElement("label");
    label.className = "x0-item";
    label.innerHTML = `<span>x<sub>${i + 1}</sub><sup>(0)</sup></span>`;
    const xInput = document.createElement("input");
    xInput.type = "number";
    xInput.step = "any";
    xInput.className = "x0-input";
    xInput.dataset.index = i;
    xInput.value = values ? values.x0[i] : 0;
    xInput.setAttribute("aria-label", `Valor inicial x ${i + 1}`);
    label.append(xInput);
    vectorX0.append(label);
  }

  renderEquationPreview();
  invalidateAnalysis();
}

function readNumber(input, label) {
  if (input.value.trim() === "") throw new Error(`${label} no puede estar vacío.`);
  const value = Number(input.value);
  if (!Number.isFinite(value)) throw new Error(`${label} debe ser un número finito.`);
  return value;
}

function readSystem() {
  const A = Array.from({ length: state.n }, () => Array(state.n).fill(0));
  $$(".matrix-input").forEach((input) => {
    const i = Number(input.dataset.row);
    const j = Number(input.dataset.col);
    A[i][j] = readNumber(input, `A[${i + 1},${j + 1}]`);
  });
  const b = $$(".b-input").map((input, i) => readNumber(input, `b[${i + 1}]`));
  return { A, b };
}

function readConfiguration() {
  const x0 = $$(".x0-input").map((input, i) => readNumber(input, `x0[${i + 1}]`));
  const epsilon = readNumber($("#epsilon"), "epsilon");
  const maxRaw = $("#max-iterations").value.trim();
  if (!/^[+-]?\d+$/.test(maxRaw)) throw new Error("El máximo de iteraciones debe ser un entero.");
  const max_iteraciones = Number(maxRaw);
  return { x0, epsilon, max_iteraciones };
}

function renderEquationPreview() {
  const container = $("#equations-preview");
  const matrixInputs = $$(".matrix-input");
  const bInputs = $$(".b-input");
  if (!matrixInputs.length) return;
  const lines = [];
  for (let i = 0; i < state.n; i += 1) {
    const terms = [];
    for (let j = 0; j < state.n; j += 1) {
      const raw = matrixInputs[i * state.n + j].value.trim();
      const coefficient = raw === "" ? null : Number(raw);
      if (coefficient === 0) continue;
      if (coefficient === null || !Number.isFinite(coefficient)) {
        terms.push(`${terms.length ? "+ " : ""}?x${j + 1}`);
        continue;
      }
      const magnitude = Math.abs(coefficient);
      const factor = magnitude === 1 ? "" : formatNumber(magnitude);
      if (!terms.length) terms.push(`${coefficient < 0 ? "−" : ""}${factor}x${j + 1}`);
      else terms.push(`${coefficient < 0 ? "−" : "+"} ${factor}x${j + 1}`);
    }
    const right = bInputs[i]?.value.trim() || "?";
    lines.push(`${terms.join(" ") || "0"} = ${right}`);
  }
  container.replaceChildren(...lines.map((line) => {
    const p = document.createElement("div");
    p.textContent = line;
    return p;
  }));
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  let data;
  try { data = await response.json(); }
  catch { throw new Error("El servidor devolvió una respuesta que no es JSON."); }
  if (!response.ok || !data.ok) throw new Error(data.error || `Error HTTP ${response.status}.`);
  return data;
}

function renderAnalysis(data) {
  const { analisis, formulas } = data;
  const grid = $("#dominance-content");
  grid.innerHTML = "";
  analisis.filas.forEach((row) => {
    const card = document.createElement("article");
    card.className = "dominance-row";
    const absoluteTerms = row.valores_absolutos.map((value) => `|${formatNumber(value)}|`).join(" + ") || "0";
    card.innerHTML = `
      <h3>Fila ${row.fila}</h3>
      <p class="math">|${formatNumber(row.diagonal)}| &gt; ${absoluteTerms}</p>
      <p class="math"><strong>${formatNumber(row.diagonal_absoluta)} &gt; ${formatNumber(row.suma_externos)}</strong></p>
      <p>Margen: ${formatNumber(row.margen)}</p>
      <span class="status ${row.cumple ? "status--ok" : "status--warn"}">${row.cumple ? "✓ Cumple" : "! No cumple"}</span>`;
    grid.append(card);
  });

  const conclusion = $("#dominance-conclusion");
  conclusion.className = `conclusion ${analisis.es_estrictamente_dominante ? "conclusion--ok" : "conclusion--warn"}`;
  conclusion.innerHTML = `<strong>${analisis.conclusion}</strong><p>${analisis.explicacion}</p>`;

  const list = $("#formula-list");
  list.innerHTML = "";
  formulas.forEach((formula) => {
    const item = document.createElement("div");
    item.className = "formula";
    item.textContent = formula.texto;
    list.append(item);
  });
  ["#paso-2", "#paso-3", "#paso-4", "#paso-5"].forEach((id) => { $(id).hidden = false; });
}

function renderTable(result) {
  const table = $("#iterations-table");
  const head = table.querySelector("thead");
  const body = table.querySelector("tbody");
  const headers = ["k", ...result.solucion.map((_, i) => `x${i + 1}`), "E relativo", "E %"];
  head.innerHTML = `<tr>${headers.map((header) => `<th scope="col">${header}</th>`).join("")}</tr>`;
  body.innerHTML = "";
  result.iteraciones.forEach((iteration) => {
    const row = document.createElement("tr");
    const values = [iteration.k, ...iteration.vector.map((v) => formatNumber(v)), formatNumber(iteration.error_maximo), iteration.error_porcentual === null ? "—" : `${formatNumber(iteration.error_porcentual)} %`];
    row.innerHTML = values.map((value) => `<td>${value}</td>`).join("");
    body.append(row);
  });
}

function renderDetails(result) {
  const container = $("#iteration-details");
  container.innerHTML = "";
  result.iteraciones.slice(1).forEach((iteration, index) => {
    const detail = document.createElement("details");
    detail.className = "iteration-detail";
    detail.open = index < 2;
    const components = iteration.componentes.map((component) => `
      <article class="component-card">
        <h4>x${component.variable}<sup>(${iteration.k})</sup></h4>
        <p class="calculation-line"><span>Fórmula</span><code>${component.formula_texto}</code></p>
        <p class="calculation-line"><span>Sustitución</span><code>${component.sustitucion_texto}</code></p>
        <p class="calculation-line"><span>Operación</span><code>${component.operacion_texto}</code></p>
        <p class="calculation-line"><span>Resultado</span><code>x${component.variable}^(${iteration.k}) = ${formatNumber(component.resultado)}</code></p>
        <p class="calculation-line"><span>Error</span><code>${formatNumber(component.error)} (${component.tipo_error}; |Δ| = ${formatNumber(component.diferencia_absoluta)})</code></p>
      </article>`).join("");
    const decision = iteration.convergio ? "Sí — criterio de parada satisfecho." : "No — se requiere una nueva iteración.";
    detail.innerHTML = `
      <summary><span>Iteración ${iteration.k}</span><span>E = ${formatNumber(iteration.error_maximo)}</span></summary>
      <div class="iteration-body">
        ${components}
        <p class="vector-line">x^(${iteration.k}) = ${vectorText(iteration.vector)}</p>
        <div class="error-summary">
          ${iteration.componentes.map((c) => `<p>E${c.variable} = ${formatNumber(c.error)} · ${c.tipo_error}</p>`).join("")}
          <p><strong>Emax = ${formatNumber(iteration.error_maximo)}</strong> (${formatNumber(iteration.error_porcentual)} % informativo)</p>
          <p>Emax &lt; epsilon (${formatNumber(result.epsilon)})? <strong>${decision}</strong></p>
        </div>
      </div>`;
    container.append(detail);
  });
}

function renderFinal(result) {
  const solutionValues = result.solucion.map((value, i) => `<div class="solution-value">x${i + 1} ≈ ${formatNumber(value)}</div>`).join("");
  $("#final-result").innerHTML = `
    <div class="result-hero">
      <div class="solution-card"><h3>Solución aproximada</h3><div class="solution-list">${solutionValues}</div></div>
      <div class="metrics">
        <div class="metric"><span>Estado</span><strong class="${result.convergio ? "state-ok" : "state-warn"}">${result.estado}</strong></div>
        <div class="metric"><span>Iteraciones</span><strong>${result.iteraciones_realizadas}</strong></div>
        <div class="metric"><span>Error relativo final</span><strong>${formatNumber(result.error_final)}</strong></div>
        <div class="metric"><span>Epsilon</span><strong>${formatNumber(result.epsilon)} (${formatNumber(result.epsilon_porcentual)} %)</strong></div>
      </div>
    </div>`;

  const check = result.comprobacion;
  $("#residual-result").innerHTML = `
    <h3>Comprobación adicional</h3><p class="muted">${check.nota}</p>
    <div class="residual-grid">
      <div><span>Ax</span><code>${vectorText(check.Ax)}</code></div>
      <div><span>b</span><code>${vectorText(check.b)}</code></div>
      <div><span>r = b − Ax</span><code>${vectorText(check.residuo)}</code></div>
      <div><span>||r||∞</span><code>${formatNumber(check.norma_infinito)}</code></div>
    </div>`;
}

function renderSolution(result) {
  renderTable(result);
  renderDetails(result);
  renderFinal(result);
  ["#paso-6", "#paso-7", "#paso-8"].forEach((id) => { $(id).hidden = false; });
}

function buildProcedure(result) {
  const lines = [
    "MÉTODO DE JACOBI — PROCEDIMIENTO COMPLETO",
    "",
    "1. SISTEMA ORIGINAL",
    ...result.A.map((row, i) => equationText(row, result.b[i])),
    `A = ${JSON.stringify(result.A)}`,
    `b = ${vectorText(result.b)}`,
    "",
    "2. ANÁLISIS DE DOMINANCIA DIAGONAL ESTRICTA",
    ...result.analisis.filas.map((row) => `Fila ${row.fila}: ${row.comparacion} → ${row.cumple ? "cumple" : "no cumple"}. Margen = ${formatNumber(row.margen)}`),
    result.analisis.conclusion,
    result.analisis.explicacion,
    "",
    "3. FÓRMULAS DESPEJADAS",
    ...result.formulas.map((formula) => formula.texto),
    "",
    "4. CONFIGURACIÓN",
    `x^(0) = ${vectorText(result.x0)}`,
    `epsilon = ${formatNumber(result.epsilon)} (adimensional; ${formatNumber(result.epsilon_porcentual)} % equivalente)`,
    `máximo de iteraciones = ${result.max_iteraciones}`,
    "criterio de parada: Emax < epsilon",
  ];

  result.iteraciones.slice(1).forEach((iteration) => {
    lines.push("", `ITERACIÓN ${iteration.k}`, `Vector anterior: ${vectorText(iteration.vector_anterior)}`);
    iteration.componentes.forEach((component) => {
      lines.push(
        `x${component.variable}^(${iteration.k})`,
        `  Fórmula: ${component.formula_texto}`,
        `  Sustitución: ${component.sustitucion_texto}`,
        `  Suma no diagonal = ${formatNumber(component.suma)}`,
        `  Operación: ${component.operacion_texto}`,
        `  Resultado: ${formatNumber(component.resultado)}`,
        `  |Δ| = ${formatNumber(component.diferencia_absoluta)}`,
        `  E${component.variable} = ${formatNumber(component.error)} (${component.tipo_error})`,
      );
    });
    lines.push(
      `x^(${iteration.k}) = ${vectorText(iteration.vector)}`,
      `Emax = ${formatNumber(iteration.error_maximo)} (${formatNumber(iteration.error_porcentual)} % informativo)`,
      `¿Emax < epsilon? ${iteration.convergio ? "Sí. Criterio de parada satisfecho." : "No. Se requiere una nueva iteración."}`,
    );
  });

  lines.push(
    "", "5. RESULTADO FINAL",
    `Estado: ${result.estado}`,
    `Solución aproximada: ${vectorText(result.solucion)}`,
    `Iteraciones: ${result.iteraciones_realizadas}`,
    `Error relativo final: ${formatNumber(result.error_final)}`,
    "", "6. COMPROBACIÓN ADICIONAL",
    `Ax = ${vectorText(result.comprobacion.Ax)}`,
    `b = ${vectorText(result.comprobacion.b)}`,
    `r = b - Ax = ${vectorText(result.comprobacion.residuo)}`,
    `||r||∞ = ${formatNumber(result.comprobacion.norma_infinito)}`,
    "El residuo es una comprobación adicional y no forma parte del criterio de parada.",
  );
  return lines.join("\n");
}

async function analyzeSystem() {
  hideMessage();
  const button = $("#analyze-button");
  try {
    const payload = readSystem();
    setBusy(button, true, "Analizando…");
    const data = await postJson("/api/jacobi/analizar", payload);
    state.analysis = data;
    state.result = null;
    hideSections(".solution-section");
    renderAnalysis(data);
    $("#paso-2").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) { showMessage(error.message); }
  finally { setBusy(button, false, ""); }
}

async function solveSystem() {
  hideMessage();
  const button = $("#solve-button");
  try {
    const payload = { ...readSystem(), ...readConfiguration() };
    setBusy(button, true, "Calculando…");
    const result = await postJson("/api/jacobi/resolver", payload);
    state.result = result;
    renderAnalysis(result);
    renderSolution(result);
    $("#paso-6").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) { showMessage(error.message); }
  finally { setBusy(button, false, ""); }
}

async function copyProcedure() {
  if (!state.result) return;
  const text = buildProcedure(state.result);
  const status = $("#copy-status");
  try {
    await navigator.clipboard.writeText(text);
    status.textContent = "Procedimiento copiado.";
  } catch {
    const area = document.createElement("textarea");
    area.value = text;
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.append(area);
    area.select();
    const copied = document.execCommand("copy");
    area.remove();
    status.textContent = copied ? "Procedimiento copiado." : "No fue posible copiar automáticamente.";
  }
}

$("#size-select").addEventListener("change", (event) => buildEditor(Number(event.target.value)));
$("#load-example").addEventListener("click", () => {
  buildEditor(4, OFFICIAL);
  $("#epsilon").value = OFFICIAL.epsilon;
  $("#max-iterations").value = OFFICIAL.max_iteraciones;
  hideMessage();
});
$("#clear-system").addEventListener("click", () => {
  buildEditor(state.n);
  $("#epsilon").value = "0.0001";
  $("#max-iterations").value = "100";
  hideMessage();
});
$("#analyze-button").addEventListener("click", analyzeSystem);
$("#solve-button").addEventListener("click", solveSystem);
$("#copy-procedure").addEventListener("click", copyProcedure);
$("#matrix-a").addEventListener("input", () => { renderEquationPreview(); invalidateAnalysis(); });
$("#vector-b").addEventListener("input", () => { renderEquationPreview(); invalidateAnalysis(); });
$("#vector-x0").addEventListener("input", invalidateSolution);
$("#epsilon").addEventListener("input", invalidateSolution);
$("#max-iterations").addEventListener("input", invalidateSolution);

buildEditor(4, OFFICIAL);

