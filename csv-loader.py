import streamlit as st
import polars as pl
import plotly.express as px
from sqlalchemy import create_engine
import io
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# Titolo dell'app
st.title("Analisi Avanzata dei File CSV con Polars e Streamlit")

# Caricamento del file CSV o Excel
uploaded_file = st.file_uploader("Carica un file (CSV o Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # Determina il tipo di file e carica con Polars
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pl.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pl.read_excel(uploaded_file)

        # Mostra un'anteprima dei dati
        st.subheader("Anteprima dei dati")
        st.dataframe(df.head(10).to_pandas())  # Mostra solo i primi 10 record

        # Informazioni di base
        st.subheader("Informazioni sul dataset")
        st.write(f"Numero di righe: {df.shape[0]}")
        st.write(f"Numero di colonne: {df.shape[1]}")

        # Esplorazione delle colonne
        st.subheader("Esplorazione delle colonne")
        column_to_explore = st.selectbox("Seleziona una colonna da esplorare:", df.columns)

        if column_to_explore:
            unique_values = df[column_to_explore].unique()
            st.write(f"Valori unici in '{column_to_explore}': {unique_values}")

            # Grafico di distribuzione
            if df[column_to_explore].dtype in [pl.Float64, pl.Int64]:
                st.bar_chart(df[column_to_explore].to_pandas().value_counts())

        # Visualizzazione grafica
        st.subheader("Visualizzazione grafica")
        x_axis = st.selectbox("Seleziona la colonna per l'asse X:", df.columns)
        y_axis = st.selectbox("Seleziona la colonna per l'asse Y:", df.columns)

        if st.button("Crea grafico"):
            fig = px.scatter(df.to_pandas(), x=x_axis, y=y_axis, title="Grafico a dispersione")
            st.plotly_chart(fig)

            # Scarica il grafico
            if st.button("Scarica grafico come immagine"):
                buf = io.BytesIO()
                fig.write_image(buf, format="png")
                st.download_button(
                    label="Scarica grafico come immagine",
                    data=buf.getvalue(),
                    file_name="grafico.png",
                    mime="image/png",
                )

        # Filtraggio avanzato
        st.subheader("Filtraggio avanzato")
        filters = {}
        for col in df.columns:
            if df[col].dtype == pl.Utf8:  # Colonne testuali
                value = st.text_input(f"Valore da cercare in '{col}':")
                if value:
                    filters[col] = value
            elif df[col].dtype in [pl.Float64, pl.Int64]:  # Colonne numeriche
                min_val = st.number_input(f"Minimo per '{col}':", value=df[col].min(), key=f"min_{col}")
                max_val = st.number_input(f"Massimo per '{col}':", value=df[col].max(), key=f"max_{col}")
                filters[col] = (min_val, max_val)

        if st.button("Applica filtri avanzati"):
            filtered_df = df
            for col, val in filters.items():
                if isinstance(val, tuple):  # Range numerico
                    filtered_df = filtered_df.filter((filtered_df[col] >= val[0]) & (filtered_df[col] <= val[1]))
                else:  # Testo
                    filtered_df = filtered_df.filter(filtered_df[col].str.contains(val))
            st.dataframe(filtered_df.to_pandas())

        # Raggruppamento e aggregazione
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

        # Analisi statistica
        st.subheader("Analisi statistica")
        if st.button("Mostra riepilogo statistico"):
            stats = df.describe().to_pandas()
            st.dataframe(stats)

        # Salvataggio dei dati modificati
        st.subheader("Esporta i dati modificati")
        if st.button("Scarica il dataset"):
            csv = df.write_csv()
            st.download_button(
                label="Scarica CSV",
                data=csv,
                file_name="dataset_modificato.csv",
                mime="text/csv",
            )

        # Integrazione con database
        st.subheader("Salva i dati in un database")
        db_url = st.text_input("Inserisci la stringa di connessione al database (es. SQLite o PostgreSQL):")

        if st.button("Salva nel database"):
            try:
                engine = create_engine(db_url)
                df.to_pandas().to_sql("dataset", con=engine, if_exists="replace", index=False)
                st.success("Dati salvati con successo nel database!")
            except Exception as e:
                st.error(f"Errore durante il salvataggio: {e}")

        # Machine Learning
        st.subheader("Regressione lineare di base")
        target_column = st.selectbox("Seleziona la colonna target:", df.columns)

        if st.button("Addestra modello"):
            X = df.drop(columns=[target_column]).to_pandas()
            y = df[target_column].to_pandas()
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            model = LinearRegression()
            model.fit(X_train, y_train)
            score = model.score(X_test, y_test)
            st.write(f"R2 Score del modello: {score}")

    except Exception as e:
        st.error(f"Errore durante la lettura del file: {e}")
