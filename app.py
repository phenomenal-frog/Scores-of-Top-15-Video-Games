from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import statsmodels

TOP_GAMES = 15
MIN_YEAR = 2007
MAX_YEAR = 2018

# Read the entire dataset into the dataframe
main_df = pd.read_csv("Modified_2007-2018_game_sales_data.csv", encoding='unicode_escape')
# Combine the names and platforms columns. Each version of a game will be treated as a separate game.
main_df["Name"] = main_df["Name"] + " (" + main_df["Platform"] + ")"


# Returns a dataframe with only the top 15 shipped games for the specified year
def get_year_data(selected_year):
    data = []  # Think like a 2-D list
    for i in range(TOP_GAMES):  # Returns a list of rows for the conditional
        row = main_df.loc[main_df.Year == selected_year].values[i]
        data.append(row)
    new_df = pd.DataFrame(data)
    new_df.columns = ["Rank", "Name", "Platform", "Publisher", "Developer",
                      "Critic_Score", "User_Score", "Total_Shipped", "Year"]
    return new_df


# Returns the average amount of copies shipped for the top 15 shipped games for the specified year
def get_mean_shipped(selected_year):
    temp_df = get_year_data(selected_year)
    mean = 0.0
    for i in range(len(temp_df)):
        mean += temp_df.Total_Shipped[i]
    mean /= TOP_GAMES
    return mean


# Returns the average user score for the top 15 shipped games for the specified year
def get_mean_user_score(selected_year):
    temp_df = get_year_data(selected_year)
    mean = 0.0
    for i in range(len(temp_df)):
        mean += temp_df.User_Score[i]
    mean /= TOP_GAMES
    return mean


# Returns the average critic score for the top 15 shipped games for the specified year
def get_mean_critic_score(selected_year):
    temp_df = get_year_data(selected_year)
    mean = 0.0
    for i in range(len(temp_df)):
        mean += temp_df.Critic_Score[i]
    mean /= TOP_GAMES
    return mean


# Creates the dataframe for creating the scatter plot for looking at the relationship between year and average score
# for each 15 game
def create_scatter_df():
    data = []
    for i in range(MIN_YEAR, MAX_YEAR + 1):
        mean_shipped = get_mean_shipped(i)
        mean_user_score = get_mean_user_score(i)
        mean_critic_score = get_mean_critic_score(i)
        row1 = [i, mean_shipped, mean_user_score, "User"]
        row2 = [i, mean_shipped, mean_critic_score, "Critic"]
        data.append(row1)
        data.append(row2)
    new_df = pd.DataFrame(data)
    new_df.columns = ["Year ", "Average_Total_Shipped (millions) ", "Average_Score ", "Score_Type "]
    return new_df


# Creates the dataframe for the box plot that can be used to create statistical information around scores
def create_box_plot_df(selected_year_1, selected_year_2):
    data = []
    # The simplified data from the first year input will be collected
    temp_df_1 = get_year_data(selected_year_1)
    for i in range(len(temp_df_1)):
        year = str(selected_year_1)  # Changing the year to a string will keep box plot x-axis from changing
        name = temp_df_1.Name[i]
        score = temp_df_1.User_Score[i]
        row1 = [year, name, score, "User"]
        score = temp_df_1.Critic_Score[i]
        row2 = [year, name, score, "Critic"]
        data.append(row1)
        data.append(row2)
    # The simplified data from the second year input will be collected
    temp_df_2 = get_year_data(selected_year_2)
    for i in range(len(temp_df_2)):
        year = str(selected_year_2)
        name = temp_df_2.Name[i]
        score = temp_df_2.User_Score[i]
        row1 = [year, name, score, "User"]
        score = temp_df_2.Critic_Score[i]
        row2 = [year, name, score, "Critic"]
        data.append(row1)
        data.append(row2)
    new_df = pd.DataFrame(data)
    new_df.columns = ["Year ", "Name ", "Score ", "Score_Type "]
    return new_df


