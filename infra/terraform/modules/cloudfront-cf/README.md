# modules/cloudfront-cf (not yet implemented)

CDN distribution for `apps/web`'s static assets, per
`docs/architecture/01-system-architecture.md` §7 (Cloudflare in front of everything; CloudFront
specifically fronts the Next.js static build output, not the API). There is no frontend code to
serve yet — `apps/web` is still a placeholder (see its README) pending Phase 2 Core Frontend work.
Building the CDN distribution now would mean guessing at cache behaviors, origin paths, and build
output structure that don't exist yet. Build this alongside the first `apps/web` deploy.
