from data_loader import load_and_clean_data
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go

# Loading the data
df = load_and_clean_data()

# FIGURE 1: Monthly Orders with Promotion Periods
df['orders'] = df['orders'][df['orders']['status'] != 'Cancelled']
df['orders']['order_date'] = pd.to_datetime(df['orders']['order_date'])
monthly_orders = df['orders'].set_index('order_date').resample('ME').size().reset_index(name='order_count')

promo_ranges = [
    ("Summer Sale 2024", pd.to_datetime(df['promotions'].loc[1, 'start_date']), pd.to_datetime(df['promotions'].loc[1, 'end_date']), '#FF9900'),
    ("Black Friday Deal", pd.to_datetime(df['promotions'].loc[2, 'start_date']), pd.to_datetime(df['promotions'].loc[2, 'end_date']), '#FF4C4C'),
    ("New Year Special", pd.to_datetime(df['promotions'].loc[3, 'start_date']), pd.to_datetime(df['promotions'].loc[3, 'end_date']), '#33CC99'),
    ("Spring Cleaning", pd.to_datetime(df['promotions'].loc[4, 'start_date']), pd.to_datetime(df['promotions'].loc[4, 'end_date']), '#3399FF'),
    ("Back to School", pd.to_datetime(df['promotions'].loc[5, 'start_date']), pd.to_datetime(df['promotions'].loc[5, 'end_date']), '#CC66FF')
]

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=monthly_orders['order_date'],
    y=monthly_orders['order_count'],
    mode='lines+markers',
    name='Monthly Orders',
    line=dict(color='#005B99', width=2.5),
    marker=dict(size=8)
))
for label, start, end, color in promo_ranges:
    fig1.add_vrect(
        x0=start,
        x1=end,
        fillcolor=color,
        opacity=0.2,
        layer="below",
        line_width=0
    )
for label, _, _, color in promo_ranges:
    fig1.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='lines',
        name=label,
        line=dict(color=color, width=10)
    ))
fig1.update_layout(
    title=dict(text='Monthly Order Volume with Promotion Periods', font=dict(size=18, color='#333')),
    xaxis_title='Date',
    yaxis_title='Number of Orders',
    height=500,
    template='plotly_white',
    font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.9)", bordercolor="#E0E0E0", borderwidth=1),
    margin=dict(l=50, r=50, t=80, b=50),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# FIGURE 2: Category Distribution Pie Chart
