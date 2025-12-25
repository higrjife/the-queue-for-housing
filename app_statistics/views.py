import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from django.shortcuts import render
from io import BytesIO
import base64
from housing_units.models import HousingUnit

sns.set_style("whitegrid")
plt.rcParams['figure.facecolor'] = 'white'

def get_housing_units():
    housing_units = HousingUnit.objects.all()
    
    df = pd.DataFrame()
    for unit in housing_units:
        new_data = pd.DataFrame([{
            "area_type": "Carpet  Area",
            "availability": unit.status,
            "location": unit.address,
            "size": f'{unit.rooms_count} BHK',
            "society": "",
            "total_sqft": unit.total_area,
            "bath": 1,
            "balcony": 1,
            "price": 50
        }])
        df = pd.concat([df, new_data], ignore_index=True)
    
    return df

def get_plot(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=80, bbox_inches='tight')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img

def statistics(request):
    df = pd.read_csv('house_data.csv')
    db_df = get_housing_units()
    df = pd.concat([df, db_df], ignore_index=True)
    
    # Clean data
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['bath'] = pd.to_numeric(df['bath'], errors='coerce')
    df['balcony'] = pd.to_numeric(df['balcony'], errors='coerce')
    
    def get_sqft(x):
        try:
            if '-' in str(x):
                vals = str(x).split('-')
                return (float(vals[0]) + float(vals[1])) / 2
            return float(x)
        except:
            return np.nan
    
    df['sqft'] = df['total_sqft'].apply(get_sqft)
    df = df.dropna(subset=['price', 'sqft'])
    
    df['price_per_sqft'] = df['price'] * 100000 / df['sqft']
    
    plots = {}
    
    # 1. Price Distribution
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df['price'], bins=40, color='#3B82F6', edgecolor='black', alpha=0.7)
    ax.set_xlabel('Price (Lakhs)', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Price Distribution', fontsize=13, fontweight='bold')
    plots['price_hist'] = get_plot(fig)
    


    # 2. Square Feet Distribution
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df['sqft'], bins=40, color='#10B981', edgecolor='black', alpha=0.7)
    ax.set_xlabel('Square Feet', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Square Feet Distribution', fontsize=13, fontweight='bold')
    plots['sqft_hist'] = get_plot(fig)
    


    # 3. Top 15 Locations
    fig, ax = plt.subplots(figsize=(10, 6))
    top_loc = df.groupby('location')['price'].mean().sort_values(ascending=False).head(15)
    ax.barh(range(len(top_loc)), top_loc.values, color='#8B5CF6')
    ax.set_yticks(range(len(top_loc)))
    ax.set_yticklabels(top_loc.index, fontsize=9)
    ax.set_xlabel('Average Price (Lakhs)', fontsize=11)
    ax.set_title('Top 15 Locations by Price', fontsize=13, fontweight='bold')
    plots['top_locations'] = get_plot(fig)
    


    # 4. Property Size (BHK) Distribution
    fig, ax = plt.subplots(figsize=(10, 5))
    size_counts = df['size'].value_counts().head(6)
    ax.bar(range(len(size_counts)), size_counts.values, color='#F59E0B', edgecolor='black')
    ax.set_xticks(range(len(size_counts)))
    ax.set_xticklabels(size_counts.index, rotation=45)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Property Size Distribution', fontsize=13, fontweight='bold')
    plots['size_dist'] = get_plot(fig)
    
    # 5. Price by Size (BHK)
    fig, ax = plt.subplots(figsize=(10, 5))
    size_price = df.groupby('size')['price'].mean().sort_values().head(8)
    ax.barh(range(len(size_price)), size_price.values, color='#EF4444')
    ax.set_yticks(range(len(size_price)))
    ax.set_yticklabels(size_price.index)
    ax.set_xlabel('Average Price (Lakhs)', fontsize=11)
    ax.set_title('Average Price by Property Size', fontsize=13, fontweight='bold')
    plots['price_by_size'] = get_plot(fig)
    
    # 6. Availability Status
    fig, ax = plt.subplots(figsize=(10, 5))
    avail = df['availability'].value_counts().head(8)
    ax.bar(range(len(avail)), avail.values, color='#06B6D4', edgecolor='black')
    ax.set_xticks(range(len(avail)))
    ax.set_xticklabels(avail.index, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Property Availability', fontsize=13, fontweight='bold')
    plots['availability'] = get_plot(fig)
    
    # 7. Area Type Distribution
    fig, ax = plt.subplots(figsize=(10, 5))
    area_counts = df['area_type'].value_counts()
    colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444']
    ax.pie(area_counts.values, labels=area_counts.index, autopct='%1.1f%%', 
           colors=colors, startangle=90)
    ax.set_title('Area Type Distribution', fontsize=13, fontweight='bold')
    plots['area_type'] = get_plot(fig)
    
    # 8. Bathrooms Analysis
    fig, ax = plt.subplots(figsize=(10, 5))
    bath_counts = df['bath'].value_counts().sort_index().head(6)
    ax.bar(bath_counts.index, bath_counts.values, color='#8B5CF6', edgecolor='black')
    ax.set_xlabel('Number of Bathrooms', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Bathroom Distribution', fontsize=13, fontweight='bold')
    plots['bathrooms'] = get_plot(fig)
    
    # 9. Balcony Analysis
    fig, ax = plt.subplots(figsize=(10, 5))
    balcony_counts = df['balcony'].value_counts().sort_index().head(6)
    ax.bar(balcony_counts.index, balcony_counts.values, color='#EC4899', edgecolor='black')
    ax.set_xlabel('Number of Balconies', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Balcony Distribution', fontsize=13, fontweight='bold')
    plots['balconies'] = get_plot(fig)
    
    # 10. Price per Square Foot Distribution
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(df['price_per_sqft'], bins=40, color='#14B8A6', edgecolor='black', alpha=0.7)
    ax.set_xlabel('Price per Sq Ft (₹)', fontsize=11)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Price per Square Foot Distribution', fontsize=13, fontweight='bold')
    plots['price_per_sqft'] = get_plot(fig)
    
    # 11. Price vs Sqft Scatter
    fig, ax = plt.subplots(figsize=(10, 5))
    sample = df.sample(min(1000, len(df)))
    ax.scatter(sample['sqft'], sample['price'], alpha=0.5, s=30, color='#3B82F6')
    ax.set_xlabel('Square Feet', fontsize=11)
    ax.set_ylabel('Price (Lakhs)', fontsize=11)
    ax.set_title('Price vs Square Feet', fontsize=13, fontweight='bold')
    plots['scatter'] = get_plot(fig)
    
    # 12. Bath vs Price
    fig, ax = plt.subplots(figsize=(10, 5))
    bath_price = df.groupby('bath')['price'].mean().dropna().head(7)
    ax.plot(bath_price.index, bath_price.values, marker='o', linewidth=2, 
            markersize=8, color='#8B5CF6')
    ax.set_xlabel('Bathrooms', fontsize=11)
    ax.set_ylabel('Average Price (Lakhs)', fontsize=11)
    ax.set_title('Price by Number of Bathrooms', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plots['bath_price'] = get_plot(fig)
    
    
    # 13. Balcony vs Price
    fig, ax = plt.subplots(figsize=(10, 5))
    balcony_price = df.groupby('balcony')['price'].mean().dropna().head(7)
    ax.plot(balcony_price.index, balcony_price.values, marker='s', linewidth=2,
            markersize=8, color='#EC4899')
    ax.set_xlabel('Balconies', fontsize=11)
    ax.set_ylabel('Average Price (Lakhs)', fontsize=11)
    ax.set_title('Price by Number of Balconies', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plots['balcony_price'] = get_plot(fig)
    

    # 14. Properties by Location (Top 15)
    fig, ax = plt.subplots(figsize=(10, 6))
    loc_counts = df['location'].value_counts().head(15)
    ax.barh(range(len(loc_counts)), loc_counts.values, color='#F59E0B')
    ax.set_yticks(range(len(loc_counts)))
    ax.set_yticklabels(loc_counts.index, fontsize=9)
    ax.set_xlabel('Number of Properties', fontsize=11)
    ax.set_title('Top 15 Locations by Property Count', fontsize=13, fontweight='bold')
    plots['location_counts'] = get_plot(fig)
    
    # 15. Price Range Categories
    fig, ax = plt.subplots(figsize=(10, 5))
    bins = [0, 50, 100, 150, 200, df['price'].max()]
    labels = ['0-50L', '50-100L', '100-150L', '150-200L', '200L+']
    df['price_range'] = pd.cut(df['price'], bins=bins, labels=labels)
    range_counts = df['price_range'].value_counts().sort_index()
    colors = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6']
    ax.bar(range(len(range_counts)), range_counts.values, color=colors, edgecolor='black')
    ax.set_xticks(range(len(range_counts)))
    ax.set_xticklabels(range_counts.index)
    ax.set_ylabel('Count', fontsize=11)
    ax.set_title('Properties by Price Range', fontsize=13, fontweight='bold')
    plots['price_ranges'] = get_plot(fig)
    
    # 16. Size vs Square Feet
    fig, ax = plt.subplots(figsize=(10, 5))
    size_sqft = df.groupby('size')['sqft'].mean().sort_values().head(8)
    ax.barh(range(len(size_sqft)), size_sqft.values, color='#06B6D4')
    ax.set_yticks(range(len(size_sqft)))
    ax.set_yticklabels(size_sqft.index)
    ax.set_xlabel('Average Square Feet', fontsize=11)
    ax.set_title('Average Square Feet by Property Size', fontsize=13, fontweight='bold')
    plots['size_sqft'] = get_plot(fig)
    
    # Stats
    stats = {
        'total': len(df),
        'avg_price': round(df['price'].mean(), 1),
        'avg_sqft': round(df['sqft'].mean(), 0),
        'avg_price_per_sqft': round(df['price_per_sqft'].mean(), 0),
    }
    
    return render(request, 'statistics.html', {'plots': plots, 'stats': stats})



def dataframe_info(request):
    df = pd.read_csv('house_data.csv')
    
    info = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'memory': f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
    }
    
    # Describe for numeric columns
    describe_raw = df.describe().to_dict()
    describe = {}
    for col, stats in describe_raw.items():
        describe[col] = {
            'count': stats.get('count'),
            'mean': stats.get('mean'),
            'std': stats.get('std'),
            'min': stats.get('min'),
            'q25': stats.get('25%'),
            'q50': stats.get('50%'),
            'q75': stats.get('75%'),
            'max': stats.get('max'),
        }
    
    missing = df.isnull().sum().to_dict()
    
    value_counts = {
        'location': df['location'].value_counts().head(5).to_dict(),
        'size': df['size'].value_counts().to_dict(),
        'area_type': df['area_type'].value_counts().to_dict(),
    }
    
    context = {
        'info': info,
        'describe': describe,
        'missing': missing,
        'value_counts': value_counts,
    }
    
    return render(request, 'pd_info.html', context)