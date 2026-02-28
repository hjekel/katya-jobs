// Katya's JobFinder — Frontend (Jobs page)

let currentOffset = 0;
let currentTotal = 0;
const PAGE_SIZE = 50;
let searchTimeout = null;
const HOME_ENCODED = "Laan+van+Decima+1B,+Haarlem";

// Active filters state
const activeFilters = {
    category: null,
    city: null,
    company: null,
    posting_type: null,
    source: null,
};

// Filter counts data
let filterData = null;
let companiesExpanded = false;
const MAX_COMPANIES_VISIBLE = 15;
const isMobile = () => window.innerWidth <= 768;

document.addEventListener("DOMContentLoaded", () => {
    loadStats();
    loadFilters();
    loadJobs();
});

async function api(path, opts = {}) {
    const resp = await fetch(path, opts);
    return resp.json();
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

    // Location list
    const cities = Object.entries(filterData.cities || {}).filter(([c]) => c);
    renderListFromEntries("list-location", cities, "city");

    // Company list
    renderCompanyList();

    // Posting type list (with dot indicators)
    const typeLabels = { direct: "Direct employer", recruiter: "Via recruiter", job_board: "Job board" };
    const ptContainer = document.getElementById("list-posting-type");
    ptContainer.innerHTML = "";
    for (const [ptype, count] of Object.entries(filterData.posting_types || {})) {
        ptContainer.appendChild(createFilterRow(
            typeLabels[ptype] || ptype, count, "posting_type", ptype, `dot-${ptype}`
        ));
    }

    // Source list
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

function renderCompanyList() {
    const container = document.getElementById("list-company");
    container.innerHTML = "";
    const companies = Object.entries(filterData.companies || {});
    const showBtn = document.getElementById("btn-show-all-companies");

    const limit = companiesExpanded ? companies.length : MAX_COMPANIES_VISIBLE;
    companies.slice(0, limit).forEach(([company, count]) => {
        container.appendChild(createFilterRow(company, count, "company", company));
    });

    if (companies.length > MAX_COMPANIES_VISIBLE) {
        showBtn.style.display = "block";
        showBtn.textContent = companiesExpanded
            ? "Show less"
            : `Show all (${companies.length})`;
    } else {
        showBtn.style.display = "none";
    }
}

function showAllCompanies() {
    companiesExpanded = !companiesExpanded;
    renderCompanyList();
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
        category: "Category",
        city: "Location",
        company: "Company",
        posting_type: "Type",
        source: "Source",
    };
    const typeLabels = { direct: "Direct", recruiter: "Via recruiter", job_board: "Job board" };

    let hasActive = false;
    for (const [key, value] of Object.entries(activeFilters)) {
        if (value !== null) {
            hasActive = true;
            const chip = document.createElement("span");
            chip.className = "active-chip";
            const displayValue = key === "posting_type" ? (typeLabels[value] || value) : value;
            chip.innerHTML = `${filterLabels[key]}: ${escHtml(displayValue)} <span class="active-chip-remove" data-key="${key}">&times;</span>`;
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

    const search = document.getElementById("search-input").value.trim();
    const onlyNew = document.getElementById("toggle-new").checked;
    const sort = document.getElementById("sort-select").value;

    const params = new URLSearchParams({ limit: PAGE_SIZE, offset: currentOffset, sort });
    if (search) params.set("search", search);
    if (onlyNew) params.set("only_new", "true");
    if (activeFilters.category) params.set("category", activeFilters.category);
    if (activeFilters.city) params.set("city", activeFilters.city);
    if (activeFilters.company) params.set("company", activeFilters.company);
    if (activeFilters.posting_type) params.set("posting_type", activeFilters.posting_type);
    if (activeFilters.source) params.set("source", activeFilters.source);

    const data = await api(`/api/jobs?${params}`);
    currentTotal = data.total;

    const container = document.getElementById("jobs-container");
    const emptyState = document.getElementById("empty-state");
    const loadMoreContainer = document.getElementById("load-more-container");

    if (!append) container.innerHTML = "";

    if (data.jobs.length === 0 && !append) {
        emptyState.style.display = "block";
        loadMoreContainer.style.display = "none";
        document.getElementById("results-count").textContent = "No jobs found";
        return;
    }

    emptyState.style.display = "none";
    data.jobs.forEach(job => container.appendChild(createJobCard(job)));

    const shown = currentOffset + data.jobs.length;
    loadMoreContainer.style.display = shown < currentTotal ? "block" : "none";
    document.getElementById("results-count").textContent = `Showing ${shown} of ${currentTotal} jobs`;
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
        salaryHtml = `<div class="job-salary no-salary">Salary not listed</div>`;
    }

    // Commute display
    let commuteHtml = "";
    if (job.location) {
        const url = mapsUrl(job.location);
        commuteHtml = `
            <div class="job-commute">
                <span>\uD83D\uDE86 Commute from Haarlem</span>
                <a href="${escHtml(url)}" target="_blank" rel="noopener"
                   onclick="event.stopPropagation()">Get directions \u2192</a>
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
        typeBadge = `<span class="badge-recruiter">Via recruiter</span>`;
    } else if (job.posting_type === "direct") {
        typeBadge = `<span class="badge-direct">Direct</span>`;
    } else if (job.posting_type === "job_board") {
        typeBadge = `<span class="badge-jobboard">Job board</span>`;
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
            <span class="job-score ${scoreClass}">${job.score}pts</span>
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
                <span class="job-source ${sourceClass}">Posted on ${escHtml(job.source)}</span>
            </div>
            <div class="job-actions">
                <button class="btn-save" id="save-${job.id}"
                        onclick="event.stopPropagation(); saveJob(${job.id})">Save</button>
                <button class="btn-hide"
                        onclick="event.stopPropagation(); hideJob(${job.id})">Hide</button>
                <a class="btn-apply" href="${escHtml(job.url)}" target="_blank" rel="noopener"
                   onclick="event.stopPropagation()">View \u2192</a>
            </div>
        </div>
        <div class="expand-hint">Click card to see why Katya fits</div>
        <div class="job-fit" id="fit-${job.id}"></div>
    `;

    card.addEventListener("click", (e) => {
        if (e.target.closest("a, button")) return;
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

    fitEl.innerHTML = `<p class="job-fit-loading">Analysing fit...</p>`;
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
        fitEl.innerHTML = `<p class="job-fit-loading">Could not load analysis.</p>`;
    }
}

// ——— Save job to application tracker ———

async function saveJob(jobId) {
    const data = await api(`/api/applications/${jobId}/save`, { method: "POST" });
    const btn = document.getElementById(`save-${jobId}`);
    if (btn) {
        btn.classList.add("saved");
        btn.textContent = data.status === "created" ? "Saved!" : "Already saved";
    }
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
    statusText.textContent = "Scanning 6 job boards... this may take a minute.";

    try {
        const data = await api("/api/scrape", { method: "POST" });
        if (data.status === "completed") {
            const parts = Object.entries(data.results)
                .map(([src, count]) => `${src}: ${count} new`)
                .join(", ");
            statusText.textContent = `Done! ${parts}`;
        } else {
            statusText.textContent = "Scrape is already running.";
        }
        loadStats();
        loadFilters();
        loadJobs();
    } catch (err) {
        statusText.textContent = "Error scanning. Try again later.";
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
    document.getElementById("stat-total").textContent = `${data.total} jobs`;
    const newBadge = document.getElementById("stat-new");
    if (data.new > 0) {
        newBadge.textContent = `${data.new} new`;
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
