import pandas as pd
import streamlit as st

from job_finder import fetch_jobs
from freelance_finder import fetch_gigs
from utils.eligibility import check_eligibility

st.set_page_config(page_title="AutoApply", page_icon="🚀", layout="wide")
st.title("🚀 AutoApply")
st.caption("AI-powered Job & Freelance Application Assistant")


@st.cache_data(ttl=1800, show_spinner=False)
def load_jobs(keyword, pages, remote_only, junior_only, yc_only):
    return fetch_jobs(keyword, pages, remote_only, junior_only, yc_only)


@st.cache_data(ttl=1800, show_spinner=False)
def load_gigs(keyword, pages):
    return fetch_gigs(keyword=keyword, pages=pages)


tab1, tab2 = st.tabs(["💼 Job Opportunities", "🧑‍💻 Freelancing Gigs"])

with tab1:
    st.header("Multi-Platform Job Discovery")
    keyword = st.text_input(
        "Search Jobs", placeholder="Python, Machine Learning, AI...", key="job_keyword"
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        remote_only = st.checkbox("Remote only (freehire)")
    with c2:
        junior_only = st.checkbox("Intern / Junior only (freehire)")
    with c3:
        yc_only = st.checkbox("YC startups only (freehire)")

    job_pages = st.slider("freehire pages (100 jobs/page)", 1, 10, 2)

    if st.button("Find Jobs", type="primary", key="find_jobs"):
        st.session_state["job_search_args"] = (
            keyword, job_pages, remote_only, junior_only, yc_only
        )

    if "job_search_args" in st.session_state:
        try:
            with st.spinner("Searching job sources..."):
                jobs, source_counts, errors = load_jobs(
                    *st.session_state["job_search_args"]
                )
        except Exception as error:
            st.error(f"Could not load job listings: {error}")
            jobs, source_counts, errors = [], {}, {}

        st.subheader("Discovery Summary (raw counts)")
        if source_counts:
            metric_columns = st.columns(min(4, len(source_counts)))
            for index, (source, count) in enumerate(source_counts.items()):
                metric_columns[index % len(metric_columns)].metric(source, count)

        st.caption(
            "Remote, junior and YC search filters currently apply only to freehire. "
            "Other sources use keyword matching."
        )

        if jobs:
            df = pd.DataFrame(jobs)

            if "eligibility" not in df.columns:
                df["eligibility"] = df.apply(
                    lambda row: check_eligibility(row.to_dict()), axis=1
                )
            else:
                missing = df["eligibility"].isna() | (
                    df["eligibility"].astype(str).str.strip() == ""
                )
                if missing.any():
                    df.loc[missing, "eligibility"] = df.loc[missing].apply(
                        lambda row: check_eligibility(row.to_dict()), axis=1
                    )

            available_sources = sorted(df["source"].dropna().unique().tolist())
            selected_sources = st.multiselect(
                "Filter by Platform",
                options=available_sources,
                default=available_sources,
                key="job_sources",
            )
            df = df[df["source"].isin(selected_sources)].copy()

            eligibility_options = ["Eligible", "Needs Review", "Ineligible"]
            selected_eligibility = st.multiselect(
                "Geographic Eligibility",
                options=eligibility_options,
                default=["Eligible", "Needs Review"],
                key="job_eligibility",
            )
            df = df[df["eligibility"].isin(selected_eligibility)].copy()

            st.success(f"Found {len(df)} matching opportunities!")
            st.caption(
                "Eligibility labels are preliminary, rule-based screening results. "
                "Review the original listing before applying."
            )

            display_columns = [
                "title", "company", "location", "eligibility",
                "category", "source", "url",
            ]
            st.dataframe(
                df.reindex(columns=display_columns),
                hide_index=True,
                use_container_width=True,
                column_config={"url": st.column_config.LinkColumn("View / Apply")},
            )
        else:
            st.warning("No matching jobs retrieved.")

        if errors:
            with st.expander("Platform Errors"):
                for source, error in errors.items():
                    st.error(f"{source}: {error}")

        if st.button("Refresh Job Data", key="refresh_jobs"):
            load_jobs.clear()
            st.rerun()

with tab2:
    st.header("Freelancing Opportunities")
    gig_keyword = st.text_input(
        "Search Freelance Projects",
        placeholder="Python, Machine Learning, AI...",
        key="gig_search",
    )
    gig_pages = st.slider("Pages to Search", 1, 10, 3, key="gig_pages")
    min_relevance = st.slider(
        "Minimum Relevance Score", 0, 100, 20, key="gig_min_relevance"
    )
    min_budget = st.number_input(
        "Minimum Project Budget (original currency)",
        min_value=0.0,
        value=0.0,
        step=50.0,
        key="gig_min_budget",
    )

    if st.button("Find Gigs", type="primary", key="find_gigs"):
        with st.spinner("Searching freelance platforms..."):
            try:
                gigs, source_counts, errors = load_gigs(gig_keyword, gig_pages)
                st.session_state["gigs"] = gigs
                st.session_state["gig_source_counts"] = source_counts
                st.session_state["gig_errors"] = errors
            except Exception as error:
                st.error(f"Error fetching gigs: {error}")
                st.session_state["gigs"] = []
                st.session_state["gig_source_counts"] = {}
                st.session_state["gig_errors"] = {}

    if "gigs" in st.session_state:
        st.subheader("Platform Discovery Summary")
        for source, count in st.session_state.get("gig_source_counts", {}).items():
            st.write(f"**{source}:** {count} projects")

        gig_errors = st.session_state.get("gig_errors", {})
        if gig_errors:
            with st.expander("Platform Errors", key="gig_errors_expander"):
                for source, error in gig_errors.items():
                    st.error(f"{source}: {error}")

        gigs = st.session_state["gigs"]
        if gigs:
            df_gigs = pd.DataFrame(gigs)
            df_gigs = df_gigs[
                df_gigs["relevance_score"] >= min_relevance
            ].copy()

            if min_budget > 0:
                df_gigs["budget_max"] = pd.to_numeric(
                    df_gigs["budget_max"], errors="coerce"
                )
                df_gigs = df_gigs[df_gigs["budget_max"] >= min_budget]

            st.success(f"Found {len(df_gigs)} matching freelance projects!")
            st.metric("Projects Retrieved Before Filtering", len(gigs))
            st.caption(
                "Budget amounts are in their original currencies; "
                "the numeric filter does not convert between currencies."
            )
            display_columns = [
                "title", "relevance_score", "matched_skills",
                "budget_min", "budget_max", "currency", "source", "url",
            ]
            st.dataframe(
                df_gigs.reindex(columns=display_columns),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "relevance_score": st.column_config.ProgressColumn(
                        "Relevance", min_value=0, max_value=100, format="%d"
                    ),
                    "url": st.column_config.LinkColumn("View Project"),
                },
            )
        else:
            st.warning("No freelance projects retrieved.")

    if st.button("Refresh Freelance Data", key="refresh_gigs"):
        load_gigs.clear()
        st.rerun()
