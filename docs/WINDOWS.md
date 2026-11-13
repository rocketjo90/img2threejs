# Windows compatibility fork

This fork of [img2threejs/img2threejs](https://github.com/img2threejs/img2threejs)
adds Windows compatibility to v2.0.1. The original project's Apache-2.0 license,
attribution, and reconstruction workflow are preserved.

## Install this fork in Codex

Install Git, Node.js 18 or newer, and Python 3.10 or newer. In PowerShell, verify
`git --version`, `node --version`, and `py --version`, then clone this fork into
an unused Codex skill directory:

```powershell
git clone https://github.com/rocketjo90/img2threejs.git "$env:USERPROFILE\.codex\skills\img2threejs"
```

Git refuses to overwrite an existing nonempty directory. If a copied installation
already exists, back it up before replacing it. For an existing clone of this fork,
update from its directory with `git pull --ff-only`.

Start a new Codex chat or restart Codex, attach a reference image, and ask:

```text
Use img2threejs to rebuild this image as a procedural Three.js model.
```

Use `py` in place of `python3` in the workflow's commands. The upstream npm package
and its release installer still download the upstream repository; they do not install
this fork. No separate npm package or fork release has been published.

## Windows fixes

- Installer directory junctions avoid the need for administrator rights or Developer Mode.
  Failed link replacement restores the previous installation.
- Bare `python3` plugin commands use the running Python interpreter on Windows;
  explicit interpreter paths keep their meaning.
- Search output uses UTF-8, including redirected output and multilingual text.
- Generated TypeScript uses consistent LF line endings without changing the frozen oracle.
- Source indexing rejects directory junctions as well as symbolic links.
- Installer fixtures work without Unix tools and test paths containing spaces.

## Validation

Local Windows validation used Python 3.14.7 and Node 26.13.0:

| Suite | Passed | Skipped | Failed |
| --- | ---: | ---: | ---: |
| Python core | 1,353 | 65 | 0 |
| Installer | 21 | 0 | 0 |
| Documentation tools | 23 | 0 | 0 |

The Python skips comprise 64 checks requiring optional showcase or plugin checkouts
and one file-symlink test requiring Windows privileges. Directory-junction checks run
without those privileges. Tests retain failure, timeout, output-integrity, and path
checks. These results do not establish visual reconstruction quality.

The [CI workflow](../.github/workflows/ci.yml) checks Windows with Python 3.10 and
3.14, retains Linux coverage, and tests the installer on Windows and Linux with
Node 18 and 22. Consult the fork's Actions page for hosted results.
