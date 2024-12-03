import streamlit as st
import polars as pl

# Titolo dell'app
st.title("Analisi dei file CSV con Polars e Streamlit")

# Caricamento del file CSV
uploaded_file = st.file_uploader("Carica un file CSV", type=["csv"])

if uploaded_file:
    # Leggi il CSV con Polars
    try:
        # Leggere il file con Polars
        df = pl.read_csv(uploaded_file)

        # Mostra una preview dei dati
        st.subheader("Anteprima dei dati")
        st.dataframe(df.head(10).to_pandas())  # Converti in pandas per visualizzazione

        # Informazioni di base sul dataset
        st.subheader("Informazioni sul dataset")
        st.write(f"Numero di righe: {df.shape[0]}")
        st.write(f"Numero di colonne: {df.shape[1]}")

        # Operazioni sui dati
        st.subheader("Operazioni sui dati")
        
        # 1. Filtraggio su una colonna
        column_to_filter = st.selectbox("Seleziona una colonna per il filtraggio:", df.columns)
        if column_to_filter:
            unique_values = df[column_to_filter].unique()
            value_to_filter = st.selectbox(f"Filtra per valore in '{column_to_filter}':", unique_values)
            if st.button("Applica filtro"):
                filtered_df = df.filter(df[column_to_filter] == value_to_filter)
                st.dataframe(filtered_df.to_pandas())
                st.write(f"Righe filtrate: {filtered_df.shape[0]}")

        # 2. Raggruppamento e aggregazione
        st.subheader("Raggruppamento e aggregazione")
        column_to_group = st.selectbox("Seleziona una colonna per il raggruppamento:", df.columns)
        aggregation_type = st.selectbox("Tipo di aggregazione:", ["count", "sum", "mean", "max", "min"])
        if st.button("Applica aggregazione"):
            if aggregation_type == "count":
                result = df.groupby(column_to_group).count()
            elif aggregation_type == "sum":
                result = df.groupby(column_to_group).sum()
            elif aggregation_type == "mean":
                result = df.groupby(column_to_group).mean()
            elif aggregation_type == "max":
                result = df.groupby(column_to_group).max()
            elif aggregation_type == "min":
                result = df.groupby(column_to_group).min()

            st.dataframe(result.to_pandas())
            st.write("Risultato dell'aggregazione.")

        # 3. Salvataggio del file manipolato
        st.subheader("Esporta i dati modificati")
        if st.button("Scarica il file filtrato o aggregato"):
            csv = filtered_df.write_csv() if 'filtered_df' in locals() else df.write_csv()
            st.download_button(
                label="Scarica CSV",
                data=csv,
                file_name="dataset_modificato.csv",
                mime="text/csv",
            )
    except Exception as e:
        st.error(f"Errore durante la lettura del file CSV: {e}")
