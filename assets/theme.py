
import streamlit as st

# ---------------------------------------------------------------------------
# Corporate rose / pink palette
# ---------------------------------------------------------------------------
PRIMARY_DARK = "#7A284B"
PRIMARY = "#A83D68"
SECONDARY = "#C65A82"
ACCENT = "#D98AA5"
LIGHT_ACCENT = "#F3DCE5"
BG_LIGHT_ACCENT = "#FAF3F6"
MAIN_BG = "#F8F9FB"
CARD_BG = "#FFFFFF"
MAIN_TEXT = "#25252A"
SECONDARY_TEXT = "#6B7280"
BORDER = "#E5E7EB"

SUCCESS = "#1E8E5A"
SUCCESS_BG = "rgba(30,142,90,0.10)"
WARNING = "#B7791F"
WARNING_BG = "rgba(183,121,31,0.12)"
DANGER = "#C0392B"
DANGER_BG = "rgba(192,57,43,0.10)"
INFO_BG = "rgba(168,61,104,0.10)"

# Ordered dark -> light rose shades for chart series / categorical hierarchy
ROSE_SCALE = ["#7A284B", "#A83D68", "#C65A82", "#B8506F", "#D98AA5", "#E3A9BE", "#F3DCE5"]

FONT_STACK = ("-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto, "
              "'Helvetica Neue', Arial, sans-serif")


def rose_palette(n: int) -> list[str]:
    """Return n rose shades (dark -> light), cycling the base scale if n is larger."""
    if n <= len(ROSE_SCALE):
        return ROSE_SCALE[:n]
    return [ROSE_SCALE[i % len(ROSE_SCALE)] for i in range(n)]


# ---------------------------------------------------------------------------
# Minimal, original monochrome icon set (inline SVG, inherits currentColor)
# Used in place of decorative emoji for section headers.
# ---------------------------------------------------------------------------
_ICON_PATHS = {
    "dashboard": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/>'
                 '<rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    "users": '<circle cx="8.5" cy="8" r="3"/><circle cx="16" cy="9" r="2.3"/>'
             '<path d="M3 20c0-3 2.5-5 5.5-5s5.5 2 5.5 5"/><path d="M14.5 15.3c2.4.2 4 1.9 4 4.7"/>',
    "user": '<circle cx="12" cy="8" r="3.4"/><path d="M5 20c0-3.6 3-6 7-6s7 2.4 7 6"/>',
    "cash": '<rect x="2.5" y="6" width="19" height="12" rx="2"/><circle cx="12" cy="12" r="2.6"/>'
            '<line x1="6" y1="9" x2="6" y2="9"/><line x1="18" y1="15" x2="18" y2="15"/>',
    "award": '<circle cx="12" cy="8.5" r="5"/><path d="M9 13l-1.5 7L12 18l4.5 2L15 13"/>',
    "folder": '<path d="M3 6.5A1.5 1.5 0 0 1 4.5 5H10l2 2.5h7A1.5 1.5 0 0 1 20.5 9V18A1.5 1.5 0 0 1 19 19.5H4.5A1.5 1.5 0 0 1 3 18z"/>',
    "bar-chart": '<line x1="5" y1="20" x2="5" y2="10"/><line x1="12" y1="20" x2="12" y2="5"/><line x1="19" y1="20" x2="19" y2="14"/>',
    "pie-chart": '<circle cx="12" cy="12" r="8.5"/><path d="M12 3.5V12l7.2 4.2"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><line x1="15.3" y1="15.3" x2="20.5" y2="20.5"/>',
    "briefcase": '<rect x="2.5" y="7.5" width="19" height="12" rx="1.8"/><path d="M8 7.5V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v1.5"/>'
                 '<line x1="2.5" y1="13" x2="21.5" y2="13"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3.2 2"/>',
    "download": '<path d="M12 3.5v11"/><path d="M7.5 10.5 12 15l4.5-4.5"/><path d="M4.5 18.5h15"/>',
    "alert-triangle": '<path d="M12 4.5 21 19.5H3z"/><line x1="12" y1="10" x2="12" y2="14.5"/><circle cx="12" cy="17.2" r="0.15" stroke-width="2.2"/>',
    "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.8"/><circle cx="12" cy="12" r="1.2" fill="currentColor" stroke="none"/>',
    "robot": '<rect x="5" y="8" width="14" height="11" rx="2.2"/><circle cx="9.5" cy="13" r="1.3" fill="currentColor" stroke="none"/>'
             '<circle cx="14.5" cy="13" r="1.3" fill="currentColor" stroke="none"/><line x1="12" y1="8" x2="12" y2="4.5"/>'
             '<circle cx="12" cy="3.3" r="1.1"/>',
    "sitemap": '<rect x="9.5" y="3" width="5" height="4" rx="1"/><rect x="3" y="16" width="5" height="4" rx="1"/>'
               '<rect x="16" y="16" width="5" height="4" rx="1"/><path d="M12 7v5M12 12H5.5v4M12 12h6.5v4"/>',
    "check-circle": '<circle cx="12" cy="12" r="8.5"/><path d="M8 12.3l2.7 2.7L16.5 9"/>',
    "chevron-right": '<polyline points="9 5 16 12 9 19"/>',
    "sliders": '<line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/>'
               '<circle cx="9" cy="6" r="2" fill="white"/><circle cx="16" cy="12" r="2" fill="white"/><circle cx="7" cy="18" r="2" fill="white"/>',
}


