# NGINX 502 Bad Gateway

## Symptoms
Clients get HTTP 502 responses. The NGINX error log shows lines like
`connect() failed (111: Connection refused) while connecting to upstream` or
`upstream timed out (110: Connection timed out) while reading response header from upstream`.

## Likely causes
A 502 means NGINX reached the upstream but got no valid response. Usual causes:
the backend app process is down or crashed, the backend is up but overloaded and slow,
the upstream host/port in the NGINX config is wrong, or a firewall/security group is
blocking the connection between NGINX and the backend.

## Fix steps
1. Check the backend is running: `systemctl status <app>` or `docker ps`.
2. Curl the backend directly, bypassing NGINX: `curl -v http://127.0.0.1:8080/health`.
3. If the backend is down, restart it and watch its own logs for the crash reason.
4. If the backend is up but slow, raise `proxy_read_timeout` only as a temporary bridge,
   then fix the slow dependency (DB, downstream API).
5. Confirm `upstream` host and port in the NGINX site config match where the app listens.

## Verify
`curl -I https://your-site/` returns 200, and the NGINX error log stops adding new
`upstream` lines. Watch for 60 seconds before calling it resolved.
