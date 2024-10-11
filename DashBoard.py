import pandas as pd
import panel as pn
import hvplot.pandas
import plotly.graph_objects as go
import sankey as sk

# Data Handling Functions
def load_data(filename):
    """Load the CSV data and return a DataFrame."""
    df = pd.read_csv(filename)
    return pd.DataFrame(df)

def default_table(brand='All'):
    """Return a table filtered by brand or display the entire dataset."""
    filtered_data = car_data if brand == 'All' else car_data[car_data['Brand'] == brand]
    return pn.widgets.Tabulator(filtered_data, pagination='local', page_size=100, selectable=False)

def get_catalog(brand='All', year=None, price=None):
    """Apply filters for brand, year, and price, and return the filtered dataset."""
    filtered_data = car_data[
        ((car_data['Brand'] == brand) if brand != 'All' else True) &
        (car_data['Year'] >= year if year else True) &
        (car_data['Price'] <= price if price else True)
    ]
    return pn.widgets.Tabulator(filtered_data, selectable=False)

# Plotting Functions
def sankey_plot(car_brand, width, height):
    """Create a Sankey plot for the selected brand."""
    filtered_data = car_data[car_data['Brand'] == car_brand] if car_brand != 'All' else car_data
    return sk.make_sankey(filtered_data, 'Transmission', 'Fuel Type', width=width, height=height)

def interactive_plot(car_brand, year_slider, price_slider, width, height):
    """Create an interactive scatter plot."""
    filtered_data = car_data[(car_data['Year'] >= year_slider) & (car_data['Price'] <= price_slider)]
    if car_brand != 'All':
        filtered_data = filtered_data[filtered_data['Brand'] == car_brand]
    return filtered_data.hvplot.scatter(x='Year', y='Price', height=height, width=width, color='Brand')


def create_bar_chart(car_brand, year_slider, price_slider, width, height):
    """Create a bar chart to compare Model with EngineSize and Mileage based on selected brand, year, and price."""
    # Filter the data based on selected car brand, year, and price
    if car_brand == 'All':
        df = car_data  # Show all models if 'All' is selected
    else:
        df = car_data[car_data['Brand'] == car_brand]

    # Further filter by year and price
    df = df[(df['Year'] >= year_slider) & (df['Price'] <= price_slider)]

    # Select the relevant columns (Model, EngineSize, Mileage)
    df = df[['Model', 'Engine Size', 'Mileage']]

    # Reshape the data to long format (for better visualization)
    long_df = df.melt(id_vars='Model', value_vars=['Engine Size', 'Mileage'],
                      var_name='Attribute', value_name='Value')

    # Create the bar chart with enhancements (color, legend, tooltips, etc.)
    bar_chart = long_df.hvplot.bar(
        x='Model', y='Value', by='Attribute',
        title=f"Comparison of Engine Size and Mileage by Model for {car_brand}",
        width=width, height=height,
        stacked=False,  # Side-by-side bars
        color=['red', 'blue'],  # Custom colors for EngineSize and Mileage
        legend='top_right',  # Position the legend at the top right
        xlabel='Car Model', ylabel='Value',  # Axis labels
        hover_cols=['Model', 'Value', 'Attribute']  # Tooltip to show details
    )

    return bar_chart


# Plot Selection Logic
def get_selected_plot(plot_type, car_brand, year_slider, price_slider, width, height):
    """Switch between Scatter Plot and Sankey Diagram based on user selection."""
    if plot_type == 'Scatter Plot':
        return interactive_plot(car_brand, year_slider, price_slider, width, height)
    elif plot_type == 'Sankey Diagram':
        return sankey_plot(car_brand, width, height)
    elif plot_type == 'Bar Chart':
        return create_bar_chart(car_brand, year_slider, price_slider, width, height)

# Main function (the entry point of the script)
def main():
    """Initialize the dashboard components and serve the layout."""
    # Load data
    global car_data
    car_data = load_data('car_price.csv')
    pn.extension('plotly')

    # Widget Declarations
    car_brand = pn.widgets.Select(name='Brand', options=['All'] + list(car_data['Brand'].unique()), value='All')
    plot_selector = pn.widgets.Select(name='Plot Type', options=['Scatter Plot', 'Sankey Diagram', 'Bar Chart'], value='Scatter Plot')
    width = pn.widgets.IntSlider(name="Width", start=250, end=2000, step=250, value=1000)
    height = pn.widgets.IntSlider(name="Height", start=200, end=2500, step=100, value=500)
    year_slider = pn.widgets.IntSlider(name='Year', start=car_data['Year'].min(), end=car_data['Year'].max(), step=1)
    price_slider = pn.widgets.FloatSlider(name='Price', start=car_data['Price'].min(), end=car_data['Price'].max(), step=1000)

    # Create card containers for filters and results
    filter_card = pn.Card(pn.Column(year_slider, price_slider), title="Filter", width=320, collapsed=False)
    car_card = pn.Card(pn.Column(car_brand), title="Vehicle", width=320, collapsed=False)
    plot_card = pn.Card(pn.Column(plot_selector, width, height), title="Plot", width=320, collapsed=True)

    # Bindings
    plot = pn.bind(get_selected_plot, plot_selector, car_brand, year_slider, price_slider, width, height)
    catalog = pn.bind(get_catalog, car_brand, year_slider, price_slider)
    table = pn.bind(default_table, car_brand)

    main_content = pn.Tabs(
        ("Dataset", table),
        ("Filtered Data", catalog),
        ("Visualization", pn.Row(plot)),
        active=0
    )

    # Layout for the dashboard with background image and cool styling
    layout = pn.template.FastListTemplate(
        title="🚗 Cars Insights Dashboard",  # Adding icon for a cooler effect
        sidebar=[car_card, filter_card, plot_card],
        main=[main_content],
        header_background='black',  # Set the background color for the header
        accent_base_color="darkgray",  # Accent color for the theme
        header_color="white"  # Set the header text color to white for better readability
    )

    # Serve the layout
    layout.servable()
    layout.show()


# Run the main function to initialize and serve the dashboard
if __name__ == '__main__':
    main()
