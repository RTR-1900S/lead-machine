import os
import streamlit as st
import pandas as pd
from scraper_runner import run_scraper
from lead_scorer import score_leads, get_latest_leads_file
from pathlib import Path

# ============== PAGE CONFIGURATION ==============
st.set_page_config(
    page_title="Lead Machine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== CUSTOM STYLING ==============
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 2rem;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
    }
    .header-logo {
        font-size: 4rem;
        font-weight: bold;
    }
    .header-text h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .header-text p {
        margin: 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    .metric-box {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    .success-box {
        background: #d4edda;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        color: #155724;
    }
    .error-box {
        background: #f8d7da;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        color: #721c24;
    }
    .lead-preview {
        background: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# ============== HELPER FUNCTIONS ==============
def get_leads_files():
    """Get all leads files (raw and scored)"""
    output_dir = "output"
    if not os.path.exists(output_dir):
        return []
    files = [f for f in os.listdir(output_dir) if f.startswith("leads_") and f.endswith(".csv")]
    return sorted(files, reverse=True)

def get_latest_raw_leads():
    """Get the most recent unscored leads file"""
    files = get_leads_files()
    for f in files:
        if "scored" not in f:
            return os.path.join("output", f)
    return None

def get_latest_scored_leads():
    """Get the most recent scored leads file"""
    files = get_leads_files()
    for f in files:
        if "scored" in f:
            return os.path.join("output", f)
    return None

def calculate_stats(df):
    """Calculate stats from leads dataframe"""
    stats = {
        "total_leads": len(df),
        "avg_score": df.get("lead_score", pd.Series()).mean() if "lead_score" in df.columns else 0,
        "high_quality": len(df[df["lead_score"] >= 7]) if "lead_score" in df.columns else 0,
        "categories": df["category"].nunique() if "category" in df.columns else 0,
    }
    return stats

# ============== HEADER ==============
col_logo, col_text = st.columns([1, 4])

with col_logo:
    # Try to display the custom logo, fallback to emoji
    try:
        logo_path = os.path.join("logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=120)
        else:
            st.markdown('<div style="font-size: 5rem; text-align: center;">🎯</div>', unsafe_allow_html=True)
    except Exception:
        st.markdown('<div style="font-size: 5rem; text-align: center;">🎯</div>', unsafe_allow_html=True)

with col_text:
    st.markdown("""
    <div style="padding-top: 20px;">
        <h1 style="margin: 0; color: #667eea;">Lead Machine</h1>
        <p style="margin: 0; font-size: 1.1rem; color: #666;">Find and score local business leads for social media services</p>
    </div>
    """, unsafe_allow_html=True)

# Create output directory
os.makedirs("output", exist_ok=True)

# ============== QUICK START GUIDE ==============
with st.expander("📖 How to Use (Click to Expand)", expanded=False):
    st.markdown("""
    ### 🚀 Quick Start Guide

    **Step 1: Search for Leads** 🔍
    - Go to the "Search" tab
    - Click a business type (e.g., 🍽️ Restaurants) OR type your own
    - Enter the city (e.g., "Orlando FL")
    - Click "🚀 Run Search"
    - ✅ Results appear instantly

    **Step 2: Filter for Top Payers** 💰
    - In the Search tab, select **"🏆 Top Paying"** (default)
    - This shows only established businesses (4.5+ rating, 50+ reviews)
    - These are the ones with MONEY and ready to buy

    **Step 3: Score Leads with AI** ⭐
    - Go to the "Score Leads" tab
    - Click "⭐ Start Scoring"
    - Watch the progress bar fill up
    - AI analyzes each lead and scores 1-10
    - 🟢 Green (7+) = Great prospects
    - 🟠 Orange (5-6) = Good prospects
    - 🔴 Red (<5) = Lower priority

    **Step 4: Download & Use Results** 📥
    - Download as **Excel** (formatted, color-coded, ready to share)
    - Or download as **CSV** (for spreadsheets)
    - All files automatically saved with date/time stamps

    **💡 Pro Tips:**
    - Click "🏆 Top Paying" to focus on serious businesses with budgets
    - Use the "Dashboard" tab to see all your previous searches
    - Excel downloads are professionally formatted (perfect for showing clients)
    - You can always download "All" results if you want to see everything
    """)

# ============== TABS ==============
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔍 Search", "⭐ Score Leads"])

# ============== TAB 1: DASHBOARD ==============
with tab1:
    st.header("Dashboard")

    # Get available data
    latest_raw = get_latest_raw_leads()
    latest_scored = get_latest_scored_leads()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if latest_raw:
            df_raw = pd.read_csv(latest_raw)
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{len(df_raw)}</div>
                    <div class="metric-label">Total Leads</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="metric-box">
                    <div class="metric-value">0</div>
                    <div class="metric-label">Total Leads</div>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        if latest_scored:
            df_scored = pd.read_csv(latest_scored)
            avg_score = pd.to_numeric(df_scored["lead_score"], errors="coerce").mean() if "lead_score" in df_scored.columns else 0
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{avg_score:.1f}</div>
                    <div class="metric-label">Average Score</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="metric-box">
                    <div class="metric-value">-</div>
                    <div class="metric-label">Average Score</div>
                </div>
            """, unsafe_allow_html=True)

    with col3:
        if latest_scored:
            high_quality = len(df_scored[pd.to_numeric(df_scored["lead_score"], errors="coerce").fillna(0) >= 7])
            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{high_quality}</div>
                    <div class="metric-label">High Quality (7+)</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="metric-box">
                    <div class="metric-value">0</div>
                    <div class="metric-label">High Quality (7+)</div>
                </div>
            """, unsafe_allow_html=True)

    with col4:
        if latest_raw:
            categories = df_raw["category"].nunique() if "category" in df_raw.columns else 0

            st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{categories}</div>
                    <div class="metric-label">Categories</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="metric-box">
                    <div class="metric-value">0</div>
                    <div class="metric-label">Categories</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Display recent files
    st.subheader("Recent Searches")
    files = get_leads_files()
    if files:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Raw Leads Files**")
            raw_files = [f for f in files if "scored" not in f]
            if raw_files:
                for f in raw_files[:5]:
                    st.caption(f"📄 {f}")
            else:
                st.caption("No raw leads yet")

        with col2:
            st.markdown("**Scored Leads Files**")
            scored_files = [f for f in files if "scored" in f]
            if scored_files:
                for f in scored_files[:5]:
                    st.caption(f"📊 {f}")
            else:
                st.caption("No scored leads yet")
    else:
        st.info("No searches yet. Start by searching for leads in the 'Search' tab.")

# ============== TAB 2: SEARCH ==============
with tab2:
    st.header("Search for Leads")

    # Define popular business types that benefit from social media
    business_suggestions = [
        {"emoji": "🍽️", "name": "Restaurants & Cafes", "keyword": "restaurant"},
        {"emoji": "💇", "name": "Hair & Beauty Salons", "keyword": "salon"},
        {"emoji": "🦷", "name": "Dental Offices", "keyword": "dentist"},
        {"emoji": "🏋️", "name": "Fitness & Gyms", "keyword": "gym"},
        {"emoji": "🏠", "name": "Real Estate Agents", "keyword": "real estate"},
        {"emoji": "💅", "name": "Nail Salons", "keyword": "nail salon"},
        {"emoji": "🐾", "name": "Pet Grooming", "keyword": "pet grooming"},
        {"emoji": "🏥", "name": "Chiropractors", "keyword": "chiropractor"},
        {"emoji": "📸", "name": "Photography Studios", "keyword": "photography"},
        {"emoji": "🌳", "name": "Landscaping Services", "keyword": "landscaping"},
        {"emoji": "🔧", "name": "HVAC & Plumbing", "keyword": "plumbing"},
        {"emoji": "👗", "name": "Boutiques & Fashion", "keyword": "boutique"},
    ]

    # AI-Suggested Business Types (shown first for visibility)
    st.subheader("💡 Popular Businesses That Need Social Media Help")
    st.caption("Click any to instantly search for that business type")

    # Create a grid of suggestion buttons
    cols = st.columns(4)

    for idx, business in enumerate(business_suggestions):
        col = cols[idx % 4]
        with col:
            if st.button(
                f"{business['emoji']}\n{business['name']}",
                key=f"biz_{idx}",
                use_container_width=True,
                help=f"Search for {business['name']}"
            ):
                st.session_state.selected_keyword = business['keyword']

    st.markdown("---")

    # Prospect Quality Filter
    st.subheader("🤑 Focus on High-Value Prospects")

    col_filter1, col_filter2 = st.columns(2)

    with col_filter1:
        prospect_quality = st.radio(
            "Target prospect quality:",
            options=["top_paying", "established", "all"],
            index=0,
            horizontal=False,
            format_func=lambda x: {
                "top_paying": "🏆 Top Paying (4.5+ rating, 50+ reviews)",
                "established": "💰 Established (4.0+ rating, 20+ reviews)",
                "all": "📈 All Businesses",
            }[x],
            help="Filter by business maturity and revenue potential"
        )

    with col_filter2:
        st.info(
            """
            **What this means:**
            - **Top Paying**: Established businesses with proven customer base (higher budget)
            - **Established**: Serious businesses with customers (good budget)
            - **All**: Everyone, including startups (smaller budgets)
            """
        )

    st.markdown("---")
    st.subheader("Or Enter Your Own")

    # Input section
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        # Use session state to persist the selected keyword
        default_keyword = st.session_state.get('selected_keyword', '')
        keyword = st.text_input(
            "Search keyword",
            value=default_keyword,
            placeholder="e.g., restaurant, salon, dental office",
            help="Type of business to search for"
        )
        # Update session state if user types
        if keyword:
            st.session_state.selected_keyword = keyword

    with col2:
        city = st.text_input(
            "City",
            placeholder="e.g., Orlando FL or New York NY",
            help="City and state to search in"
        )

    with col3:
        max_results = st.number_input(
            "Max results",
            min_value=1,
            max_value=500,
            value=20,
            help="Number of results to scrape"
        )

    # Search button
    if st.button("🚀 Run Search", key="search_button", use_container_width=True):
        if not keyword or not city:
            st.error("❌ Please enter both keyword and city")
        else:
            with st.spinner("🔄 Scraping Google Maps... This may take a minute..."):
                result = run_scraper(keyword, city, max_results)

            if result["success"]:
                st.markdown(f"""
                    <div class="success-box">
                    ✅ <b>Found {result['count']} leads!</b> Saved as: <code>{result['filename']}</code>
                    </div>
                """, unsafe_allow_html=True)

                # Load and display results
                leads_file = os.path.join("output", result['filename'])
                if os.path.exists(leads_file):
                    df = pd.read_csv(leads_file)

                    # Apply prospect quality filter
                    df_filtered = df.copy()
                    filter_label = ""

                    rating_col = "review_rating" if "review_rating" in df_filtered.columns else "rating"
                    if prospect_quality == "top_paying":
                        # High-value prospects: 4.5+ rating and 50+ reviews
                        df_filtered = df_filtered[
                            (pd.to_numeric(df_filtered[rating_col], errors="coerce").fillna(0) >= 4.5) &
                            (pd.to_numeric(df_filtered["review_count"], errors="coerce").fillna(0) >= 50)
                        ]
                        filter_label = "🏆 Top Paying (4.5+ rating, 50+ reviews)"
                    elif prospect_quality == "established":
                        # Established: 4.0+ rating and 20+ reviews
                        df_filtered = df_filtered[
                            (pd.to_numeric(df_filtered[rating_col], errors="coerce").fillna(0) >= 4.0) &
                            (pd.to_numeric(df_filtered["review_count"], errors="coerce").fillna(0) >= 20)
                        ]
                        filter_label = "💰 Established (4.0+ rating, 20+ reviews)"

                    # Show filter info if applied
                    if filter_label:
                        st.info(f"📊 Showing {filter_label}")

                    # Display summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Qualified Leads", len(df_filtered))
                    with col2:
                        if "category" in df_filtered.columns:
                            st.metric("Categories", df_filtered["category"].nunique())
                    with col3:
                        rating_col = "review_rating" if "review_rating" in df_filtered.columns else "rating"
                        if rating_col in df_filtered.columns and len(df_filtered) > 0:
                            avg_rating = pd.to_numeric(df_filtered[rating_col], errors="coerce").mean()
                            st.metric("Avg Rating", f"{avg_rating:.1f}⭐")

                    # Display full table (filtered or all)
                    st.subheader(f"Lead Results ({len(df_filtered)} qualified)")

                    if len(df_filtered) > 0:
                        st.dataframe(df_filtered, use_container_width=True, height=400)

                        # Download options
                        st.markdown("---")
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            csv_data = df_filtered.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Filtered CSV",
                                data=csv_data,
                                file_name=result['filename'].replace(".csv", "_filtered.csv"),
                                mime="text/csv",
                                key="download_filtered_csv"
                            )

                        with col2:
                            # Option to download all (unfiltered)
                            if prospect_quality != "all":
                                csv_all = df.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download All (Unfiltered)",
                                    data=csv_all,
                                    file_name=result['filename'],
                                    mime="text/csv",
                                    key="download_all_csv"
                                )

                        with col2 if prospect_quality == "all" else col3:
                            st.info("💡 Next: Go to the 'Score Leads' tab to analyze these leads with AI")
                    else:
                        st.warning(
                            f"❌ No leads match the '{filter_label}' criteria.\n\n"
                            "Try:\n"
                            "- Lowering the quality filter (select 'All Businesses')\n"
                            "- Searching a different city\n"
                            "- Searching a different business type"
                        )

                        # Show statistics from all leads
                        if len(df) > 0:
                            st.info(f"📊 **All {len(df)} leads found (before filter):**")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                r_col = "review_rating" if "review_rating" in df.columns else "rating"
                                max_rating = pd.to_numeric(df[r_col], errors="coerce").max() if r_col in df.columns else 0
                                st.metric("Max Rating", f"{max_rating:.1f}⭐")
                            with col2:
                                max_reviews = pd.to_numeric(df["review_count"], errors="coerce").max() if "review_count" in df.columns else 0
                                st.metric("Max Reviews", int(max_reviews))
                            with col3:
                                avg_rating = pd.to_numeric(df[r_col], errors="coerce").mean() if r_col in df.columns else 0
                                st.metric("Avg Rating", f"{avg_rating:.1f}⭐")
                            with col4:
                                avg_reviews = df["review_count"].mean() if "review_count" in df.columns else 0
                                st.metric("Avg Reviews", int(avg_reviews))

            else:
                st.markdown(f"""
                    <div class="error-box">
                    ❌ <b>Search failed</b><br>
                    {result['error']}
                    </div>
                """, unsafe_allow_html=True)

    # Show existing leads
    st.markdown("---")
    st.subheader("Existing Searches")

    latest_raw = get_latest_raw_leads()
    if latest_raw:
        with st.expander("📂 View latest raw leads"):
            df_existing = pd.read_csv(latest_raw)
            st.caption(f"File: {os.path.basename(latest_raw)}")
            st.dataframe(df_existing, use_container_width=True)

            # Filtering and deletion UI
            st.markdown("**Lead Management**")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🗑️ Clear Low-Quality Leads", key="filter_low"):
                    # Remove leads with rating < 4
                    r_col = "review_rating" if "review_rating" in df_existing.columns else "rating"
                    if r_col in df_existing.columns:
                        filtered_df = df_existing[pd.to_numeric(df_existing[r_col], errors="coerce").fillna(0) >= 4.0]
                        removed = len(df_existing) - len(filtered_df)
                        st.success(f"Removed {removed} leads with rating < 4.0")
                        # Save filtered version
                        filtered_file = os.path.join("output", f"leads_filtered_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M')}.csv")
                        filtered_df.to_csv(filtered_file, index=False)
                        st.info(f"Filtered leads saved to: {os.path.basename(filtered_file)}")

            with col2:
                if st.button("📊 Score These Leads Now", key="score_from_tab2"):
                    st.session_state.proceed_to_scoring = True
    else:
        st.info("No leads yet. Run a search above to get started.")

# ============== TAB 3: SCORE LEADS ==============
with tab3:
    st.header("Score Leads with Gemini AI")

    latest_raw = get_latest_raw_leads()

    if not latest_raw:
        st.warning("⚠️ No leads found. Run a search first in the 'Search' tab.")
    else:
        # Load leads
        df_leads = pd.read_csv(latest_raw)

        # Show preview
        st.subheader(f"📋 Preview ({len(df_leads)} leads)")

        preview_cols = [col for col in ["title", "name", "category", "review_rating", "rating", "review_count", "emails", "website"] if col in df_leads.columns]
        if preview_cols:
            st.dataframe(df_leads[preview_cols].head(10), use_container_width=True)
        else:
            st.dataframe(df_leads.head(10), use_container_width=True)

        st.markdown("---")

        # Scoring options
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Ready to Score?")
        with col2:
            if st.button("⭐ Start Scoring", key="score_button", use_container_width=True):
                st.session_state.start_scoring = True

        # Execute scoring if button pressed
        if st.session_state.get("start_scoring", False):
            st.session_state.start_scoring = False

            try:
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(current, total):
                    progress_bar.progress(min(current / total, 1.0))
                    status_text.text(f"Scoring lead {current} of {total}...")

                with st.spinner("🤖 Scoring leads with Gemini AI..."):
                    df_scored = score_leads(input_file=latest_raw, progress_callback=update_progress)

                progress_bar.progress(1.0)
                status_text.text("✅ Scoring complete!")

                st.markdown("""
                    <div class="success-box">
                    ✅ <b>Scoring complete!</b> All leads have been analyzed with AI.
                    </div>
                """, unsafe_allow_html=True)

                # Display statistics
                st.subheader("Scoring Statistics")
                col1, col2, col3, col4 = st.columns(4)

                scores = pd.to_numeric(df_scored["lead_score"], errors="coerce").fillna(0)
                with col1:
                    st.metric("Average Score", f"{scores.mean():.1f}")

                with col2:
                    st.metric("High Quality (7+)", int((scores >= 7).sum()))

                with col3:
                    st.metric("Medium Quality (5-6)", int(((scores >= 5) & (scores < 7)).sum()))

                with col4:
                    st.metric("Low Quality (<5)", int((scores < 5).sum()))

                # Display results
                st.markdown("---")
                st.subheader("🎯 Scored Leads")

                # Sorting and filtering
                col1, col2 = st.columns(2)
                with col1:
                    sort_by = st.selectbox("Sort by:", ["Score (High to Low)", "Score (Low to High)", "Name", "Category"])
                with col2:
                    min_score_filter = st.slider("Minimum Score:", 0, 10, 0)

                # Apply filters and sorting
                df_scored["_score_num"] = pd.to_numeric(df_scored["lead_score"], errors="coerce").fillna(0)
                df_filtered = df_scored[df_scored["_score_num"] >= min_score_filter].copy()

                name_col = "title" if "title" in df_filtered.columns else "name"
                if sort_by == "Score (High to Low)":
                    df_filtered = df_filtered.sort_values("_score_num", ascending=False)
                elif sort_by == "Score (Low to High)":
                    df_filtered = df_filtered.sort_values("_score_num", ascending=True)
                elif sort_by == "Name":
                    df_filtered = df_filtered.sort_values(name_col)
                elif sort_by == "Category":
                    df_filtered = df_filtered.sort_values("category")
                df_filtered = df_filtered.drop(columns=["_score_num"])

                # Display table with key columns
                display_cols = [col for col in ["title", "name", "category", "phone", "emails", "lead_score", "why_good_fit", "suggested_pitch"] if col in df_filtered.columns]
                st.dataframe(
                    df_filtered[display_cols],
                    use_container_width=True,
                    height=500,
                    column_config={
                        "title": st.column_config.TextColumn("Business Name", width="medium"),
                        "name": st.column_config.TextColumn("Business Name", width="medium"),
                        "category": st.column_config.TextColumn("Category", width="small"),
                        "phone": st.column_config.TextColumn("Phone", width="small"),
                        "emails": st.column_config.TextColumn("Email", width="medium"),
                        "lead_score": st.column_config.NumberColumn("Score", format="%d ⭐", width="small"),
                        "why_good_fit": st.column_config.TextColumn("Why Good Fit", width="large"),
                        "suggested_pitch": st.column_config.TextColumn("Suggested Pitch", width="large"),
                    }
                )

                # Download options
                st.markdown("---")
                st.subheader("📥 Download Results")

                col1, col2, col3 = st.columns(3)

                with col1:
                    # CSV download
                    csv_data = df_scored.to_csv(index=False)
                    st.download_button(
                        label="📄 Download CSV",
                        data=csv_data,
                        file_name=f"leads_scored_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                with col2:
                    # Try Excel download
                    latest_scored = get_latest_scored_leads()
                    xlsx_path = latest_scored.replace(".csv", ".xlsx") if latest_scored else None
                    if xlsx_path and os.path.exists(xlsx_path):
                        with open(xlsx_path, "rb") as f:
                            excel_data = f.read()
                        st.download_button(
                            label="📊 Download Excel (Formatted)",
                            data=excel_data,
                            file_name=f"leads_scored_{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:
                        st.warning("Excel file not available — CSV download works")

                with col3:
                    st.info("✅ All files are automatically saved to the output folder")

            except ValueError as e:
                st.error(f"❌ Configuration Error: {str(e)}")
                st.info("Make sure GEMINI_API_KEY is set in config/.env")

            except FileNotFoundError as e:
                st.error(f"❌ File Error: {str(e)}")

            except Exception as e:
                st.error(f"❌ Error Scoring Leads: {str(e)}")
                st.info("Check your API key and internet connection")

        else:
            st.info("💡 Click 'Start Scoring' above to analyze these leads with AI")

# ============== FOOTER ==============
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #999; font-size: 11px; margin-top: 2rem;'>
    <b>Lead Machine</b> • Powered by Google Maps & Gemini AI<br>
    All files are automatically saved to the <code>output/</code> folder with timestamps
    </div>
""", unsafe_allow_html=True)
