// Katya's JobFinder — Frontend (Jobs page)

let currentOffset = 0;
let currentTotal = 0;
const PAGE_SIZE = 50;
let searchTimeout = null;
let loadGeneration = 0;
const HOME_ENCODED = "Laan+van+Decima+1B,+Haarlem";

// Active filters state (company and posting_type removed, only source remains)
const activeFilters = {
    category: null,
    city: null,
    source: null,
};

// Filter counts data
let filterData = null;
const isMobile = () => window.innerWidth <= 768;

// Exclude Dutch toggle — default ON, stored in cookie
let excludeDutch = getCookie('excludeDutch') !== 'false';

document.addEventListener("DOMContentLoaded", () => {
    // Restore exclude Dutch toggle from cookie
    const toggle = document.getElementById("toggle-dutch");
    if (toggle) toggle.checked = excludeDutch;

    loadStats();
    loadFilters();
    loadJobs();
    loadCustomKeywords();
    loadCustomBoards();

    // Enter key for keyword/board inputs
    const kwInput = document.getElementById("input-keyword");
    if (kwInput) kwInput.addEventListener("keydown", e => { if (e.key === "Enter") addCustomKeyword(); });
    const boardInput = document.getElementById("input-add-board");
    if (boardInput) boardInput.addEventListener("keydown", e => { if (e.key === "Enter") addCustomBoard(); });
});

// Called by theme.js when language changes
function onLanguageChange() {
    renderFilterLists();
    renderActiveFilters();
    loadJobs();
    loadStats();
}

async function api(path, opts = {}) {
    const resp = await fetch(path, opts);
    return resp.json();
}

// ——— Exclude Dutch toggle ———

function onDutchToggle() {
    excludeDutch = document.getElementById("toggle-dutch").checked;
    setCookie('excludeDutch', excludeDutch);
    loadJobs();
}

// ——— Filter panels ———

async function loadFilters() {
    filterData = await api("/api/filters");
    renderFilterLists();
}

function renderFilterLists() {
    if (!filterData) return;

    // Category list
    renderList("list-category", filterData.categories || {}, "category");

    // Location list — Haarlem always first with separator
    const allCities = Object.entries(filterData.cities || {}).filter(([c]) => c);
    const haarlem = allCities.filter(([c]) => c === "Haarlem");
    const rest = allCities.filter(([c]) => c !== "Haarlem");
    const container = document.getElementById("list-location");
    container.innerHTML = "";
    for (const [label, count] of haarlem) {
        container.appendChild(createFilterRow(label, count, "city", label));
    }
    if (haarlem.length > 0 && rest.length > 0) {
        const divider = document.createElement("li");
        divider.className = "filter-list-divider";
        container.appendChild(divider);
    }
    for (const [label, count] of rest) {
        container.appendChild(createFilterRow(label, count, "city", label));
    }

    // Source list (job boards)
    renderList("list-source", filterData.sources || {}, "source");
}

function renderList(containerId, dataObj, filterKey) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";
    for (const [label, count] of Object.entries(dataObj)) {
        container.appendChild(createFilterRow(label, count, filterKey, label));
    }
}

function renderListFromEntries(containerId, entries, filterKey) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";
    for (const [label, count] of entries) {
        container.appendChild(createFilterRow(label, count, filterKey, label));
    }
}

function createFilterRow(label, count, filterKey, filterValue, dotClass) {
    const li = document.createElement("li");
    li.className = "filter-row";
    if (activeFilters[filterKey] === filterValue) li.classList.add("active");

    let dotHtml = "";
    if (dotClass) dotHtml = `<span class="filter-row-dot ${dotClass}"></span>`;

    li.innerHTML = `${dotHtml}<span class="filter-row-label">${escHtml(label)}</span><span class="filter-row-count">${count}</span>`;
    li.addEventListener("click", () => {
        if (activeFilters[filterKey] === filterValue) {
            activeFilters[filterKey] = null;
        } else {
            activeFilters[filterKey] = filterValue;
        }
        renderFilterLists();
        renderActiveFilters();
        loadJobs();
    });
    return li;
}

function togglePanel(headerEl) {
    const panel = headerEl.closest(".filter-panel");
    const body = panel.querySelector(".panel-body");

    if (isMobile()) {
        panel.classList.toggle("expanded");
    } else {
        headerEl.classList.toggle("collapsed");
        body.classList.toggle("collapsed");
    }
}

// ——— Active filters bar ———

