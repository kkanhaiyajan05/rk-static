/* ==========================================================================
   R K Packers & Movers — site interactions (vanilla, no dependencies)
   ========================================================================== */
(function () {
  "use strict";

  /* ---- Business config (single source of truth) ------------------------- */
  var CONFIG = {
    phone: "+917003827993",          // primary click-to-call
    whatsapp: "917003827993",        // wa.me number (no +)
    email: "rkpackers6613@gmail.com"
  };
  window.RK = CONFIG;

  var doc = document;
  var body = doc.body;

  /* ---- Mobile nav ------------------------------------------------------- */
  var toggle = doc.querySelector(".nav-toggle");
  var navClose = doc.querySelector(".nav-close");
  var backdrop = doc.querySelector(".nav-backdrop");

  function closeNav() { body.classList.remove("nav-open"); }
  if (toggle) toggle.addEventListener("click", function () { body.classList.toggle("nav-open"); });
  if (navClose) navClose.addEventListener("click", closeNav);
  if (backdrop) backdrop.addEventListener("click", closeNav);

  // Mobile dropdown expand
  doc.querySelectorAll(".nav .has-drop > a").forEach(function (a) {
    a.addEventListener("click", function (e) {
      if (window.matchMedia("(max-width: 992px)").matches) {
        e.preventDefault();
        a.parentElement.classList.toggle("open");
      }
    });
  });

  /* ---- Reveal on scroll ------------------------------------------------- */
  var reveals = doc.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && reveals.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { threshold: 0.12 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---- Animated counters ------------------------------------------------ */
  var counters = doc.querySelectorAll("[data-count]");
  if ("IntersectionObserver" in window && counters.length) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target, target = parseFloat(el.getAttribute("data-count"));
        var suffix = el.getAttribute("data-suffix") || "";
        var dur = 1400, start = null;
        function step(ts) {
          if (!start) start = ts;
          var p = Math.min((ts - start) / dur, 1);
          var val = Math.floor(p * target);
          el.textContent = val.toLocaleString("en-IN") + suffix;
          if (p < 1) requestAnimationFrame(step);
          else el.textContent = target.toLocaleString("en-IN") + suffix;
        }
        requestAnimationFrame(step);
        cio.unobserve(el);
      });
    }, { threshold: 0.4 });
    counters.forEach(function (el) { cio.observe(el); });
  }

  /* ---- FAQ / accordion -------------------------------------------------- */
  doc.querySelectorAll(".acc-q").forEach(function (q) {
    q.addEventListener("click", function () {
      var item = q.parentElement;
      var ans = item.querySelector(".acc-a");
      var isOpen = item.classList.contains("open");
      item.classList.toggle("open");
      ans.style.maxHeight = isOpen ? null : ans.scrollHeight + "px";
    });
  });

  /* ---- Gallery filter + lightbox --------------------------------------- */
  var tabs = doc.querySelectorAll(".gallery-tabs button");
  tabs.forEach(function (btn) {
    btn.addEventListener("click", function () {
      tabs.forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      var f = btn.getAttribute("data-filter");
      doc.querySelectorAll(".gallery-item").forEach(function (item) {
        var cat = item.getAttribute("data-cat");
        item.classList.toggle("hide", !(f === "all" || f === cat));
      });
    });
  });

  var lb = doc.querySelector(".lightbox");
  if (lb) {
    var lbBody = lb.querySelector(".lb-body");
    var lbClose = lb.querySelector(".lb-close");
    function openLb(html) { lbBody.innerHTML = html; lb.classList.add("open"); }
    function closeLb() { lb.classList.remove("open"); lbBody.innerHTML = ""; }
    doc.querySelectorAll(".gallery-item").forEach(function (item) {
      item.addEventListener("click", function () {
        var video = item.getAttribute("data-video");
        if (video) {
          openLb('<iframe src="https://www.youtube.com/embed/' + video + '?autoplay=1" title="Video" allow="autoplay; encrypted-media" allowfullscreen></iframe>');
        } else {
          var img = item.querySelector("img");
          openLb('<img src="' + (item.getAttribute("data-full") || img.src) + '" alt="' + (img.alt || "") + '">');
        }
      });
    });
    lbClose.addEventListener("click", closeLb);
    lb.addEventListener("click", function (e) { if (e.target === lb) closeLb(); });
    doc.addEventListener("keydown", function (e) { if (e.key === "Escape") closeLb(); });
  }

  /* ---- Enquiry forms -> WhatsApp / mailto ------------------------------- */
  // Any <form data-enquiry> is intercepted. data-enquiry="whatsapp" (default) or "email".
  doc.querySelectorAll("form[data-enquiry]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var mode = form.getAttribute("data-enquiry") || "whatsapp";
      var data = new FormData(form);
      var lines = ["*New Enquiry — R K Packers & Movers*", ""];
      var labels = {
        name: "Name", phone: "Phone", email: "Email", service: "Service",
        from: "Moving From", to: "Moving To", date: "Preferred Date", message: "Details"
      };
      data.forEach(function (val, key) {
        if (val && String(val).trim()) lines.push((labels[key] || key) + ": " + val);
      });
      var text = lines.join("\n");

      if (mode === "email") {
        var subject = "Enquiry from website — " + (data.get("name") || "Website");
        window.location.href = "mailto:" + CONFIG.email +
          "?subject=" + encodeURIComponent(subject) +
          "&body=" + encodeURIComponent(text);
      } else {
        window.open("https://wa.me/" + CONFIG.whatsapp + "?text=" + encodeURIComponent(text), "_blank");
      }
      var note = form.querySelector(".form-note");
      if (note) { note.textContent = "Opening " + (mode === "email" ? "your email app" : "WhatsApp") + "… If nothing happens, call us at " + CONFIG.phone + "."; note.style.display = "block"; }
      form.reset();
    });
  });

  /* ---- WhatsApp forms with validation (quote + physical survey) --------- */
  function initWaForm(form, compile) {
    if (!form) return;
    var v = function (name) { var el = form.querySelector("[name='" + name + "']"); return el ? el.value.trim() : ""; };
    var radio = function (name) { var el = form.querySelector("[name='" + name + "']:checked"); return el ? el.value : ""; };

    var validate = function () {
      var first = null;
      var mark = function (el, msg) {
        var f = el.closest(".field");
        if (f) { f.classList.add("invalid"); var em = f.querySelector(".err-msg"); if (em && msg) em.textContent = msg; }
        if (!first) first = el;
      };
      form.querySelectorAll(".field.invalid").forEach(function (f) { f.classList.remove("invalid"); });
      form.querySelectorAll("input[required], select[required], textarea[required]").forEach(function (el) {
        if (!el.value.trim()) mark(el, "This field is required.");
      });
      var mob = form.querySelector("[name='mobile']");
      if (mob && mob.value.trim() && !/^(\+?91[\-\s]?)?[6-9]\d{9}$/.test(mob.value.replace(/[\s\-]/g, ""))) {
        mark(mob, "Enter a valid 10-digit mobile number.");
      }
      var em = form.querySelector("[name='email']");
      if (em && em.value.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em.value.trim())) {
        mark(em, "Enter a valid email address.");
      }
      if (first) {
        first.focus({ preventScroll: true });
        first.scrollIntoView({ behavior: "smooth", block: "center" });
        return false;
      }
      return true;
    };

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validate()) return;
      var text = compile(v, radio, form);
      window.open("https://wa.me/" + CONFIG.whatsapp + "?text=" + encodeURIComponent(text), "_blank");
      var note = form.querySelector(".form-note");
      if (note) {
        note.textContent = "Opening WhatsApp with your request… If it doesn't open, please call us at " + CONFIG.phone + ".";
        note.style.display = "block";
      }
    });

    var clear = function (e) { var f = e.target.closest && e.target.closest(".field.invalid"); if (f) f.classList.remove("invalid"); };
    form.addEventListener("input", clear);
    form.addEventListener("change", clear);
  }

  // Online quote form
  initWaForm(doc.getElementById("quoteForm"), function (v, radio, form) {
    var items = [];
    form.querySelectorAll("[data-item]").forEach(function (el) {
      var q = parseInt(el.value, 10);
      if (q && q > 0) items.push(el.getAttribute("data-item") + ": " + q);
    });
    var addons = [];
    form.querySelectorAll("input[name='addons']:checked").forEach(function (el) { addons.push(el.value); });

    var L = ["*New Moving Quote Request*", "_via rkmoverspackers.com_", ""];
    L.push("*Contact Details*");
    L.push("Name: " + v("name"));
    L.push("Mobile: " + v("mobile"));
    if (v("email")) L.push("Email: " + v("email"));
    L.push("");
    L.push("*Service:* " + v("service"));
    if (v("housesize")) L.push("*Home Size:* " + v("housesize"));
    L.push("");
    L.push("*Moving From*");
    L.push("City: " + v("fromcity"));
    if (v("fromarea")) L.push("Area: " + v("fromarea"));
    if (v("fromfloor") || radio("fromlift"))
      L.push("Floor: " + (v("fromfloor") || "-") + (radio("fromlift") ? "  (Lift: " + radio("fromlift") + ")" : ""));
    L.push("");
    L.push("*Moving To*");
    L.push("City: " + v("tocity"));
    if (v("toarea")) L.push("Area: " + v("toarea"));
    if (v("tofloor") || radio("tolift"))
      L.push("Floor: " + (v("tofloor") || "-") + (radio("tolift") ? "  (Lift: " + radio("tolift") + ")" : ""));
    L.push("");
    L.push("*Tentative Moving Date:* " + v("movedate"));
    if (items.length) { L.push(""); L.push("*Items to Shift*"); L.push(items.join(", ")); }
    if (addons.length) { L.push(""); L.push("*Add-on Services:* " + addons.join(", ")); }
    if (v("remarks")) { L.push(""); L.push("*Remarks:* " + v("remarks")); }
    return L.join("\n");
  });

  // Physical survey booking form
  initWaForm(doc.getElementById("surveyForm"), function (v) {
    var L = ["*Physical Survey Request*", "_via rkmoverspackers.com_", ""];
    L.push("*Contact Details*");
    L.push("Name: " + v("name"));
    L.push("WhatsApp/Mobile: " + v("mobile"));
    if (v("email")) L.push("Email: " + v("email"));
    L.push("");
    L.push("*Service:* " + v("service"));
    L.push("");
    L.push("*Survey Address:* " + v("address"));
    if (v("city")) L.push("*City / Area:* " + v("city"));
    L.push("");
    L.push("*Preferred Survey Date:* " + v("surveydate"));
    L.push("*Preferred Time Slot:* " + v("surveytime"));
    if (v("remarks")) { L.push(""); L.push("*Remarks:* " + v("remarks")); }
    return L.join("\n");
  });

  /* ---- Back to top ------------------------------------------------------ */
  var toTop = doc.querySelector(".to-top");
  if (toTop) {
    window.addEventListener("scroll", function () {
      toTop.classList.toggle("show", window.scrollY > 500);
    }, { passive: true });
    toTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
  }

  /* ---- Footer year ------------------------------------------------------ */
  var yr = doc.querySelector("[data-year]");
  if (yr) yr.textContent = new Date().getFullYear();
})();
