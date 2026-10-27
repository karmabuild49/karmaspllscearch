# karmaspllscearch
people tracker.. usernames, real names,  emails or all same time, if you got it


## 1. Installation. 🚀

You need Python 3.8+ installed on your system (Termux, Linux, macOS, or Windows).

```bash
# Install the required dependencies
pip install aiohttp requests beautifulsoup4
```

Save the person-osint.py script to your machine. Make it executable:

```bash
chmod +x person-osint.py
```

---

2. How to Run It

The tool accepts three types of input: Username (-u), Full Name (-n), and Email (-e). You can use them individually or combine them for a deeper scan.

A. Username Scan (600+ Platforms) 🚀

Searches for the username across hundreds of social networks, forums, and gaming platforms simultaneously.

```bash
python person-osint.py -u "anders123"
```

Finds: GitHub, Reddit, Instagram, Steam, Twitch, OnlyFans, etc.

B. Full Name Scan (Dorks) 🦝

Runs targeted searches for a person's real name. You can add a location to narrow the results.

```bash
python person-osint.py -n "Anders Andersen" -l "London"
```

Finds: LinkedIn profiles, public PDFs, company records, and general web mentions.

C. Email Scan (Gravatar)

Checks if the email address is linked to a Gravatar profile (often reveals profile pictures and linked blogs).

```bash
python person-osint.py -e "anders@example.com"
```

Finds: Profile pictures, linked websites, and confirms the email format.

D. The Full Package (Combine them)

For the most comprehensive scan, combine all three flags:

```bash
python person-osint.py -u "anders123" -n "Anders Andersen" -e "anders@example.com"
```

---

3. Output

When the scan finishes, the tool generates a file called osint_report.html in the same folder.

Open it in your browser:

```bash
# In Termux, you can open it with:
termux-open osint_report.html
```

The report will show you:

· Gravatar: The target's profile picture (if found).
· Profiles: A clickable list of all discovered social media accounts.
· Dorks: A list of search results containing the target's name or documents.
Actor - kArmasec  <trace>      <map>
                      <track>