function renderActiveFilters() {
    const container = document.getElementById("active-filters");
    const chipsContainer = document.getElementById("active-filters-chips");
    chipsContainer.innerHTML = "";

    const filterLabels = {
        category: t('filter-label-category'),
        city: t('filter-label-location'),
        source: t('filter-label-source'),
    };

    let hasActive = false;
    for (const [key, value] of Object.entries(activeFilters)) {
        if (value !== null) {
            hasActive = true;
            const chip = document.createElement("span");
            chip.className = "active-chip";
            chip.innerHTML = `${filterLabels[key]}: ${escHtml(value)} <span class="active-chip-remove" data-key="${key}">&times;</span>`;
            chip.querySelector(".active-chip-remove").addEventListener("click", (e) => {
                e.stopPropagation();
                activeFilters[key] = null;
                renderFilterLists();
                renderActiveFilters();
                loadJobs();
            });
            chipsContainer.appendChild(chip);
        }
    }

    container.style.display = hasActive ? "flex" : "none";
}

function clearAllFilters() {
    for (const key of Object.keys(activeFilters)) {
        activeFilters[key] = null;
    }
    renderFilterLists();
    renderActiveFilters();
    loadJobs();
}

// ——— Load jobs ———

async function loadJobs(append = false) {
    if (!append) currentOffset = 0;

    const thisGen = ++loadGeneration;

    const search = document.getElementById("search-input").value.trim();
    const onlyNew = document.getElementById("toggle-new").checked;
    const sort = document.getElementById("sort-select").value;

    const params = new URLSearchParams({ limit: PAGE_SIZE, offset: currentOffset, sort });
    if (search) params.set("search", search);
    if (onlyNew) params.set("only_new", "true");
    if (excludeDutch) params.set("exclude_dutch", "true");
    if (activeFilters.category) params.set("category", activeFilters.category);
    if (activeFilters.city) params.set("city", activeFilters.city);
    if (activeFilters.source) params.set("source", activeFilters.source);

    const data = await api(`/api/jobs?${params}`);

    if (thisGen !== loadGeneration) return;

    currentTotal = data.total;

    const container = document.getElementById("jobs-container");
    const emptyState = document.getElementById("empty-state");
    const loadMoreContainer = document.getElementById("load-more-container");

    if (!append) container.innerHTML = "";

    if (data.jobs.length === 0 && !append) {
        emptyState.style.display = "block";
        loadMoreContainer.style.display = "none";
        document.getElementById("results-count").textContent = t('no-jobs-found');
        return;
    }

    emptyState.style.display = "none";
    data.jobs.forEach(job => container.appendChild(createJobCard(job)));

    const shown = currentOffset + data.jobs.length;
    loadMoreContainer.style.display = shown < currentTotal ? "block" : "none";
    document.getElementById("results-count").textContent = t('showing-jobs', { shown: shown, total: currentTotal });
}

function loadMore() {
    currentOffset += PAGE_SIZE;
    loadJobs(true);
}

// ——— Build Google Maps commute URL ———

function mapsUrl(location) {
    if (!location) return null;
    const dest = encodeURIComponent(location);
    return `https://www.google.com/maps/dir/${HOME_ENCODED}/${dest}?travelmode=transit`;
}

// ——— Score breakdown popup ———

function showScorePopup(job, event) {
    event.stopPropagation();
    const popup = document.getElementById("score-popup");
    const overlay = document.getElementById("score-popup-overlay");
    const body = document.getElementById("score-popup-body");

    const breakdown = job.score_breakdown;
    if (!breakdown || !breakdown.components) return;

    let html = '<ul class="score-breakdown-list">';
    for (const comp of breakdown.components) {
        const sign = comp.points >= 0 ? "+" : "";
        const cls = comp.points >= 0 ? "positive" : "negative";
        html += `<li class="${cls}"><span class="sbl-label">${escHtml(comp.label)}</span><span class="sbl-pts">${sign}${comp.points}pts</span></li>`;
    }
    html += '</ul>';
    html += `<div class="score-breakdown-total"><span>${escHtml(t('score-total'))}</span><span>${breakdown.total}pts</span></div>`;

    body.innerHTML = html;
    popup.style.display = "block";
    overlay.style.display = "block";
}

function closeScorePopup() {
    document.getElementById("score-popup").style.display = "none";
    document.getElementById("score-popup-overlay").style.display = "none";
}

// ——— Create a job card ———

