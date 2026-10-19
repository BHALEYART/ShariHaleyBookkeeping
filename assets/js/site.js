/* Shari Haley Bookkeeping — progressive enhancement only.
   Every page works without this file; it adds the mobile menu,
   the click-to-load video, and accessible form validation/submission. */
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");

  /* ---------- Mobile navigation ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
    };
    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });
  }

  /* ---------- YouTube facade (loads the player only on request) ---------- */
  document.querySelectorAll(".video-facade[data-video]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var iframe = document.createElement("iframe");
      iframe.className = "video-frame";
      iframe.src = "https://www.youtube-nocookie.com/embed/" + btn.dataset.video + "?autoplay=1&rel=0";
      iframe.title = btn.dataset.title || "Video";
      iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
      iframe.allowFullscreen = true;
      btn.replaceWith(iframe);
      iframe.focus();
    });
  });

  /* ---------- Thank-you page: booked-meeting note ---------- */
  var bookedNote = document.getElementById("booked-note");
  if (bookedNote && /[?&]meeting=booked\b/.test(location.search)) bookedNote.hidden = false;

  /* ---------- Intake form ---------- */
  var form = document.getElementById("intake-form");
  if (!form) return;

  form.noValidate = true; // we take over validation so errors are announced consistently
  var summary = document.getElementById("error-summary");
  var status = document.getElementById("form-status");
  var submitBtn = form.querySelector('[type="submit"]');
  var subject = form.querySelector('input[name="_subject"]');
  var subjectBase = subject ? subject.value : "";

  /* Simple / Advanced: questions for the other mode are hidden AND disabled,
     so they're skipped by validation and left out of the submission. */
  function applyMode(mode, announce) {
    form.querySelectorAll("[data-mode]").forEach(function (el) {
      var on = el.dataset.mode === mode;
      el.hidden = !on;
      if (el.tagName === "FIELDSET") el.disabled = !on;
      el.querySelectorAll("fieldset").forEach(function (f) { f.disabled = !on; });
    });
    var n = 0;
    form.querySelectorAll(".step-legend .num").forEach(function (num) {
      if (!num.closest("[hidden]")) num.textContent = ++n;
    });
    if (subject) subject.value = subjectBase + " (" + mode + " form)";
    summary.hidden = true;
    if (announce) {
      document.getElementById("mode-status").textContent = mode === "Simple"
        ? "Simple form selected. Showing basic questions only."
        : "Advanced form selected. Showing all questions.";
    }
  }
  var modeRadios = form.querySelectorAll('input[name="form_type"]');
  modeRadios.forEach(function (r) {
    r.addEventListener("change", function () { if (r.checked) applyMode(r.value, true); });
  });
  if (modeRadios.length) {
    document.getElementById("form_type-simple").checked = true; // Simple is the default
    applyMode("Simple", false);
  }

  function errorEl(id) { return document.getElementById(id + "-error"); }

  function labelText(el) {
    var group = el.closest("fieldset[data-group]");
    if (group) return group.querySelector("legend").textContent.replace("*", "").replace(/\s*\(required\)\s*/i, "").trim();
    var label = form.querySelector('label[for="' + el.id + '"]');
    return label ? label.childNodes[0].textContent.replace("*", "").trim() : el.name;
  }

  function validateField(el) {
    var msg = "";
    var v = (el.value || "").trim();
    if (el.required && !v) {
      msg = el.tagName === "SELECT" ? "Please choose an option." : "This field is required.";
    } else if (v && el.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) {
      msg = "Enter an email address like name@example.com.";
    } else if (v && el.type === "tel" && v.replace(/\D/g, "").length < 10) {
      msg = "Enter a 10-digit phone number, including area code.";
    }
    setError(el, el.id, msg);
    return msg;
  }

  function validateGroup(fs) {
    var checked = fs.querySelector("input:checked");
    var msg = checked ? "" : (fs.dataset.groupMsg || "Please choose at least one option.");
    fs.classList.toggle("fieldset-invalid", !!msg);
    var first = fs.querySelector("input");
    fs.querySelectorAll("input").forEach(function (i) { i.setAttribute("aria-invalid", msg ? "true" : "false"); });
    writeError(errorEl(fs.dataset.group), msg);
    return msg ? { el: first, msg: msg, name: labelText(first) } : null;
  }

  function validateConsent(el) {
    var msg = el.checked ? "" : "Please check this box so we can contact you.";
    setError(el, el.id, msg);
    return msg;
  }

  // When an error clears, keep its line height so the form doesn't jump
  // under the pointer while someone is moving to the next question.
  function writeError(err, msg) {
    if (!err) return;
    err.textContent = msg || (err.textContent ? "\u00a0" : "");
  }

  function setError(el, id, msg) {
    el.setAttribute("aria-invalid", msg ? "true" : "false");
    writeError(errorEl(id), msg);
  }

  // Re-validate as people fix things, but don't nag while they first type.
  form.addEventListener("change", function (e) {
    var t = e.target;
    if (t.name === "form_type") return;
    var fs = t.closest("fieldset[data-group]");
    if (fs && fs.classList.contains("fieldset-invalid")) validateGroup(fs);
    else if (t.type === "checkbox" && t.required) validateConsent(t);
    else if (t.getAttribute("aria-invalid") === "true") validateField(t);
  });
  form.addEventListener("blur", function (e) {
    var t = e.target;
    if (t.matches("input[type=text], input[type=email], input[type=tel], select, textarea") && t.getAttribute("aria-invalid") === "true") validateField(t);
  }, true);

  function runValidation() {
    var problems = [];
    form.querySelectorAll("input[type=text][required], input[type=email], input[type=tel], select[required], textarea[required]").forEach(function (el) {
      if (el.closest(".hp") || el.matches(":disabled")) return;
      var m = validateField(el);
      if (m) problems.push({ el: el, msg: m, name: labelText(el) });
    });
    form.querySelectorAll("fieldset[data-group][data-required]").forEach(function (fs) {
      if (fs.matches(":disabled")) return;
      var p = validateGroup(fs);
      if (p) problems.push(p);
    });
    var consent = document.getElementById("consent");
    if (consent && validateConsent(consent)) problems.push({ el: consent, msg: "Please check the box to agree to be contacted.", name: "Permission to contact you" });

    // keep summary in document order
    problems.sort(function (a, b) {
      return a.el.compareDocumentPosition(b.el) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
    });
    return problems;
  }

  function showSummary(problems) {
    var list = summary.querySelector("ul");
    list.innerHTML = "";
    problems.forEach(function (p) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = "#" + p.el.id;
      a.textContent = p.name + ": " + p.msg;
      a.addEventListener("click", function (e) { e.preventDefault(); p.el.focus(); p.el.scrollIntoView({ block: "center" }); });
      li.appendChild(a);
      list.appendChild(li);
    });
    summary.querySelector("h2").textContent =
      problems.length === 1 ? "There is 1 problem with your form" : "There are " + problems.length + " problems with your form";
    summary.hidden = false;
    summary.focus();
  }

  var DEFAULT_LABEL = submitBtn.textContent;
  var steps = document.getElementById("form-steps");
  var scheduler = document.getElementById("scheduler");
  var schedFrame = document.getElementById("scheduler-frame");
  var schedStatus = document.getElementById("scheduler-status");
  var bookBox = document.getElementById("book_meeting");
  var CALENDLY = form.dataset.calendly;
  var CALENDLY_ORIGIN = "https://calendly.com";
  var sending = false;

  function wantsMeeting() { return !!(bookBox && bookBox.checked && CALENDLY && scheduler); }
  function idleLabel() { return wantsMeeting() ? "Continue to pick a time" : DEFAULT_LABEL; }
  if (bookBox) bookBox.addEventListener("change", function () { submitBtn.textContent = idleLabel(); });

  function collect(extra) {
    // Combine multi-select checkbox groups into one readable line per question.
    var data = {};
    new FormData(form).forEach(function (value, key) {
      var k = key.replace(/\[\]$/, "");
      data[k] = data[k] ? data[k] + ", " + value : value;
    });
    Object.keys(extra || {}).forEach(function (k) { data[k] = extra[k]; });
    return data;
  }

  function send(extra, opts) {
    opts = opts || {};
    var data = collect(extra);
    if (data._honey || sending) return; // honeypot tripped, or already sending
    sending = true;
    var out = opts.statusEl || status;
    submitBtn.disabled = true;
    submitBtn.textContent = "Sending…";
    out.className = "form-status";
    out.textContent = opts.sendingText || "Sending your request…";

    // FormSubmit's AJAX endpoint returns JSON instead of redirecting.
    fetch(form.action.replace("formsubmit.co/", "formsubmit.co/ajax/"), {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(data)
    })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, body: j }; }); })
      .then(function (res) {
        // FormSubmit sends success as the string "true"/"false".
        if (res.ok && String(res.body.success) !== "false") {
          var thanks = form.dataset.thanks || "/thank-you/";
          window.location.href = thanks + (opts.booked ? "?meeting=booked" : "");
        } else {
          throw new Error(res.body && res.body.message);
        }
      })
      .catch(function (err) {
        sending = false;
        var reason = (err && err.message) || "";
        out.className = "form-status is-error";
        if (/activat/i.test(reason)) {
          // First submission to a new FormSubmit address: it emails an activation link.
          out.textContent = "This form isn't activated yet. An activation email has been sent to the business inbox. Once its “Activate Form” link is clicked, please try again, or call 386-320-9378.";
        } else {
          out.textContent = opts.failText ||
            ("Sorry, your request didn't go through" + (reason && !/fetch|network|load failed/i.test(reason) ? " (" + reason + ")" : "") + ". Please try again, or call 386-320-9378.");
        }
        submitBtn.disabled = false;
        submitBtn.textContent = idleLabel();
      });
  }

  /* ---------- Calendly step ----------
     The scheduler is Shari's own Calendly page in an iframe, prefilled with the
     visitor's name and email. Calendly creates the appointment when they confirm;
     it then posts "calendly.event_scheduled" to this page, which sends the form
     with the booking attached. Nothing loads from Calendly unless they opt in. */
  function calendlySrc() {
    var q = [
      "embed_domain=" + encodeURIComponent(location.host || "localhost"),
      "embed_type=Inline",
      "hide_gdpr_banner=1",
      "name=" + encodeURIComponent(form.elements.name.value.trim()),
      "email=" + encodeURIComponent(form.elements.email.value.trim())
    ];
    return CALENDLY + (CALENDLY.indexOf("?") > -1 ? "&" : "?") + q.join("&");
  }

  function openScheduler() {
    var src = calendlySrc();
    var iframe = schedFrame.querySelector("iframe");
    if (!iframe || iframe.dataset.src !== src) {
      schedFrame.innerHTML = "";
      iframe = document.createElement("iframe");
      iframe.title = "Shari Haley’s Calendly scheduler: choose a meeting time";
      iframe.src = src;
      iframe.dataset.src = src;
      iframe.allow = "payment";
      iframe.addEventListener("load", function () {
        if (schedStatus.textContent.indexOf("Loading") === 0) schedStatus.textContent = "";
      });
      schedFrame.appendChild(iframe);
      schedStatus.className = "form-status";
      schedStatus.textContent = "Loading Shari’s calendar…";
    }
    steps.hidden = true;
    scheduler.hidden = false;
    var title = document.getElementById("scheduler-title");
    title.focus();
    title.scrollIntoView({ block: "start" });
  }

  function closeScheduler() {
    scheduler.hidden = true;
    steps.hidden = false;
    if (bookBox) { bookBox.focus(); bookBox.scrollIntoView({ block: "center" }); }
  }

  if (scheduler) {
    document.getElementById("scheduler-back").addEventListener("click", closeScheduler);
    document.getElementById("scheduler-skip").addEventListener("click", function () {
      send({ meeting_requested: "Yes", meeting_booked: "No (skipped scheduling)" },
           { statusEl: schedStatus });
    });

    window.addEventListener("message", function (e) {
      if (e.origin !== CALENDLY_ORIGIN || scheduler.hidden) return;
      var d = e.data;
      if (!d || typeof d.event !== "string" || d.event.indexOf("calendly.") !== 0) return;
      var payload = d.payload || {};
      var iframe = schedFrame.querySelector("iframe");

      if (d.event === "calendly.page_height" && iframe && payload.height) {
        var h = parseInt(payload.height, 10);
        if (h > 300) iframe.style.height = h + "px";
      } else if (d.event === "calendly.profile_page_viewed" || d.event === "calendly.event_type_viewed") {
        if (schedStatus.textContent.indexOf("Loading") === 0) schedStatus.textContent = "";
      } else if (d.event === "calendly.date_and_time_selected") {
        schedStatus.className = "form-status";
        schedStatus.textContent = "Time selected. Confirm it in the scheduler to finish.";
      } else if (d.event === "calendly.event_scheduled") {
        send({
          meeting_requested: "Yes",
          meeting_booked: "Yes, booked on Calendly (see Calendly for the time)",
          meeting_event: (payload.event && payload.event.uri) || "",
          meeting_invitee: (payload.invitee && payload.invitee.uri) || ""
        }, {
          statusEl: schedStatus,
          booked: true,
          sendingText: "Meeting booked. Sending your request…",
          failText: "Your meeting is booked, but your answers didn't send. Please press “Skip” to try sending again, or call 386-320-9378."
        });
      }
    });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    status.textContent = "";
    status.className = "form-status";

    var problems = runValidation();
    if (problems.length) { showSummary(problems); return; }
    summary.hidden = true;

    if (wantsMeeting()) { openScheduler(); return; }
    send(bookBox ? { meeting_requested: "No" } : {});
  });
})();
