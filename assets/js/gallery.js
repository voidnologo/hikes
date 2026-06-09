/* ==========================================================================
   Hike with Me — gallery grid + lightbox
   Reads the photo list from assets/img/photos/manifest.json so you never have
   to hand-edit this page: re-run the converter and the grid updates itself.
   (Fetch needs http — use `python3 -m http.server` for local preview, not file://.)
   ========================================================================== */

(async function initGallery() {
  const grid = document.getElementById("gallery");
  if (!grid) return;

  const base = "assets/img/photos";
  let files = [];
  try {
    const res = await fetch(`${base}/manifest.json`);
    files = await res.json();
  } catch (e) {
    grid.innerHTML = "<p>Couldn't load photos. (If viewing locally, serve over http rather than opening the file directly.)</p>";
    return;
  }

  files.forEach((name, i) => {
    const a = document.createElement("a");
    a.href = `${base}/${name}`;
    a.dataset.index = String(i);
    const img = document.createElement("img");
    img.src = `${base}/thumbs/${name}`;
    img.alt = "";
    img.loading = "lazy";
    a.appendChild(img);
    grid.appendChild(a);
  });

  setupLightbox(grid, files, base);
})();

function setupLightbox(grid, files, base) {
  const box = document.createElement("div");
  box.className = "lightbox";
  box.innerHTML = `
    <button class="lightbox__close" aria-label="Close">&times;</button>
    <button class="lightbox__nav lightbox__nav--prev" aria-label="Previous">&#8249;</button>
    <img alt="">
    <button class="lightbox__nav lightbox__nav--next" aria-label="Next">&#8250;</button>`;
  document.body.appendChild(box);

  const imgEl = box.querySelector("img");
  let current = 0;

  const show = (i) => {
    current = (i + files.length) % files.length;
    imgEl.src = `${base}/${files[current]}`;
  };
  const open = (i) => { show(i); box.classList.add("open"); };
  const close = () => box.classList.remove("open");

  grid.addEventListener("click", (e) => {
    const link = e.target.closest("a");
    if (!link) return;
    e.preventDefault();
    open(Number(link.dataset.index));
  });

  box.querySelector(".lightbox__close").addEventListener("click", close);
  box.querySelector(".lightbox__nav--next").addEventListener("click", () => show(current + 1));
  box.querySelector(".lightbox__nav--prev").addEventListener("click", () => show(current - 1));
  box.addEventListener("click", (e) => { if (e.target === box) close(); });
  document.addEventListener("keydown", (e) => {
    if (!box.classList.contains("open")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowRight") show(current + 1);
    if (e.key === "ArrowLeft") show(current - 1);
  });
}