def icon(name: str, size: int = 18, color: str = "currentColor", stroke_width: float = 1.8) -> str:
    """Return an inline SVG <span> for the given icon name."""
    inner = _ICON_PATHS.get(name, _ICON_PATHS["dashboard"])
    return (f'<span style="display:inline-flex;vertical-align:-3px;color:{color};margin-right:6px;">'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
            f'fill="none" stroke="currentColor" stroke-width="{stroke_width}" stroke-linecap="round" '
            f'stroke-linejoin="round">{inner}</svg></span>')


# ---------------------------------------------------------------------------
# Global CSS injection
# ---------------------------------------------------------------------------
def apply_theme():
    st.markdown(f"""
    <style>
        html, body, [class*="css"] {{
            font-family: {FONT_STACK};
        }}

        .stApp {{ background-color: {MAIN_BG}; }}

        section[data-testid="stSidebar"] {{
            background-color: {CARD_BG};
            border-right: 1px solid {BORDER};
        }}
        section[data-testid="stSidebar"] > div {{ padding-top: 0.6rem; }}

        div[data-testid="stSidebarNav"] {{ display: none; }}

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }}

        /* Brand block at top of sidebar */
        .nexhr-brand {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 4px 4px 14px 4px;
            margin-bottom: 10px;
            border-bottom: 1px solid {BORDER};
        }}
        .nexhr-brand-mark {{
            width: 34px; height: 34px;
            border-radius: 9px;
            background: linear-gradient(135deg, {PRIMARY_DARK}, {SECONDARY});
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: 700; font-size: 15px;
            flex-shrink: 0;
        }}
        .nexhr-brand-text {{ line-height: 1.15; }}
        .nexhr-brand-title {{ font-weight: 700; font-size: 1.05rem; color: {MAIN_TEXT}; }}
        .nexhr-brand-sub {{ font-size: 0.72rem; color: {SECONDARY_TEXT}; }}

        /* Page header */
        .nexhr-page-title {{
            font-size: 1.55rem;
            font-weight: 700;
            color: {MAIN_TEXT};
            margin-bottom: 2px;
            letter-spacing: -0.01em;
        }}
        .nexhr-page-subtitle {{
            font-size: 0.92rem;
            color: {SECONDARY_TEXT};
            margin-bottom: 1.4rem;
        }}

        /* Section title used inside pages */
        .nexhr-section-title {{
            font-size: 1.02rem;
            font-weight: 650;
            color: {MAIN_TEXT};
            margin: 0.3rem 0 0.7rem 0;
            display: flex;
            align-items: center;
        }}
        .nexhr-section-title svg {{ color: {PRIMARY}; }}

        /* KPI metric cards */
        div[data-testid="stMetric"] {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-top: 3px solid {PRIMARY};
            border-radius: 12px;
            padding: 14px 18px 12px 18px;
            box-shadow: 0 1px 2px rgba(37,37,42,0.04);
        }}
        div[data-testid="stMetric"] label {{
            color: {SECONDARY_TEXT} !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
        }}
        div[data-testid="stMetricValue"] {{
            color: {MAIN_TEXT} !important;
            font-weight: 700 !important;
        }}

        /* Generic card container */
        .nexhr-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 14px;
            box-shadow: 0 1px 2px rgba(37,37,42,0.04);
        }}
        .nexhr-card-header {{
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: {SECONDARY_TEXT};
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 1px solid {BORDER};
        }}
        .nexhr-field-label {{ font-size: 0.76rem; color: {SECONDARY_TEXT}; margin-bottom: 1px; }}
        .nexhr-field-value {{ font-size: 0.95rem; color: {MAIN_TEXT}; font-weight: 560; margin-bottom: 10px; }}

        /* Status badges / pills */
        .status-pill {{
            display: inline-block;
            padding: 3px 11px;
            border-radius: 6px;
            font-size: 0.74rem;
            font-weight: 600;
            letter-spacing: 0.01em;
        }}
        .pill-green {{ background-color: {SUCCESS_BG}; color: {SUCCESS}; }}
        .pill-red   {{ background-color: {DANGER_BG}; color: {DANGER}; }}
        .pill-amber {{ background-color: {WARNING_BG}; color: {WARNING}; }}
        .pill-rose  {{ background-color: {INFO_BG}; color: {PRIMARY_DARK}; }}

        /* Buttons */
        .stButton > button {{
            border-radius: 8px;
            font-weight: 550;
            padding: 0.45rem 1rem;
            border: 1px solid {BORDER};
            transition: all 0.12s ease;
        }}
        .stButton > button[kind="primary"] {{
            background-color: {PRIMARY};
            border: 1px solid {PRIMARY};
            color: white;
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {PRIMARY_DARK};
            border-color: {PRIMARY_DARK};
        }}
        .stButton > button[kind="secondary"] {{
            background-color: {CARD_BG};
            color: {MAIN_TEXT};
        }}
        .stButton > button[kind="secondary"]:hover {{
            border-color: {PRIMARY};
            color: {PRIMARY_DARK};
        }}
        .stDownloadButton > button {{
            border-radius: 8px;
            border: 1px solid {PRIMARY};
            color: {PRIMARY_DARK};
            background-color: {BG_LIGHT_ACCENT};
            font-weight: 560;
        }}
        .stDownloadButton > button:hover {{
            background-color: {LIGHT_ACCENT};
        }}

        /* Inputs */
        div[data-baseweb="input"], div[data-baseweb="select"] > div {{
            border-radius: 8px !important;
        }}
        div[data-testid="stDataFrame"] {{
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid {BORDER};
        }}

        hr {{ border-color: {BORDER}; }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0 0;
            padding: 8px 16px;
            font-weight: 550;
        }}

        /* Progress bar (native) already themed via primaryColor */

        [data-testid="stMetricDelta"] svg {{ display: none; }}
    </style>
    """, unsafe_allow_html=True)