cat_to_prod = pd.merge(left=df['categories'], right=df['products'], left_on='category_id', right_index=True, how='inner')
prod_to_OI = pd.merge(left=cat_to_prod, right=df['order_items'], left_index=True, right_on='product_id', how='left')
category_order_counts = prod_to_OI.groupby('category_name').size().reset_index(name='count')
fig2 = px.pie(
    category_order_counts,
    values='count',
    names='category_name',
    title='Category Distribution by Order Volume',
    color_discrete_sequence=px.colors.sequential.Teal,
    height=500
)
fig2.update_layout(
    font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
    title=dict(font=dict(size=18, color='#333')),
    margin=dict(l=50, r=50, t=80, b=50),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# FIGURE 3: Supplier Lead Time vs Orders
supplier_merged = df['product_suppliers'].merge(df['products'][['product_name']], left_on='product_id', right_index=True, how='left')
OI_to_sup = df['order_items'].merge(supplier_merged[['product_id', 'lead_time_days']], on='product_id', how='left')
order_counts = OI_to_sup.groupby(['product_id', 'lead_time_days'], observed=True).size().reset_index(name='order_count')
fig3 = px.scatter(
    order_counts,
    x='lead_time_days',
    y='order_count',
    trendline='ols',
    title='Product Order Volume vs Supplier Lead Time',
    labels={'lead_time_days': 'Lead Time (Days)', 'order_count': 'Number of Orders'},
    height=500,
    color_discrete_sequence=['#005B99']
)
fig3.update_layout(
    font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
    title=dict(font=dict(size=18, color='#333')),
    template='plotly_white',
    margin=dict(l=50, r=50, t=80, b=50),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# FIGURE 4: Review Ratings Distribution
df['reviews']['rating'] = df['reviews']['rating'].astype(dtype='int32')
review_counts = df['reviews']['rating'].value_counts().sort_index()
fig4 = px.bar(
    review_counts,
    x=review_counts.index,
    y=review_counts.values,
    labels={'x': 'Rating (Stars)', 'y': 'Number of Reviews'},
    title='Distribution of Product Review Ratings',
    template='plotly_white',
    color_discrete_sequence=['#33CC99'],
    height=500
)
fig4.update_layout(
    font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
    title=dict(font=dict(size=18, color='#333')),
    margin=dict(l=50, r=50, t=80, b=50),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# FIGURE 5: Customer Funnel
registered_cust_count = df['customers']['registration_date'].shape[0]
cust_placed_orders_count = df['orders']['customer_id'].nunique()
repeated_cust_count = (df['orders'].groupby('customer_id').size() > 1).sum()
cust_review_count = df['reviews']['customer_id'].nunique()
funnel_data = dict(
    number=[registered_cust_count, cust_placed_orders_count, repeated_cust_count, cust_review_count],
    stage=["Registered", "Placed Orders", "Repeated Customers", "Reviewers"]
)
fig5 = px.funnel(
    funnel_data,
    x='number',
    y='stage',
    title='Customer Engagement Funnel',
    color='stage',
    color_discrete_sequence=px.colors.sequential.Blues_r,
    height=500
)
fig5.update_layout(
    font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
    title=dict(font=dict(size=18, color='#333')),
    margin=dict(l=50, r=50, t=80, b=50),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# FIGURE 6: Days Since Last Order
today = pd.Timestamp.today()
last_orders = df['orders'].groupby('customer_id')['order_date'].max().reset_index()
last_orders['days_since_last_order'] = (today - last_orders['order_date']).dt.days
fig6 = px.histogram(
    last_orders,
    x='days_since_last_order',
    nbins=30,
    labels={'days_since_last_order': 'Days Since Last Order', 'y': 'Number of Customers'},
    title='Customer Retention Analysis',
    color_discrete_sequence=['#FF9900'],
    height=500
)
fig6.update_layout(
    font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
    title=dict(font=dict(size=18, color='#333')),
    template='plotly_white',
    margin=dict(l=50, r=50, t=80, b=50),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# FIGURE 7: State-wise Distribution
orders_per_states = df['orders'].groupby('shipping_state').size().reset_index(name='count')
customers_per_state = df['customers'].groupby('state').size().reset_index(name='count')
fig7 = px.choropleth(
    orders_per_states,
    locations='shipping_state',
    locationmode="USA-states",
    color='count',
    scope="usa",
    title='Orders Distribution by State',
    color_continuous_scale="Viridis",
    height=500
)
fig7.update_layout(
    font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
    title=dict(font=dict(size=18, color='#333')),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    geo=dict(
        showlakes=True,
        lakecolor='#E6F3FF',
        showland=True,
        landcolor='#F5F5F5',
        showsubunits=True,
        subunitcolor="#D0D0D0"
    ),
    margin=dict(l=50, r=50, t=80, b=50)
)

# FIGURE 8: Average Order Value
aov_value = df['orders']['total_amount'].mean()
fig8 = go.Figure(go.Indicator(
    mode="number",
    value=aov_value,
    title={"text": "Average Order Value (AOV)", "font": {"size": 22, "color": "#333"}},
    number={"font": {"size": 48, "color": "#2e8b57"}, "prefix": "$", "valueformat": ".2f"},
))
fig8.update_layout(
    height=200,
    font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=50, b=20)
)

# FIGURE 9: Top 10 SKUs
OI_to_prod = df['order_items'].merge(df['products'][['category_id']], left_on='product_id', right_index=True, how='inner')
OI_to_cat = OI_to_prod.merge(df['categories'][['category_name']], left_on='category_id', right_index=True, how='inner')
top_skus = OI_to_cat.groupby(['product_id', 'category_id', 'category_name'])['quantity'].sum().reset_index()
top_skus = top_skus.sort_values(by='quantity', ascending=False).head(10)
top_skus = top_skus.merge(df['products'][['product_name']], left_on='product_id', right_index=True, how='left')
fig9 = px.bar(
    top_skus,
    x='product_name',
    y='quantity',
    color='category_name',
    title='Top 10 Selling SKUs by Quantity',
    labels={'product_name': 'Product', 'quantity': 'Units Sold'},
    hover_data=['product_id'],
    color_discrete_sequence=px.colors.sequential.Magenta,
    height=500
)
fig9.update_layout(
    xaxis_tickangle=-45,
    font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
    title=dict(font=dict(size=18, color='#333')),
    template='plotly_white',
    margin=dict(l=50, r=50, t=80, b=50),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

# FIGURE 10: Orders Per Category Heatmap
cat_prod = pd.merge(df['categories'], df['products'], left_index=True, right_on='category_id', how='inner')
prod_orders = pd.merge(cat_prod, df['order_items'], left_index=True, right_on='product_id', how='inner')
final_df = pd.merge(prod_orders, df['orders'][['order_date']], left_on='order_id', right_index=True, how='inner')
final_df['month'] = pd.to_datetime(final_df['order_date']).dt.to_period('M').dt.to_timestamp()
final_df = final_df.reset_index()
heatmap_data = pd.pivot_table(
    final_df,
    values='order_item_id',
    index='category_name',
    columns='month',
    aggfunc='count',
    fill_value=0
)
fig10 = px.imshow(
    heatmap_data,
    aspect='auto',
    color_continuous_scale='Viridis',
    title='Orders Per Category Over Time',
    labels=dict(x='Month', y='Category', color='Order Count'),
    height=500
)
fig10.update_layout(
    xaxis_tickangle=-45,
    font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
    title=dict(font=dict(size=18, color='#333')),
    yaxis_nticks=len(heatmap_data.index),
    margin=dict(l=50, r=50, t=80, b=50),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)


# FIGURE 11: Average Review Rating
avg_rating = df['reviews']['rating'].mean()
fig11 = go.Figure(go.Indicator(
    mode="number",
    value=avg_rating,
    title={"text": "Average Stars", "font": {"size": 22, "color": "#333"}},
    number={"font": {"size": 48, "color": "#005B99"}},
))
fig11.update_layout(
    height=200,
    font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=50, b=20)
)

# FIGURE 12: Orders Per Category Heatmap

# Step 1: Filter out cancelled orders
orders_df = df['orders'].reset_index()
valid_orders = orders_df[orders_df['status'] != 'Cancelled']

# Step 2: Merge valid orders with order_items
order_items_df = df['order_items']
order_details = pd.merge(valid_orders[['order_id']], order_items_df, on='order_id', how='inner')

# Step 3: Merge with product_suppliers to get supply price
product_suppliers_df = df['product_suppliers'].drop_duplicates(subset='product_id')  # Handle duplicates
order_with_costs = pd.merge(order_details, product_suppliers_df[['product_id', 'supply_price']], on='product_id', how='left')

# Step 4: Compute total cost and total revenue
order_with_costs['total_cost'] = order_with_costs['quantity'] * order_with_costs['supply_price']
total_revenue = order_with_costs['total_price'].sum()
total_cost = order_with_costs['total_cost'].sum()
profit = total_revenue - total_cost

fig12 = go.Figure(go.Indicator(
    mode="number",
    value=profit,
    title={"text": "Total Profit", "font": {"size": 22, "color": "#333"}},
    number={"font": {"size": 48, "color": '#2e8b57'}, "prefix": "$"},
))
fig12.update_layout(
    height=200,
    font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=50, b=20)
)

# -----------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------



# Dash App
app = Dash(__name__)

app.layout = html.Div([
    # Header Section
        html.Div([
        html.H1("Executive KPI Dashboard", style={"fontSize": "32px", "fontWeight": "600", "color": "#FFFFFF"}),
        html.H2("E-Commerce Performance Analytics", style={"fontSize": "22px", "fontWeight": "400", "color": "#FFFFFFA6"}),
        html.H3("by Abdul Mohaimin", style={"fontSize": "18px", "fontWeight": "300", "color": "#FFFFFF"}),
    ], style={
        "textAlign": "center",
        "padding": "5px",  # reduced from 30px
        "backgroundColor": "#1C8407",
        "borderRadius": "10px",
        "margin": "10px",   # reduced from 30px
        "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",  # lighter shadow
    }),

    # AOV Indicator at Top
    # html.Div([
    #     dcc.Graph(figure=fig8, style={"width": "100%", "textAlign": "center"})
    # ], style={
    #     "backgroundColor": "#FFFFFF",
    #     "borderRadius": "8px",
    #     "padding": "20px",
    #     "margin": "20px",
    #     "boxShadow": "0 4px 12px rgba(0,0,0,0.1)"
    # }),

    # Main Dashboard Grid
    html.Div([
        # Row 1: Numerical Insights
        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(
                        figure=fig8.update_layout(
                            title_font=dict(color='#2e8b57', size=18, family='Arial', weight='bold'),
                            font=dict(color='#2e8b57', family='Arial'),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            height=120,
                            margin=dict(l=10, r=10, t=40, b=10)
                        )
                    )
                ], style={"flex": "1", "minWidth": "1", "border": "1px solid #e6e6e6", "padding": "15px", "borderRadius": "5px"}),
                
                html.Div([
                    dcc.Graph(
                        figure=fig11.update_layout(
                            title_font=dict(color='#2e8b57', size=18, family='Arial', weight='bold'),
                            font=dict(color='#2e8b57', family='Arial'),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            height=120,
                            margin=dict(l=10, r=10, t=40, b=10)
                        )
                    )
                ], style={"flex": "1", "minWidth": "1", "border": "1px solid #e6e6e6", "padding": "15px", "borderRadius": "5px"}),

                html.Div([
                    dcc.Graph(
                        figure=fig12.update_layout(
                            title_font=dict(color='#2e8b57', size=18, family='Arial', weight='bold'),
                            font=dict(color='#2e8b57', family='Arial'),
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            height=120,
                            margin=dict(l=10, r=10, t=40, b=10)
                        )
                    )
                ], style={"flex": "1", "minWidth": "1", "border": "1px solid #e6e6e6", "padding": "15px", "borderRadius": "5px"}),
            ], style={
                "display": "flex", 
                "gap": "20px", 
                "flexWrap": "wrap",
                "justifyContent": "space-between"
            }),
        ], style={
            "backgroundColor": "#FFFFFF",
            "borderRadius": "8px",
            "padding": "10px",
            "margin": "15px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.1)",
            "fontFamily": "Arial, sans-serif"
        }),
        # Row 2: First Row of Three Graphs
        html.Div([
            html.Div([
                html.Div([dcc.Graph(figure=fig1.update_layout(height=350))], style={"flex": "1", "minWidth": "300px"}),
                html.Div([dcc.Graph(figure=fig10.update_layout(height=350))], style={"flex": "1", "minWidth": "300px"}),
                html.Div([dcc.Graph(figure=fig2.update_layout(height=350))], style={"flex": "1", "minWidth": "300px"}),
            ], style={"display": "flex", "gap": "15px", "flexWrap": "wrap", "justifyContent": "center"}),
        ], style={
            "backgroundColor": "#FFFFFF",
            "borderRadius": "8px",
            "padding": "15px",
            "margin": "15px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.1)",
        }),

        # Row 3: Second Row of Three Graphs
        html.Div([
            html.Div([
                html.Div([dcc.Graph(figure=fig5.update_layout(height=350))], style={"flex": "1", "minWidth": "300px"}),
                html.Div([dcc.Graph(figure=fig6.update_layout(height=350))], style={"flex": "1", "minWidth": "300px"}),
                html.Div([dcc.Graph(figure=fig9.update_layout(height=350))], style={"flex": "1", "minWidth": "300px"}),
            ], style={"display": "flex", "gap": "15px", "flexWrap": "wrap", "justifyContent": "center"}),
        ], style={
            "backgroundColor": "#FFFFFF",
            "borderRadius": "8px",
            "padding": "15px",
            "margin": "15px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.1)"
        }),

        # Row 4: Third Row of Three Graphs
        html.Div([
            html.Div([
                html.Div([dcc.Graph(figure=fig3.update_layout(height=350))], style={"flex": "1", "minWidth": "300px"}),
                html.Div([
                    html.Div([
                        dcc.RadioItems(
                            id='map-view-selector',
                            options=[
                                {'label': 'Orders per State', 'value': 'orders'},
                                {'label': 'Customers per State', 'value': 'customers'}
                            ],
                            value='orders',
                            labelStyle={'display': 'inline-block', 'marginRight': '20px', 'fontSize': '14px', 'color': '#333'},
                            style={
                                "marginBottom": "10px",
                                "padding": "10px",
                                "backgroundColor": "#F8F9FA",
                                "borderRadius": "5px",
                                "width": "100%",
                                "textAlign": "center"
                            }
                        ),
                    ], style={"width": "100%"}),
                    html.Div([
                        dcc.Graph(
                            id='choropleth-map',
                            figure=fig7.update_layout(height=300),
                            style={"height": "300px"}
                        )
                    ], style={"width": "100%"})
                ], style={
                    "flex": "1",
                    "minWidth": "300px",
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center"
                }),
                html.Div([dcc.Graph(figure=fig4.update_layout(height=350))], style={"flex": "1", "minWidth": "300px"}),
            ], style={"display": "flex", "gap": "15px", "flexWrap": "wrap", "justifyContent": "center"}),
        ], style={
            "backgroundColor": "#FFFFFF",
            "borderRadius": "8px",
            "padding": "15px",
            "margin": "15px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.1)"
        }),
    ], style={"margin": "20px"}),
], style={
    "padding": "30px",
    "fontFamily": "Segoe UI, Arial, sans-serif",
    "backgroundColor": "#F0F2F5",
    "minHeight": "100vh"
})



# -----------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------



# Callback for Map Toggle
@callback(
    Output('choropleth-map', 'figure'),
    Input('map-view-selector', 'value')
)
def update_map(selected_view):
    if selected_view == 'orders':
        data = orders_per_states
        location_col = 'shipping_state'
        title = 'Orders Distribution by State'
    else:
        data = customers_per_state
        location_col = 'state'
        title = 'Customers Distribution by State'
    
    fig = px.choropleth(
        data,
        locations=location_col,
        locationmode="USA-states",
        color='count',
        scope="usa",
        title=title,
        color_continuous_scale="Viridis",
        height=300
    )
    fig.update_layout(
        font=dict(family="Segoe UI, sans-serif", size=14, color="#333"),
        title=dict(font=dict(size=18, color='#333')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        geo=dict(
            showlakes=True,
            lakecolor='#E6F3FF',
            showland=True,
            landcolor='#F5F5F5',
            showsubunits=True,
            subunitcolor="#D0D0D0"
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)