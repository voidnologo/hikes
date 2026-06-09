/* ==========================================================================
   Hike with Me — minimal dependency-free carousel
   --------------------------------------------------------------------------
   WHY this exists: keep the landing page photo carousel zero-dependency so it
   runs on GitHub Pages with no build step and nothing to keep updated.

   HOW TO ADD YOUR PHOTOS (no JS edits required):
     1. Drop image files into assets/img/  (e.g. assets/img/smokies-ridge.jpg)
     2. In index.html, inside <div class="carousel__track">, add one slide:
          <div class="carousel__slide">
            <img src="assets/img/smokies-ridge.jpg" alt="Sunrise on the ridge">
            <div class="carousel__caption">Sunrise on the AT, GSMNP</div>
          </div>
     3. Delete the placeholder slides. The arrows and dots wire up automatically.
   ========================================================================== */

(function initCarousels() {
  const carousels = document.querySelectorAll("[data-carousel]");
  carousels.forEach(setupCarousel);
})();

function setupCarousel(root) {
  const track = root.querySelector(".carousel__track");
  const slides = Array.from(root.querySelectorAll(".carousel__slide"));
  if (slides.length === 0) return;

  let index = 0;
  const dotsWrap = root.querySelector(".carousel__dots");
  const dots = buildDots(dotsWrap, slides.length, goTo);

  function render() {
    track.style.transform = `translateX(-${index * 100}%)`;
    dots.forEach((dot, i) => dot.setAttribute("aria-current", i === index ? "true" : "false"));
  }

  function goTo(i) {
    index = (i + slides.length) % slides.length; // wrap both directions
    render();
  }

  const next = () => goTo(index + 1);
  const prev = () => goTo(index - 1);

  root.querySelector(".carousel__btn--next")?.addEventListener("click", next);
  root.querySelector(".carousel__btn--prev")?.addEventListener("click", prev);

  // Keyboard support when the carousel is focused
  root.tabIndex = 0;
  root.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") next();
    if (e.key === "ArrowLeft") prev();
  });

  enableSwipe(root, next, prev);

  // Autoplay only when there is more than one slide and the user hasn't
  // asked to reduce motion; pause on hover so captions stay readable.
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (slides.length > 1 && !reduceMotion) {
    let timer = setInterval(next, 6000);
    root.addEventListener("mouseenter", () => clearInterval(timer));
    root.addEventListener("mouseleave", () => { timer = setInterval(next, 6000); });
  }

  render();
}

function buildDots(container, count, onClick) {
  if (!container) return [];
  const dots = [];
  for (let i = 0; i < count; i++) {
    const dot = document.createElement("button");
    dot.className = "carousel__dot";
    dot.setAttribute("aria-label", `Go to slide ${i + 1}`);
    dot.addEventListener("click", () => onClick(i));
    container.appendChild(dot);
    dots.push(dot);
  }
  return dots;
}

// Basic touch-swipe: a horizontal drag past the threshold flips one slide.
function enableSwipe(root, next, prev) {
  let startX = null;
  root.addEventListener("touchstart", (e) => { startX = e.touches[0].clientX; }, { passive: true });
  root.addEventListener("touchend", (e) => {
    if (startX === null) return;
    const dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) > 40) (dx < 0 ? next : prev)();
    startX = null;
  }, { passive: true });
}
