# PODStudio — Risk Register

**Version:** 1.0.0  
**Date:** October 22, 2025  
**Status:** Design Specification

---

## Table of Contents

1. [Overview](#overview)
2. [Technical Risks](#technical-risks)
3. [User Experience Risks](#user-experience-risks)
4. [Performance Risks](#performance-risks)
5. [Dependency Risks](#dependency-risks)
6. [Legal & Licensing Risks](#legal--licensing-risks)
7. [Market & Adoption Risks](#market--adoption-risks)
8. [Risk Mitigation Summary](#risk-mitigation-summary)

---

## Overview

This document identifies **known risks** to PODStudio's development, launch, and adoption, along with **mitigation strategies**. Risks are rated by:
- **Probability:** High | Medium | Low
- **Impact:** High | Medium | Low
- **Priority:** Critical | High | Medium | Low

---

## Technical Risks

### Risk T1: GPU Driver Incompatibility

**Description:** NVIDIA/AMD/Intel GPU drivers vary widely; pynvml or DirectML may fail on older/updated drivers.

**Probability:** Medium  
**Impact:** High  
**Priority:** High

**Symptoms:**
- pynvml fails to initialize
- GPU detection returns None
- CUDA/DirectML errors during job execution

**Mitigation:**
1. **Graceful Fallback:** If GPU detection fails, default to CPU-only mode
2. **Driver Version Check:** Warn if driver is <6 months old or known problematic
3. **User Override:** Settings option to force CPU or specific backend
4. **Comprehensive Logging:** Capture driver versions, error codes for troubleshooting
5. **Documentation:** Provide "Known Issues" doc with driver update links

**Residual Risk:** Low (fallback ensures functionality)

---

### Risk T2: ffmpeg Not in PATH or Missing

**Description:** ffmpeg is essential for video/audio ops but not bundled by default on Windows.

**Probability:** High (on fresh installs)  
**Impact:** High  
**Priority:** Critical

**Mitigation:**
1. **Bundle ffmpeg:** Include ffmpeg.exe in installer (60 MB overhead)
2. **Auto-Download:** On first launch, if missing, offer one-click download
3. **PATH Detection:** Check both bundled location and system PATH
4. **Fallback Prompt:** If not found, show clear instructions with download link
5. **Graceful Degradation:** Disable video/audio ops until installed; rest of app works

**Residual Risk:** Low (bundle + auto-download covers 95%+ cases)

---

### Risk T3: SQLite Database Corruption

**Description:** Power loss, disk failure, or concurrent write could corrupt database.

**Probability:** Low  
**Impact:** High (data loss)  
**Priority:** High

**Mitigation:**
1. **WAL Mode:** Enable SQLite Write-Ahead Logging for better concurrency
2. **Auto-Backup:** Daily backup of `podstudio.db` to `.backup/`
3. **Integrity Check:** On startup, run `PRAGMA integrity_check`
4. **Recovery Tool:** Built-in DB repair/recovery option in Settings
5. **User Education:** Docs remind users to back up project folder

**Residual Risk:** Low (backups + WAL mode very reliable)

---

### Risk T4: Long Video Jobs Timeout or Crash

**Description:** Processing 10-minute 4K video can take 1+ hour; risk of OOM or process kill.

**Probability:** Medium  
**Impact:** Medium (user frustration)  
**Priority:** Medium

**Mitigation:**
1. **Pre-Flight Checks:** Block unsafe operations (see Hardware Policy)
2. **Resume Support:** Checkpoint progress every 10% (future feature)
3. **User Warning:** Show estimated time before starting
4. **Resource Monitoring:** Kill job if RAM exceeds 90% of available
5. **Splitting Suggestion:** Offer to split long videos into chunks

**Residual Risk:** Medium (inherent to heavy processing)

---

### Risk T5: ML Model Download Failures

**Description:** rembg, Real-ESRGAN models downloaded on first use; network issues could fail download.

**Probability:** Medium  
**Impact:** Medium (feature blocked)  
**Priority:** Medium

**Mitigation:**
1. **Retry Logic:** Retry download up to 3 times with exponential backoff
2. **Cache Models:** Once downloaded, never re-download
3. **Manual Download:** Provide links for manual download + install instructions
4. **Offline Mode:** Detect network offline, defer downloads, show clear message
5. **Model Bundling (future):** Offer installer with pre-bundled models (larger download)

**Residual Risk:** Low (retry + manual fallback)

---

## User Experience Risks

### Risk U1: Overwhelming First Launch

**Description:** Users may not understand watch folders, prompts, or pack builder on first launch.

**Probability:** High (for non-technical users)  
**Impact:** Medium (confusion, abandonment)  
**Priority:** High

**Mitigation:**
1. **Welcome Wizard:** Optional 3-step onboarding (watch folder, import sample, build sample pack)
2. **Tooltips:** Hover help on all panels and buttons
3. **Sample Project:** Include pre-loaded sample project with 10 assets
4. **Video Tutorial:** Link to 5-minute "Getting Started" video
5. **In-App Help:** Context-sensitive help panel

**Residual Risk:** Low (onboarding + help reduces friction)

---

### Risk U2: Jobs Appear Stuck (Progress Not Updating)

**Description:** Polling-based progress updates may seem laggy; users think job frozen.

**Probability:** Medium  
**Impact:** Medium (perceived bug)  
**Priority:** Medium

**Mitigation:**
1. **Frequent Polling:** Poll every 500ms (not 1s)
2. **Spinner During Gaps:** Show spinner when progress unchanged for 5s
3. **Elapsed Time:** Always show elapsed time (proves job is alive)
4. **Cancel Button Responsive:** [Cancel] works immediately
5. **Future: WebSockets:** Real-time updates in v1.1

**Residual Risk:** Low (polling + elapsed time sufficient)

---

### Risk U3: Asset Grid Slow with 1000+ Assets

**Description:** Rendering 1000 thumbnails can lag UI.

**Probability:** Medium (power users)  
**Impact:** Medium (sluggish UI)  
**Priority:** Medium

**Mitigation:**
1. **Virtual Scrolling:** Only render visible rows (50-100 items max on screen)
2. **Thumbnail Caching:** Pre-generate thumbnails in background
3. **Lazy Loading:** Load thumbnails as user scrolls
4. **Pagination (optional):** Show 100 assets per page with pagination
5. **Filter by Date:** Default view shows last 30 days

**Residual Risk:** Low (virtual scrolling + lazy load scales well)

---

## Performance Risks

### Risk P1: CPU-Only Mode Too Slow to Be Useful

**Description:** Users without GPU may wait 10+ minutes per upscale, leading to abandonment.

**Probability:** High (30-40% of users lack dedicated GPU)  
**Impact:** High (poor experience)  
**Priority:** High

**Mitigation:**
1. **Clear Expectations:** Show estimated time before starting job
2. **Background Jobs:** User can continue working while job runs
3. **Batch Overnight:** Suggest running batch jobs overnight
4. **Cloud Burst (future):** Offer paid cloud processing for heavy jobs
5. **Optimize CPU Path:** Use ncnn (lighter than PyTorch) for CPU

**Residual Risk:** Medium (CPU will always be slower; transparency helps)

---

### Risk P2: Thumbnail Generation Bottleneck

**Description:** Generating thumbnails for 100 assets on import takes time.

**Probability:** Medium  
**Impact:** Low (cosmetic)  
**Priority:** Low

**Mitigation:**
1. **Background Worker:** Generate thumbnails async after import
2. **Placeholder:** Show generic icon while thumbnail generates
3. **Priority Queue:** Visible assets first, rest later
4. **Cache Forever:** Never regenerate unless file changes

**Residual Risk:** Low (async + cache solves it)

---

## Dependency Risks

### Risk D1: PySide6 Version Conflicts

**Description:** PySide6 rapid updates may introduce breaking changes.

**Probability:** Low  
**Impact:** High (app won't start)  
**Priority:** Medium

**Mitigation:**
1. **Pin Version:** Lock PySide6 to tested version (e.g., 6.5.2)
2. **Test Before Upgrade:** Never upgrade PySide6 without full regression test
3. **Virtual Environment:** Always use venv to isolate dependencies
4. **Fallback:** Keep previous working version in git history

**Residual Risk:** Low (pinning is standard practice)

---

### Risk D2: Real-ESRGAN Model Updates Break API

**Description:** Real-ESRGAN library updates could change API, breaking our integration.

**Probability:** Low  
**Impact:** Medium (feature broken)  
**Priority:** Low

**Mitigation:**
1. **Pin Version:** Lock Real-ESRGAN version
2. **Test Suite:** Automated tests for all processor integrations
3. **Abstraction Layer:** Wrapper class around Real-ESRGAN (easy to swap)
4. **Monitor Releases:** Watch GitHub repo for breaking changes

**Residual Risk:** Low (abstraction + pinning)

---

### Risk D3: Windows API Changes (Future OS Updates)

**Description:** Windows 12 or future updates could break hardware detection, file watchers, etc.

**Probability:** Low (Windows very backward-compatible)  
**Impact:** Medium  
**Priority:** Low

**Mitigation:**
1. **Test on Insider Builds:** Test on Windows Insider Preview before public release
2. **Compatibility Mode:** Offer Windows 10 compatibility mode if needed
3. **Community Reports:** Monitor user reports for OS-specific issues
4. **Patch Quickly:** Plan for rapid hotfix releases post-Windows updates

**Residual Risk:** Low (historical Windows compat is good)

---

## Legal & Licensing Risks

### Risk L1: User Generates Copyrighted Content

**Description:** User uses PODStudio to package AI-generated assets that violate copyright (e.g., trained on copyrighted art).

**Probability:** Medium  
**Impact:** High (legal liability for user, reputation for us)  
**Priority:** High

**Mitigation:**
1. **Disclaimer:** Clear TOS: "User responsible for ensuring content is legal and licensed"
2. **No Content Moderation:** We don't host or review content (tool-only)
3. **Educational Content:** Docs include section on copyright, AI ethics, fair use
4. **Prompt Templates:** Our templates emphasize original concepts, not copying
5. **License Generator:** Reminds users to verify rights before selling

**Residual Risk:** Medium (user behavior outside our control)

---

### Risk L2: Third-Party Model Licenses

**Description:** U2Net (rembg), Real-ESRGAN, CodeFormer have open-source licenses; misuse could expose us.

**Probability:** Low  
**Impact:** High (legal action)  
**Priority:** High

**Mitigation:**
1. **License Audit:** Verify all models are MIT/Apache/GPL-compatible
2. **Attribution:** Include LICENSES.txt in installer with all third-party licenses
3. **GPL Compliance:** If using GPL code, offer source code access
4. **Legal Review:** Have lawyer review before public release

**Residual Risk:** Low (most models are MIT/Apache)

---

### Risk L3: User Sells Pack with PODStudio-Generated LICENSE.txt

**Description:** User exports pack with our license template but doesn't customize it (e.g., wrong copyright holder).

**Probability:** Medium  
**Impact:** Low (user's issue, not ours)  
**Priority:** Low

**Mitigation:**
1. **Template Warnings:** LICENSE.txt includes "REPLACE THIS WITH YOUR INFO" placeholders
2. **Validation:** Pre-export check warns if LICENSE has placeholders
3. **Docs:** README explains importance of customizing licenses
4. **Default Safe:** Default license is restrictive (personal use only)

**Residual Risk:** Low (user responsibility + warnings)

---

## Market & Adoption Risks

### Risk M1: Competing Tools (Photoshop, Topaz, etc.)

**Description:** Professional tools like Photoshop + Topaz AI offer similar features.

**Probability:** High (competition exists)  
**Impact:** Medium (limits adoption)  
**Priority:** Medium

**Mitigation:**
1. **Unique Value Prop:** End-to-end POD workflow (not just image editing)
2. **Lower Cost:** Free/open-source vs. $100+ subscriptions
3. **Automation:** Watch folders + batch ops save time over manual tools
4. **Community Focus:** Built for POD creators, not general photo editing
5. **Integration:** Future plugins for Gumroad, Etsy (competitors don't have)

**Residual Risk:** Medium (niche focus reduces competition)

---

### Risk M2: AI Generation Platforms Add Pack Export

**Description:** MidJourney, DALL-E could add native pack export features.

**Probability:** Medium  
**Impact:** High (reduces our unique value)  
**Priority:** Medium

**Mitigation:**
1. **Platform-Agnostic:** We support ALL platforms, not just one
2. **Post-Processing:** We offer upscaling, bg-removal, etc. (they don't)
3. **Provenance:** Our manifest tracks full history (they don't)
4. **First-Mover:** Establish user base before they catch up
5. **Pivot Ready:** Can pivot to B2B (white-label for platforms)

**Residual Risk:** Medium (long-term strategic risk)

---

### Risk M3: Low Adoption (Ghost Town Problem)

**Description:** Despite build, users don't adopt; community doesn't form.

**Probability:** Medium  
**Impact:** High (project failure)  
**Priority:** High

**Mitigation:**
1. **Pre-Launch Community:** Build Discord/Reddit before launch
2. **Influencer Outreach:** Partner with POD YouTubers for demos
3. **Free Tier:** Keep core features free (no paywall)
4. **Templates & Samples:** Provide starter packs, tutorials
5. **Feedback Loop:** Rapid iteration based on early user feedback
6. **Open Source:** GitHub community can contribute features

**Residual Risk:** Medium (market validation risk inherent to new products)

---

## Risk Mitigation Summary

### Critical Priorities (Fix Before v1.0)

1. **Bundle ffmpeg** (Risk T2) — Eliminates #1 support issue
2. **Hardware Policy Enforcement** (Risk T4) — Prevents crashes
3. **Legal Compliance** (Risk L2) — Avoid legal issues
4. **Onboarding UX** (Risk U1) — Reduce first-launch abandonment

### High Priorities (Launch Week)

1. **GPU Driver Fallback** (Risk T1) — CPU-only users can still use app
2. **Clear Job Progress** (Risk U2) — Reduce perceived bugs
3. **Copyright Disclaimers** (Risk L1) — Protect reputation

### Medium Priorities (v1.1)

1. **Virtual Scrolling** (Risk U3) — Scale to power users
2. **WebSocket Job Updates** (Risk U2) — Better UX
3. **Cloud Burst** (Risk P1) — Monetization + better CPU-only UX

### Low Priorities (Future)

1. **Model Bundling** (Risk T5) — Convenience, not critical
2. **Resume Support** (Risk T4) — Nice-to-have
3. **Pagination** (Risk U3) — Virtual scrolling sufficient

---

## Risk Review Cadence

- **Weekly (During Development):** Review new risks from testing
- **Pre-Release:** Full risk audit, verify all critical mitigations complete
- **Monthly (Post-Launch):** User feedback may reveal new risks
- **Quarterly:** Strategic risks (market, competition) review

---

**End of Risk Register**  
**Next Steps:** Implement critical mitigations before implementation phase; monitor residual risks post-launch.
