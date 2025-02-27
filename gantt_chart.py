import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------
# 1. Load JSON Data from File
# -----------------------------
with open("tasks.json", "r") as f:
    data = json.load(f)

# Normalize the JSON data into a DataFrame
df = pd.json_normalize(data["data"])

# Capitalize each word in the task name
df["name"] = df["name"].str.title()

# -----------------------------
# 2. Process and Transform Data
# -----------------------------
# Convert created_at (tz-aware) to tz-naive and use it as the Start Date.
df["Start Date"] = pd.to_datetime(df["created_at"], utc=True).dt.tz_convert(None)

# Convert due_on to datetime (assumed tz-naive)
df["Due Date"] = pd.to_datetime(df["due_on"], errors="coerce")

# Extract Section/Column from memberships
df["Section/Column"] = df["memberships"].apply(
    lambda x: x[0]["section"]["name"] if isinstance(x, list) and len(x) > 0 else None
)

# Now, the assignee is provided as a string—strip any extra whitespace and default to "Unassigned"
df["Assignee"] = df["assignee"].fillna("Unassigned").astype(str).str.strip()

# Extract Priority from custom_fields (looking for the field named "Priority")
def get_priority(cf_list):
    for field in cf_list:
        if field.get("name") == "Priority" and field.get("enum_value") is not None:
            return field["enum_value"].get("name")
    return None

df["Priority"] = df["custom_fields"].apply(get_priority)

# -----------------------------
# 3. Define Color Mappings
# -----------------------------
# Fill colors for sections (bar interior)
section_colors = {
    "Project Planning & Logistics": "lightblue",
    "System Concept Proposal (Milestone 1)": "lightgreen",
    "Prototype Development": "lightyellow",
    "Prototype Demonstration (Milestone 2)": "lightcoral",
    "Final Design Review & Documentation (Milestone 3)": "lightgrey"
}

# Border (outline) colors based on the assignee names (the six names)
assignee_colors = {
    "Nora Amrani": "blue",
    "Edwards Doh": "purple",
    "Lizeth Ramirez": "green",
    "Ethan Katz": "red",
    "Blake Leichter": "orange",
    "Vidyut Baskar": "brown"
}

# Create a border_color column based on the Assignee using our mapping
df["border_color"] = df["Assignee"].map(lambda x: assignee_colors.get(x, "black"))

# -----------------------------
# 4. Sort DataFrame Chronologically
# -----------------------------
df.sort_values("Start Date", inplace=True)
task_order = df["name"].tolist()

# -----------------------------
# 5. Build the Gantt Chart
# -----------------------------
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

# Reverse y-axis so that earlier tasks appear at the top
fig.update_yaxes(autorange="reversed")

# Update each trace's marker to use the border_color for each task.
for trace in fig.data:
    section_tasks = df[df["Section/Column"] == trace.name]
    colors = section_tasks["border_color"].tolist()
    trace.marker.line.color = colors
    trace.marker.line.width = 2
    trace.showlegend = False

# Add dummy scatter traces for custom legend items.
# First, for Sections (using the fill colors only, no border).
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

# Next, for Persons (black square with a border in the assigned color).
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

# -----------------------------
# 6. Update Layout: Bold Headings and Custom Legend Title Formatting
# -----------------------------
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


fig.update_xaxes(tickformat="%m/%d", dtick=648000000)  # Adjust dtick as desired
fig.show()
fig.write_html("index.html")