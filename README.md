# sharihaleybookkeeping.com

Static rebuild of the Shari Haley Bookkeeping site (replacing the WordPress/Elementor version). Plain HTML, one CSS file, one small JS file — no build step, no frameworks, no external fonts.

## Pages

| Path | Purpose |
|---|---|
| `/` | Home |
| `/about-us/` | About Shari, mission, values, video |
| `/our-services/` | Services detail + FAQ |
| `/contact/` | Free consultation intake form (`#consultation`) |
| `/thank-you/` | Form confirmation (noindex) |
| `/accessibility/`, `/privacy/` | Statements |
| `404.html` | Not-found page |

Old WordPress URLs (`/about/`, `/wp-admin/`, etc.) redirect via `vercel.json`. The old site's `#calendar` buttons pointed at an anchor that didn't exist; every booking button now goes to the form.

## Launch checklist

1. **Images** — the first push to `main` runs the *Import images* GitHub Action, which downloads the current images from WordPress, makes WebP + resized versions, and commits them to `assets/img/`. **This must happen before the domain stops pointing at WordPress.** Re-run any time from the Actions tab.
2. **Form** — requests go to sharihaleybookkeeping@gmail.com through [FormSubmit](https://formsubmit.co) (no account or key). The **first** submission triggers a one-time activation email to that inbox; Shari must click its link before requests are delivered, so send a test and activate it before launch. Optional: after activating, FormSubmit offers a random alias you can swap into the form's `action` so the address isn't in the page source.
3. **Deploy** — import the repo into Vercel (framework: *Other*, no build command, output directory `.`), add the domain, and update DNS.
4. **Search Console** — verify the domain in Google Search Console and submit `https://sharihaleybookkeeping.com/sitemap.xml`. Do the same in Bing Webmaster Tools.
5. **Google Business Profile** — make sure the name, phone (386-320-9378), and website match the site exactly; this drives local "bookkeeper near me" results more than anything on the page.

## Booking a meeting (Calendly)

The form has an optional "Also book a meeting time" checkbox. When it's checked, finishing the form opens Shari's Calendly (`https://calendly.com/sharihaleybookkeeping`, set in `data-calendly` on the form) with the visitor's name and email filled in. When they confirm a time, Calendly creates the appointment and the form sends with `meeting_booked: Yes` plus the Calendly event link. The exact time is in Calendly and its confirmation email. "Skip" sends the request without a time.

## Editing

Edit the HTML directly. Header, footer, and structured data (JSON-LD) are repeated in each page, so change them everywhere. Pages load `site.css?v=…` and `site.js?v=…`: when you change either file, change its `?v=` value on every page so browsers fetch the new copy instead of a cached one. When page content changes, update `<lastmod>` in `sitemap.xml`.

## Accessibility

Targets WCAG 2.2 AA: skip link, landmarks, keyboard-operable menu (Esc closes), visible focus, AA contrast, labelled and grouped form fields, an error summary plus inline errors announced to screen readers, reduced-motion support, and a click-to-load video.