function createJobCard(job) {
    const card = document.createElement("div");
    card.className = "job-card" + (job.is_new ? " is-new" : "");
    card.id = `job-${job.id}`;

    const scoreClass = job.score >= 70 ? "high" : job.score >= 40 ? "medium" : "low";
    const sourceClass = `source-${job.source}`;

    // Salary display
    let salaryHtml;
    if (job.salary_min && job.salary_max) {
        if (job.salary_min === job.salary_max) {
            salaryHtml = `<div class="job-salary has-salary">\u20AC${job.salary_min.toLocaleString()}/month</div>`;
        } else {
            salaryHtml = `<div class="job-salary has-salary">\u20AC${job.salary_min.toLocaleString()} \u2013 \u20AC${job.salary_max.toLocaleString()}/month</div>`;
        }
    } else {
        salaryHtml = `<div class="job-salary no-salary">${escHtml(t('salary-not-listed'))}</div>`;
    }

    // Commute display
    let commuteHtml = "";
    if (job.location) {
        const url = mapsUrl(job.location);
        commuteHtml = `
            <div class="job-commute">
                <span>${escHtml(t('commute-from'))}</span>
                <a href="${escHtml(url)}" target="_blank" rel="noopener"
                   onclick="event.stopPropagation()">${escHtml(t('get-directions'))}</a>
            </div>`;
    }

    // Posting age
    let ageHtml = "";
    if (job.posting_age_text) {
        const ageColor = job.posting_age_color || "grey";
        ageHtml = `<span><span class="age-dot ${ageColor}"></span> ${escHtml(job.posting_age_text)}</span>`;
    } else if (job.date_posted) {
        ageHtml = `<span>\uD83D\uDCC5 ${escHtml(job.date_posted)}</span>`;
    }

    // Posting type badge
    let typeBadge = "";
    if (job.posting_type === "recruiter") {
        typeBadge = `<span class="badge-recruiter">${escHtml(t('chip-recruiter'))}</span>`;
    } else if (job.posting_type === "direct") {
        typeBadge = `<span class="badge-direct">${escHtml(t('chip-direct'))}</span>`;
    } else if (job.posting_type === "job_board") {
        typeBadge = `<span class="badge-jobboard">${escHtml(t('chip-job_board'))}</span>`;
    }

    // Category badge
    let categoryBadge = "";
    if (job.category && job.category !== "Other") {
        categoryBadge = `<span class="badge-category">${escHtml(job.category)}</span>`;
    }

    card.innerHTML = `
        <div class="job-card-header">
            <a class="job-title" href="${escHtml(job.url)}" target="_blank" rel="noopener"
               onclick="event.stopPropagation()">
                ${escHtml(job.title)}
            </a>
            <span class="job-score ${scoreClass}" data-job-id="${job.id}">${job.score}pts</span>
        </div>
        <div class="job-meta">
            ${job.company ? `<span>\uD83C\uDFE2 ${escHtml(job.company)}</span>` : ""}
            ${job.location ? `<span>\uD83D\uDCCD ${escHtml(job.location)}</span>` : ""}
            ${ageHtml}
            ${typeBadge}
            ${categoryBadge}
        </div>
        ${salaryHtml}
        ${commuteHtml}
        ${job.snippet ? `<p class="job-snippet">${escHtml(job.snippet)}</p>` : ""}
        <div class="job-footer">
            <div class="job-footer-left">
                <span class="job-source ${sourceClass}">${escHtml(t('posted-on', { source: job.source }))}</span>
            </div>
            <div class="job-actions">
                <button class="btn-save" id="save-${job.id}"
                        onclick="event.stopPropagation(); saveJob(${job.id})">${escHtml(t('btn-save'))}</button>
                <button class="btn-hide"
                        onclick="event.stopPropagation(); hideJob(${job.id})">${escHtml(t('btn-hide'))}</button>
                <a class="btn-apply" href="${escHtml(job.url)}" target="_blank" rel="noopener"
                   onclick="event.stopPropagation()">${escHtml(t('btn-view'))}</a>
            </div>
        </div>
        <div class="expand-hint">${escHtml(t('expand-hint'))}</div>
        <div class="job-fit" id="fit-${job.id}"></div>
    `;

    // Score badge click → score breakdown popup
    const scoreBadge = card.querySelector(".job-score");
    scoreBadge.addEventListener("click", (e) => {
        showScorePopup(job, e);
    });
    scoreBadge.style.cursor = "pointer";

    // Card body click → fit analysis (excluding links, buttons, score badge)
    card.addEventListener("click", (e) => {
        if (e.target.closest("a, button, .job-score")) return;
        toggleFit(job);
    });

    return card;
}

// ——— Toggle fit analysis ———

async function toggleFit(job) {
    const fitEl = document.getElementById(`fit-${job.id}`);
    if (!fitEl) return;

    if (fitEl.classList.contains("open")) {
        fitEl.classList.remove("open");
        return;
    }
    if (fitEl.dataset.loaded) {
        fitEl.classList.add("open");
        return;
    }

    fitEl.innerHTML = `<p class="job-fit-loading">${escHtml(t('analysing-fit'))}</p>`;
    fitEl.classList.add("open");

    try {
        const params = new URLSearchParams({
            title: job.title || "",
            snippet: job.snippet || "",
            location: job.location || "",
        });
        const data = await api(`/api/fit?${params}`);
        fitEl.innerHTML = `
            <p class="job-fit-tagline">${escHtml(data.tagline)}</p>
            <ul class="job-fit-bullets">
                ${data.bullets.map(b => `<li>${escHtml(b)}</li>`).join("")}
            </ul>
        `;
        fitEl.dataset.loaded = "1";
    } catch (err) {
        fitEl.innerHTML = `<p class="job-fit-loading">${escHtml(t('fit-error'))}</p>`;
    }
}

