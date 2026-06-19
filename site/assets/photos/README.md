# Photos

Drop your real product photos in this folder with these exact filenames and the site will use them automatically:

| Filename             | What goes here                                              | Used on             |
| -------------------- | ----------------------------------------------------------- | ------------------- |
| `hero-cart.jpg`      | Black HAVOC 4-seater lifted cart (the wide-stance one)       | Hero right panel    |
| `motor-install.jpg`  | Under-the-cart shot of an installed WLM motor with the sticker | "The Upgrade" section |
| `truck-side.jpg`     | F-150 wrap, driver-side view                                  | Trust band          |
| `truck-back.jpg`     | F-150 wrap, rear view                                         | Footer / about      |

Recommended specs:
- JPG or WebP, ~1600px on the long edge
- Under 400KB each (use https://squoosh.app to compress)
- 4:5 portrait for `hero-cart.jpg` ideally; landscape ok for the others

After dropping them in, commit + push — Cloudflare Pages will auto-deploy:

```bash
git add site/assets/photos/
git commit -m "add real product photos"
git push
```
