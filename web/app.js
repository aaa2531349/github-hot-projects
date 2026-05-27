const dataUrl = "./data/latest.json";
const datesUrl = "./data/dates.json";

let availableDates = [];
let latestDate = "";

const imageForRepo = (repo, index) => {
  const clean = encodeURIComponent(repo).replace("%2F", "/");
  return `https://opengraph.githubassets.com/daily-radar-${index}/${clean}`;
};

const shorten = (text, max = 148) => {
  if (!text) return "";
  return text.length > max ? `${text.slice(0, max - 1)}...` : text;
};

const starsToNumber = (value) => Number(String(value || "0").replace(/,/g, "")) || 0;

const trendToNumber = (value) => {
  const match = String(value || "").replace(/,/g, "").match(/(\d+)/);
  return match ? Number(match[1]) : 0;
};

const localizeTrend = (value) => {
  const match = String(value || "").replace(/,/g, "").match(/(\d+)/);
  if (!match) return value || "";
  return `今日新增 ${Number(match[1]).toLocaleString()} stars`;
};

const languageTone = (language = "") => {
  const key = language.toLowerCase();
  if (key.includes("type")) return "tone-blue";
  if (key.includes("python")) return "tone-green";
  if (key.includes("java")) return "tone-yellow";
  if (key.includes("shell")) return "tone-gray";
  return "tone-purple";
};

const renderSpotlight = (repos) => {
  const top = repos[0];
  const spotlight = document.querySelector("#spotlight");
  if (!top || !spotlight) return;
  const description = top.description_zh || top.description;

  spotlight.innerHTML = `
    <img src="${imageForRepo(top.repo, 0)}" alt="${top.repo} social preview" />
    <div>
      <span class="status-pill">今日第 1</span>
      <h3>${top.repo}</h3>
      <p>${shorten(description, 170)}</p>
      <div class="meta-row">
        ${top.language ? `<span class="${languageTone(top.language)}">${top.language}</span>` : ""}
        ${top.stars ? `<span>${top.stars} stars</span>` : ""}
        ${top.trend ? `<span>${localizeTrend(top.trend)}</span>` : ""}
      </div>
    </div>
  `;
};

const renderMiniList = (repos) => {
  const list = document.querySelector("#mini-list");
  if (!list) return;

  list.innerHTML = repos
    .slice(1, 4)
    .map(
      (repo, index) => `
        <a href="${repo.url}" target="_blank" rel="noreferrer" class="mini-item">
          <span>${String(index + 2).padStart(2, "0")}</span>
          <strong>${repo.repo}</strong>
          <em>${localizeTrend(repo.trend) || repo.stars || "趋势项目"}</em>
        </a>
      `
    )
    .join("");
};

const renderRepos = (repos) => {
  const grid = document.querySelector("#repo-grid");
  if (!grid) return;

  grid.innerHTML = repos
    .map(
      (repo, index) => {
        const description = repo.description_zh || repo.description;
        return `
          <a class="repo-row" href="${repo.url}" target="_blank" rel="noreferrer">
            <span class="row-rank">${String(index + 1).padStart(2, "0")}</span>
            <img src="${imageForRepo(repo.repo, index + 1)}" alt="${repo.repo} social preview" loading="lazy" />
            <div class="repo-main">
              <div class="repo-heading">
                <h3>${repo.repo}</h3>
                <span class="status-pill">${repo.history_status || "今日热门"}</span>
              </div>
              <p>${shorten(description)}</p>
            </div>
            <div class="repo-meta">
              ${repo.language ? `<span class="${languageTone(repo.language)}">${repo.language}</span>` : ""}
              ${repo.stars ? `<span>${repo.stars}</span>` : ""}
              ${repo.trend ? `<span>${localizeTrend(repo.trend)}</span>` : ""}
            </div>
          </a>
        `;
      }
    )
    .join("");
};

