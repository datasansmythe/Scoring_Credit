import pandas as pd
import numpy as np
class DataAnalyzer():
    def __init__(self, df, metadata_df=None):
        """
        df : DataFrame principal à analyser
        metadata_df : DataFrame contenant les métadonnées (optionnel, doit avoir une colonne 'Row' et une 4e colonne avec la description)
        """
        self.df = df
        self.metadata_df = metadata_df

    def data_col_type(self):
        """Retourne les colonnes numériques, catégorielles et booléennes"""
        numerical_cols = self.df.select_dtypes(include=['int64', 'float64']).columns.tolist()

        bool_cols = [col for col in numerical_cols if self.df[col].dropna().nunique() == 2]
        numerical_cols = [col for col in numerical_cols if col not in bool_cols]

        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()

        return numerical_cols, categorical_cols, bool_cols

    def variable_description(self, name_variable):
        """Retourne la description d'une variable à partir de la table metadata"""
        if self.metadata_df is None:
            return "Aucune metadata disponible."
        try:
            return self.metadata_df[self.metadata_df.Row == name_variable].iloc[0, 3]
        except IndexError:
            return "Description non trouvée."

    def global_description_table(self, df=None):
        """
        Retourne une table de description globale sur les variables du DataFrame.
        Peut recevoir un DataFrame spécifique en argument pour décrire seulement une partie des colonnes.
        """
        if df is None:
            df = self.df  # par défaut, on utilise le dataframe principal

        rows = []
        numerical_cols, categorical_cols, bool_cols = self.data_col_type()

        # Restreindre les colonnes détectées aux colonnes présentes dans le df passé en argument
        numerical_cols = [col for col in numerical_cols if col in df.columns]
        categorical_cols = [col for col in categorical_cols if col in df.columns]
        bool_cols = [col for col in bool_cols if col in df.columns]

        # Variables numériques
        for col in numerical_cols:
            rows.append({
                'colonne': col,
                'nb_valeurs': df[col].count(),
                'valeurs_manquantes en %': round((df[col].isnull().sum()/df.shape[0] )*100,2),
                'moyenne': df[col].mean(),
                'max': df[col].max(),
                'min': df[col].min(),
                'Col_Description': self.variable_description(col)
            })

        # Variables booléennes
        for col in bool_cols:
            value_counts = df[col].value_counts(dropna=False)
            rows.append({
                'colonne': col,
                'nb_valeurs': df[col].count(),
                'valeurs_manquantes en %': round((df[col].isnull().sum()/df.shape[0])* 100, 2) ,
                'répartition en %': ', '.join([f"{k} ({round(v/df.shape[0]* 100,2)})" for k, v in value_counts.items()]),
                'Col_Description': self.variable_description(col)
            })

        # Variables catégorielles
        for col in categorical_cols:
            value_counts = df[col].value_counts(dropna=False)
            rows.append({
                'colonne': col,
                'nb_valeurs': df[col].count(),
                'valeurs_manquantes en %': round((df[col].isnull().sum()/df.shape[0] )* 100, 2),
                'nb_catégories_distinctes': df[col].nunique(dropna=True),
                'top_catégories en %': ', '.join([f"{k} ({round(v/df.shape[0]* 100,2)})" for k, v in value_counts.items()]),
                'Col_Description': self.variable_description(col)
            })
        
        data = pd.DataFrame(rows)
        data_final = data.sort_values(by= 'valeurs_manquantes en %' , ascending= False)
        return data_final
    
    def Global_info(self):
        """
        Retourne une liste d'informations sur la DataFrame.
        """
        rows = []
        col_const = [col for col in self.df.columns if self.df[col].nunique()==1]
        doublons = self.df[self.df.duplicated()]
        numerical_cols, categorical_cols, bool_cols = self.data_col_type()
        rows.append({
            'nombre de lignes' : self.df.shape[0],                                                                                        
            'nombre de colonnes' : self.df.shape[1], 
            'nombre de doublons' : doublons.shape[0],                                                                                
            'nombre de colonnes constantes ' :len(col_const), 
            'colonnes constantes' : col_const,   
            "Pourcentage de valeurs manquantes %" :  round((self.df.isnull().sum().sum()/np.prod(self.df.shape))* 100, 2),
            "dtypes"  : {"nombre de variables catégorielles" : len(categorical_cols), 
                         "nombre de variables numeriques": len(numerical_cols),
                         "nombre de variables Booléennes": len(bool_cols)}                                                                         
        })
        return rows
