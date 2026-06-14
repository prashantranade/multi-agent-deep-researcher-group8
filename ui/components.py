import html

import streamlit as st

from ui.constants import PERSONA_LABELS


def render_header() -> None:
    session_short = st.session_state.session_id[:8]
    trace = st.session_state.get("trace_id")
    meta_parts = [f"session {session_short}"]
    if trace:
        meta_parts.append(f"trace {trace[:12]}…")

    st.markdown(
        f"""
        <div class="dr-header">
            <h1 class="dr-header__title">Deep Researcher</h1>
            <p class="dr-header__thesis">
                Build a source-verified research brief, then let your agent crew
                produce the artifacts you choose.
            </p>
            <p class="dr-header__meta">{' · '.join(meta_parts)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def phase_heading(title: str, subtitle: str = "") -> None:
    sub = f'<p class="dr-phase-sub">{html.escape(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f'<h2 class="dr-phase-title">{html.escape(title)}</h2>{sub}',
        unsafe_allow_html=True,
    )


def persona_card_html(title: str, promise: str, selected: bool) -> str:
    cls = "dr-persona-card dr-persona-card--selected" if selected else "dr-persona-card"
    return f"""
    <div class="{cls}">
        <p class="dr-persona-card__title">{html.escape(title)}</p>
        <p class="dr-persona-card__promise">{html.escape(promise)}</p>
    </div>
    """


def source_card_html(title: str, domain: str, date: str, score: float) -> str:
    pct = int(score * 100)
    if score >= 0.7:
        color = "var(--dr-score-high)"
    elif score >= 0.4:
        color = "var(--dr-score-mid)"
    else:
        color = "var(--dr-score-low)"
    width = max(pct, 4)
    return f"""
    <div class="dr-source-card">
        <p class="dr-source-card__title">{html.escape(title)}</p>
        <p class="dr-source-card__meta">{html.escape(domain)} · {html.escape(date)}</p>
        <div class="dr-confidence-bar">
            <div class="dr-confidence-bar__fill" style="width:{width}%;background:{color};"></div>
        </div>
        <p class="dr-confidence-label">{pct}% confidence</p>
    </div>
    """


def dossier_field(label: str, value: str, *, mono: bool = False, empty: bool = False) -> str:
    val_cls = "dr-dossier__value"
    if mono:
        val_cls += " dr-dossier__value--mono"
    if empty:
        val_cls += " dr-dossier__value--empty"
    display = html.escape(value) if value else "—"
    return f"""
    <div class="dr-dossier__field">
        <span class="dr-dossier__label">{html.escape(label)}</span>
        <span class="{val_cls}">{display}</span>
    </div>
    """


def persona_label(persona_key: str | None) -> str:
    if not persona_key:
        return ""
    return PERSONA_LABELS.get(persona_key, persona_key.replace("_", " ").title())