const renderSignals = (repos) => {
  const grid = document.querySelector("#signal-grid");
  if (!grid) return;

  const languageCounts = repos.reduce((counts, repo) => {
    const language = repo.language || "Mixed";
    counts[language] = (counts[language] || 0) + 1;
    return counts;
  }, {});
  const topLanguage = Object.entries(languageCounts).sort((a, b) => b[1] - a[1])[0] || ["Mixed", 0];
  const newCount = repos.filter((repo) => repo.history_status === "新上榜").length;
  const totalTrend = repos.reduce((sum, repo) => sum + trendToNumber(repo.trend), 0);
  const totalStars = repos.reduce((sum, repo) => sum + starsToNumber(repo.stars), 0);

  grid.innerHTML = `
    <article class="signal-card">
      <span>主力语言</span>
      <strong>${topLanguage[0]}</strong>
      <p>${topLanguage[1]} 个席位，今天最密集的技术栈。</p>
    </article>
    <article class="signal-card">
      <span>新鲜度</span>
      <strong>${newCount}/10</strong>
      <p>标记为新上榜，降低连续多日重复。</p>
    </article>
    <article class="signal-card">
      <span>今日增速</span>
      <strong>${totalTrend.toLocaleString()}</strong>
      <p>前 10 今日新增 star 粗略合计。</p>
    </article>
    <article class="signal-card">
      <span>总关注度</span>
      <strong>${Math.round(totalStars / 1000)}k</strong>
      <p>榜单仓库累计 star 量级。</p>
    </article>
  `;
};

const updateDateControl = (selectedDate) => {
  const picker = document.querySelector("#date-picker");
  if (!picker || !availableDates.length) return;
  picker.min = availableDates[0];
  picker.max = availableDates[availableDates.length - 1];
  picker.value = selectedDate;
  picker.disabled = false;
};

const updateIssueLabels = (payload, repos) => {
  const date = payload.date || "每日更新";
  const isLatest = !latestDate || date === latestDate;
  document.querySelector("#issue-date").textContent = date;
  document.querySelector("#issue-count").textContent = `前 ${repos.length}`;
  document.querySelector("#data-source").textContent = `来源：${payload.source || "GitHub Trending"}`;
  document.querySelector("#rank-title").textContent = isLatest ? "今日推送" : `${date} 推送`;
  document.querySelector("#rank-note").textContent = isLatest
    ? "优先展示最近 7 天没有推过的新鲜项目；如果候选不足，再补入仍然热门的重复项目。"
    : "正在查看历史归档榜单，项目热度和 star 数据保留为当天记录。";
  updateDateControl(date);
};

const renderPayload = (payload) => {
  const repos = payload.repositories || [];
  updateIssueLabels(payload, repos);
  renderSpotlight(repos);
  renderMiniList(repos);
  renderRepos(repos);
  renderSignals(repos);
};

const loadPayload = async (url) => {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`无法加载数据 ${response.status}`);
  return response.json();
};

const loadByDate = async (date) => {
  const url = date === latestDate ? dataUrl : `./data/archive/${date}.json`;
  try {
    renderPayload(await loadPayload(url));
  } catch (error) {
    document.querySelector("#repo-grid").innerHTML = `<p class="load-error">${date} 暂无归档数据。</p>`;
  }
};

const initDateControl = () => {
  const picker = document.querySelector("#date-picker");
  const filter = document.querySelector("#date-filter");
  if (!picker) return;

  const openPicker = () => {
    picker.focus({ preventScroll: true });
    if (typeof picker.showPicker === "function") {
      picker.showPicker();
    }
  };

  if (filter) {
    filter.addEventListener("click", (event) => {
      event.preventDefault();
      openPicker();
    });
    filter.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openPicker();
      }
    });
  }

  picker.addEventListener("change", () => {
    if (picker.value) loadByDate(picker.value);
  });
};

const init = async () => {
  try {
    const dates = await loadPayload(datesUrl);
    availableDates = [...(dates.dates || [])].sort();
    latestDate = dates.latest || availableDates[availableDates.length - 1] || "";
  } catch {
    availableDates = [];
    latestDate = "";
  }

  initDateControl();
  const response = await fetch(dataUrl);
  const payload = await response.json();
  if (!latestDate) latestDate = payload.date || "";
  if (!availableDates.length && payload.date) availableDates = [payload.date];
  renderPayload(payload);
};

init().catch((error) => {
  document.querySelector("#repo-grid").innerHTML = `<p class="load-error">数据加载失败：${error.message}</p>`;
});
