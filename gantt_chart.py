import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

# Your tab-delimited data (as a multi-line string)
data = """
Task ID	Created At	Completed At	Last Modified	Name	Section/Column	Assignee	Assignee Email	Start Date	Due Date	Tags	Notes	Projects	Parent task	Blocked By (Dependencies)	Blocking (Dependencies)	Priority	Status	Notes
1.20936E+15	2/8/25	2/11/25	2/11/25	Define roles & responsibilities	Project Planning & Logistics	Nora Amrani	nora24amrani@gmail.com		2/8/25			IED Project				Low		
1.20936E+15	2/8/25	2/11/25	2/11/25	Select project idea	Project Planning & Logistics				2/11/25			IED Project				High		
1.20936E+15	2/8/25	2/8/25	2/8/25	"Set up a communication platform
"	Project Planning & Logistics	Nora Amrani	nora24amrani@gmail.com		2/8/25			IED Project						
1.20936E+15	2/8/25		2/15/25	Establish budget & acquire materials	Project Planning & Logistics	Ethan Katz	thnkatz@gmail.com		2/15/25			IED Project				Medium		
1.20936E+15	2/8/25	2/25/25	2/25/25	Research & benchmarking	System Concept Proposal (Milestone 1)	Edwards F8	edwardsdf8@gmail.com		2/16/25			IED Project						
1.20936E+15	2/8/25	2/25/25	2/25/25	Create Doc concept memo	System Concept Proposal (Milestone 1)	Lizeth Ramirez	lizethgr0924@gmail.com		2/18/25			IED Project						
1.20936E+15	2/8/25	2/25/25	2/25/25	Create PowerPoint presentation	System Concept Proposal (Milestone 1)	Lizeth Ramirez	lizethgr0924@gmail.com		2/18/25			IED Project						
1.20936E+15	2/8/25	2/25/25	2/25/25	System Concept Presentation	System Concept Proposal (Milestone 1)	Nora Amrani	nora24amrani@gmail.com		2/21/25			IED Project						
1.20936E+15	2/8/25		2/25/25	System Concept Memo	System Concept Proposal (Milestone 1)	Nora Amrani	nora24amrani@gmail.com		2/25/25			IED Project						
1.2095E+15	2/25/25		2/25/25	Assemble components	Prototype Development				3/20/25			IED Project						
1.20936E+15	2/8/25		2/26/25	Delegate design subsystems (hardware, software, integration)	Prototype Development				2/25/25			IED Project						
1.20936E+15	2/8/25		2/25/25	Purchase components	Prototype Development				3/2/25			IED Project						
1.20936E+15	2/8/25		2/26/25	Integrate subsystems	Prototype Development	Lizeth Ramirez	lizethgr0924@gmail.com		4/7/25			IED Project						
1.20936E+15	2/8/25		2/26/25	Conduct performance testing	Prototype Demonstration (Milestone 2)	Ethan Katz	thnkatz@gmail.com		\t\tIED Project				High		
1.20936E+15	2/8/25		2/8/25	Prepare demo script & materials	Prototype Demonstration (Milestone 2)							IED Project						
1.20936E+15	2/8/25		2/8/25	Demonstration	Prototype Demonstration (Milestone 2)							IED Project						
1.20936E+15	2/8/25		2/8/25	Peer evaluation & feedback	Prototype Demonstration (Milestone 2)							IED Project						
1.20936E+15	2/8/25		2/8/25	Final refinements	Final Design Review & Documentation (Milestone 3)							IED Project						
1.20936E+15	2/8/25		2/8/25	Prepare technical report & PowerPoint	Final Design Review & Documentation (Milestone 3)							IED Project						
1.20936E+15	2/8/25		2/8/25	Rehearse final presentation	Final Design Review & Documentation (Milestone 3)							IED Project						
1.20936E+15	2/8/25		2/8/25	Design Review Report	Final Design Review & Documentation (Milestone 3)							IED Project						
1.20936E+15	2/8/25		2/8/25	Design Review Presentation	Final Design Review & Documentation (Milestone 3)							IED Project	
"""

# Read the data into a DataFrame
df = pd.read_csv(StringIO(data), sep="\t")

# Fill missing Start Dates with the "Created At" date and convert dates to datetime objects.
df['Start Date'] = df['Start Date'].fillna(df['Created At'])
df['Start Date'] = pd.to_datetime(df['Start Date'], format='%m/%d/%y', errors='coerce')
df['Due Date'] = pd.to_datetime(df['Due Date'], format='%m/%d/%y', errors='coerce')

# --- Define color mappings ---
# Fill color (for bar body) based on the task section.
section_colors = {
    "Project Planning & Logistics": "lightblue",
    "System Concept Proposal (Milestone 1)": "lightgreen",
    "Prototype Development": "lightyellow",
    "Prototype Demonstration (Milestone 2)": "lightcoral",
    "Final Design Review & Documentation (Milestone 3)": "lightgrey"
}
# Accent (border) color based on the assignee.
assignee_colors = {
    "Nora Amrani": "blue",
    "Ethan Katz": "red",
    "Lizeth Ramirez": "green",
    "Edwards F8": "purple"
}

# --- Create the timeline chart.
# Using color="Section/Column" and providing a discrete color mapping gives us a legend for sections.
fig = px.timeline(
    df,
    x_start="Start Date",
    x_end="Due Date",
    y="Name",
    color="Section/Column",
    color_discrete_map=section_colors,
    hover_data=['Assignee', 'Priority']
)

# Reverse the y-axis so that tasks are listed top-down.
fig.update_yaxes(autorange="reversed")

# --- Update each trace's marker to include an accent (border) color per task based on assignee.
# When using color grouping, each trace represents a section.
for trace in fig.data:
    # 'trace.name' holds the section (e.g., "Project Planning & Logistics")
    # Filter rows for this section to get the assignees for each bar in the trace.
    sub_df = df[df['Section/Column'] == trace.name]
    border_colors = sub_df['Assignee'].map(assignee_colors).fillna('black').tolist()
    trace.marker.line.color = border_colors
    trace.marker.line.width = 2
    # Assign a legendgroup to these section traces so their legend remains together.
    trace.legendgroup = "Section"

# --- Add dummy scatter traces to create a separate legend for assignees.
# These traces will not be plotted but will show the assignee names and their accent colors.
unique_assignees = df['Assignee'].dropna().unique()
for assignee in unique_assignees:
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=10, color=assignee_colors.get(assignee, 'black')),
            legendgroup="Assignee",
            showlegend=True,
            name=f"Assignee: {assignee}"
        )
    )

# --- Update layout for clarity.
fig.update_layout(
    title="Project Gantt Chart",
    xaxis_title="Date",
    yaxis_title="Task",
    margin=dict(l=20, r=20, t=50, b=20)
)

fig.show()
fig.write_html("index.html")
