import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set style for better looking plots
plt.style.use('default')
sns.set_theme(style="darkgrid")

def parse_datetime(date_str, time_str):
    try:
        # Try to parse the date and time
        date_time_str = f"{date_str} {time_str}"
        return pd.to_datetime(date_time_str, format='%d.%m.%Y %H:%M:%S.%f')
    except:
        return None

# Read the CSV files
data_folder = 'Data'
csv_files = glob.glob(os.path.join(data_folder, '*.csv'))

dataframes = []
for file in csv_files:
    try:
        # Try different encodings and handle errors
        df = pd.read_csv(file, encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file, encoding='latin1', on_bad_lines='skip')
        except Exception as e:
            print(f"Could not read file {file}: {str(e)}")
            continue
    
    # Add a source column to track which file the data came from
    df['Source'] = os.path.basename(file)
    
    # Try to create a datetime index if possible
    if 'Date' in df.columns and 'Time' in df.columns:
        df['DateTime'] = df.apply(lambda row: parse_datetime(row['Date'], row['Time']), axis=1)
        df = df.set_index('DateTime')
    
    dataframes.append(df)

# Print information about each dataset
for i, df in enumerate(dataframes):
    print(f"\n📊 Dataset {i+1} from: {df['Source'].iloc[0]}")
    print(f"📈 Number of rows: {len(df)}")
    print(f"📋 Number of columns: {len(df.columns)}")
    print("\n🔍 Key performance metrics available:")
    
    # Group metrics by category
    metrics = {
        'CPU': [],
        'GPU': [],
        'Memory': [],
        'Temperature': [],
        'Power': [],
        'Other': []
    }
    
    for col in df.columns:
        col_lower = col.lower()
        if 'cpu' in col_lower:
            metrics['CPU'].append(col)
        elif 'gpu' in col_lower:
            metrics['GPU'].append(col)
        elif 'memory' in col_lower:
            metrics['Memory'].append(col)
        elif 'temperature' in col_lower or 'temp' in col_lower:
            metrics['Temperature'].append(col)
        elif 'power' in col_lower or 'watt' in col_lower:
            metrics['Power'].append(col)
        elif any(term in col_lower for term in ['load', 'usage', 'fps', 'frequency']):
            metrics['Other'].append(col)
    
    for category, cols in metrics.items():
        if cols:
            print(f"\n{category}:")
            for col in cols:
                print(f"  - {col}")

def plot_performance_metrics(df, title):
    """Plot CPU, GPU, and Memory usage over time"""
    fig, axes = plt.subplots(3, 1, figsize=(15, 12))
    fig.suptitle(f'Performance Metrics - {title}', fontsize=16)
    
    # CPU Usage
    cpu_cols = [col for col in df.columns if 'cpu' in col.lower() and 'usage' in col.lower()]
    if cpu_cols:
        for col in cpu_cols:
            axes[0].plot(df.index, df[col], label=col)
        axes[0].set_title('CPU Usage')
        axes[0].set_ylabel('Usage %')
        axes[0].legend()
    
    # GPU Usage
    gpu_cols = [col for col in df.columns if 'gpu' in col.lower() and 'usage' in col.lower()]
    if gpu_cols:
        for col in gpu_cols:
            axes[1].plot(df.index, df[col], label=col)
        axes[1].set_title('GPU Usage')
        axes[1].set_ylabel('Usage %')
        axes[1].legend()
    
    # Memory Usage
    mem_cols = [col for col in df.columns if 'memory' in col.lower() and 'load' in col.lower()]
    if mem_cols:
        for col in mem_cols:
            axes[2].plot(df.index, df[col], label=col)
        axes[2].set_title('Memory Usage')
        axes[2].set_ylabel('Usage %')
        axes[2].legend()
    
    plt.tight_layout()
    plt.show()

def plot_temperature_power(df, title):
    """Plot temperature and power consumption over time"""
    fig, axes = plt.subplots(2, 1, figsize=(15, 10))
    fig.suptitle(f'Temperature and Power - {title}', fontsize=16)
    
    # Temperature
    temp_cols = [col for col in df.columns if 'temperature' in col.lower() or 'temp' in col.lower()]
    if temp_cols:
        for col in temp_cols:
            axes[0].plot(df.index, df[col], label=col)
        axes[0].set_title('Temperature')
        axes[0].set_ylabel('Temperature (°C)')
        axes[0].legend()
    
    # Power
    power_cols = [col for col in df.columns if 'power' in col.lower() or 'watt' in col.lower()]
    if power_cols:
        for col in power_cols:
            axes[1].plot(df.index, df[col], label=col)
        axes[1].set_title('Power Consumption')
        axes[1].set_ylabel('Power (W)')
        axes[1].legend()
    
    plt.tight_layout()
    plt.show()

# Plot metrics for each dataset
for df in dataframes:
    title = df['Source'].iloc[0]
    print(f"\n📈 Generating plots for: {title}")
    
    plot_performance_metrics(df, title)
    plot_temperature_power(df, title)
    
    # Calculate and print some statistics
    print("\n📊 Performance Statistics:")
    
    # CPU Statistics
    cpu_cols = [col for col in df.columns if 'cpu' in col.lower() and 'usage' in col.lower()]
    if cpu_cols:
        for col in cpu_cols:
            print(f"\n{col}:")
            print(f"  Average: {df[col].mean():.2f}%")
            print(f"  Max: {df[col].max():.2f}%")
            print(f"  Min: {df[col].min():.2f}%")
    
    # GPU Statistics
    gpu_cols = [col for col in df.columns if 'gpu' in col.lower() and 'usage' in col.lower()]
    if gpu_cols:
        for col in gpu_cols:
            print(f"\n{col}:")
            print(f"  Average: {df[col].mean():.2f}%")
            print(f"  Max: {df[col].max():.2f}%")
            print(f"  Min: {df[col].min():.2f}%")
    
    # Temperature Statistics
    temp_cols = [col for col in df.columns if 'temperature' in col.lower() or 'temp' in col.lower()]
    if temp_cols:
        for col in temp_cols:
            print(f"\n{col}:")
            print(f"  Average: {df[col].mean():.2f}°C")
            print(f"  Max: {df[col].max():.2f}°C")
            print(f"  Min: {df[col].min():.2f}°C") 