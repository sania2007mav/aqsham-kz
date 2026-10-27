#!/usr/bin/env python3
"""Deploy AQSHAM redesign samples to CT 200 (Hestia)."""
from __future__ import annotations

import base64
import json
import os
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import paramiko

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SITE_DIR = Path(__file__).resolve().parents[1]
HOST = os.environ.get("PVE_HOST", "192.168.0.200")
PW = os.environ.get("PVE_PASSWORD", "")
CTID = int(os.environ.get("PVE_CTID", "200"))
CT_IP = os.environ.get("CT_IP", "192.168.0.203")
ADMIN = os.environ.get("HESTIA_ADMIN", "admin")
DOMAIN = os.environ.get("AQSHAM_DOMAIN", "aqsham.melnichuk.kz")
WEB = f"/home/{ADMIN}/web/{DOMAIN}/public_html"

CF_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
ZONE_ID = os.environ.get("CF_ZONE_ID", "25ec564914a8fb0febc34aaff2f37104")
TUNNEL_CNAME = os.environ.get(
    "CF_TUNNEL_CNAME",
    "419be2fe-2b95-49a8-92f1-f0aebe7e1c90.cfargotunnel.com",
)

INCLUDE = (
    "index.html",
    "hub.html",
    "css",
    "js",
    "samples",
    "assets",
)


def cf_api(method: str, path: str, data=None) -> dict:
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        data=json.dumps(data).encode() if data else None,
        method=method,
        headers={
            "Authorization": f"Bearer {CF_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"CF HTTP {e.code}: {body[:400]}")
        return json.loads(body) if body.startswith("{") else {"success": False}


def ensure_dns() -> None:
    recs = cf_api("GET", f"/zones/{ZONE_ID}/dns_records?name={DOMAIN}")
    payload = {
        "type": "CNAME",
        "name": "aqsham",
        "content": TUNNEL_CNAME,
        "proxied": True,
        "ttl": 1,
    }
    if recs.get("result"):
        res = cf_api("PUT", f"/zones/{ZONE_ID}/dns_records/{recs['result'][0]['id']}", payload)
        print(f"DNS updated: {DOMAIN} success={res.get('success')}")
    else:
        res = cf_api("POST", f"/zones/{ZONE_ID}/dns_records", payload)
        print(f"DNS created: {DOMAIN} success={res.get('success')}")


def make_tarball() -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False)
    tmp.close()
    with tarfile.open(tmp.name, "w:gz") as tar:
        for name in INCLUDE:
            path = SITE_DIR / name
            if not path.exists():
                print(" WARN missing:", name)
                continue
            if name == "assets":
                # skip bulky unused css dumps from plugins if any — include all visual assets
                tar.add(path, arcname=name)
            else:
                tar.add(path, arcname=name)
            print(" +", name)
    return Path(tmp.name)


def main() -> None:
    if not PW:
        raise SystemExit("Set PVE_PASSWORD (and optionally CLOUDFLARE_API_TOKEN) in env before deploy.")

    tar_path = make_tarball()
    print(f"Archive: {tar_path} ({tar_path.stat().st_size} bytes)")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        HOST,
        username="root",
        password=PW,
        timeout=45,
        banner_timeout=60,
        auth_timeout=60,
        allow_agent=False,
        look_for_keys=False,
    )

    sftp = ssh.open_sftp()
    sftp.put(str(tar_path), "/tmp/aqsham-site.tar.gz")
    sftp.close()
    tar_path.unlink(missing_ok=True)

    _, o, e = ssh.exec_command(
        f"pct push {CTID} /tmp/aqsham-site.tar.gz /tmp/aqsham-site.tar.gz",
        timeout=180,
    )
    push_err = e.read().decode("utf-8", errors="replace").strip()
    if push_err:
        print("pct push:", push_err)
    o.read()
    time.sleep(1)

    script = f"""#!/bin/bash
set -e
ADMIN={ADMIN}
DOMAIN={DOMAIN}
IP={CT_IP}
WEB={WEB}

if ! /usr/local/hestia/bin/v-list-web-domains "$ADMIN" plain | awk '{{print $1}}' | grep -qx "$DOMAIN"; then
  /usr/local/hestia/bin/v-add-web-domain "$ADMIN" "$DOMAIN" "$IP"
  echo "CREATED $DOMAIN"
else
  echo "EXISTS $DOMAIN"
fi

mkdir -p "$WEB"
find "$WEB" -mindepth 1 -maxdepth 1 -exec rm -rf {{}} +
tar -xzf /tmp/aqsham-site.tar.gz -C "$WEB"
chown -R {ADMIN}:www-data "$WEB"
find "$WEB" -type d -exec chmod 755 {{}} \\;
find "$WEB" -type f -exec chmod 644 {{}} \\;
rm -f /tmp/aqsham-site.tar.gz

/usr/local/hestia/bin/v-rebuild-web-domain "$ADMIN" "$DOMAIN" >/dev/null || true
systemctl reload nginx 2>/dev/null || true

echo "=== files ==="
ls -la "$WEB" | head -25
curl -sk -o /dev/null -w "home=%{{http_code}}\\n" -H "Host: $DOMAIN" http://127.0.0.1/
curl -sk -H "Host: $DOMAIN" http://127.0.0.1/ | grep -oE '<title>[^<]*</title>' | head -1
"""

    b64 = base64.b64encode(script.encode()).decode()
    _, o, e = ssh.exec_command(
        f"pct exec {CTID} -- bash -lc 'echo {b64} | base64 -d | bash'",
        timeout=240,
    )
    print(o.read().decode("utf-8", errors="replace"))
    err = e.read().decode("utf-8", errors="replace").strip()
    if err:
        print("ERR:", err[-1000:])

    ssh.exec_command("rm -f /tmp/aqsham-site.tar.gz", timeout=10)
    ssh.close()

    print("\n=== Cloudflare DNS ===")
    if not CF_TOKEN:
        print("Skip DNS: CLOUDFLARE_API_TOKEN not set")
    else:
        try:
            ensure_dns()
        except Exception as ex:
            print("DNS note:", ex)

    print("\n=== Public check ===")
    for url in (
        f"https://{DOMAIN}/",
        f"https://{DOMAIN}/hub.html",
        f"https://{DOMAIN}/samples/v2-dark.html",
        f"https://{DOMAIN}/samples/v3-aurora.html",
        f"https://{DOMAIN}/assets/logo.svg",
    ):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="GET")
            with urllib.request.urlopen(req, timeout=40) as r:
                body = r.read(800).decode("utf-8", errors="replace")
                title = ""
                if "<title>" in body:
                    title = body.split("<title>", 1)[1].split("</title>", 1)[0]
                print(f"{url} -> {r.status} title={title!r}")
        except Exception as ex:
            print(f"{url} -> {ex}")

    print(f"\nDone.\n  https://{DOMAIN}/")


if __name__ == "__main__":
    main()
