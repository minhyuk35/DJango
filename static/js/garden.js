"use strict";
const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const roundRect = (ctx, x, y, w, h, r) => {
    const radius = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.arcTo(x + w, y, x + w, y + h, radius);
    ctx.arcTo(x + w, y + h, x, y + h, radius);
    ctx.arcTo(x, y + h, x, y, radius);
    ctx.arcTo(x, y, x + w, y, radius);
    ctx.closePath();
};
const parseRgba = (c) => {
    const hex = c.trim();
    if (hex.startsWith("#")) {
        const v = hex.slice(1);
        if (v.length === 3) {
            const r = parseInt(v[0] + v[0], 16);
            const g = parseInt(v[1] + v[1], 16);
            const b = parseInt(v[2] + v[2], 16);
            return [r, g, b, 1];
        }
        if (v.length === 6) {
            const r = parseInt(v.slice(0, 2), 16);
            const g = parseInt(v.slice(2, 4), 16);
            const b = parseInt(v.slice(4, 6), 16);
            return [r, g, b, 1];
        }
    }
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m)
        return [255, 255, 255, 1];
    const parts = m[1].split(",").map((p) => parseFloat(p.trim()));
    const [r, g, b] = parts;
    const a = parts.length > 3 ? parts[3] : 1;
    return [r, g, b, a];
};
const mixColor = (a, b, t) => {
    const A = parseRgba(a);
    const B = parseRgba(b);
    const r = A[0] + (B[0] - A[0]) * t;
    const g = A[1] + (B[1] - A[1]) * t;
    const bl = A[2] + (B[2] - A[2]) * t;
    const al = A[3] + (B[3] - A[3]) * t;
    return `rgba(${r.toFixed(0)},${g.toFixed(0)},${bl.toFixed(0)},${al.toFixed(2)})`;
};
const draw = (canvas, data) => {
    const ctx = canvas.getContext("2d");
    if (!ctx)
        return [];
    const dpr = window.devicePixelRatio || 1;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, width, height);
    const bg = cssVar("--surface");
    const border = cssVar("--border");
    const text = cssVar("--text");
    const muted = cssVar("--muted");
    const accent = cssVar("--brand");
    const theme = document.documentElement.getAttribute("data-theme") || "dark";
    // Slightly stronger contrast in light theme so the heatmap doesn't disappear.
    const emptyCell = theme === "light" ? "rgba(17,24,39,0.16)" : "rgba(255,255,255,0.08)";
    ctx.fillStyle = bg || "rgba(255,255,255,0.06)";
    ctx.strokeStyle = border || "rgba(255,255,255,0.14)";
    roundRect(ctx, 0, 0, width, height, 16);
    ctx.fill();
    ctx.stroke();
    const padding = 16;
    const headerTop = 26;
    const subTop = 46;
    const gridTop = 66;
    const gridLeft = padding;
    const gridRight = width - padding;
    ctx.fillStyle = text || "#fff";
    ctx.font = "600 14px system-ui, -apple-system, Segoe UI, Roboto";
    ctx.fillText("성장하는 디지털 정원", padding, headerTop);
    ctx.fillStyle = muted || "rgba(255,255,255,.7)";
    ctx.font = "12px system-ui, -apple-system, Segoe UI, Roboto";
    ctx.fillText("최근 180일 기록(글/노트)", padding, subTop);
    const startDate = data.daily[0]?.date;
    const endDate = data.daily[data.daily.length - 1]?.date;
    if (startDate && endDate) {
        const rangeText = `${startDate} ~ ${endDate}`;
        const w = ctx.measureText(rangeText).width;
        ctx.fillText(rangeText, Math.max(padding, width - padding - w), subTop);
    }
    const cats = data.categories
        .map((c) => ({ ...c, total: c.post_count + c.note_count }))
        .sort((a, b) => b.total - a.total)
        .slice(0, 6);
    const label = "카테고리";
    ctx.font = "12px system-ui, -apple-system, Segoe UI, Roboto";
    const labelWidth = ctx.measureText(label).width;
    const labelGap = 26;
    // Keep bubble size consistent to avoid overlap with the grid above.
    const bubbleR = 8;
    const lineHeight = bubbleR * 2 + 10;
    const legendStartX = padding + Math.ceil(labelWidth) + labelGap;
    let lines = 1;
    let testX = legendStartX;
    cats.forEach((c) => {
        const r = bubbleR;
        const t = `${c.name} (${c.total})`;
        const w = r * 2 + 8 + ctx.measureText(t).width + 18;
        if (testX + w > width - padding) {
            lines += 1;
            testX = legendStartX;
        }
        testX += w;
    });
    const legendTop = height - padding - (lines - 1) * lineHeight;
    const gridBottom = legendTop - 24;
    const cols = 30;
    const rows = 6;
    const cellGap = 4;
    const cellSize = Math.min((gridRight - gridLeft - cellGap * (cols - 1)) / cols, (gridBottom - gridTop - cellGap * (rows - 1)) / rows);
    const max = Math.max(1, ...data.daily.map((d) => d.count));
    const startIndex = Math.max(0, data.daily.length - cols * rows);
    const slice = data.daily.slice(startIndex);
    const cells = [];
    for (let i = 0; i < cols * rows; i++) {
        const x = gridLeft + (i % cols) * (cellSize + cellGap);
        const y = gridTop + Math.floor(i / cols) * (cellSize + cellGap);
        const v = slice[i]?.count ?? 0;
        const t = v / max;
        ctx.fillStyle = mixColor(emptyCell, accent || "rgba(124,58,237,1)", Math.min(1, t * 1.1));
        roundRect(ctx, x, y, cellSize, cellSize, 5);
        ctx.fill();
        const date = slice[i]?.date;
        if (date)
            cells.push({ x, y, size: cellSize, date, count: v });
    }
    ctx.fillStyle = muted || "rgba(255,255,255,.7)";
    ctx.font = "12px system-ui, -apple-system, Segoe UI, Roboto";
    ctx.fillText(label, padding, legendTop);
    let lx = legendStartX;
    let ly = legendTop;
    cats.forEach((c) => {
        const r = bubbleR;
        ctx.fillStyle = "rgba(6,182,212,0.9)";
        ctx.beginPath();
        const labelText = `${c.name} (${c.total})`;
        const bubbleWidth = r * 2 + 8 + ctx.measureText(labelText).width + 18;
        if (lx + bubbleWidth > width - padding) {
            lx = legendStartX;
            ly += lineHeight;
        }
        ctx.arc(lx + r, ly - 4, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = text || "#fff";
        ctx.font = "12px system-ui, -apple-system, Segoe UI, Roboto";
        ctx.fillText(labelText, lx + r * 2 + 8, ly);
        lx += bubbleWidth;
    });
    return cells;
};
(() => {
    const canvas = document.querySelector("[data-garden]");
    if (!canvas)
        return;
    let lastData = null;
    let lastCells = [];
    const tip = document.createElement("div");
    tip.className = "garden-tooltip is-hidden";
    document.body.appendChild(tip);
    const hideTip = () => tip.classList.add("is-hidden");
    const showTip = () => tip.classList.remove("is-hidden");
    const load = async () => {
        const resp = await fetch("/api/garden/");
        if (!resp.ok)
            return;
        const data = (await resp.json());
        lastData = data;
        lastCells = draw(canvas, data);
    };
    const onResize = () => load();
    window.addEventListener("resize", onResize);
    const observer = new MutationObserver(() => {
        if (lastData)
            lastCells = draw(canvas, lastData);
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    canvas.addEventListener("mouseleave", hideTip);
    canvas.addEventListener("mousemove", (e) => {
        if (!lastCells.length)
            return hideTip();
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const hit = lastCells.find((c) => mx >= c.x && mx <= c.x + c.size && my >= c.y && my <= c.y + c.size);
        if (!hit)
            return hideTip();
        tip.textContent = `${hit.date} · ${hit.count}개`;
        showTip();
        const offset = 12;
        const pad = 8;
        let left = e.clientX + offset;
        let top = e.clientY + offset;
        const tw = tip.offsetWidth;
        const th = tip.offsetHeight;
        if (left + tw + pad > window.innerWidth)
            left = e.clientX - tw - offset;
        if (top + th + pad > window.innerHeight)
            top = e.clientY - th - offset;
        tip.style.left = `${Math.max(pad, left)}px`;
        tip.style.top = `${Math.max(pad, top)}px`;
    });
    load();
})();
