# Emergency rollback 0.31.4

This rollback removes the experimental shell/scroll correction layers introduced after 0.31.0 and restores the 0.31.0 shell loading behavior. The service worker cache key is intentionally bumped to `kmreg-shell-0.31.4-rollback` so existing clients replace stale caches and reload the working shell.
