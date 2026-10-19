#!/usr/bin/env bash
# Pulls the existing images from the current WordPress site, then resizes,
# strips metadata, and writes WebP + fallback versions into assets/img/.
#
# Run this BEFORE the domain is pointed away from WordPress (the source URLs
# stop working after the switch). It runs automatically via the
# "Import images" GitHub Action, or locally with:  bash scripts/import-images.sh
#
# Requires: curl, ImageMagick (convert), cwebp
set -euo pipefail

WP="https://sharihaleybookkeeping.com/wp-content/uploads"
OUT="assets/img"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$OUT"

fetch() { # fetch <url> <local-name>
  echo "↓ $2"
  curl -fsSL --retry 3 -o "$TMP/$2" "$1"
}

webp() { # webp <in> <out.webp> [quality]
  cwebp -quiet -q "${3:-78}" -metadata none "$1" -o "$2"
}

photo() { # photo <src> <name> <width>  -> name.jpg + name.webp
  convert "$TMP/$1" -auto-orient -strip -resize "${3}x>" -sampling-factor 4:2:0 -interlace JPEG -quality 80 "$OUT/$2.jpg"
  webp "$OUT/$2.jpg" "$OUT/$2.webp"
}

graphic() { # graphic <src> <name> <maxw> <maxh>  -> name.png + name.webp
  convert "$TMP/$1" -strip -resize "${3}x${4}>" "$OUT/$2.png"
  webp "$OUT/$2.png" "$OUT/$2.webp" 85
}

# ---- download originals
fetch "$WP/2026/04/HaleyLogo_allWhite.png"                          logo-white.png
fetch "$WP/elementor/thumbs/HaleyLogo-rmqagx7dsslk00o7jgyzb4zgl34ax10u7h0gyvfo3o.png" logo.png
fetch "$WP/2025/02/cropped-BK-logo-270x270.png"                     icon.png
fetch "$WP/2025/02/pexels-karolina-grabowska-4386375-scaled.jpg"    hero.jpg
fetch "$WP/2025/02/image-220x300.png"                               chamber.png
fetch "$WP/2025/02/QB-ProAdvisor-Payroll-Badge-300x300.png"         qb-payroll.png
fetch "$WP/2025/03/image-5.png"                                     about-1.png
fetch "$WP/2025/03/image-4.png"                                     about-2.png
fetch "$WP/2025/03/IMG_5241.png"                                    client-stephanie.png
fetch "$WP/2025/03/unnamed-4.png"                                   client-kendra.png
fetch "$WP/2025/02/pexels-tara-winstead-7111517-1024x1536.jpg"      svc-catch-up.jpg
fetch "$WP/2025/02/pexels-n-voitkevich-6863514-scaled.jpg"          svc-clean-up.jpg
fetch "$WP/2025/02/pexels-tara-winstead-7111602-scaled.jpg"         svc-monthly.jpg
fetch "$WP/2025/02/pexels-n-voitkevich-6863260-scaled.jpg"          svc-admin.jpg

# ---- hero: responsive sizes (preloaded on the home page)
convert "$TMP/hero.jpg" -auto-orient -strip -resize "1600x>" -interlace JPEG -quality 62 "$OUT/hero-1600.jpg"
convert "$TMP/hero.jpg" -auto-orient -strip -resize "1600x>" "$TMP/hero-1600.png"
webp "$TMP/hero-1600.png" "$OUT/hero-1600.webp" 55
convert "$TMP/hero.jpg" -auto-orient -strip -resize "800x>" "$TMP/hero-800.png"
webp "$TMP/hero-800.png" "$OUT/hero-800.webp" 55

# ---- content photos
for s in svc-catch-up svc-clean-up svc-monthly svc-admin; do photo "$s.jpg" "$s" 900; done
photo about-1.png about-1 800
photo about-2.png about-2 800

# ---- badges and logos (2x the display size for sharp screens)
graphic qb-payroll.png qb-payroll 240 240
graphic chamber.png    chamber    240 240
graphic logo-white.png logo-white 400 140
graphic logo.png       logo       600 600

# ---- testimonial avatars: square crop
for c in client-stephanie client-kendra; do
  convert "$TMP/$c.png" -strip -resize 112x112^ -gravity center -extent 112x112 "$OUT/$c.png"
  webp "$OUT/$c.png" "$OUT/$c.webp" 82
done

# ---- icons
# The source icon is white on transparent, so set it on the brand green
# (otherwise it disappears on light browser tabs and home screens).
icon() { # icon <size> <out>
  convert -size "${1}x${1}" xc:"#143630" \( "$TMP/icon.png" -resize "$(( $1 * 72 / 100 ))x$(( $1 * 72 / 100 ))" \) \
    -gravity center -composite -strip "$2"
}
icon 192 "$OUT/icon-192.png"
icon 512 "$OUT/icon-512.png"
icon 180 "$OUT/apple-touch-icon.png"
icon 48 "$TMP/fav48.png"
convert "$TMP/fav48.png" -define icon:auto-resize=48,32,16 favicon.ico

# ---- social share image (1200x630): darkened hero + white logo
convert "$TMP/hero.jpg" -resize 1200x630^ -gravity center -extent 1200x630 \
  -fill "#143630" -colorize 62% \
  \( "$TMP/logo-white.png" -resize 640x260 \) -gravity center -composite \
  -strip -quality 82 "$OUT/og-image.jpg"

echo "✓ images written to $OUT"
ls -la "$OUT"
