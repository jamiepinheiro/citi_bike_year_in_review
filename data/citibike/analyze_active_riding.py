import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

# Load the data
df = pd.read_csv('/home/ubuntu/.cache/kagglehub/datasets/hassanabsar/nyc-citi-bike-ride-share-system-data-2023/versions/2/sample_citibike_2023.csv', 
                 usecols=['started_at', 'ended_at'])

# Convert to datetime
df['started_at'] = pd.to_datetime(df['started_at'])
df['ended_at'] = pd.to_datetime(df['ended_at'])

# Calculate duration
df['duration_minutes'] = (df['ended_at'] - df['started_at']).dt.total_seconds() / 60

# Create 10-minute intervals for the day
intervals = []
for hour in range(24):
    for minute in range(0, 60, 10):
        intervals.append(f"{hour:02d}:{minute:02d}")

# Initialize counts for each 10-minute interval
interval_counts = {interval: 0 for interval in intervals}

# Process each ride
for _, row in df.iterrows():
    start_time = row['started_at']
    end_time = row['ended_at']
    
    # Round start time down to nearest 10-minute interval
    start_rounded = start_time.replace(minute=(start_time.minute // 10) * 10, second=0, microsecond=0)
    
    # Round end time up to nearest 10-minute interval
    end_minute = ((end_time.minute // 10) + 1) * 10
    if end_minute >= 60:
        new_hour = (end_time.hour + 1) % 24
        end_rounded = end_time.replace(hour=new_hour, minute=0, second=0, microsecond=0)
    else:
        end_rounded = end_time.replace(minute=end_minute, second=0, microsecond=0)
    
    # Add counts for each 10-minute interval this ride spans
    current_time = start_rounded
    while current_time < end_rounded:
        interval_key = current_time.strftime("%H:%M")
        if interval_key in interval_counts:
            interval_counts[interval_key] += 1
        current_time += timedelta(minutes=10)

# Convert to DataFrame for plotting
interval_df = pd.DataFrame(list(interval_counts.items()), columns=['Time', 'Active_Rides'])
interval_df['Time'] = pd.to_datetime(interval_df['Time'], format='%H:%M').dt.time
interval_df = interval_df.sort_values('Time')

# Create the plot
plt.figure(figsize=(20, 10))
plt.bar(range(len(interval_df)), interval_df['Active_Rides'], width=0.8)

# Set x-axis labels (every 6th interval to avoid crowding)
x_labels = [str(t)[:5] for t in interval_df['Time']]
plt.xticks(range(0, len(x_labels), 6), [x_labels[i] for i in range(0, len(x_labels), 6)], rotation=45)

plt.xlabel('Time of Day (10-minute intervals)')
plt.ylabel('Number of Active Rides')
plt.title('Citi Bike Active Riding by Time of Day (2023) - 10-minute granularity')
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save the plot
plt.savefig('/workspace/citibike_active_riding_10min_2023.png', dpi=300, bbox_inches='tight')
print('Active riding histogram with 10-minute granularity saved as citibike_active_riding_10min_2023.png')

# Print some statistics
print(f"\nTotal rides analyzed: {len(df)}")
print(f"Average ride duration: {df['duration_minutes'].mean():.2f} minutes")
print(f"Peak active riding time: {interval_df.loc[interval_df['Active_Rides'].idxmax(), 'Time']}")
print(f"Peak active rides: {interval_df['Active_Rides'].max()}")