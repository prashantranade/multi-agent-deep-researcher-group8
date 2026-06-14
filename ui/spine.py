import streamlit as st

from ui.constants import PHASES


def render_spine(current_step: int) -> int:
    """Render phase navigation. Returns active workspace step."""
    st.markdown('<div class="dr-spine-wrap">', unsafe_allow_html=True)
    view_step = st.session_state.get("view_step")

    for step_num, label in PHASES:
        if step_num > 7:
            continue
        if step_num < current_step:
            state = "done"
        elif step_num == current_step:
            state = "active"
        else:
            state = "upcoming"

        if state == "done":
            if st.button(f"✓ {label}", key=f"spine_{step_num}", use_container_width=True):
                st.session_state.view_step = step_num
                st.rerun()
        else:
            active_marker = view_step == step_num if view_step else step_num == current_step
            cls = "dr-spine-item"
            if state == "active" or active_marker:
                cls += " dr-spine-item--active"
            dot = "●" if state == "active" else "○"
            st.markdown(
                f'<div class="{cls}"><span class="dr-spine-dot"></span>{dot} {label}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    if view_step and view_step < current_step:
        return view_step
    return current_step
