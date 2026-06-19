# White Lightning Motors

Static marketing site for [whitelightningmotors.com](https://whitelightningmotors.com) — performance golf cart motors, lithium upgrades, Navitas controllers, full AC kits.

## Deploy

Cloudflare Pages auto-deploys `site/` on every push to `main`. Two ways to wire it:

**Easiest — Cloudflare dashboard:**
1. Cloudflare → Pages → Create a project → Connect to Git → pick `aaronconsent/whitelightning`.
2. Build settings:
   - **Build command:** *(leave blank)*
   - **Build output directory:** `site`
3. Save → it auto-deploys on every `git push`.

**Optional — GitHub Actions** (gives you PR preview deploys):
1. In CF dashboard create a Pages project named `whitelightning` (or edit `.github/workflows/deploy.yml` to match).
2. Add two repo secrets in GitHub:
   - `CLOUDFLARE_API_TOKEN` (Pages:Edit permission)
   - `CLOUDFLARE_ACCOUNT_ID` (right sidebar of CF dashboard)
3. Push to main → workflow deploys.

If neither is configured, the workflow gracefully no-ops.

## Photos

Drop real product photos into `site/assets/photos/`:

| Filename            | What                                        |
| ------------------- | ------------------------------------------- |
| `hero-cart.jpg`     | Lifted black 4-seater w/ HAVOC graphics     |
| `motor-install.jpg` | Installed motor with WLM sticker (under cart) |
| `truck-side.jpg`    | F-150 wrap, driver-side view                |
| `truck-back.jpg`    | F-150 wrap, rear view                       |

Specs: ~1600px long edge, <400KB each (use [squoosh.app](https://squoosh.app) to compress).

The site falls back to an SVG cart illustration if `hero-cart.jpg` isn't present, so it never breaks.

## Local preview

```bash
python3 -m http.server 8796 --directory site
# open http://localhost:8796
```
