# Initial Plektra release

The local checkout retains the Pastiera asset repository history. `origin` targets
`pkb-rocks/plektra-dict`; `upstream` points to `palsoftware/pastiera-dict`.
The output of `prepare_initial_release.py` contains 19 dictionaries, 16 layouts,
license/provenance notices, release notes and `SHA256SUMS`. No corpus is rebuilt.
The three other layout files in the checkout were not in the upstream published
manifest and are excluded from this first release.

The script verifies all input assets against the immutable upstream manifest
snapshots before writing anything. It refuses to replace an existing output
directory. Keep release outputs under ignored `.local-work/releases/`.

## Publication order

1. Create the public `pkb-rocks/plektra-dict` repository and push the reviewed
   commit, preserving attribution and the upstream history.
2. Create the `v1` tag at that commit and a draft release. Upload every file in
   `.local-work/releases/v1/`; use `RELEASE_NOTES.md` as the release body.
3. Verify uploaded asset names, byte counts and SHA-256 values, then publish
   the dictionary release. The inherited updater workflow maintains manifests
   from published release assets.
4. Enable GitHub Pages from the default branch's `/docs` directory. Keep the
   project site's custom domain unset: it inherits the organization's `pkb.rocks`
   domain. See [GitHub's custom-domain documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages).
5. Check both canonical manifest URLs and download a dictionary and a layout
   through their published URLs. Validate checksums and app import.
6. Only then sign and publish the Plektra Nightly using these URLs. First ship
   the full APK with variant-aware updating; offer both APK variants afterwards.

Repo creation, push, tag/release publication and Pages configuration require
explicit maintainer authorization. This local preparation performs none of them.
