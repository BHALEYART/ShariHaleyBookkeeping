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
2. **Form** — create a free access key at [web3forms.com](https://web3forms.com) using the email that should receive requests, then replace `YOUR_WEB3FORMS_ACCESS_KEY` in `contact/index.html`. Send a test submission.
3. **Deploy** — import the repo into Vercel (framework: *Other*, no build command, output directory `.`), add the domain, and update DNS.
4. **Search Console** — verify the domain in Google Search Console and submit `https://sharihaleybookkeeping.com/sitemap.xml`. Do the same in Bing Webmaster Tools.
5. **Google Business Profile** — make sure the name, phone (386-320-9378), and website match the site exactly; this drives local "bookkeeper near me" results more than anything on the page.

## Editing

Edit the HTML directly. Header, footer, and structured data (JSON-LD) are repeated in each page, so change them everywhere. When page content changes, update `<lastmod>` in `sitemap.xml`.

## Accessibility

Targets WCAG 2.2 AA: skip link, landmarks, keyboard-operable menu (Esc closes), visible focus, AA contrast, labelled and grouped form fields, an error summary plus inline errors announced to screen readers, reduced-motion support, and a click-to-load video.
