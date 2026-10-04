(() => {
  const nav = document.querySelector(".main-nav");
  const menuToggle = document.querySelector(".menu-toggle");
  const currentPath = location.pathname;
  const navPath = currentPath.startsWith("/projects/")
    ? "/projects/"
    : currentPath.startsWith("/blog/")
      ? "/blog/"
      : currentPath;

  nav?.querySelectorAll("a").forEach((link) => {
    if (new URL(link.href).pathname === navPath)
      link.setAttribute("aria-current", "page");
    link.addEventListener("click", () => closeMenu());
  });

  function closeMenu() {
    nav?.classList.remove("is-open");
    menuToggle?.setAttribute("aria-expanded", "false");
    menuToggle?.setAttribute("aria-label", "باز کردن فهرست");
  }

  menuToggle?.addEventListener("click", (event) => {
    event.stopPropagation();
    const open = nav.classList.toggle("is-open");
    menuToggle.setAttribute("aria-expanded", String(open));
    menuToggle.setAttribute(
      "aria-label",
      open ? "بستن فهرست" : "باز کردن فهرست",
    );
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
  });
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".site-header")) closeMenu();
  });

  const heroSlides = [...document.querySelectorAll(".hero-media .hero-slide")];
  const heroSlideControls = document.querySelector(".hero-slide-controls");
  if (heroSlides.length > 1 && heroSlideControls) {
    let activeSlide = 0;
    let slideTimer;

    function stopSlideshow() {
      window.clearInterval(slideTimer);
      slideTimer = undefined;
    }

    function showSlide(nextSlide) {
      const nextImage = heroSlides[nextSlide].querySelector("img");
      if (!nextImage?.complete || !nextImage.naturalWidth)
        return;
      heroSlides[activeSlide].classList.remove("is-active");
      heroSlides[activeSlide].setAttribute("aria-hidden", "true");
      heroSlides[nextSlide].classList.add("is-active");
      heroSlides[nextSlide].setAttribute("aria-hidden", "false");
      activeSlide = nextSlide;
    }

    function startSlideshow() {
      stopSlideshow();
      if (document.hidden) return;
      slideTimer = window.setInterval(
        () => showSlide((activeSlide + 1) % heroSlides.length),
        5000,
      );
    }

    heroSlideControls.hidden = false;
    heroSlideControls.querySelectorAll("[data-hero-slide]").forEach((button) => {
      button.addEventListener("click", () => {
        const step = button.dataset.heroSlide === "next" ? 1 : -1;
        showSlide((activeSlide + step + heroSlides.length) % heroSlides.length);
        startSlideshow();
      });
    });
    startSlideshow();
    document.addEventListener("visibilitychange", startSlideshow);
  }

  const projectCarousel = document.querySelector(".project-carousel");
  if (projectCarousel) {
    const slides = [...projectCarousel.querySelectorAll(".project-slide")];
    const marks = [...projectCarousel.querySelectorAll(".project-carousel-mark")];
    const controls = projectCarousel.querySelector(".project-carousel-controls");
    const status = projectCarousel.querySelector(".project-carousel-status");
    const openButton = projectCarousel.querySelector(".project-carousel-open");
    const lightbox = document.querySelector(".project-single .project-lightbox");
    let activeSlide = 0;

    function showProjectSlide(nextSlide) {
      activeSlide = (nextSlide + slides.length) % slides.length;
      slides.forEach((slide, index) => {
        const active = index === activeSlide;
        slide.classList.toggle("is-active", active);
        slide.setAttribute("aria-hidden", String(!active));
        marks[index]?.classList.toggle("is-active", active);
      });
      status.textContent = `تصویر ${(activeSlide + 1).toLocaleString("fa-IR")} از ${slides.length.toLocaleString("fa-IR")}`;
      openButton?.setAttribute("aria-label", `نمایش ${slides[activeSlide].alt} در گالری`);
    }

    if (slides.length > 1 && controls) {
      controls.hidden = false;
      controls.querySelectorAll("[data-project-slide]").forEach((button) => {
        button.addEventListener("click", () => {
          const step = button.dataset.projectSlide === "next" ? 1 : -1;
          showProjectSlide(activeSlide + step);
        });
      });
    }

    if (lightbox && openButton && slides.length) {
      const image = lightbox.querySelector(".project-lightbox-image");
      const lightboxStatus = lightbox.querySelector(".project-lightbox-status");
      const closeButton = lightbox.querySelector(".project-lightbox-close");

      function showLightboxSlide(nextSlide) {
        showProjectSlide(nextSlide);
        image.src = slides[activeSlide].getAttribute("src");
        image.alt = slides[activeSlide].alt;
        lightboxStatus.textContent = status.textContent;
      }

      openButton.addEventListener("click", () => {
        showLightboxSlide(activeSlide);
        lightbox.showModal();
        closeButton.focus();
      });

      lightbox.querySelectorAll("[data-lightbox-step]").forEach((button) => {
        button.addEventListener("click", () => {
          showLightboxSlide(activeSlide + Number(button.dataset.lightboxStep));
        });
      });

      closeButton.addEventListener("click", () => lightbox.close());
      lightbox.addEventListener("click", (event) => {
        if (event.target === lightbox) lightbox.close();
      });
      lightbox.addEventListener("keydown", (event) => {
        if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
          event.preventDefault();
          showLightboxSlide(activeSlide + (event.key === "ArrowLeft" ? 1 : -1));
        }
      });
      lightbox.addEventListener("close", () => {
        openButton.focus({ preventScroll: true });
      });
    }
  }

  const teamGrid = document.querySelector(".team-grid");
  const teamControls = document.querySelector(".team-controls");
  if (teamGrid && teamControls && teamGrid.children.length > 1) {
    const status = document.querySelector(".team-carousel-status");
    const cards = Array.from(teamGrid.children);
    const cardCount = cards.length;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const pendingShifts = [];
    let currentIndex = cardCount;
    let animating = false;
    let transitionTimer;

    function cloneCard(card) {
      const clone = card.cloneNode(true);
      clone.setAttribute("aria-hidden", "true");
      clone.setAttribute("inert", "");
      return clone;
    }

    teamGrid.prepend(...cards.map(cloneCard));
    teamGrid.append(...cards.map(cloneCard));

    function positionTrack() {
      const cardWidth = teamGrid.firstElementChild.getBoundingClientRect().width;
      const gap = parseFloat(getComputedStyle(teamGrid).gap) || 0;
      teamGrid.style.transform = `translateX(${currentIndex * (cardWidth + gap)}px)`;
    }

    function positionWithoutAnimation() {
      teamGrid.style.transition = "none";
      positionTrack();
      teamGrid.getBoundingClientRect();
      teamGrid.style.transition = "";
    }

    function finishShift() {
      if (!animating) return;
      clearTimeout(transitionTimer);
      if (currentIndex === 0 || currentIndex === cardCount * 2) {
        currentIndex = cardCount;
        positionWithoutAnimation();
      }
      animating = false;
      shiftNext();
    }

    function shiftNext() {
      if (animating || !pendingShifts.length) return;
      currentIndex += pendingShifts.shift();
      animating = true;
      positionTrack();
      if (reducedMotion.matches) finishShift();
      else transitionTimer = setTimeout(finishShift, 500);
    }

    positionWithoutAnimation();

    teamGrid.addEventListener("transitionend", (event) => {
      if (event.target === teamGrid && event.propertyName === "transform") {
        finishShift();
      }
    });

    window.addEventListener("resize", () => {
      clearTimeout(transitionTimer);
      animating = false;
      positionWithoutAnimation();
      shiftNext();
    });

    teamControls.querySelectorAll("[data-team-shift]").forEach((button) => {
      button.addEventListener("click", () => {
        const movingRight = button.dataset.teamShift === "right";
        pendingShifts.push(movingRight ? -1 : 1);
        shiftNext();
        if (status) {
          status.textContent = movingRight
            ? "اعضا یک جایگاه به راست جابه‌جا شدند."
            : "اعضا یک جایگاه به چپ جابه‌جا شدند.";
        }
      });
    });
  }

  const blogSort = document.querySelector(".blog-sort");
  const blogGrid = document.querySelector(".blog-archive .archive-grid");
  const blogCategory = document.querySelector(".blog-category-filter");
  if (blogCategory && blogGrid) {
    const trigger = blogCategory.querySelector(".blog-category-trigger");
    const options = blogCategory.querySelector(".blog-category-options");
    const label = blogCategory.querySelector(".blog-category-label");

    function closeBlogCategory() {
      options.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
    }

    trigger.addEventListener("click", () => {
      options.hidden = !options.hidden;
      trigger.setAttribute("aria-expanded", String(!options.hidden));
    });

    options.querySelectorAll("[data-blog-category]").forEach((option) => {
      option.addEventListener("click", (event) => {
        blogGrid.dataset.activeCategory = option.dataset.blogCategory;
        blogGrid.dispatchEvent(new Event("archive:reorder"));
        options.querySelectorAll("[data-blog-category]").forEach((item) => {
          item.setAttribute("aria-pressed", String(item === option));
        });
        label.textContent = option.textContent;
        closeBlogCategory();
        if (event.detail === 0) trigger.focus();
        else option.blur();
      });
    });

    document.addEventListener("click", (event) => {
      if (!blogCategory.contains(event.target)) closeBlogCategory();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !options.hidden) {
        closeBlogCategory();
        trigger.focus();
      }
    });
  }
  if (blogSort && blogGrid) {
    const trigger = blogSort.querySelector(".blog-sort-trigger");
    const options = blogSort.querySelector(".blog-sort-options");
    const label = blogSort.querySelector(".blog-sort-label");

    function closeBlogSort() {
      options.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
    }

    trigger.addEventListener("click", () => {
      options.hidden = !options.hidden;
      trigger.setAttribute("aria-expanded", String(!options.hidden));
    });

    options.querySelectorAll("[data-blog-sort]").forEach((option) => {
      option.addEventListener("click", () => {
        const newestFirst = option.dataset.blogSort === "newest";
        const cards = [...blogGrid.querySelectorAll(".archive-card")];
        cards.sort((a, b) =>
          newestFirst
            ? b.dataset.date.localeCompare(a.dataset.date)
            : a.dataset.date.localeCompare(b.dataset.date),
        );
        blogGrid.replaceChildren(...cards);
        blogGrid.dispatchEvent(new Event("archive:reorder"));
        options.querySelectorAll("[data-blog-sort]").forEach((item) => {
          item.setAttribute("aria-pressed", String(item === option));
        });
        label.textContent = option.textContent;
        trigger.focus();
        closeBlogSort();
      });
    });

    document.addEventListener("click", (event) => {
      if (!blogSort.contains(event.target)) closeBlogSort();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !options.hidden) {
        closeBlogSort();
        trigger.focus();
      }
    });
  }

  document.querySelectorAll("[data-paginated-grid]").forEach((grid) => {
    const pagination = grid.parentElement.querySelector(".pagination");
    const pageSize = Number(grid.dataset.pageSize) || grid.children.length;
    let currentPage = 1;

    function render() {
      const allCards = [...grid.querySelectorAll(".archive-card")];
      const activeCategory = grid.dataset.activeCategory;
      const cards = activeCategory && activeCategory !== "all"
        ? allCards.filter((card) => card.dataset.category === activeCategory)
        : allCards;
      const pageCount = Math.max(1, Math.ceil(cards.length / pageSize));
      currentPage = Math.min(currentPage, pageCount);
      allCards.forEach((card) => {
        card.hidden = true;
      });
      cards
        .slice((currentPage - 1) * pageSize, currentPage * pageSize)
        .forEach((card) => {
          card.hidden = false;
        });
      pagination.replaceChildren();
      if (pageCount <= 1) return;
      for (let page = 1; page <= pageCount; page += 1) {
        const button = document.createElement("button");
        button.className = "page-button";
        button.type = "button";
        button.textContent = page.toLocaleString("fa-IR");
        button.setAttribute(
          "aria-label",
          `صفحهٔ ${page.toLocaleString("fa-IR")}`,
        );
        if (page === currentPage) button.setAttribute("aria-current", "page");
        button.addEventListener("click", () => {
          currentPage = page;
          render();
          grid.scrollIntoView({ behavior: "smooth", block: "start" });
        });
        pagination.append(button);
      }
    }

    grid.addEventListener("archive:reorder", () => {
      currentPage = 1;
      render();
    });
    render();
  });

  const contactForm = document.querySelector(".cta-form");
  const contactSubjectPicker = contactForm?.querySelector(".contact-subject-picker");
  const contactSubjectTrigger = contactSubjectPicker?.querySelector(".contact-subject-trigger");
  if (contactSubjectPicker) {
    const trigger = contactSubjectTrigger;
    const options = contactSubjectPicker.querySelector(".contact-subject-options");
    const label = contactSubjectPicker.querySelector(".contact-subject-label");
    const subject = contactForm.elements.subject;

    function closeContactSubject() {
      options.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
    }

    trigger.addEventListener("click", () => {
      options.hidden = !options.hidden;
      trigger.setAttribute("aria-expanded", String(!options.hidden));
    });

    options.querySelectorAll("[data-contact-subject]").forEach((option) => {
      option.addEventListener("click", (event) => {
        subject.value = option.dataset.contactSubject;
        label.textContent = option.textContent;
        options.querySelectorAll("[data-contact-subject]").forEach((item) => {
          item.setAttribute("aria-pressed", String(item === option));
        });
        trigger.removeAttribute("aria-invalid");
        const message = contactForm.querySelector(".form-message");
        message.classList.remove("is-error");
        message.hidden = true;
        closeContactSubject();
        if (event.detail === 0) trigger.focus();
        else option.blur();
      });
    });

    document.addEventListener("click", (event) => {
      if (!contactSubjectPicker.contains(event.target)) closeContactSubject();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !options.hidden) {
        closeContactSubject();
        trigger.focus();
      }
    });
    contactForm.addEventListener("reset", () => {
      queueMicrotask(() => {
        subject.value = "";
      });
      label.textContent = "انتخاب کنید";
      trigger.removeAttribute("aria-invalid");
      options.querySelectorAll("[data-contact-subject]").forEach((item) => {
        item.setAttribute("aria-pressed", String(!item.dataset.contactSubject));
      });
      closeContactSubject();
    });
  }
  contactForm?.elements.phone.addEventListener("input", () => {
    contactForm.elements.phone.setCustomValidity("");
  });
  contactForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const phone = contactForm.elements.phone;
    const digits = phone.value
      .replace(/[۰-۹]/g, (digit) => String("۰۱۲۳۴۵۶۷۸۹".indexOf(digit)))
      .replace(/[٠-٩]/g, (digit) => String("٠١٢٣٤٥٦٧٨٩".indexOf(digit)))
      .replace(/\D/g, "");
    phone.setCustomValidity(
      digits.length < 10 || digits.length > 15 ? "شماره تماس معتبر وارد کنید." : "",
    );
    const message = contactForm.querySelector(".form-message");
    message.classList.remove("is-error");
    message.hidden = true;
    if (!contactForm.reportValidity()) return;
    if (!contactForm.elements.subject.value) {
      message.textContent = "موضوع پروژه / نیاز را انتخاب کنید.";
      message.classList.add("is-error");
      message.hidden = false;
      contactSubjectTrigger?.setAttribute("aria-invalid", "true");
      contactSubjectTrigger?.focus();
      return;
    }
    const submitButton = contactForm.querySelector('[type="submit"]');
    submitButton.disabled = true;
    try {
      const response = await fetch(contactForm.action, {
        method: "POST",
        body: new FormData(contactForm),
        headers: {
          "Accept": "application/json",
          "X-CSRFToken": contactForm.querySelector('[name="csrfmiddlewaretoken"]').value,
        },
        credentials: "same-origin",
      });
      const result = await response.json();
      if (!response.ok || !result.ok) {
        const firstError = Object.values(result.errors || {})[0]?.[0];
        throw new Error(firstError || result.message || "ثبت درخواست انجام نشد.");
      }
      message.textContent = result.message;
      contactForm.reset();
    } catch (error) {
      message.textContent = error.message || "ارتباط برقرار نشد. دوباره تلاش کنید.";
      message.classList.add("is-error");
    } finally {
      message.hidden = false;
      submitButton.disabled = false;
    }
  });
})();