# Creates the scatter plot that shows the average score for each top 15 game per year
def create_scatter_plot():
    return px.scatter(data_frame=create_scatter_df(),
                      x="Year ", y="Average_Score ",
                      color="Score_Type ",
                      symbol="Score_Type ",
                      symbol_sequence=['diamond', 'x'],
                      title="Average score of top 15 games vs the year",
                      hover_data=["Average_Total_Shipped (millions) "],
                      custom_data=["Score_Type "],  # Retrieve on click
                      trendline="ols")


# Creates the bar chart that shows the total shipment and score for each top game in the selected year
def create_bar_chart(selected_year, input_score_type):
    score_type = ''
    if input_score_type == 'User':
        score_type = "User_Score"
    elif input_score_type == 'Critic':
        score_type = "Critic_Score"
    return px.bar(data_frame=get_year_data(selected_year),
                  x="Name", y="Total_Shipped",
                  color=score_type,
                  barmode="group",
                  hover_data=["Publisher", "Developer"],
                  color_continuous_scale='bluered_r',
                  range_color=[1.0, 10.0],
                  title="Video games in " + str(selected_year),
                  labels={
                      "Name": "Video Game",
                      "Total_Shipped": "Lifetime copies shipped (millions)"},
                  height=600
                  )


# Creates the box plot that shows the variability of the scores for each top game in the selected years
def create_box_plot(selected_year_1, selected_year_2):
    return px.box(data_frame=create_box_plot_df(selected_year_1, selected_year_2),
                  x="Year ",
                  y="Score ",
                  color="Score_Type ",
                  points="all",
                  title="The spread of scores",
                  hover_data=["Name "]
                  )


# This specific visualization is always present
fig1 = create_scatter_plot()
fig1.update_layout(clickmode='event')  # Retrieve the x-value and y-value
fig1.update_traces(marker_size=8)


# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
app = Dash(__name__)

# The layout of how the website will look
app.layout = html.Div(children=[
    html.H1(children='Top 15 video games over the years'),

    html.Div(children='''
        Select the markers in the scatter plot below to view specific bar charts and box plots
    '''),

    dcc.Graph(
        id='scatter-plot-graph',
        figure=fig1
    ),

    html.Label('Right box plot selection'),
    dcc.Dropdown(
        id="right-box-plot-selector",
        options=create_scatter_df()['Year '].unique(),
        value='2018'  # Selected option
    ),
    html.Br(),

    dcc.Graph(
        id='box-plot-graph',
    ),

    dcc.Graph(
        id='bar-chart-graph'
    )
])


# Updates the visualization based on interactive features
@app.callback(
    Output(component_id='bar-chart-graph', component_property='figure'),
    Output(component_id='box-plot-graph', component_property='figure'),
    Input(component_id='scatter-plot-graph', component_property='clickData'),
    Input(component_id='right-box-plot-selector', component_property='value')
)
def update(clickData, value):
    # The default bar chart
    bar_fig = create_bar_chart(MIN_YEAR, 'Critic')
    bar_fig.update_layout(transition_duration=200)
    # The default box plot
    box_fig = create_box_plot(MIN_YEAR, MAX_YEAR)
    box_fig.update_layout(transition_duration=200)

    # Click input from scatter plot to update the bar chart
    if clickData is not None:
        if 'customdata' in clickData['points'][0]:
            # Use the year and score type from the clickData
            bar_fig = create_bar_chart(clickData['points'][0]['x'], clickData['points'][0]['customdata'][0])
            bar_fig.update_layout(transition_duration=200)

    # Click input from scatter plot to update the box plot
    if clickData is not None:
        if 'customdata' in clickData['points'][0]:
            box_fig = create_box_plot(clickData['points'][0]['x'], int(value))
            box_fig.update_layout(transition_duration=200)

    return bar_fig, box_fig


if __name__ == '__main__':
    app.run_server(debug=False)
