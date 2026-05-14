import streamlit as st

# ------------------- PAGE CONFIG -------------------
st.set_page_config(
    page_title="FASTA Analyzer",
    page_icon="🧬",
    layout="wide"
)

# ------------------- CUSTOM CSS -------------------

st.markdown("""
<style>

/* -------- IMPORT FONTS -------- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

/* -------- GLOBAL -------- */
html, body {
    font-family: 'Inter', sans-serif;
    background-color: #0b1120;
    color: #f3f4f6;
}

/* -------- MAIN CONTAINER -------- */
.block-container {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* -------- TITLES -------- */
h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px;
    color: white;
}
h2, h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: #f9fafb;
}

/* -------- SIDEBAR -------- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #111827);
    border-right: 1px solid #1f2937;
    color: #f3f4f6;
}
[data-testid="stSidebar"] * {
    color: #f3f4f6 !important;   /* force text visible */
    font-family: 'Inter', sans-serif !important;
}

/* -------- BUTTONS -------- */
.stButton>button,
.stDownloadButton>button {
    background: linear-gradient(90deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 0.6rem 1rem !important;
    font-weight: 600 !important;
    transition: 0.3s ease-in-out;
}
.stButton>button:hover,
.stDownloadButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0px 4px 15px rgba(37,99,235,0.4);
}

/* -------- METRIC CARDS -------- */
[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1f2937;
    padding: 18px;
    border-radius: 14px;
}

/* -------- DATAFRAME -------- */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #1f2937;
}

/* -------- ALERTS -------- */
.stSuccess {
    background-color: rgba(34,197,94,0.15);
    border: 1px solid #22c55e;
    border-radius: 12px;
}
.stInfo, .stWarning {
    border-radius: 12px;
}

/* -------- CHART SECTION -------- */
.element-container:has(canvas) {
    background-color: #111827;
    padding: 15px;
    border-radius: 16px;
    border: 1px solid #1f2937;
    margin-bottom: 20px;
}

/* -------- FOOTER -------- */
footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ------------------- SIDEBAR -------------------
st.sidebar.title("🧬 FASTA Analyzer")
st.sidebar.markdown("### Navigation")

section = st.sidebar.radio(
    "Go to",
    ["📤 Upload & Overview", "📊 Analysis", "🧾 Export", "About Us"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Built for genomic insights")

# ------------------- MAIN LOGIC -------------------

# SESSION STATE INIT
if "data" not in st.session_state:
    st.session_state["data"] = None

# ------------------- SECTION 1 -------------------
if section == "📤 Upload & Overview":

    st.markdown("""
    <h1 style='font-family: Space Grotesk;'>
    🧬 FASTA Analyzer
    </h1>
    """, unsafe_allow_html=True)
    st.caption("Upload FASTA files and generate genomic insights instantly")

    uploaded_file = st.file_uploader("📤 Upload FASTA file", type=["fasta"])

    if uploaded_file:

        with st.spinner("🔄 Processing sequences..."):
            from Bio import SeqIO
            from io import StringIO
            import pandas as pd

            def read_fasta(uploaded_file):
                stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
                return list(SeqIO.parse(stringio, "fasta"))

            def gc_content(seq):
                return float(seq.count("G") + seq.count("C")) / len(seq) * 100

            records = read_fasta(uploaded_file)

            data = pd.DataFrame({
                "Protein_Name": [rec.description for rec in records],
                "ID": [rec.id for rec in records],
                "Length": [len(rec.seq) for rec in records],
                "GC_Content": [gc_content(rec.seq) for rec in records]
                
            })

            st.subheader("Detailed Analysis")
            st.dataframe(data)

            # --- CSV Download Button ---
            csv = data.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="FASTA_Analysis.csv",
                mime="text/csv"
            )

 

        st.session_state["data"] = data

        st.success(f"✅ {len(data)} sequences analyzed successfully!")

        # -------- METRICS --------
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sequences", len(data))
        col2.metric("Avg Length", int(data["Length"].mean()))
        col3.metric("Avg GC %", round(data["GC_Content"].mean(), 2))

    else:
        st.info("📁 Upload a FASTA file to begin")

# ------------------- SECTION 2 -------------------
elif section == "📊 Analysis":

    st.title("📊 Detailed Analysis")

    if st.session_state["data"] is None:
        st.warning("⚠️ Please upload a file first")
    else:
        import matplotlib.pyplot as plt

        data = st.session_state["data"]

        st.dataframe(data, use_container_width=True)

        col1, col2 = st.columns(2)

        # -------- GC Distribution --------
        with col1:
            st.subheader("GC Distribution")
            fig1, ax = plt.subplots(figsize = (10,7))
            ax.hist(data["GC_Content"], bins=10)
            ax.set_title("GC Content Distribution Across Multiple FASTA Files")
            ax.set_xlabel("GC%")
            ax.set_ylabel("Frequency")
            st.pyplot(fig1)

            file_path1 = "gc_distribution.png"
            fig1.savefig(file_path1, dpi=80, bbox_inches="tight")
            with open(file_path1, "rb") as f:
                st.download_button("Download GC Content Distribution", f, file_name="gc_distribution.png")

        # -------- GC Comparison --------
        with col2:
            st.subheader("GC Comparison")
            fig2, ax = plt.subplots(figsize = (10,5))
            ax.bar(data["ID"], data["GC_Content"])
            ax.set_xlabel("Gene")
            ax.set_ylabel("GC Content (%)")
            ax.set_title("GC Content Comparison Across Multiple FASTA Files")
            plt.xticks(rotation=60)
            st.pyplot(fig2)

            file_path2 = "gc_comparison.png"
            fig2.savefig(file_path2, dpi=80, bbox_inches="tight")
            with open(file_path2, "rb") as f:
                st.download_button("Download GC Content Comparison", f, file_name="gc_comparison.png")

        # -------- GC Trend --------
        st.subheader("GC Trend")
        fig3, ax = plt.subplots(figsize = (10,4))
        ax.plot(data["GC_Content"], marker='o')
        ax.set_xlabel("Sequence Index")
        ax.set_ylabel("GC Content (%)")
        ax.set_title("GC Content Trend Across Sequences")
        st.pyplot(fig3)

        file_path3 = "gc_trend.png"
        fig3.savefig(file_path3, dpi=80, bbox_inches="tight")
        with open(file_path3, "rb") as f:
            st.download_button("Download GC Content Trend", f, file_name="gc_trend.png")



        

        # --- New Section: Additional Plots ---
        st.subheader("Additional GC Content Analysis")

        fig, axs = plt.subplots(2, 2, figsize=(14,10))

        # Top-left: GC Content (%) per gene
        axs[0,0].bar(data["ID"], data["GC_Content"])
        axs[0,0].set_title("GC Content (%)")
        axs[0,0].set_ylabel("GC %")
        axs[0,0].tick_params(axis='x', rotation=60)

        # Top-right: Gene Length
        axs[0,1].bar(data["ID"], data["Length"])
        axs[0,1].set_title("Gene Length")
        axs[0,1].set_ylabel("Length")
        axs[0,1].tick_params(axis='x', rotation=60)

        # Bottom-left: GC Content Distribution
        axs[1,0].hist(data["GC_Content"], bins=10)
        axs[1,0].set_title("GC Content Distribution")
        axs[1,0].set_xlabel("GC %")
        axs[1,0].set_ylabel("Frequency")

        # Bottom-right: GC Content Spread (Boxplot)
        axs[1,1].boxplot(data["GC_Content"], patch_artist=True, boxprops=dict())
        axs[1,1].set_title("GC Content Spread")
        axs[1,1].set_ylabel("GC %")

        plt.tight_layout()
        st.pyplot(fig)

        file_path3 = "additional_plot.png"
        fig.savefig(file_path3, dpi=80, bbox_inches="tight")
        with open(file_path3, "rb") as f:
            st.download_button("Download Additional Plot Chart", f, file_name="additional_plot.png")




# ------------------- SECTION 3 -------------------
# ------------------- SECTION 3 -------------------
# ------------------- SECTION 3 -------------------
elif section == "🧾 Export":

    st.markdown("""
    <h1 style='font-family:Space Grotesk;'>
    🧾 Export Analysis Report
    </h1>
    """, unsafe_allow_html=True)

    st.caption("Generate a professional genomic analysis report with charts, sequence summaries, and biological insights.")

    if st.session_state["data"] is None:
        st.warning("⚠️ No data available. Upload first.")

    else:

        from fpdf import FPDF
        import os

        data = st.session_state["data"]

        st.subheader("📋 Sequence Summary")
        st.dataframe(data, use_container_width=True)

        st.info("The generated report will include uploaded sequence information, graphical analysis, interpretation, and community information.")

        # ---------------- PDF FUNCTION ----------------
        def create_report(data, filename="report.pdf"):

            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)

            # ---------------- COVER PAGE ----------------
            pdf.add_page()

            pdf.set_fill_color(15, 23, 42)
            pdf.rect(0, 0, 210, 297, 'F')

            pdf.set_text_color(255,255,255)

            pdf.ln(50)

            pdf.set_font("Arial", "B", 28)
            pdf.cell(190, 15, "FASTA Analysis Report", ln=True, align="C")

            pdf.ln(10)

            pdf.set_font("Arial", "", 14)
            pdf.multi_cell(
                0,
                10,
                "A professional genomic analysis report generated from uploaded FASTA sequences including GC content analysis, comparative visualization, and sequence trend interpretation.",
                align="C"
            )

            pdf.ln(30)

            pdf.set_font("Arial", "I", 12)
            pdf.cell(190, 10, "Generated using FASTA Analyzer Dashboard", ln=True, align="C")

            # ---------------- SUMMARY PAGE ----------------
            pdf.add_page()

            pdf.set_text_color(37, 99, 235)

            pdf.set_font("Arial", "B", 22)
            pdf.cell(190, 12, "Sequence Overview", ln=True)

            pdf.ln(5)

            pdf.set_text_color(80,80,80)

            pdf.set_font("Arial", "", 11)

            intro = (
                "This section summarizes uploaded FASTA sequences including protein information, sequence length, and GC content values used for downstream analysis."
            )

            pdf.multi_cell(0, 8, intro)

            pdf.ln(8)

            # ---------------- TABLE ----------------

            pdf.set_fill_color(37, 99, 235)
            pdf.set_text_color(255,255,255)

            pdf.set_font("Arial", "B", 9)

            pdf.cell(70, 10, "Protein Name", 1, 0, 'C', True)
            pdf.cell(40, 10, "ID", 1, 0, 'C', True)
            pdf.cell(30, 10, "Length", 1, 0, 'C', True)
            pdf.cell(40, 10, "GC %", 1, 1, 'C', True)

            pdf.set_text_color(0,0,0)
            pdf.set_font("Arial", "", 8)

            for _, row in data.iterrows():

                protein = str(row["Protein_Name"])[:35]
                seq_id = str(row["ID"])[:18]

                pdf.cell(70, 10, protein, 1)
                pdf.cell(40, 10, seq_id, 1)
                pdf.cell(30, 10, str(row["Length"]), 1)
                pdf.cell(40, 10, f"{row['GC_Content']:.2f}", 1, 1)

            # ---------------- CHART PAGES ----------------

            charts = [

                (
                    "GC Content Distribution",
                    "gc_distribution.png",
                    "This histogram represents the frequency distribution of GC content values among uploaded FASTA sequences. It helps identify variability and clustering of GC composition."
                ),

                (
                    "GC Content Comparison",
                    "gc_comparison.png",
                    "This comparative bar chart visualizes GC percentages across different genomic sequences, enabling comparative biological interpretation."
                ),

                (
                    "GC Content Trend",
                    "gc_trend.png",
                    "This trend plot illustrates sequential changes in GC content values across analyzed sequences."
                ),

                (
                    "Additional GC Content Analysis",
                    "additional_plot.png",
                    "This advanced visualization combines multiple analytical perspectives including GC distribution, gene length variation, comparative GC content, and spread analysis."
                )

            ]

            # ---------------- ADD CHARTS ----------------

            for title, image_path, description in charts:

                if os.path.exists(image_path):

                    pdf.add_page()

                    # TITLE
                    pdf.set_text_color(37,99,235)

                    pdf.set_font("Arial", "B", 20)

                    pdf.cell(190, 12, title, ln=True)

                    pdf.ln(4)

                    # DESCRIPTION
                    pdf.set_text_color(70,70,70)

                    pdf.set_font("Arial", "", 11)

                    pdf.multi_cell(0, 7, description)

                    pdf.ln(5)

                    # IMAGE
                    pdf.image(image_path, x=15, w=180)

            # ---------------- COMMUNITY PAGE ----------------

            pdf.add_page()

            pdf.set_text_color(37,99,235)

            pdf.set_font("Arial", "B", 22)

            pdf.cell(190, 12, "About Biocode Innovators", ln=True)

            pdf.ln(8)

            pdf.set_text_color(50,50,50)

            pdf.set_font("Arial", "", 12)

            about_text = (
                "Biocode Innovators bridges the gap between biology and computational technology. "
                "The community focuses on empowering students, researchers, and professionals through "
                "bioinformatics education, biological data visualization, computational biology, and "
                "modern genomic analysis tools.\n\n"

                "Core Focus Areas:\n"
                "- Computational Biology\n"
                "- Biological Data Visualization\n"
                "- In-silico Analysis\n"
                "- Python and R for Biology\n"
                "- Data-driven Life Science Research\n\n"

                "Mission:\n"
                "Make biological data accessible, understandable, and actionable.\n\n"

                "Vision:\n"
                "Enable the next generation of scientists to leverage computational technologies in biology."
            )

            pdf.multi_cell(0, 8, about_text)

            pdf.ln(15)

            pdf.set_font("Arial", "I", 11)

            pdf.set_text_color(100,100,100)

            pdf.multi_cell(
                0,
                7,
                "Generated using FASTA Analyzer Dashboard | Developed for genomic insight and educational bioinformatics applications."
            )

            # ---------------- SAVE ----------------
            pdf.output(filename)

        # ---------------- GENERATE BUTTON ----------------

        if st.button("🚀 Generate Professional PDF Report"):

            create_report(data)

            st.success("✅ Professional FASTA report generated successfully!")

            with open("report.pdf", "rb") as f:

                st.download_button(
                    "📥 Download FASTA Analysis Report",
                    f,
                    file_name="FASTA_Report.pdf"
                )




elif section == "About Us":


    # ------------------- ABOUT US SECTION -------------------

    st.markdown("""
    <div style="max-width: 900px; margin: auto;">

    <h1 style="
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #2563eb, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    ">
    🚀 About Biocode Innovators
    </h1>

    <p style="text-align:center; font-size:16px; color:#9ca3af;">
    Bridging Biology 🧬 and Technology 💻 through modern computational solutions
    </p>

    <br>

    <div style="
        background-color:#111827;
        padding:20px;
        border-radius:12px;
        margin-bottom:20px;
    ">
    <p style="font-size:15px; line-height:1.7;">
    <strong>Biocode Innovators</strong> is dedicated to transforming biological data into meaningful insights.
    We empower students, researchers, and professionals with hands-on tools, training, and real-world applications in 
    <strong>bioinformatics, genomics, and data-driven life sciences</strong>.
    </p>
    </div>

    <div style="display:flex; gap:20px; flex-wrap:wrap;">

    <div style="
        flex:1;
        background-color:#111827;
        padding:20px;
        border-radius:12px;
    ">
    <h3>👩‍🔬 Founder</h3>
    <p>Abeera Iftikhar</p>

    <h3>🎯 Mission</h3>
    <p>Make biological data accessible, understandable, and actionable.</p>

    <h3>💡 Vision</h3>
    <p>Enable the next generation of scientists to leverage computation in biology.</p>
    </div>

    <div style="
        flex:1;
        background-color:#111827;
        padding:20px;
        border-radius:12px;
    ">
    <h3>📌 Focus Areas</h3>
    <ul>
    <li>🧬 Computational Biology</li>
    <li>📊 Data Analysis</li>
    <li>📈 Biological Data Visualization</li>
    <li>⚙️ In-silico Analysis</li>
    <li>🐍 Python for Biology</li>
    <li>📉 R for Biology</li>
    </ul>
    </div>

    </div>

    <br>

    <div style="
        background-color:#111827;
        padding:20px;
        border-radius:12px;
    ">
    <h3>🏢 Company Details</h3>
    <p><strong>Industry:</strong> E-Learning & Bioinformatics Solutions</p>
    <p><strong>Team Size:</strong> 2–10 members</p>
    <p><strong>Founded:</strong> 2025</p>
    <p><strong>Contact:</strong> 📞 03159633608</p>
    </div>

    <br>

    <p style="text-align:center; font-style:italic; color:#60a5fa;">
    ✨ “Let’s decode biology together.” ✨
    </p>

    </div>
    """, unsafe_allow_html=True)



# ------------------- FOOTER -------------------
st.markdown("---")
st.caption("🧬 FASTA Analyzer • Built for genomic data insights")





# --- Hide Streamlit default footer ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- Custom Footer CSS ---
st.markdown("""
<style>
.custom-footer {
    background-color: #111827;   /* dark background */
    padding: 20px;
    text-align: center;
    border-top: 1px solid #2563eb;
    margin-top: 40px;
    border-radius: 8px;
}
.custom-footer h4 {
    font-size: 18px;
    font-weight: bold;
    color: #60a5fa;
    margin: 0;
}
.custom-footer p {
    font-size: 14px;
    color: #e5e7eb;
    margin: 5px 0;
}
.custom-footer span {
    color: #93c5fd;
}
</style>
""", unsafe_allow_html=True)

# --- Footer HTML ---
st.markdown("""
<div class="custom-footer">
    <h4>🧬 Powered by <span>BioCode Innovators</span></h4>
    <p>Developed with precision by <strong style="color:#ffffff;">Abeera Iftikhar</strong></p>
    <p>
        FASTA Analyzer Dashboard designed for
        <span>genomic sequence analysis</span>,
        <span>GC content visualization</span>,
        and modern <span>bioinformatics education</span>.
    </p>
    <p>✨ Bridging Biology, Data Science, and Computational Intelligence ✨</p>
</div>
""", unsafe_allow_html=True)

