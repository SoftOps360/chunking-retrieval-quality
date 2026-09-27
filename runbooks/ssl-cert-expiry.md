# Expired TLS / SSL Certificate

## Symptoms
Browsers show `NET::ERR_CERT_DATE_INVALID`. Tools fail with
`certificate has expired` or `SSL certificate problem: certificate has expired`.
Health checks and API clients that verify TLS start failing at the same instant for everyone.

## Likely causes
The certificate reached its `notAfter` date and was not renewed. Common reasons: an
auto-renew job (certbot / cert-manager) stopped running, renewal succeeded but the web
server was never reloaded to pick up the new file, or a manually issued cert with no automation.

## Fix steps
1. Check the expiry on the live endpoint:
   `echo | openssl s_client -connect your-site:443 2>/dev/null | openssl x509 -noout -dates`.
2. Renew it. With certbot: `certbot renew` then reload the server: `nginx -s reload`
   (renewal without a reload does NOT serve the new cert).
3. With cert-manager on Kubernetes, check the Certificate resource:
   `kubectl describe certificate <name>` and look at the `Ready` condition and events.
4. Re-enable and test the auto-renew timer so this cannot silently lapse again.

## Verify
`openssl ... -noout -dates` shows a future `notAfter`, and the site loads without a
certificate warning in a real browser.
