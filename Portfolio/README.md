# Swetha Biju — Developer Portfolio

A React + Vite portfolio for Swetha Biju. It uses Framer Motion for interface motion, Lucide React for icons, and a small Canvas layer in the hero. Project artwork is labeled concept UI until real project screenshots are added.

## Run locally

From this folder in the terminal:

```powershell
npm install
npm run dev
```

Open the local URL printed by Vite. To create and preview a deployment build:

```powershell
npm run build
npm run preview
```

## Personal details and assets

- Email, LinkedIn, GitHub, location, and resume URL are set in `src/data/profile.js`.
- The hero portrait is optimized as `public/swetha-biju-portrait.webp` and appears in a pointer-tilted, scroll-parallax frame.
- The resume is `public/Swetha-Biju-Resume.pdf` and is linked from the hero and resume section.
- Project descriptions, technology labels, and GitHub source links live in `src/data/projects.js`.
- The featured source links are OpsMind AI, RecipeSense, and Gallery Vault. No live demos are linked because the available OpsMind deployment URL currently returns a 404 and the other two projects have no verified demo URLs.
- Add real screenshots under `public/projects/` and set the matching project's `image` in `src/data/projects.js` to replace the concept preview.

## Contact form delivery

The form submits its fields to FormSubmit's AJAX endpoint for `swethabiju215@gmail.com`; the email address is the configured recipient. FormSubmit emails the submission and lets Swetha reply to the sender using the sender's address as Reply-To.

The first submission triggers a one-time activation email to Swetha. Click its activation link to turn on forwarding. FormSubmit holds submissions while the address is awaiting confirmation, for up to 30 days. The site only shows its submitted state after FormSubmit responds successfully. The visitor's message passes through FormSubmit before arriving by email.

See the [FormSubmit AJAX documentation](https://formsubmit.co/ajax-documentation) and [activation FAQ](https://formsubmit.co/help).

## Deploy

Import the `Portfolio` folder as a Vite project, or set the base directory to `Portfolio` if the repository root is its parent. Use `npm run build` as the build command and `dist` as the output directory. The contact form does not need a separate server or private API key.

## Notes

- The portfolio intentionally features exactly OpsMind AI, RecipeSense, and Gallery Vault.
- Project descriptions are based on Swetha's CV and available public repository details.
- Reduced-motion preferences disable the typing, magnetic, cursor, tilt, and ambient movement effects where possible. Mobile uses a responsive skill grid and no custom cursor.
