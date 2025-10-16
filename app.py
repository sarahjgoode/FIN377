
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Company Dashboard", layout="wide")

# ===== Left NAV (as a fixed first column) =====
nav, main = st.columns([1, 4], gap="large")

with nav:
    st.header("🧭")
    ticker = st.text_input("Ticker", value="LMT")
    st.caption("Tip: Use same tickers as your CSV headers for plotting.")
    
    st.markdown("**Competitors**")
    # Users can type up to 3 competitors; these should match columns in the uploads
    c1 = st.text_input("Comp 1", value="NOC")
    c2 = st.text_input("Comp 2", value="RTX")
    c3 = st.text_input("Comp 3", value="GD")
    competitors = [t for t in [c1, c2, c3] if t.strip()]
    
    st.markdown("---")
    st.subheader("Ask a question")
    question = st.text_area("Ask about the charts or financials:", height=90, placeholder="e.g., What changes most if WACC rises by 100 bps?")
    if st.button("Ask"):
        response = (
            "Here's a quick checklist to answer that:\n"
            "• Check the **Financials → WACC** inputs to see sensitivity.\n"
            "• In **Stock**, look at indexed lines to compare relative performance.\n"
            "• If you uploaded headlines, correlate date spikes with events.\n"
            "• Consider running an event window around major dates (earnings, contract awards).\n"
        )
        st.info(response)

with main:
    # ===== Tabs on top =====
    tabs = st.tabs(["Financials", "Stock"])
    
    # Headlines area (center top)
    st.markdown("### Headlines")
    st.caption("Optional: upload a CSV with columns `date, headline`.")
    headlines_file = st.file_uploader("Headlines CSV (optional)", type=["csv"], key="hlu")
    if headlines_file is not None:
        h = pd.read_csv(headlines_file)
        if set(["date","headline"]).issubset(h.columns):
            h = h.sort_values("date", ascending=False).head(10)
            for _, row in h.iterrows():
                st.write(f"• **{row['date']}** — {row['headline']}")
        else:
            st.warning("Expected columns: date, headline")
    else:
        st.info("No headlines uploaded yet.")
    
    with tabs[0]:
        st.subheader("Financials")
        st.caption("Adjust inputs to compute WACC. You can also upload a metrics table to plot trends.")
        
        colA, colB, colC = st.columns(3)
        with colA:
            rf = st.number_input("Risk-free rate (%)", value=4.0, step=0.1)
            mrp = st.number_input("Market risk premium (%)", value=5.0, step=0.1)
            beta = st.number_input("Equity beta (β)", value=0.75, step=0.01)
        with colB:
            kd_pre = st.number_input("Pre-tax cost of debt (%)", value=4.5, step=0.1)
            tax = st.number_input("Tax rate (%)", value=21.0, step=0.1)
        with colC:
            wE = st.number_input("Equity weight (E/V, %)", value=75.0, step=0.1)
            wD = st.number_input("Debt weight (D/V, %)", value=25.0, step=0.1)
        
        # Normalize and compute
        total = max(wE + wD, 1e-6)
        E, D = wE/total, wD/total
        ke = rf + beta*mrp
        kd = kd_pre*(1 - tax/100.0)
        wacc = (E*ke + D*kd)/100.0
        
        st.metric("Cost of Equity (k_e)", f"{ke:.2f}%")
        st.metric("After-Tax Cost of Debt (k_d(1-T))", f"{kd:.2f}%")
        st.metric("WACC", f"{wacc*100:.2f}%")
        
        st.markdown("**Metrics (optional upload)**")
        metrics_file = st.file_uploader("CSV with columns like: Year, Revenue, EBITDA, EPS...", type=["csv"], key="met")
        if metrics_file is not None:
            m = pd.read_csv(metrics_file)
            st.dataframe(m, use_container_width=True)
            numeric_cols = m.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                ycol = st.selectbox("Plot a metric", options=numeric_cols, index=0)
                xcol = st.selectbox("X-axis", options=m.columns.tolist(), index=0)
                fig = plt.figure()
                plt.plot(m[xcol], m[ycol])
                plt.title(f"{ycol} over {xcol}")
                plt.xlabel(xcol); plt.ylabel(ycol)
                st.pyplot(fig)
        else:
            st.caption("Skip if you don't have this yet.")

    with tabs[1]:
        st.subheader("Stock")
        st.caption("Upload an indexed price table or returns we can index. Recommended format below.")
        
        st.markdown("**Option A: Indexed Prices CSV**")
        st.caption("Columns: date, and one column per ticker (e.g., LMT,NOC,RTX,GD). Values should already be indexed to 100 at start.")
        px_file = st.file_uploader("Indexed prices CSV", type=["csv"], key="px")
        
        st.markdown("**Option B: Daily Returns CSV**")
        st.caption("Columns: date, and one column per ticker (returns in decimal). We'll index them to 100 for you.")
        ret_file = st.file_uploader("Returns CSV", type=["csv"], key="rets")
        
        series_to_plot = [ticker] + [c for c in competitors if c != ticker]
        
        def plot_lines(df_indexed, cols):
            missing = [c for c in cols if c not in df_indexed.columns]
            if missing:
                st.warning(f"Missing columns in data: {missing}")
                return
            fig = plt.figure()
            for c in cols:
                plt.plot(df_indexed["date"], df_indexed[c], label=c)
            plt.legend()
            plt.title("Indexed Price (Start=100)")
            plt.xlabel("Date"); plt.ylabel("Index")
            st.pyplot(fig)
        
        if px_file is not None:
            px = pd.read_csv(px_file)
            if "date" in px.columns:
                px["date"] = pd.to_datetime(px["date"])
                px = px.sort_values("date")
                plot_lines(px, series_to_plot)
            else:
                st.error("Expected a 'date' column in indexed prices CSV.")
        elif ret_file is not None:
            r = pd.read_csv(ret_file)
            if "date" in r.columns:
                r["date"] = pd.to_datetime(r["date"])
                r = r.sort_values("date")
                cols = [c for c in series_to_plot if c in r.columns]
                if not cols:
                    st.error("No matching ticker columns found in returns file.")
                else:
                    base = pd.DataFrame({"date": r["date"].values})
                    for c in cols:
                        idx = (1 + r[c].fillna(0)).cumprod()*100
                        base[c] = idx
                    plot_lines(base, cols)
            else:
                st.error("Expected a 'date' column in returns CSV.")
        else:
            st.info("Upload either indexed prices or returns to see the multi-line chart.")
