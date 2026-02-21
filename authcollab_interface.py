# app.py
import streamlit as st
import pandas as pd
import ast
import zipfile
from io import TextIOWrapper

# === CONFIGURATION ===
ACTORS_COL = "actors"
SUMMARY_COL = "summary"
COLLAB_TYPE_COL = "collab_type"
ID_COL = "id"
SOURCE_COL = "source"
DATE_COL = "date"

# === LOAD DATA ===
@st.cache_data
@st.cache_data
def load_data():
    try:
        with zipfile.ZipFile("authcollab_25.zip", "r") as z:
            with z.open("authcollab_25.csv") as f:
                df = pd.read_csv(TextIOWrapper(f, "utf-8"))

        def safe_parse_actor_ids(x):
            try:
                if pd.notnull(x):
                    x = str(x).replace("‘", "'").replace("’", "'")
                    return set(ast.literal_eval(x))
            except:
                pass
            return set()

        df[ACTORS_COL] = df[ACTORS_COL].apply(safe_parse_actor_ids)
        return df

    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        return pd.DataFrame()

        def safe_parse_actor_ids(x):
            try:
                if pd.notnull(x):
                    x = str(x).replace("‘", "'").replace("’", "'")
                    return set(ast.literal_eval(x))
            except:
                pass
            return set()

        df[ACTORS_COL] = df[ACTORS_COL].apply(safe_parse_actor_ids)
        return df
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("⚠️ No data loaded. Check path or file format.")
    st.stop()

# === INTERFACE ===
st.title("🔎 AuthCollab Explorer")

# Collaboration type dropdown
collab_type_options = ["(Any)"] + sorted(df[COLLAB_TYPE_COL].dropna().unique().tolist())
selected_collab_type = st.selectbox("Filter by collaboration type", collab_type_options)

# Actor multiselect
all_actors = sorted({actor for actor_set in df[ACTORS_COL] for actor in actor_set})
selected_actors = st.multiselect("Select actor(s) to filter by (requires all selected)", all_actors)

# Summary search bar
summary_search = st.text_input("Search text in summary (case-insensitive, all words must match)").strip()

# === FILTER LOGIC ===
def row_matches(row):
    actor_ids = {a.lower() for a in row[ACTORS_COL]}
    selected_ids = {a.lower() for a in selected_actors}
    has_all_actors = selected_ids.issubset(actor_ids)

    collab_type_ok = (
        row.get(COLLAB_TYPE_COL) == selected_collab_type
        if selected_collab_type != "(Any)"
        else True
    )

    # Combine summary + id search
    summary_text = str(row.get(SUMMARY_COL, "")).lower()
    id_text = str(row.get(ID_COL, "")).lower()
    combined_text = f"{summary_text} {id_text}"

    search_words = summary_search.lower().split()
    search_ok = all(word in combined_text for word in search_words)

    return has_all_actors and collab_type_ok and search_ok

filtered_df = df[df.apply(row_matches, axis=1)]

# === DISPLAY ===
st.markdown(f"### 🎯 Showing {len(filtered_df)} result(s)")

if not filtered_df.empty:
    display_cols = [ID_COL, DATE_COL, SUMMARY_COL, COLLAB_TYPE_COL, ACTORS_COL, SOURCE_COL]
    st.dataframe(filtered_df[display_cols], use_container_width=True)

    st.download_button(
        label="📥 Download filtered results as CSV",
        data=filtered_df[display_cols].to_csv(index=False),
        file_name="authcollab_filtered.csv",
        mime="text/csv"
    )
else:
    st.info("No matching rows. Try adjusting your filters.")
