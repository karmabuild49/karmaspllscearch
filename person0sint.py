#!/usr/bin/env python3
"""
person-osint v4 — Multi-Database OSINT Framework.
Integrates WhatsMyName, GitHub, Keybase, EmailRep, Pastebin, and HIBP.
Actor - kArmasec ☠ SYSTEM BREACHED ☠
"""
import sys
import os
import json
import time
import hashlib
import argparse
import urllib.parse
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup

C_GRN = "\033[38;2;0;255;136m"
C_RED = "\033[38;2;255;34;68m"
C_ORG = "\033[38;2;255;140;0m"
C_CYN = "\033[38;2;0;255;255m"
C_PUR = "\033[38;2;255;0;255m"
C_RST = "\033[0m"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
WAM_URL = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"

async def check_site(session, site, username):
    url = site['uri_check'].replace("{account}", username)
    try:
        async with session.get(url, timeout=10, allow_redirects=True) as resp:
            text = await resp.text()
            if resp.status == site.get("e_code", 200):
                if site.get("e_string", "") in text and site.get("m_string", "") not in text:
                    return {"platform": site["name"], "url": url, "status": "FOUND"}
    except Exception:
        pass
    return None

async def run_username_scan(username):
    print(f"\n{C_CYN}[*] Starter Async Username Scan (WhatsMyName)...{C_RST}")
    try:
        r = requests.get(WAM_URL, timeout=15)
        sites = r.json().get("sites", [])
    except Exception:
        print(f"{C_RED}[!] Kunne ikke hente WhatsMyName.{C_RST}")
        return []

    found_profiles = []
    connector = aiohttp.TCPConnector(ssl=False, limit=50)
    async with aiohttp.ClientSession(headers=HEADERS, connector=connector) as session:
        tasks = [check_site(session, site, username) for site in sites]
        results = await asyncio.gather(*tasks)
        for res in results:
            if res:
                print(f"  {C_GRN}[+]{C_RST} {res['platform']}: {C_ORG}{res['url']}{C_RST}")
                found_profiles.append(res)
    return found_profiles

