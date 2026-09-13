# Lumina Final Audit Loop Skill

## Audit Protocol
1. Run backend tests: `pytest -v` (100% pass rate required).
2. Run security matrix: `pytest tests/test_security.py -v`.
3. Run frontend type check: `npx tsc --noEmit`.
4. Run frontend build: `npm run build` (generates `dist/`).
5. Verify task ledger: `docs/TASK_LEDGER.md` has `TODO = 0`, `IN_PROGRESS = 0`, `critical BLOCKED = 0`.
6. Scan for forbidden strings: `TODO|FIXME|NotImplementedError|placeholder|coming soon|mock|debug|dev-token|hardcoded secret` in production paths.
7. Confirm all 22 Production Gates passed.
