import streamlit as st
import pandas as pd
import plotly.express as px
import os
import warnings
warnings.filterwarnings('ignore')

# Set page title
st.set_page_config(page_title='Dashboard', page_icon=':bar_chart:', layout='wide')
st.title(':bar_chart: Simple SuperStore Dashboard')
st.markdown('<style>div.block-container{padding-top: 1rem;}</style>', unsafe_allow_html=True) # Add padding between elements

# Load data
fl = st.file_uploader(':file_folder: Upload your data', type=(['csv', 'xlsx', 'xls', 'txt']))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding='ISO-8859-1')
else:
    os.chdir(r"C:\Users\S\OneDrive\Desktop\AKC2023\streamlit_apps")
    df = pd.read_csv('Superstore.csv', encoding='ISO-8859-1')

col1, col2 = st.columns((2))
df['Order Date'] = pd.to_datetime(df['Order Date'])

# getting the min and max date
starDate = pd.to_datetime(df['Order Date']).min()
endDate = pd.to_datetime(df['Order Date']).max()

with col1:
    date1 = pd.to_datetime(st.date_input('Start Date', starDate))

with col2:
    date2 = pd.to_datetime(st.date_input('End Date', endDate))

# filtering the data
df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= date2)].copy()

st.sidebar.header('Filter by Category')
region = st.sidebar.multiselect('Region', df['Region'].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df['Region'].isin(region)]

# Create for State
state = st.sidebar.multiselect('State', df['State'].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2['State'].isin(state)]

# Create for City
city = st.sidebar.multiselect('City', df['City'].unique())
if not city:
    df4 = df3.copy()
else:
    df4 = df3[df3['City'].isin(city)]

# Filter the data based on Region, State, City
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df['Region'].isin(region)]
elif not region and not city:
    filtered_df = df[df['State'].isin(state)]
elif state and city:
    filtered_df = df[df['State'].isin(state) & df['City'].isin(city)]
elif region and city:
    filtered_df = df[df['Region'].isin(region) & df['City'].isin(city)]
elif region and state:
    filtered_df = df[df['Region'].isin(region) & df['State'].isin(state)]
elif city:
    filtered_df = df[df['City'].isin(city)]
else:
    filtered_df = df[df['Region'].isin(region) & df['State'].isin(state) & df['City'].isin(city)]

category_df = filtered_df.groupby(by=['Category'], as_index=False)['Sales'].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x='Category', y='Sales', text=['${:,.2f}'.format(x) for x in category_df['Sales']],
                 template='seaborn')
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values='Sales', names='Region', hole=0.4, template='seaborn')
    fig.update_traces(text=filtered_df['Region'] ,textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True, height=200)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap='Blues'))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='Category.csv',
            mime='text/csv',
            help = 'Click to download the above CSV file'
        )

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by=['Region'], as_index=False)['Sales'].sum()
        st.write(region.style.background_gradient(cmap='Oranges'))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='Region.csv',
            mime='text/csv',
            help = 'Click to download the above CSV file'
        )

filtered_df["month_year"] = filtered_df['Order Date'].dt.to_period('M')
st.subheader("Time Series Analysis")

linechart = pd.DataFrame(filtered_df.groupby(filtered_df['month_year'].dt.strftime('%Y : %b'))['Sales'].sum()).reset_index()
fig2 = px.line(linechart, x='month_year', y='Sales', labels={"Sales":"Amount"}, height=500, width=1000 ,template='gridon')
fig2.update_xaxes(tickangle=45, tickformat="%b-%Y")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("TimeSeries_ViewData"):
    st.write(linechart.T.style.background_gradient(cmap='Greens'))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='TimeSeries.csv',
        mime='text/csv',
        help = 'Click to download the above CSV file'
    )

# Create a tree map based on Region, category, sub-category
st.subheader("Hierarchical view of Sales using Tree Map")
fig3 = px.treemap(filtered_df, path=['Region', 'Category', 'Sub-Category'], values='Sales', hover_data=['Sales'], color="Sub-Category", color_discrete_sequence=px.colors.qualitative.Prism)
# fig3.update_layout(margin=dict(l=0, r=0, t=0, b=0))
fig3.update_layout(width=8000, height=600)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment with Sales")
    fig4 = px.pie(filtered_df, values='Sales', names='Segment', template='plotly_dark')
    fig4.update_traces(text=filtered_df['Segment'] ,textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig4, use_container_width=True)

with chart2:
    st.subheader("Category with Sales")
    fig4 = px.pie(filtered_df, values='Sales', names='Category', template='gridon')
    fig4.update_traces(text=filtered_df['Category'] ,textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig4, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][['Region', 'State', 'City', 'Category', 'Sales', 'Quantity', 'Discount', 'Profit']]
    fig = ff.create_table(df_sample, colorscale='Cividis')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('Month wise Sub-Category Table')
    filtered_df["month"] = filtered_df['Order Date'].dt.to_period('M')
    sub_category_year = pd.pivot_table(data=filtered_df, values='Sales', index=['Sub-Category'], columns="month", aggfunc='sum', fill_value=0)
    st.write(sub_category_year.style.background_gradient(cmap='Blues'))