def check_github(username):
    print(f"{C_CYN}[*] Tjekker GitHub for: {username}{C_RST}")
    try:
        r = requests.get(f"https://api.github.com/users/{username}", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            res = {
                "name": data.get("name", "N/A"),
                "company": data.get("company", "N/A"),
                "blog": data.get("blog", "N/A"),
                "location": data.get("location", "N/A"),
                "bio": data.get("bio", "N/A"),
                "url": data.get("html_url")
            }
            print(f"  {C_GRN}[+]{C_RST} GitHub fundet: {res['name']} | {res['company']} | {res['location']}")
            return res
    except Exception:
        pass
    return None

def check_keybase(username):
    print(f"{C_CYN}[*] Tjekker Keybase for: {username}{C_RST}")
    try:
        r = requests.get(f"https://keybase.io/_/api/1.0/user/lookup.json?username={username}", timeout=10)
        data = r.json()
        if data.get("status", {}).get("code") == 0 and data.get("them"):
            them = data["them"][0]
            proofs = [p.get("namWithKey") for p in them.get("proofs_summary", {}).get("all", [])]
            crypto = [f"{c.get('coinType')}: {c.get('address')}" for c in them.get("cryptocurrency_addresses", {}).get("all", [])]
            res = {
                "full_name": them.get("profile", {}).get("full_name", "N/A"),
                "location": them.get("profile", {}).get("location", "N/A"),
                "proofs": proofs,
                "crypto": crypto
            }
            print(f"  {C_GRN}[+]{C_RST} Keybase fundet: {res['full_name']} | {len(proofs)} proofs")
            return res
    except Exception:
        pass
    return None

def check_emailrep(email):
    print(f"{C_CYN}[*] Tjekker EmailRep for: {email}{C_RST}")
    try:
        r = requests.get(f"https://emailrep.io/{email}", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            res = {
                "reputation": data.get("reputation"),
                "suspicious": data.get("suspicious"),
                "references": data.get("references"),
                "profiles": data.get("details", {}).get("profiles", []),
                "breaches": data.get("details", {}).get("breaches", [])
            }
            print(f"  {C_GRN}[+]{C_RST} EmailRep: Reputation={res['reputation']} | Profiles={len(res['profiles'])}")
            return res
    except Exception:
        pass
    return None

def check_pastebin(query):
    print(f"{C_CYN}[*] Søger Pastebin dumps for: {query}{C_RST}")
    try:
        r = requests.get(f"https://psbdmp.ws/api/v3/search/{query}", timeout=10)
        data = r.json()
        if data:
            print(f"  {C_GRN}[+]{C_RST} Fandt {len(data)} Pastebin dumps.")
            return data[:5] # Returner top 5
    except Exception:
        pass
    return []

def check_hibp(email, api_key):
    if not api_key: return []
    print(f"{C_CYN}[*] Tjekker HaveIBeenPwned...{C_RST}")
    headers = {"User-Agent": "person-osint", "hibp-api-key": api_key}
    try:
        r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false", headers=headers, timeout=10)
        if r.status_code == 200:
            return [b["Name"] for b in r.json()]
    except Exception:
        pass
    return []

def generate_report(username, name, email, profiles, github, keybase, emailrep, pastes, hibp, filename="osint_report.html"):
    print(f"{C_CYN}[*] Genererer HTML rapport...{C_RST}")

    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
    <title>OSINT Report: {username or name or email}</title>
    <style>
        body {{ font-family: 'Consolas', monospace; background: #0a0a0f; color: #d1d1e0; padding: 20px; }}
        h1, h2 {{ color: #00ff88; border-bottom: 1px solid #00ff88; padding-bottom: 5px; }}
        a {{ color: #00ccff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .card {{ background: #151520; padding: 15px; margin-bottom: 15px; border-left: 3px solid #ff00ff; }}
        .tag {{ display: inline-block; background: #00ff88; color: #000; padding: 2px 6px; border-radius: 3px; font-weight: bold; margin-right: 5px; }}
    </style></head><body>
    <h1>OSINT Dossier: {username or name or email}</h1>
    """

    if github:
        html += f"<h2>GitHub Profile</h2><div class='card'>"
        html += f"<p><span class='tag'>Name</span> {github['name']}</p>"
        html += f"<p><span class='tag'>Company</span> {github['company']}</p>"
        html += f"<p><span class='tag'>Location</span> {github['location']}</p>"
        html += f"<p><span class='tag'>Bio</span> {github['bio']}</p>"
        html += f"<p><a href='{github['url']}'>{github['url']}</a></p></div>"

    if keybase:
        html += f"<h2>Keybase Identity</h2><div class='card'>"
        html += f"<p><span class='tag'>Name</span> {keybase['full_name']}</p>"
        html += f"<p><span class='tag'>Location</span> {keybase['location']}</p>"
        html += f"<p><span class='tag'>Proofs</span> {', '.join(keybase['proofs'])}</p>"
        if keybase['crypto']:
            html += f"<p><span class='tag'>Crypto</span> {', '.join(keybase['crypto'])}</p>"
        html += "</div>"

    if emailrep:
        html += f"<h2>Email Intelligence</h2><div class='card'>"
        html += f"<p><span class='tag'>Reputation</span> {emailrep['reputation']}</p>"
        html += f"<p><span class='tag'>Suspicious</span> {emailrep['suspicious']}</p>"
        html += f"<p><span class='tag'>Linked Profiles</span> {', '.join(emailrep['profiles'])}</p>"
        if emailrep['breaches']:
            html += f"<p><span class='tag' style='background:#ff2244;color:#fff'>Breaches</span> {', '.join(emailrep['breaches'])}</p>"
        html += "</div>"

    if hibp:
        html += f"<h2>Known Data Breaches (HIBP)</h2><div class='card' style='border-left-color: #ff2244;'>"
        html += f"<p>{', '.join(hibp)}</p></div>"

    if profiles:
        html += "<h2>Social Media Profiles (WhatsMyName)</h2>"
        for p in profiles:
            html += f"<div class='card' style='border-left-color: #00ccff;'><strong>{p['platform']}</strong><br><a href='{p['url']}' target='_blank'>{p['url']}</a></div>"

    if pastes:
        html += "<h2>Pastebin Dumps</h2>"
        for paste in pastes:
            html += f"<div class='card' style='border-left-color: #ffaa00;'>"
            html += f"<p><a href='https://pastebin.com/{paste['id']}' target='_blank'>https://pastebin.com/{paste['id']}</a></p>"
            html += f"<p style='font-size:0.8em;color:#888;'>{paste.get('tags', 'No tags')} | {paste.get('time', '')}</p></div>"

    html += "</body></html>"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{C_GRN}[+] Rapport gemt som: {filename}{C_RST}")

async def main():
    parser = argparse.ArgumentParser(description="Person OSINT v4 Pro")
    parser.add_argument("-u", "--username", help="Target username")
    parser.add_argument("-n", "--name", help="Target full name")
    parser.add_argument("-e", "--email", help="Target email")
    parser.add_argument("-k", "--hibp-key", help="HIBP API Key (optional)")
    args = parser.parse_args()

    if not args.username and not args.name and not args.email:
        print(f"{C_RED}[!] Angiv mindst én af følgende: -u, -n, eller -e{C_RST}")
        sys.exit(1)

    print(f"\n{C_PUR}=== Person OSINT v4 — Multi-Database ==={C_RST}")

    profiles, github, keybase, emailrep, pastes, hibp = [], None, None, None, [], []

    if args.username:
        profiles = await run_username_scan(args.username)
        github = check_github(args.username)
        keybase = check_keybase(args.username)
        pastes.extend(check_pastebin(args.username))

    if args.email:
        emailrep = check_emailrep(args.email)
        pastes.extend(check_pastebin(args.email))
        hibp = check_hibp(args.email, args.hibp_key)

    if args.name:
        pastes.extend(check_pastebin(args.name.replace(" ", "")))

    generate_report(args.username, args.name, args.email, profiles, github, keybase, emailrep, pastes, hibp)

if __name__ == "__main__":
    asyncio.run(main())
