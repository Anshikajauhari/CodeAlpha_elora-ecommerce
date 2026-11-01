document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector("#main-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
      toggle.textContent = open ? "×" : "☰";
    });
    nav.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
      nav.classList.remove("open"); toggle.setAttribute("aria-expanded", "false"); toggle.textContent = "☰";
    }));
  }
  const checkoutForm = document.querySelector(".checkout-layout form");
  if (checkoutForm) checkoutForm.addEventListener("submit", () => {
    const button = checkoutForm.querySelector('button[type="submit"]');
    if (button && checkoutForm.reportValidity()) { button.disabled = true; button.textContent = "Placing order…"; }
  });
});



document.addEventListener("DOMContentLoaded", () => {
    const revealItems = document.querySelectorAll(
        ".product-card, .section-title, .hero-content, .hero-image"
    );

    if (!("IntersectionObserver" in window)) {
        revealItems.forEach(item => {
            item.classList.add("is-visible");
        });
        return;
    }

    const observer = new IntersectionObserver(
        (entries, currentObserver) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    currentObserver.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.12
        }
    );

    revealItems.forEach(item => {
        item.classList.add("reveal");
        observer.observe(item);
    });
});

