from plotly.subplots import make_subplots
import plotly.graph_objects as go
import chomp_learning
import pandas as pd
import random
from typing import List
import numpy as np
import webbrowser

def choose_css_colors(n) -> List[str]:
    css_colors = ["Red", "Green", "Yellow", "Blue", 
                  "Magenta", "ForestGreen", "YellowGreen", "BlueViolet",
                  "DarkRed", "LightGreen", "Orange", "Orchid", "Salmon",
                  "Plum", "Coral", "DodgerBlue", "LimeGreen", "Gold"]

    if n > len(css_colors):
        raise ValueError("n nem lehet nagyobb minta ahány css szín van")
    
    selected_colors = random.sample(css_colors, n)
    random.shuffle(selected_colors)
    return selected_colors

def format_coord(coord_str: str) -> str:
    coord_tuple = eval(coord_str)
    return f'sor {coord_tuple[0]+1}, oszl. {coord_tuple[1]+1}'

def sort_dict_by_tuple_keys(d):
    sorted_keys = sorted(d.keys(), key=lambda k: (len(k), str(k)))
    sorted_dict = {k: d[k] for k in sorted_keys}
    return sorted_dict

def make_report(log_name: str) -> None:
    chomp_learning.init_logs(log_name)

    fig = make_subplots(rows=11, cols=3) #, subplot_titles=tuple(str(k) for k in sort_dict_by_tuple_keys(chomp_learning.logs).keys()))
    positions = []
    for r in range(11):
        for c in range(3):
            positions.append((r+1, c+1))

    added_choices = {}
    selected_colors = choose_css_colors(11)

    for p, log in enumerate(sort_dict_by_tuple_keys(chomp_learning.logs)):
        df = pd.DataFrame(chomp_learning.logs[log])
        
        df2 = pd.DataFrame(df["weights"].tolist(), columns=[f"{i}" for i in list(df.options.tolist()[0])])
        df2["total"] = np.sum(df2, axis=1)

        df3 = df2.pipe(lambda x: x.div(x['total'], axis='index'))
        df3.drop("total", axis=1, inplace=True)
        
        melteddf = pd.melt(df3, var_name='Column', value_name='Value', ignore_index=False).reset_index()
        melteddf["Column"] = melteddf["Column"].apply(format_coord)
        # legend_group_name = ",".join(melteddf.Column.unique())

        for c in melteddf.Column.unique():
            if c not in added_choices:
                added_choices.update({c: selected_colors.pop(0)})
                fig.add_trace(
                    go.Line(x=melteddf["index"], y=melteddf.loc[melteddf["Column"]==c]["Value"], name=c, legendgroup = c, showlegend=True, line=dict(color=added_choices[c])),
                    row=positions[p][0], col=positions[p][1]
                )
            else:
                fig.add_trace(
                    go.Line(x=melteddf["index"], y=melteddf.loc[melteddf["Column"]==c]["Value"], name=c, legendgroup = c, showlegend=False, line=dict(color=added_choices[c])),
                    row=positions[p][0], col=positions[p][1]
                )

    fig.update_layout(height=2000, width=900, title_text=f"Helyzetek és lépések - Memória szett neve: {log_name}")
    fig.write_html(log_name+".html")
    #fig.show()
    webbrowser.open(log_name+".html")

if __name__ == "__main__":
    make_report("alfa")
    # make_report("t10")
    # make_report("t100")
    # make_report("t500")
    # make_report("t1000")
    # make_report("t2000")
    # make_report("t10000")
    # make_report("t100000")