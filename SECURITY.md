# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.x.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in PODStudio, please report it responsibly:

1. **Do NOT open a public issue**
2. Email security details to: [your-email@example.com] (replace with actual contact)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and provide a timeline for a fix.

## Security Considerations

PODStudio is designed with security in mind:

- **Offline-First**: No network calls by default; all processing is local
- **No Remote Code Execution**: User assets processed with sandboxed libraries
- **Input Validation**: All file inputs validated (MIME type, signatures, size limits)
- **Dependency Management**: Locked dependencies via `pip-compile`
- **External Tools**: FFmpeg/ExifTool called with sanitized paths (no shell injection)

## Known Risks

- **Malicious Media Files**: Corrupted or exploit-laden media files may crash processing libraries (Pillow, FFmpeg). Mitigation: Input validation, timeouts, sandboxing.
- **GPU Drivers**: Untested GPU drivers may cause crashes. Mitigation: Hardware capability detection, fallback to CPU.
- **Third-Party Binaries**: FFmpeg, Real-ESRGAN, ExifTool must be from trusted sources. Mitigation: Document official download links only.

## Updates

Security patches will be released as minor version bumps (0.x.1, 0.x.2) with changelogs in [CHANGELOG.md](CHANGELOG.md).

---

Last updated: October 22, 2025
