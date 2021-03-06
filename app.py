# %%
import streamlit as st
import pandas as pd
import altair as alt


@st.cache
def get_data() -> pd.DataFrame:
    """
    Gets data from the GitHub repository of the Protezione Civile
    Keeps only date, region and total of cases
    """
    data = pd.read_csv(
        "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv"
    )
    # Remove the time and just focus on the date
    data["data"] = pd.to_datetime(
        pd.to_datetime(data["data"]).apply(lambda x: x.date())
    )
    return data


def formatter(name: str) -> str:
    return " ".join(name.capitalize().split("_"))


data = get_data()

st.sidebar.markdown("# Possibili visualizzazioni")
st.sidebar.markdown(
    "Scegli se preferisci visualizzare il dato totale o il relativo cambiamento rispetto al giorno precedente:"
)
choice = st.sidebar.radio(
    label="Possibili visualizzazioni", options=["totale", "giorno per giorno"]
)

st.title("COVID-19 in Italia")
is_log = st.checkbox(label="Scala logaritmica", value=False)
scale = alt.Scale(type="symlog") if is_log else alt.Scale(type="linear")

st.markdown("Che dato vorresti visualizzare?")
features = [
    "ricoverati_con_sintomi",
    "terapia_intensiva",
    "totale_ospedalizzati",
    "isolamento_domiciliare",
    "totale_attualmente_positivi",
    "nuovi_attualmente_positivi",
    "dimessi_guariti",
    "deceduti",
    "totale_casi",
    "tamponi",
]
feature = st.selectbox(
    label="Scegli...", options=features, format_func=formatter, index=8
)

# %%
# TOTAL NUMBERS
if choice == "totale":
    st.markdown("## Dato totale")
    st.markdown("### Trend in tutta Italia")

    general = data.groupby("data", as_index=False).sum()

    st.altair_chart(
        alt.Chart(general)
        .mark_line(point=True)
        .encode(
            x=alt.X("data:T", title="Mese e giorno"),
            y=alt.Y(f"{feature}:Q", title=formatter(feature), scale=scale),
            tooltip=[
                alt.Tooltip(f"{feature}", title=formatter(feature)),
                alt.Tooltip("data", title="Data", type="temporal"),
            ],
        )
        .properties(width=500, height=1000)
        .interactive()
    )

    # %%
    st.markdown("### Divisione per regione")
    region_options = data["denominazione_regione"].unique().tolist()
    regions = st.multiselect(
        label="Regioni",
        options=region_options,
        default=["Lombardia", "Veneto", "Emilia Romagna", "Trento"],
    )
    # %%
    final_all = data.groupby(["data", "denominazione_regione"], as_index=False).sum()
    final = final_all[final_all["denominazione_regione"].isin(regions)]
    # %%

    st.altair_chart(
        alt.Chart(final)
        .mark_line(point=True)
        .encode(
            x=alt.X("data:T", title="Mese e giorno"),
            y=alt.Y(f"{feature}:Q", title=formatter(feature), scale=scale),
            color="denominazione_regione:N",
            tooltip=[
                alt.Tooltip("denominazione_regione", title="Regione"),
                alt.Tooltip(f"{feature}", title=formatter(feature)),
                alt.Tooltip("data", title="Data", type="temporal"),
            ],
        )
        .properties(width=500, height=1000)
        .interactive()
    )
else:
    st.markdown("## Variazione giorno-per-giorno")
    st.markdown("### Trend in tutta Italia")

    general = data.groupby("data", as_index=False).sum()
    general[f"{feature}"] = general[f"{feature}"].diff()
    general = general.dropna()

    st.altair_chart(
        alt.Chart(general)
        .mark_line(point=True)
        .encode(
            x=alt.X("data:T", title="Mese e giorno"),
            y=alt.Y(f"{feature}:Q", title=formatter(feature), scale=scale),
            tooltip=[
                alt.Tooltip(f"{feature}", title=formatter(feature)),
                alt.Tooltip("data", title="Data", type="temporal"),
            ],
        )
        .properties(width=500, height=1000)
        .interactive()
    )

    # %%
    st.markdown("### Divisione per regione")
    region_options = data["denominazione_regione"].unique().tolist()
    regions = st.multiselect(
        label="Selectable regions",
        options=region_options,
        default=["Lombardia", "Veneto", "Emilia Romagna", "Trento"],
    )
    # %%
    final_all = data.groupby(["data", "denominazione_regione"], as_index=False).sum()
    final_all = final_all[final_all["denominazione_regione"].isin(regions)]
    final = []
    for _, region in final_all.groupby("denominazione_regione"):
        region = region.sort_values("data")
        region["change"] = region[f"{feature}"].diff()
        final.append(region.dropna())

    final = pd.concat(final).reset_index(drop=True)
    # %%

    st.altair_chart(
        alt.Chart(final)
        .mark_line(point=True)
        .encode(
            x=alt.X("data:T", title="Mese e giorno"),
            y=alt.Y("change:Q", title=formatter(feature), scale=scale),
            color="denominazione_regione:N",
            tooltip=[
                alt.Tooltip("denominazione_regione", title="Region"),
                alt.Tooltip("change", title=f"{formatter(feature)} giorno-per-giorno"),
                alt.Tooltip(f"{feature}", title=f"{formatter(feature)} totale"),
                alt.Tooltip("data", title="Data", type="temporal"),
            ],
        )
        .properties(width=500, height=1000)
        .interactive()
    )
