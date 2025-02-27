import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


with open("tasks.json", "r") as f:
    data = json.load(f)


df = pd.json_normalize(data["data"])


df["name"] = df["name"].str.title()


df["Start Date"] = pd.to_datetime(df["created_at"], utc=True).dt.tz_convert(None)


df["Due Date"] = pd.to_datetime(df["due_on"], errors="coerce")


df["Section/Column"] = df["memberships"].apply(
    lambda x: x[0]["section"]["name"] if isinstance(x, list) and len(x) > 0 else None
)


df["Assignee"] = df["assignee"].fillna("Unassigned").astype(str).str.strip()


def get_priority(cf_list):
    for field in cf_list:
        if field.get("name") == "Priority" and field.get("enum_value") is not None:
            return field["enum_value"].get("name")
    return None

df["Priority"] = df["custom_fields"].apply(get_priority)


section_colors = {
    "Project Planning & Logistics": "lightblue",
    "System Concept Proposal (Milestone 1)": "lightgreen",
    "Prototype Development": "lightyellow",
    "Prototype Demonstration (Milestone 2)": "lightcoral",
    "Final Design Review & Documentation (Milestone 3)": "lightgrey"
}


assignee_colors = {
    "Nora Amrani": "blue",
    "Edwards Doh": "purple",
    "Lizeth Ramirez": "green",
    "Ethan Katz": "red",
    "Blake Leichter": "orange",
    "Vidyut Baskar": "brown"
}


df["border_color"] = df["Assignee"].map(lambda x: assignee_colors.get(x, "black"))


df.sort_values("Start Date", inplace=True)
task_order = df["name"].tolist()


fig = px.timeline(
    df,
    x_start="Start Date",
    x_end="Due Date",
    y="name",
    color="Section/Column",
    color_discrete_map=section_colors,
    category_orders={"name": task_order},
    hover_data=["Assignee", "Priority", "notes"]
)


fig.update_yaxes(autorange="reversed")


for trace in fig.data:
    section_tasks = df[df["Section/Column"] == trace.name]
    colors = section_tasks["border_color"].tolist()
    trace.marker.line.color = colors
    trace.marker.line.width = 2
    trace.showlegend = False


for section, fill_color in section_colors.items():
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(symbol="square", size=10, color=fill_color, line=dict(width=0)),
            legendgroup="Section",
            showlegend=True,
            name=section
        )
    )


for name, border_color in assignee_colors.items():
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(symbol="square", size=10, color="black", line=dict(color=border_color, width=2)),
            legendgroup="Person",
            showlegend=True,
            name=name
        )
    )


fig.update_layout(
    title=dict(
        text="IED Gantt Chart",
        font=dict(family="Arial Black", size=20, color="black")
    ),
    xaxis_title=dict(
        text="Date",
        font=dict(family="Arial Black", size=18, color="black")
    ),
    yaxis_title=dict(
        text="Task",
        font=dict(family="Arial Black", size=18, color="black")
    ),
    legend_title_text="Legend",
    legend_title_font=dict(family="Arial Black", size=16, color="black"),
    margin=dict(l=20, r=150, t=70, b=20),
    legend=dict(x=1.02, y=1)
)


fig.update_xaxes(tickformat="%m/%d", dtick=648000000)  
fig.show()
fig.write_html("index.html")