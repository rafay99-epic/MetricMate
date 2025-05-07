import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
import matplotlib.dates as mdates

# Set style for better looking plots
plt.style.use('default')
sns.set_theme(style="darkgrid")

def parse_datetime(date_str, time_str):
    """Parse datetime from various possible formats"""
    try:
        # Try the first format
        date_time_str = f"{date_str} {time_str}"
        return pd.to_datetime(date_time_str, format='%d.%m.%Y %H:%M:%S.%f')
    except:
        try:
            # Try alternative format
            return pd.to_datetime(date_time_str)
        except:
            try:
                # Try parsing just the time if date is invalid
                time_only = pd.to_datetime(time_str)
                # If time is between 0-12, assume it's AM of the current day
                # If time is between 12-24, assume it's PM of the current day
                if time_only.hour < 12:
                    return pd.Timestamp.now().normalize() + pd.Timedelta(hours=time_only.hour, 
                                                                       minutes=time_only.minute,
                                                                       seconds=time_only.second)
                else:
                    return pd.Timestamp.now().normalize() + pd.Timedelta(hours=time_only.hour, 
                                                                       minutes=time_only.minute,
                                                                       seconds=time_only.second)
            except:
                if 'Date' in str(date_str) or 'Time' in str(date_str):
                    return None
                print(f"Warning: Could not parse datetime: {date_str} {time_str}")
                return None  # Return None instead of current time for invalid data

def clean_temperature_data(value):
    """Clean and convert temperature data to numeric values"""
    if pd.isna(value):
        return np.nan
    
    # If the value is already numeric, return it
    if isinstance(value, (int, float)):
        return value
    
    # If it's a string, try to extract the first number
    try:
        # Split by any non-numeric character and take the first valid number
        parts = ''.join(c if c.isdigit() or c == '.' else ' ' for c in str(value)).split()
        if parts:
            val = float(parts[0])
            # Filter out unrealistic values
            if val < 0 or val > 150:  # Temperature range check
                return np.nan
            return val
    except:
        pass
    
    return np.nan

def plot_session_temperatures(df, session_name):
    """Create a temperature plot for a single session"""
    try:
        # Get GPU temperature columns
        gpu_temp_cols = [col for col in df.columns if 'gpu' in col.lower() and ('temperature' in col.lower() or 'temp' in col.lower())]
        
        if not gpu_temp_cols:
            print(f"No GPU temperature data found for session {session_name}")
            return
        
        plt.figure(figsize=(12, 6))
        
        for col in gpu_temp_cols:
            # Clean and prepare the data
            temp_data = df[col].apply(clean_temperature_data)
            temp_data = temp_data.dropna()
            
            # Skip if no valid data
            if len(temp_data) == 0:
                continue
                
            # Resample data to reduce noise (1-minute intervals)
            temp_data = temp_data.resample('1min').mean()
            
            # Skip if all values are the same (likely corrupted data)
            if temp_data.min() == temp_data.max():
                continue
            
            # Plot the data
            plt.plot(temp_data.index, temp_data, label=col.replace('[°C]', '').strip(), alpha=0.8)
        
        # Configure x-axis to show time in HH:MM format
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # Set appropriate time intervals
        time_range = df.index.max() - df.index.min()
        if time_range.total_seconds() <= 1800:  # Less than 30 minutes
            plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
        elif time_range.total_seconds() <= 3600:  # Less than 1 hour
            plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
        else:
            plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
        
        plt.title(f'GPU Temperatures - {session_name}')
        plt.xlabel('Time (HH:MM)')
        plt.ylabel('Temperature (°C)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        
        # Set y-axis limits to show reasonable temperature range
        plt.ylim(40, 90)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"\nError creating plot for session {session_name}: {str(e)}")

def analyze_temperatures(df, session_name):
    """Analyze temperature patterns for a single session"""
    try:
        print(f"\n🌡️ Temperature Analysis for {session_name}")
        print("=" * 50)
        
        # Get GPU temperature columns
        gpu_temp_cols = [col for col in df.columns if 'gpu' in col.lower() and ('temperature' in col.lower() or 'temp' in col.lower())]
        
        # Analyze GPU temperatures
        if gpu_temp_cols:
            print("\nGPU Temperature Analysis:")
            for col in gpu_temp_cols:
                try:
                    # Clean the temperature data
                    temp_data = df[col].apply(clean_temperature_data)
                    
                    # Remove any NaN values
                    temp_data = temp_data.dropna()
                    
                    if len(temp_data) == 0:
                        print(f"\n{col}: No valid temperature data found")
                        continue
                    
                    avg_temp = temp_data.mean()
                    max_temp = temp_data.max()
                    min_temp = temp_data.min()
                    
                    # Find times of high and low temperatures
                    high_temp_threshold = avg_temp + (max_temp - avg_temp) * 0.8
                    low_temp_threshold = avg_temp - (avg_temp - min_temp) * 0.8
                    
                    high_temp_times = temp_data[temp_data >= high_temp_threshold].index
                    low_temp_times = temp_data[temp_data <= low_temp_threshold].index
                    
                    print(f"\n{col}:")
                    print(f"  Average: {avg_temp:.1f}°C")
                    print(f"  Maximum: {max_temp:.1f}°C")
                    print(f"  Minimum: {min_temp:.1f}°C")
                    
                    if not high_temp_times.empty:
                        print("\n  High Temperature Periods:")
                        for time in high_temp_times[:5]:
                            try:
                                print(f"    {time.strftime('%H:%M:%S')} - {temp_data[time]:.1f}°C")
                            except:
                                continue
                    
                    if not low_temp_times.empty:
                        print("\n  Low Temperature Periods:")
                        for time in low_temp_times[:5]:
                            try:
                                print(f"    {time.strftime('%H:%M:%S')} - {temp_data[time]:.1f}°C")
                            except:
                                continue
                except Exception as e:
                    print(f"\nError analyzing {col}: {str(e)}")
    except Exception as e:
        print(f"\nError analyzing session {session_name}: {str(e)}")

# Read the CSV files
data_folder = 'Data'
csv_files = glob.glob(os.path.join(data_folder, '*.csv'))

# Process each file separately
for file in csv_files:
    try:
        df = pd.read_csv(file, encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file, encoding='latin1', on_bad_lines='skip')
        except Exception as e:
            print(f"Could not read file {file}: {str(e)}")
            continue
    
    session_name = os.path.basename(file).replace('.CSV', '')
    
    if 'Date' in df.columns and 'Time' in df.columns:
        # Drop header rows
        df = df[~df['Date'].str.contains('Date', na=False)]
        
        # Create DateTime column
        df['DateTime'] = df.apply(lambda row: parse_datetime(row['Date'], row['Time']), axis=1)
        
        # Remove rows with invalid timestamps before setting index
        df = df.dropna(subset=['DateTime'])
        
        # Set the index after cleaning the data
        df = df.set_index('DateTime')
        
        # Analyze and plot the session
        analyze_temperatures(df, session_name)
        plot_session_temperatures(df, session_name) 