def render_sidebar_brand():
    st.markdown(f"""
    <div class="nexhr-brand">
        <div class="nexhr-brand-mark">N</div>
        <div class="nexhr-brand-text">
            <div class="nexhr-brand-title">NexHR</div>
            <div class="nexhr-brand-sub">Workforce Intelligence Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="nexhr-page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="nexhr-page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def section_title(text: str, icon_name: str = None):
    prefix = icon(icon_name) if icon_name else ""
    st.markdown(f'<div class="nexhr-section-title">{prefix}{text}</div>', unsafe_allow_html=True)


def status_pill(text: str, kind: str = "rose") -> str:
    """kind: 'green' | 'red' | 'amber' | 'rose'"""
    return f'<span class="status-pill pill-{kind}">{text}</span>'


def project_status_kind(status: str) -> str:
    return {"Completed": "green", "Ongoing": "rose", "Review": "amber", "Not Started": "red"}.get(status, "rose")


def card_start(header: str = None):
    html = '<div class="nexhr-card">'
    if header:
        html += f'<div class="nexhr-card-header">{header}</div>'
    st.markdown(html, unsafe_allow_html=True)


def card_end():
    st.markdown('</div>', unsafe_allow_html=True)


def field(label: str, value: str):
    st.markdown(f'<div class="nexhr-field-label">{label}</div><div class="nexhr-field-value">{value}</div>',
                unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Plotly styling
# ---------------------------------------------------------------------------
def style_fig(fig, height: int = 340, show_legend: bool = None):
    """Apply the shared corporate chart style to any Plotly figure."""
    fig.update_layout(
        height=height,
        font=dict(family=FONT_STACK, size=12.5, color=MAIN_TEXT),
        title=dict(font=dict(size=14.5, color=MAIN_TEXT, family=FONT_STACK), x=0.0, xanchor="left"),
        plot_bgcolor=CARD_BG,
        paper_bgcolor=CARD_BG,
        margin=dict(l=10, r=10, t=48, b=10),
        hoverlabel=dict(bgcolor=CARD_BG, font_size=12, font_family=FONT_STACK,
                         bordercolor=BORDER, font_color=MAIN_TEXT),
        showlegend=show_legend if show_legend is not None else fig.layout.showlegend,
        legend=dict(font=dict(size=11.5, color=SECONDARY_TEXT), bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=False, showline=True, linecolor=BORDER, tickfont=dict(color=SECONDARY_TEXT, size=11))
    fig.update_yaxes(showgrid=True, gridcolor=BORDER, gridwidth=1, zeroline=False,
                      tickfont=dict(color=SECONDARY_TEXT, size=11))
    return fig
