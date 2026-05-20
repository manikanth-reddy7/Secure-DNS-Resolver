# 🔍 Recursive DNS Resolver with DNSSEC

A Python implementation of a recursive DNS resolver built from scratch — no system DNS, no shortcuts. Resolves domain names by walking the DNS hierarchy from root servers down, with an optional DNSSEC chain-of-trust validation mode and a performance benchmarking tool.

---

## 📌 Introduction

Standard DNS resolution is handled silently by your OS or a configured resolver (like Google's `8.8.8.8`). This project replicates that process transparently — starting from the 13 root nameservers, iteratively querying authoritative nameservers at each level of the domain hierarchy, and returning the final answer.

The DNSSEC-enabled variant goes further: at each hop, it validates cryptographic signatures (RRSIGs), verifies DNSKEY records, and checks the chain of trust using DS (Delegation Signer) records — ensuring responses haven't been tampered with.

---

## 🛠️ Tech Stack

| Component | Details |
|-----------|---------|
| **Language** | Python 3.x |
| **DNS Protocol Library** | [`dnspython`](https://www.dnspython.org/) — DNS message construction, UDP/TCP queries, DNSSEC primitives |
| **Cryptography** | [`cryptography`](https://cryptography.io/) — used internally by dnspython for signature verification |
| **Data & Plotting** | [`numpy`](https://numpy.org/) + [`matplotlib`](https://matplotlib.org/) — used in `analyze.py` for CDF generation |
| **Protocol** | DNS over UDP (with TCP fallback for chain-of-trust queries) |
| **Transport** | Direct socket communication with public root/authoritative nameservers |

---

## 📂 Project Structure

```
Recursive-DNS-Resolver-with-DNSSEC/
│
├── mydig.py              # Core recursive DNS resolver (A, NS, MX)
├── mydig_dnssec.py       # DNS resolver with DNSSEC chain-of-trust validation
├── analyze.py            # Performance benchmarking + CDF plot generator
├── mydig_output.txt      # Sample output from mydig
├── Performance analysis.pdf   # Benchmark results report
└── Problem Statement.pdf      # Original assignment spec
```

---

## ⚙️ How It Works

### `mydig.py` — Recursive Resolver

1. Starts with a hardcoded list of the 13 root nameserver IPs (e.g. `198.41.0.4`)
2. Sends a UDP DNS query for the requested domain and record type
3. Parses the response:
   - **Answer section present** → return the result
   - **Additional section present** → use those IPs as the next nameservers to query
   - **Only authority section** → resolve the NS hostname first (sub-recursion), then query it
4. Follows CNAME chains by restarting resolution from root
5. Repeats until a final answer is reached or all paths are exhausted

### `mydig_dnssec.py` — DNSSEC Chain of Trust

Extends the resolver with cryptographic verification at each delegation:

1. At each nameserver hop, fetches DNSKEY records (ZSK + KSK) and RRSIG signatures
2. Validates the RRset signature using the Zone Signing Key (ZSK)
3. Validates the DNSKEY set using the Key Signing Key (KSK)
4. Fetches the DS record from the parent zone and recomputes it from the child's KSK
5. Compares digests (SHA-1, SHA-256, or SHA-384) to confirm the delegation is trusted
6. Only proceeds to the next level if the current level passes — building a verified chain from root to answer

If any step fails, it prints `DNSSec verification failed` or `DNSSEC not supported` and stops.

### `analyze.py` — Performance Benchmarking

Resolves 25 top global domains (Google, Facebook, Wikipedia, etc.) 10 times each using `mydig`, then generates a **Cumulative Distribution Function (CDF)** plot comparing:

- **mydig** (this implementation)
- **Local DNS resolver**
- **Google Public DNS** (`8.8.8.8`)

Results are saved to `plot.png`.

---

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install dnspython cryptography numpy matplotlib
```

> ⚠️ Note: `dnspython` requires `cryptography` for DNSSEC validation. The old `pycrypto` is no longer supported.

---

### 2. Run the Basic Resolver (`mydig.py`)

```bash
python3 mydig.py <DOMAIN> <RECORD_TYPE>
```

**Supported record types:** `A`, `NS`, `MX`

**Examples:**

```bash
# Resolve IP address
python3 mydig.py www.google.com A

# Resolve nameservers
python3 mydig.py wikipedia.org NS

# Resolve mail servers
python3 mydig.py gmail.com MX
```

**Sample output:**
```
['142.250.80.68']
```

---

### 3. Run the DNSSEC Resolver (`mydig_dnssec.py`)

```bash
python3 mydig_dnssec.py <DOMAIN>
```

> Only A records are resolved. DNSSEC support depends on the domain.

**Examples:**

```bash
python3 mydig_dnssec.py www.google.com
python3 mydig_dnssec.py cloudflare.com
```

**Possible outputs:**

```
['142.250.80.68']           ← DNSSEC verified successfully
DNSSEC not supported        ← Domain doesn't publish DNSSEC records
DNSSec verification failed  ← Signature or DS mismatch detected
```

---

### 4. Run the Performance Analyzer (`analyze.py`)

```bash
python3 analyze.py
```

This will:
- Resolve 25 top domains live using `mydig` (takes a few minutes)
- Use pre-recorded timing data for local DNS and Google DNS
- Display and save a CDF comparison chart as `plot.png`

> Make sure `mydig.py` is in the same directory, as `analyze.py` imports it as a module.

### 📊 Benchmark Results

![Performance Analysis Plot](./plot.png)

*As the plot shows, `mydig` (the red line) takes around 0.2 to 1.6 seconds, making it much slower than the Local DNS Resolver and Google Public DNS. This result is perfectly correct and expected! The custom script starts from the root server for every domain, avoids using a cache, and iteratively resolves the query across global authoritative nameservers. Meanwhile, Google and Local DNS answer instantly from heavily optimized, nearby cache servers.*

---

## 🔬 Example Workflow

```bash
# Install dependencies
pip install dnspython cryptography numpy matplotlib

# Basic A record lookup
python3 mydig.py github.com A

# DNSSEC-validated lookup
python3 mydig_dnssec.py github.com

# Full performance benchmark + plot
python3 analyze.py
```

---

## 📝 Notes

- **Network access required** — the resolver queries live public nameservers; a firewall blocking outbound UDP port 53 will cause failures.
- **Timeouts** — UDP queries have a 2-second timeout. Slow or unresponsive nameservers are skipped.
- **DNSSEC coverage** — not all domains support DNSSEC. Domains like `cloudflare.com` and `google.com` do; many others don't.
- **`analyze.py` local DNS** — the local resolver benchmarking section is commented out; edit `resolver.nameservers` with your actual local DNS IP to re-enable it.