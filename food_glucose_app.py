import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Sample combined_df (replace with your actual DataFrame)
# Ensure 'time' is in datetime format
combined_df=pd.read_csv("food_glucose.csv")
combined_df['time'] = pd.to_datetime(combined_df['time'])

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div([
        html.H3("Food Entries"),
        dcc.Graph(
            id='food-scatter',
            config={'displayModeBar': False}  # Hide unnecessary toolbar
        )
    ], style={'height': '50%'}),
    html.Div([
        html.H3("Glucose Levels (2 Hours After Selected Food)"),
        dcc.Graph(
            id='glucose-line',
            config={'displayModeBar': False}  # Hide unnecessary toolbar
        )
    ], style={'height': '50%'})
])

# Callback to update the food scatter plot
@app.callback(
    Output('food-scatter', 'figure'),
    Input('food-scatter', 'id')  # Dummy input to render the initial scatter plot
)
def update_food_scatter(_):
    # Create scatter plot of food entries
    # fig = px.scatter(
    #     combined_df.dropna(subset=['food']),  # Only rows with food data
    #     x='time',
    #     # y=[0] * len(combined_df.dropna(subset=['food'])),  # Align points along x-axis
    #     y='time_of_day',
    #     labels={'food': 'Food'},
    #     title="Food Scatter Plot",
    #     hover_data={'food': True}  # Show food labels on hover
    #     size=[10] * len(combined_df.dropna(subset=['food']))  # Fixed bubble size
    # )

    # Create the scatter plot
    fig = px.scatter(
        combined_df.dropna(subset=['food']),
        x='time',
        y='time_of_day',
        size='spike_size',  # Use spike size to control bubble size
        labels={'time': 'Time'},
        title="Food Scatter Plot with Bubble Size Based on Glucose Spike",
        hover_data={'food': True, 'spike_size': True}  # Show spike size on hover
    )

    return fig

@app.callback(
    Output('glucose-line', 'figure'),
    Input('food-scatter', 'clickData')  # Input from scatter plot click
)
def update_glucose_chart(clickData):
    if clickData is None:
        # Return an empty figure initially
        return go.Figure()

    # Extract the clicked time from scatter plot
    clicked_time = pd.to_datetime(clickData['points'][0]['x'])

    # Filter glucose data for 2 hours after the clicked time
    glucose_range = combined_df[
        (combined_df['time'] > clicked_time) &
        (combined_df['time'] <= clicked_time + pd.Timedelta(hours=2))
    ].dropna(subset=['glucose'])

    # Create a line chart for the filtered glucose data
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=glucose_range['time'],
        y=glucose_range['glucose'],
        mode='lines+markers',
        name='Glucose Levels',
        line=dict(color='blue'),
    ))

    # Update layout
    fig.update_layout(
        title=f"Glucose Levels (2 Hours After {clicked_time.strftime('%Y-%m-%d %H:%M:%S')})",
        xaxis_title="Time",
        yaxis_title="Glucose Levels (mg/dL)",
        template="plotly_white"
    )

    return fig


# Callback to update the glucose line chart based on selected food oarted.
if __name__ == '__main__':
    app.run_server(debug=True)