// ——— Save job to application tracker ———

async function saveJob(jobId) {
    const data = await api(`/api/applications/${jobId}/save`, { method: "POST" });
    const btn = document.getElementById(`save-${jobId}`);
    if (btn) {
        btn.classList.add("saved");
        btn.textContent = data.status === "created" ? t('btn-saved') : t('btn-already-saved');
    }
}

// ——— Custom keywords ———

async function loadCustomKeywords() {
    const data = await api("/api/custom-keywords");
    renderKeywordTags(data.keywords || []);
}

function renderKeywordTags(keywords) {
    const container = document.getElementById("keywords-tags");
    container.innerHTML = "";
    for (const kw of keywords) {
        const tag = document.createElement("span");
        tag.className = "keyword-tag";
        tag.innerHTML = `${escHtml(kw.keyword)} <span class="keyword-tag-remove" data-id="${kw.id}">&times;</span>`;
        tag.querySelector(".keyword-tag-remove").addEventListener("click", () => removeKeyword(kw.id));
        container.appendChild(tag);
    }
}

async function addCustomKeyword() {
    const input = document.getElementById("input-keyword");
    const keyword = input.value.trim();
    if (!keyword) return;
    await api("/api/custom-keywords", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword }),
    });
    input.value = "";
    loadCustomKeywords();
}

async function removeKeyword(id) {
    await api(`/api/custom-keywords/${id}`, { method: "DELETE" });
    loadCustomKeywords();
}

// ——— Custom job boards ———

async function loadCustomBoards() {
    const data = await api("/api/custom-job-boards");
    renderCustomBoards(data.boards || []);
}

function renderCustomBoards(boards) {
    const container = document.getElementById("list-custom-boards");
    container.innerHTML = "";
    for (const board of boards) {
        const li = document.createElement("li");
        li.className = "filter-row custom-board-row";
        li.innerHTML = `
            <span class="filter-row-label">${escHtml(board.name)}</span>
            <span class="custom-board-remove" data-id="${board.id}">&times;</span>
        `;
        li.querySelector(".custom-board-remove").addEventListener("click", (e) => {
            e.stopPropagation();
            removeCustomBoard(board.id);
        });
        container.appendChild(li);
    }
}

async function addCustomBoard() {
    const input = document.getElementById("input-add-board");
    const name = input.value.trim();
    if (!name) return;
    await api("/api/custom-job-boards", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, url: name }),
    });
    input.value = "";
    loadCustomBoards();
}

async function removeCustomBoard(id) {
    await api(`/api/custom-job-boards/${id}`, { method: "DELETE" });
    loadCustomBoards();
}

// ——— Search ———

function debounceSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => loadJobs(), 300);
}

// ——— Scrape ———

async function startScrape() {
    const btn = document.getElementById("btn-scrape");
    const statusBar = document.getElementById("status-bar");
    const statusText = document.getElementById("status-text");

    btn.disabled = true;
    btn.classList.add("spinning");
    statusBar.style.display = "flex";
    statusText.textContent = t('scanning-text');

    try {
        const data = await api("/api/scrape", { method: "POST" });
        if (data.status === "completed") {
            const parts = Object.entries(data.results)
                .map(([src, count]) => `${src}: ${t('scrape-new', { count: count })}`)
                .join(", ");
            statusText.textContent = t('scrape-done', { details: parts });
        } else {
            statusText.textContent = t('scrape-running');
        }
        loadStats();
        loadFilters();
        loadJobs();
    } catch (err) {
        statusText.textContent = t('scrape-error');
    } finally {
        btn.disabled = false;
        btn.classList.remove("spinning");
        setTimeout(() => { statusBar.style.display = "none"; }, 5000);
    }
}

async function hideJob(jobId) {
    await api(`/api/jobs/${jobId}/hide`, { method: "POST" });
    const card = document.getElementById(`job-${jobId}`);
    if (card) {
        card.style.transition = "opacity 0.3s, transform 0.3s";
        card.style.opacity = "0";
        card.style.transform = "translateX(30px)";
        setTimeout(() => card.remove(), 300);
    }
    loadStats();
    loadFilters();
}

async function loadStats() {
    const data = await api("/api/stats");
    document.getElementById("stat-total").textContent = t('jobs-count', { n: data.total });
    const newBadge = document.getElementById("stat-new");
    if (data.new > 0) {
        newBadge.textContent = t('new-count', { n: data.new });
        newBadge.style.display = "inline";
    } else {
        newBadge.style.display = "none";
    }
}

function escHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
