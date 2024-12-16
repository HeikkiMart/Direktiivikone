# Author: Heikki Martikainen

import pandas as pd
import numpy as np

def aggregate_content(df, col_map):
    # Nimetään sarakkeet niin että niitä voidaan käsitellä, oli kyseessä Current tai Proposal
    df = df.rename(columns=col_map)

    # Custom aggregation function
    def custom_content_aggregation(group):
        return '\n'.join(
            f"{row['Point'] if row['Point'] else ''} {row['Letter'] if row['Letter'] else ''} {row['Content']}"
            for _, row in group.iterrows()
        )

    # Apply the custom aggregation and keep the first entries for other columns
    df_grouped = df.groupby('Article', as_index=False).apply(
        lambda group: pd.Series({
            'Code': group['Code'].iloc[0],
            'Point': group['Point'].iloc[0],
            'Letter': group['Letter'].iloc[0],
            'Subsection': group['Subsection'].iloc[0],
            'Content': custom_content_aggregation(group)
        })
    )

    # Palautetaan sarakkeiden alkuperäiset nimet
    reverse_map = {v: k for k, v in col_map.items()}
    df_grouped = df_grouped.rename(columns=reverse_map)

    return df_grouped

def combine(dfCurrent,dfProposal,rel_df,settings):

    dfCurrent.rename(columns={"Code #": "Code C", "Article #": "Article C", "Point #": "Point C","Letter #": "Letter C", "Subsection #": "Subsection C", "Content": "Content C"}, inplace=True)
    dfProposal.rename(columns={"Code #": "Code P", "Article #": "Article P", "Point #": "Point P","Letter #": "Letter P", "Subsection #": "Subsection P", "Content": "Content P"}, inplace=True)

    if settings == 1:
        # Jos käyttäjä haluaa tulokset artiklan tarkkuudella.
        column_mappingC = {
            'Code C': 'Code',
            'Article C': 'Article',
            'Point C': 'Point',
            'Letter C': 'Letter',
            'Subsection C': 'Subsection',
            'Content C': 'Content'
        }
        column_mappingP = {
            'Code P': 'Code',
            'Article P': 'Article',
            'Point P': 'Point',
            'Letter P': 'Letter',
            'Subsection P': 'Subsection',
            'Content P': 'Content'
        }

        dfCurrent = aggregate_content(dfCurrent, column_mappingC)
        dfProposal = aggregate_content(dfProposal, column_mappingP)

        
    dfCurrent = dfCurrent.reset_index()
    dfCurrent.rename(columns={'index': 'Order C'}, inplace=True)
    dfProposal = dfProposal.reset_index()
    dfProposal.rename(columns={'index': 'Order P'}, inplace=True)
    
    print("Current")
    print(dfCurrent)
    print("Proposal")
    print(dfProposal)
    print("Table")
    print(rel_df)
    rel_df.to_excel('rel.xlsx', index=False)
    # Step 1: Merge df_corr and df1 on 'Code #'
    df_combined = pd.merge(rel_df,dfProposal, on='Code P', how='outer')

    # Step 2: Merge the resulting df_combined with df2 on 'Code #'
    df_combined = pd.merge(df_combined, dfCurrent, on='Code C', how='outer')
    df_combined.drop(["Article C", "Point C", "Letter C","Subsection C","Article P", "Point P", "Letter P", "Subsection P"],axis=1,inplace=True)
    df_combined.fillna('', inplace=True)
    df_combined = df_combined[["Order P","Code P", "Content P","Order C","Code C", "Content C"]]
    df_combined['Match'] = np.where(df_combined['Content C'] == df_combined['Content P'], 1, 0)
    return df_combined