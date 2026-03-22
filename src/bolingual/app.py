"""Streamlit app for Hindi-English wordplay."""

from __future__ import annotations

from importlib.resources import as_file, files

import pandas as pd
import streamlit as st

from bolingual import CandidateIndex
from bolingual.phonetics import romanize_hindi

SAMPLE_WORDS = ["वॉटसन", "सर्किट्स", "न्यू", "थैचर", "गेट", "फ्रॉस्ट", "इंडिया", "अकेडमी"]


@st.cache_resource
def load_index() -> CandidateIndex:
    data_ref = files("bolingual.data").joinpath("benchmark.csv")
    with as_file(data_ref) as data_path:
        benchmark = pd.read_csv(data_path)
    return CandidateIndex.from_words(benchmark["gold"].unique())


def main() -> None:
    st.set_page_config(page_title="Bolingual", page_icon="🗣️", layout="wide")

    st.title("🗣️ Bolingual")
    st.subheader("Find English words that sound like Hindi")

    with st.sidebar:
        st.header("Parameters")
        top_k: int = st.slider(
            "top_k (shortlist size)", min_value=50, max_value=300, value=200
        )
        alpha: float = st.slider(
            "alpha (orthographic weight)", min_value=0.0, max_value=1.0, value=0.5
        )
        num_results: int = st.slider("Results to show", min_value=5, max_value=50, value=10)
        hard_mode: bool = st.toggle("Hard mode", help="Focus on non-obvious matches")

    index = load_index()

    st.markdown("**Try these examples:**")
    cols = st.columns(len(SAMPLE_WORDS))
    for col, word in zip(cols, SAMPLE_WORDS, strict=True):
        if col.button(word, key=f"sample_{word}"):
            st.session_state.hindi_input = word

    hindi_input: str = st.text_input(
        "Enter Hindi word (Devanagari)",
        value=st.session_state.get("hindi_input", ""),
        placeholder="वॉटसन",
    )

    if hindi_input:
        romanized = romanize_hindi(hindi_input)
        st.markdown(f"**Romanization:** `{romanized}`")

        rankings = index.hybrid_ranking(hindi_input, top_k=top_k, alpha=alpha)

        best_match = rankings["hybrid"][0]
        st.markdown("---")
        st.markdown(
            f"### Best Match: **{hindi_input}** → **{best_match[1]}** "
            f"(score: {best_match[0]:.3f})"
        )

        orth_rank_map = {word: i + 1 for i, (_, word) in enumerate(rankings["orthographic"])}

        results_data: list[dict[str, object]] = []
        for i, (score, word) in enumerate(rankings["hybrid"][:num_results]):
            orth_rank = orth_rank_map.get(word)
            hybrid_rank = i + 1
            if orth_rank is not None and orth_rank <= top_k:
                improvement: int | str = orth_rank - hybrid_rank
                orth_rank_display: int | str = orth_rank
            else:
                improvement = "-"
                orth_rank_display = f">{top_k}"
            results_data.append(
                {
                    "Rank": hybrid_rank,
                    "English": word,
                    "Score": f"{score:.3f}",
                    "Orth Rank": orth_rank_display,
                    "Improvement": improvement,
                }
            )

        if hard_mode:
            hard_results = [
                r
                for r in results_data
                if isinstance(r["Improvement"], int) and r["Improvement"] > 0
            ]
            if hard_results:
                results_data = hard_results

        st.markdown("### Results")
        st.dataframe(
            pd.DataFrame(results_data),
            use_container_width=True,
            hide_index=True,
        )

        with st.expander("Orthographic vs Hybrid Comparison"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Orthographic Top 10**")
                orth_data = [
                    {"Rank": i + 1, "Word": word, "Score": f"{score:.3f}"}
                    for i, (score, word) in enumerate(rankings["orthographic"][:10])
                ]
                st.dataframe(pd.DataFrame(orth_data), use_container_width=True, hide_index=True)

            with col2:
                st.markdown("**Hybrid Top 10**")
                hybrid_data = [
                    {"Rank": i + 1, "Word": word, "Score": f"{score:.3f}"}
                    for i, (score, word) in enumerate(rankings["hybrid"][:10])
                ]
                st.dataframe(pd.DataFrame(hybrid_data), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
