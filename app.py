import streamlit as st
from strength import analyze_charset, entropy_bits, estimate_charset_size
from zxcvbn import zxcvbn
import hashing_demo as hd
import pandas as pd
import math
import streamlit.components.v1 as components
import html
from datetime import datetime
from string import Template

st.set_page_config(page_title="Password Checker — Polished Demo", layout="wide")

#Inline CSS for polish
st.markdown(
    """
    <style>
    /* gradient animated header */
    .fancy-header {
        font-size:28px;
        font-weight:700;
        background: linear-gradient(90deg,#6a11cb,#2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow 3s ease-in-out infinite alternate;
    }
    @keyframes glow {
      from {filter: drop-shadow(0 0 4px rgba(97, 97, 255, 0.6));}
      to {filter: drop-shadow(0 0 12px rgba(37, 117, 252, 0.9));}
    }
    .card {
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    }
    .badge {
        display:inline-block;
        padding:6px 10px;
        border-radius:999px;
        font-weight:700;
        color:#fff;
        font-size:12px;
    }
    .badge-red { background:#e53935; }
    .badge-orangered { background:#ff6d00; }
    .badge-orange { background:#fb8c00; }
    .badge-yellowgreen { background:#9ccc65; color:#081014; }
    .badge-green { background:#2e7d32; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="fancy-header">🔐 Password Strength Checker — Polished Demo</div>', unsafe_allow_html=True)
st.write("**Warning:** Do not enter real production passwords. Use demo/test passwords only.")

# cracking simulation animations
def render_crack_animation(target_guesses=10_000_000, visual_speed=1e6, title="Simulated cracking (visual)"):
    """
    Renders an aircrack-ng-like visual animation inside Streamlit.
    Purely visual and simulated. No real cracking or network activity.
    Uses string.Template with escaped $ in JS pools to avoid placeholder issues.
    """
    tpl = Template(r"""
    <div style="font-family: monospace;">
      <div style="display:flex; align-items:center; gap:12px;">
         <div style="font-weight:700; color:#fff; background:linear-gradient(90deg,#6a11cb,#2575fc); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:18px;">$TITLE</div>
         <div id="sim-label" style="color:#aaa; font-size:12px;">visual target: $TARGET attempts</div>
      </div>
      <div id="matrix" style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; background:#061220; padding:12px; border-radius:8px; min-height:160px;">
      </div>

      <div style="margin-top:14px; display:flex; gap:12px; align-items:center;">
        <div style="background:#0b3a5c; color:#d1f0ff; padding:10px 14px; border-radius:8px; font-size:20px; font-weight:700;" id="candidate">0000:0000:0000:0000</div>
        <div style="color:#9fb8d9; font-size:14px;">Attempts/sec: <span id="rate">0</span></div>
        <div style="color:#9fb8d9; font-size:14px;">Progress: <span id="progress">0%</span></div>
      </div>
    </div>

    <script>
    (function() {{
      const target = $TARGET;
      const visualSpeed = $SPEED;
      const duration = 6000;
      const container = document.getElementById("matrix");
      const pools = [
        "0123456789abcdef", "abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "@#$$%^&*()-_=+[]{}<>?/\\\\|"
      ];

      function randFrom(s) {{ return s.charAt(Math.floor(Math.random()*s.length)); }}

      const cols = 28;
      const rows = 6;
      const nodes = [];
      for (let c=0;c<cols;c++) {{
        const col = document.createElement("div");
        col.style.display="flex";
        col.style.flexDirection="column";
        col.style.gap="6px";
        for (let r=0;r<rows;r++) {{
          const cell = document.createElement("div");
          cell.style.width = (24 + Math.random()*8) + "px";
          cell.style.color = "rgba(180,230,255,0.9)";
          cell.style.fontSize = (10 + Math.random()*6) + "px";
          cell.style.fontFamily = "monospace";
          cell.textContent = randFrom(pools[Math.floor(Math.random()*pools.length)]);
          col.appendChild(cell);
          nodes.push(cell);
        }}
        container.appendChild(col);
      }}

      const start = performance.now();
      function frame(now) {{
        const t = Math.min(1, (now - start) / duration);
        for (let i=0;i<nodes.length;i++) {{
          if (Math.random() < 0.2 + 0.7 * t) {{
            const pool = pools[Math.floor(Math.random()*pools.length)];
            nodes[i].textContent = randFrom(pool) + (Math.random() < 0.08 ? randFrom(pool).toUpperCase() : "");
            nodes[i].style.opacity = 0.4 + 0.6 * Math.random();
            nodes[i].style.transform = 'translateY(' + (Math.random()*6 - 3) + 'px) rotate(' + (Math.random()*6 - 3) + 'deg)';
          }}
        }}
        const cand = [];
        const parts = 6;
        for (let p=0;p<parts;p++) {{
          let part = '';
          const len = 4;
          for (let i=0;i<len;i++) part += randFrom("0123456789abcdef");
          cand.push(part);
        }}
        document.getElementById("candidate").textContent = cand.join(":");
        const rate = Math.floor(visualSpeed * (0.2 + 0.8 * t));
        document.getElementById("rate").textContent = rate.toLocaleString();
        const frac = Math.pow(t, 0.7);
        document.getElementById("progress").textContent = Math.floor(frac * 100) + "%";
        if (t < 1) requestAnimationFrame(frame);
        else {{
          container.style.boxShadow = "0 10px 40px rgba(40,200,120,0.12)";
          document.getElementById("progress").textContent = "100%";
        }}
      }}
      requestAnimationFrame(frame);
    }})();
    </script>
    """)
    # substitute placeholders (TITLE, TARGET, SPEED)
    filled = tpl.substitute(TITLE=html.escape(str(title)), TARGET=int(target_guesses), SPEED=float(visual_speed))
    components.html(filled, height=380, scrolling=True)


# HTML report
def make_html_report(password_display, counts, ent_bits, zx, scenario_rows, notes=None):
    """Return an HTML string containing a styled, layman-friendly, detailed report."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    pw_safe = html.escape(password_display) if password_display else "(empty)"
    body_rows = ""
    for r in scenario_rows:
        body_rows += f"<tr><td>{html.escape(r['Scenario'])}</td><td>{html.escape(r['Naive'])}</td><td>{html.escape(r['zxcvbn'])}</td></tr>"
    zscore = zx.get("score") if zx else "n/a"
    zguesses = f"{zx.get('guesses'):,}" if zx and zx.get("guesses") else "n/a"

    # suggestions in report
    suggestions_html = ""
    if zx:
        f = zx.get("feedback", {})
        if f.get("warning"):
            suggestions_html += f"<p><strong>Warning:</strong> {html.escape(f.get('warning'))}</p>"
        if f.get("suggestions"):
            suggestions_html += "<ul>"
            for s in f.get("suggestions", []):
                suggestions_html += f"<li>{html.escape(s)}</li>"
            suggestions_html += "</ul>"

    # reccomend passphrase
    passphrase_example = "e.g. 'planet correct mango bicycle' — four random words is a strong passphrase."

    notes_html = f"<p>{html.escape(notes)}</p>" if notes else ""

    html_report = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Password Strength Report</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial; padding:24px; color:#0b2b3a; background:#f6f9fb; }}
        .header {{ background:linear-gradient(90deg,#6a11cb,#2575fc); color:#fff; padding:14px; border-radius:8px; }}
        .card {{ border-radius:8px; padding:12px; margin-top:14px; box-shadow:0 6px 20px rgba(12,34,48,0.06); background:#fff; }}
        h1,h2 {{ margin:6px 0 10px 0; }}
        table {{ width:100%; border-collapse:collapse; margin-top:8px; }}
        th, td {{ padding:8px 10px; text-align:left; border-bottom:1px solid #eee; }}
        .muted {{ color:#627781; font-size:13px; }}
        .kpi {{ font-weight:700; font-size:18px; }}
        .ok {{ color: #2e7d32; font-weight:700; }}
        .warn {{ color: #e65100; font-weight:700; }}
        .danger {{ color: #b71c1c; font-weight:700; }}
        ul {{ margin-left: 18px; }}
      </style>
    </head>
    <body>
      <div class="header">
        <h1>Password Strength Report</h1>
        <div class="muted">Generated: {now}</div>
      </div>

      <div class="card">
        <h2>Quick summary</h2>
        <p><strong>Test password:</strong> {pw_safe}</p>
        <p><strong>Length:</strong> {counts['length']} &nbsp; • &nbsp; <strong>Entropy:</strong> {ent_bits:.2f} bits &nbsp; • &nbsp; <strong>zxcvbn:</strong> {zscore} (guesses: {zguesses})</p>
        <p class="muted">Interpretation: Entropy gives a mathematical lower bound on randomness. zxcvbn models human patterns — treat both together for a balanced view.</p>
      </div>

      <div class="card">
        <h2>What the numbers mean (for non-technical readers)</h2>
        <ul>
          <li><strong>Entropy (bits)</strong>: Think of bits like 'steps' an attacker must guess; more bits = exponentially harder.</li>
          <li><strong>zxcvbn guesses</strong>: A practical estimate of how many attempts a realistic attacker might need, considering common words and patterns.</li>
          <li><strong>Online vs Offline attacks</strong>: Online = trying to log into a site (often rate-limited). Offline = attacker has password hashes and can try guesses extremely fast. The reported times compare both.</li>
        </ul>
      </div>

      <div class="card">
        <h2>Crack time comparison</h2>
        <table>
          <thead><tr><th>Scenario</th><th>Naive crack time</th><th>zxcvbn crack time</th></tr></thead>
          <tbody>
            {body_rows}
          </tbody>
        </table>
      </div>

      <div class="card">
        <h2>Actionable recommendations</h2>
        <ul>
          <li><strong>For most users:</strong> Use a 4-word random passphrase (or a password manager that generates random strings). Example: {html.escape(passphrase_example)}</li>
          <li><strong>For admins:</strong> Always store passwords with Argon2 (memory-hard) and tune cost parameters.</li>
          <li><strong>Quick fixes:</strong> increase length, avoid common words or predictable substitutions (e.g., 'P@ssw0rd' is weak), and avoid reusing passwords across sites.</li>
        </ul>
      </div>

      <div class="card">
        <h2>Detailed feedback from the automated analysis</h2>
        {('<div>' + suggestions_html + '</div>') if suggestions_html else '<p>No automated suggestions found by the pattern-aware analyzer. That typically means the password was not obviously made of dictionary words or simple patterns.</p>'}
        {notes_html}
      </div>

      <div class="card">
        <h2>Checklist (share this)</h2>
        <ul>
          <li>Length &gt;= 12 (better 16+) — check</li>
          <li>Unique for each account — check</li>
          <li>Stored with Argon2 on servers — ask the provider</li>
        </ul>
      </div>

      <div style="margin-top:14px; font-size:12px; color:#8aa0ad;">Technical note: This is an educational report combining naive entropy math and a pattern-aware library (zxcvbn). Real-world attacker capabilities vary. Use the recommendations to improve real-world resilience.</div>
    </body>
    </html>
    """
    return html_report


# UI
left, right = st.columns([1, 2])

with left:
    st.header("Input & Controls")
    pw = st.text_input("Enter password", type="password", key="pw_input")
    show_pw = st.checkbox("Show password")
    if show_pw:
        st.write("Visible:", pw)

    st.markdown("### Attacker scenarios")
    selected_presets = st.multiselect("Pick attacker scenarios to show", list(hd.OFFLINE_HASH_SPECS.keys()), default=[
        "Raw fast hash (MD5/SHA1) - single GPU",
        "bcrypt (cost=12) - single CPU core",
        "argon2 (moderate) - single machine"
    ])

    st.markdown("### Storage hash modeling")
    hash_choice = st.selectbox("Storage hash (affects offline speed)", [
        "No storage / online attempts (use the online throttle below)",
        "Raw fast hash (MD5/SHA1)",
        "SHA256 (fast)",
        "bcrypt",
        "argon2"
    ])

    bcrypt_rounds = st.slider("bcrypt rounds (cost)", min_value=4, max_value=16, value=12)
    argon2_time = st.slider("Argon2 time_cost (higher -> slower)", min_value=1, max_value=6, value=2)
    argon2_mem_mb = st.slider("Argon2 memory (MB)", min_value=8, max_value=512, value=128)

    st.markdown("### Online throttling (for online attack scenario)")
    online_speed = st.number_input("Attempts per second (online throttled)", min_value=1.0, value=10.0, step=1.0)

    st.markdown("### Actions")
    simulate = st.button("Simulate cracking (animated)")
    download_report = st.button("Prepare & show fancy HTML report (download below)")

with right:
    st.header("Analysis")
    if not pw:
        st.info("Type a password on the left to analyze. Demo examples: `password123`, `Tr0ub4dor&3`, `correct horse battery staple`, random 16-char string.")
        rows = []  
        zx = None
    else:
        # naive entropy and analyze inputed password
        counts = analyze_charset(pw)
        S = estimate_charset_size(counts)
        ent_bits = entropy_bits(pw)

        col1, col2, col3 = st.columns(3)
        col1.metric("Length", counts["length"])
        col2.metric("Charset (est.)", S)
        col3.metric("Entropy (bits)", f"{ent_bits:.2f}")

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(f"**Classes:** lower={counts['has_lower']} upper={counts['has_upper']} digits={counts['has_digit']} symbols={counts['has_symbol']} space={counts['has_space']}")
        st.markdown("</div>", unsafe_allow_html=True)

        # zxcvbn analysis
        st.subheader("Pattern-aware analysis (zxcvbn)")
        try:
            zx = zxcvbn(pw)
        except Exception as e:
            zx = None
            st.error(f"zxcvbn error: {e}")

        if zx:
            score = zx.get("score", 0)
            guesses = zx.get("guesses", 0)
            guesses_log10 = zx.get("guesses_log10", 0.0)
            feedback = zx.get("feedback", {})
            score_map = {0: "badge-red", 1: "badge-orangered", 2: "badge-orange", 3: "badge-yellowgreen", 4: "badge-green"}
            label_map = {0: "Very weak", 1:"Weak", 2:"Fair", 3:"Good", 4:"Excellent"}
            badge_html = f"<span class='badge {score_map.get(score)}'>{score} — {label_map.get(score)}</span>"
            st.markdown(badge_html, unsafe_allow_html=True)
            st.write(f"- zxcvbn estimated guesses: **{guesses:,}** (log10 ≈ {guesses_log10:.2f})")
            with st.expander("zxcvbn feedback & suggestions"):
                warning = feedback.get("warning", "")
                suggestions = feedback.get("suggestions", [])
                if warning:
                    st.warning(warning)
                for s in suggestions:
                    st.write(f"- {s}")
                if not warning and not suggestions:
                    st.write("- No additional suggestions from zxcvbn.")
        else:
            st.write("zxcvbn unavailable — only naive entropy shown.")
            guesses = None

        # Scenario simulation
        scenarios = []
        scenarios.append(("Online (throttled)", float(online_speed)))
        for k in selected_presets:
            spec = hd.OFFLINE_HASH_SPECS.get(k)
            if spec:
                scenarios.append((k, spec["speed"]))
        if hash_choice == "bcrypt":
            b_speed = hd.get_hash_speed("bcrypt (cost=12) - single CPU core", bcrypt_rounds, argon2_time, argon2_mem_mb*1024)
            scenarios.append((f"Offline (bcrypt cost={bcrypt_rounds})", b_speed))
        elif hash_choice == "argon2":
            a_speed = hd.get_hash_speed("argon2 (moderate) - single machine", bcrypt_rounds, argon2_time, argon2_mem_mb*1024)
            scenarios.append((f"Offline (argon2 t={argon2_time}, mem={argon2_mem_mb}MB)", a_speed))
        elif hash_choice == "Raw fast hash (MD5/SHA1)":
            scenarios.append(("Offline (raw fast hash - single GPU)", hd.get_hash_speed("Raw fast hash (MD5/SHA1) - single GPU")))
        elif hash_choice == "SHA256 (fast)":
            scenarios.append(("Offline (SHA256 - single GPU)", hd.get_hash_speed("SHA256 (fast) - single GPU")))

        # table for crack time
        rows = []
        for (label, speed) in scenarios:
            log10_naive_guesses = ent_bits * math.log10(2)
            log10_naive_seconds = log10_naive_guesses - math.log10(speed) if speed > 0 else float("inf")
            naive_seconds = 10 ** log10_naive_seconds if log10_naive_seconds < 300 else float("inf")
            naive_h = hd.format_seconds(naive_seconds)
            if guesses and guesses > 0:
                z_seconds = guesses / float(speed)
                z_h = hd.format_seconds(z_seconds)
            else:
                z_h = "n/a"
            rows.append({"Scenario": label, "Naive": naive_h, "zxcvbn": z_h})
        df = pd.DataFrame(rows).set_index("Scenario")
        st.subheader("Crack time comparison (human-friendly)")
        st.table(df)

        # log 10 times chart
        st.subheader("Visual: log10(seconds) (smaller -> easier for attacker)")
        chart_data = []
        for (label, speed) in scenarios:
            log10_naive = (ent_bits * math.log10(2)) - math.log10(speed) if speed > 0 else float("nan")
            log10_z = None
            if guesses and guesses > 0:
                log10_z = math.log10(max(1.0, guesses)) - math.log10(speed)
            chart_data.append({"scenario": label, "naive_log10_seconds": float(log10_naive) if math.isfinite(log10_naive) else None, "zxcvbn_log10_seconds": float(log10_z) if log10_z is not None and math.isfinite(log10_z) else None})
        chart_df = pd.DataFrame(chart_data).set_index("scenario").fillna(float("nan"))
        st.bar_chart(chart_df)

        # hash demo
        st.subheader("Hash demo (example outputs)")
        try:
            st.text("MD5: " + hd.hash_md5(pw))
            st.text("SHA256: " + hd.hash_sha256(pw))
            if hd.bcrypt:
                try:
                    b = hd.hash_bcrypt(pw, bcrypt_rounds)
                    st.text("bcrypt (truncated): " + b[:60] + " ...")
                except Exception as e:
                    st.write("bcrypt example failed:", e)
            else:
                st.write("bcrypt: not available in this environment.")
            if hd.ARGON2_AVAILABLE:
                try:
                    a = hd.hash_argon2(pw, time_cost=argon2_time, memory_cost_kb=argon2_mem_mb*1024)
                    st.text("argon2 (truncated): " + a[:60] + " ...")
                except Exception as e:
                    st.write("argon2 example failed:", e)
            else:
                st.write("argon2: not available in this environment.")
        except Exception as e:
            st.write("Hash demo error:", e)

        # simulate cracking
        if simulate:
            st.subheader("Simulation (aircrack-ng style visual)")
            sim_label, sim_speed = scenarios[0] if scenarios else ("Online (throttled)", float(online_speed))
            if guesses and guesses > 0:
                sim_total_guesses = guesses if guesses <= 10**9 else 10**8
                visual_speed = min(1e12, sim_speed)
            else:
                sim_total_guesses = int(min(10**8, 2 ** ent_bits)) if ent_bits <= 60 else 10**8
                visual_speed = sim_speed if sim_speed > 0 else 1e6

            est_seconds = (sim_total_guesses / sim_speed) if sim_speed > 0 else float("inf")
            st.write(f"Simulating: **{sim_label}**  — attacker speed ≈ **{sim_speed:.2e} guesses/sec** (visual only).")
            st.write(f"Using visual target: **{sim_total_guesses:,}** (capped for demo). Real-world estimated time: **{hd.format_seconds(est_seconds)}**")
            render_crack_animation(target_guesses=sim_total_guesses, visual_speed=visual_speed, title=f"Simulated cracking — {sim_label}")
            st.success("Simulation complete (visual). The animation compresses the real-world time to a short demonstration.")

        # report export
        if download_report:
            html_report = make_html_report(pw, counts, ent_bits, zx if 'zx' in locals() else None, rows,
                                           notes="Generated by local demo. Do not share real passwords.")
            st.markdown("### Report preview")
            st.components.v1.html(html_report, height=420, scrolling=True)
            st.download_button("Download fancy HTML report", html_report, file_name="password_report.html", mime="text/html")
            
