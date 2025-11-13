# components/theme.py
import streamlit as st

def inject_theme():
    st.markdown("""
    <style>
      :root{
        --bg1:#f6f8fc;
        --bg2:#f0f4ff;
        --ink:#0f172a;
        --muted:#64748b;
        --ring:#e5e7eb;
        --card:#ffffff;
        --shadow:0 8px 30px rgba(15, 23, 42, .06);
      }

      /* Background */
      html, body, .block-container{
        background:
          radial-gradient(1200px 600px at -10% -10%, rgba(99,102,241,.12), transparent 60%),
          radial-gradient(900px 500px at 120% -10%, rgba(34,197,94,.10), transparent 60%),
          radial-gradient(800px 500px at 50% 120%, rgba(59,130,246,.10), transparent 60%),
          linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%);
      }

      /* Layout */
      @media (min-width: 992px){ .block-container{ max-width:1180px; padding-top:.8rem; } }

      /* Typography */
      h1,h2,h3{ color:var(--ink); letter-spacing:-0.02em; }
      .muted{ color:var(--muted); }

      /* Cards & tiles */
      .card{ background:var(--card); border:1px solid var(--ring); border-radius:16px; padding:16px; box-shadow:var(--shadow); }
      .tile{ transition:transform .15s ease, box-shadow .15s ease; }
      .tile:hover{ transform:translateY(-3px); box-shadow:0 16px 40px rgba(15,23,42,.10); }

      /* Chips */
      .chip{
        display:inline-flex; gap:.5rem; padding:.4rem .7rem;
        border:1px solid var(--ring); border-radius:999px; font-size:.9rem;
        background:#fff8; backdrop-filter: blur(4px);
      }

      /* Glassy navbar (shrinks on scroll) */
      .navglass{
        position:sticky; top:0; z-index:999;
        background:rgba(255,255,255,.65);
        backdrop-filter:saturate(160%) blur(14px);
        border-bottom:1px solid rgba(148,163,184,.25);
        border-radius:16px;
        box-shadow:0 8px 20px rgba(0,0,0,.05);
        padding:12px 24px;
        transition:all .25s ease;
      }
      .logo-img{ height:42px; transition:height .25s ease, transform .25s ease; }

      /* When scrolled */
      body.scrolled .navglass{ padding:6px 20px; box-shadow:0 10px 30px rgba(0,0,0,.08); background:rgba(255,255,255,.7); }
      body.scrolled .logo-img{ height:34px; transform:translateY(-1px); }

      /* Hide default Streamlit header line */
      header[data-testid="stHeader"]{ height:0; visibility:hidden; }

      /* Divider */
      hr{ border:none; border-top:1px solid var(--ring); margin:8px 0 14px; }
    </style>
    <script>
      // Add/remove 'scrolled' class on body for shrink effect
      (function(){
        const onScroll = () => {
          if (window.scrollY > 10) document.body.classList.add('scrolled');
          else document.body.classList.remove('scrolled');
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
      })();
    </script>
    """, unsafe_allow_html=True)
