// Front-end logic: send the two texts to /analyze, then draw the result.

const form = document.getElementById("analyze-form");
const resumeEl = document.getElementById("resume");
const jdEl = document.getElementById("jd");
const analyzeBtn = document.getElementById("analyze-btn");
const clearBtn = document.getElementById("clear-btn");
const errorBox = document.getElementById("error-box");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

// ---------- small helpers ----------
function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function hideError() {
  errorBox.hidden = true;
}

function setLoading(isLoading) {
  analyzeBtn.disabled = isLoading;
  statusEl.textContent = isLoading ? "Analyzing..." : "";
}

// Builds an element with textContent (safe: never inserts raw HTML)
function makeEl(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text) node.textContent = text;
  return node;
}

function fillChips(containerId, items, chipClass, getName, getNote) {
  const box = document.getElementById(containerId);
  box.replaceChildren();
  if (items.length === 0) {
    box.append(makeEl("p", "empty", "Nothing found here."));
    return;
  }
  for (const item of items) {
    const chip = makeEl("span", "chip " + chipClass, getName(item));
    chip.append(makeEl("small", "", getNote(item)));
    box.append(chip);
  }
}

function fillList(listId, items, emptyText) {
  const list = document.getElementById(listId);
  list.replaceChildren();
  if (items.length === 0) {
    list.append(makeEl("li", "empty", emptyText));
    return;
  }
  for (const text of items) list.append(makeEl("li", "", text));
}

// ---------- draw the results ----------
function renderResults(data) {
  const c = data.comparison;
  const total = c.matches.length + c.gaps.length;

  const label = c.overall_fit === "unknown" ? "No known skills detected" : c.overall_fit + " fit";
  document.getElementById("fit-label").textContent = label.charAt(0).toUpperCase() + label.slice(1);
  document.getElementById("fit-detail").textContent =
    total === 0
      ? "The demo could not find any known skills in the job description."
      : c.matches.length + " of " + total + " requirements from the job description appear in your resume.";

  fillChips("matches", c.matches, "chip-match", (m) => m.requirement, (m) => m.status);
  fillChips("gaps", c.gaps, "chip-gap", (g) => g.requirement, (g) => g.status.replace("_", " "));
  fillList("strengths", c.strengths, "None identified yet.");
  fillList("improvements", c.improvement_areas, "None identified yet.");

  resultsEl.hidden = false;
  resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ---------- events ----------
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError();

  // quick check here; the server checks again (never trust only the browser)
  if (!resumeEl.value.trim() || !jdEl.value.trim()) {
    showError("Please paste both your resume and the job description.");
    return;
  }

  setLoading(true);
  try {
    const response = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: resumeEl.value, jd_text: jdEl.value }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Something went wrong. Try again.");
    renderResults(data);
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
});

clearBtn.addEventListener("click", () => {
  resumeEl.value = "";
  jdEl.value = "";
  hideError();
  resultsEl.hidden = true;
  resumeEl.focus();
});
