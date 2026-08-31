import pandas as pd
import numpy as np
from datetime import datetime
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Radius of the earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class FeatureEngineer:
    def __init__(self):
        pass
        
    def process_transactions(self, df: pd.DataFrame, user_history: pd.DataFrame = None) -> pd.DataFrame:
        df = df.copy()
        
        # Ensure datetime
        if 'date_time' in df.columns:
            df['date_time'] = pd.to_datetime(df['date_time'])
            
        # 0. Missing value handling & duplicates
        df = df.drop_duplicates(subset=['transaction_id']) if 'transaction_id' in df.columns else df.drop_duplicates()
        df['amount'] = df['amount'].fillna(df['amount'].median() if not df['amount'].isna().all() else 0.0)
            
        # 1. Monetary Features
        if user_history is not None and not user_history.empty:
            user_avg = user_history.groupby('customer_id')['amount'].mean().to_dict()
            user_std = user_history.groupby('customer_id')['amount'].std().fillna(1).to_dict()
        else:
            user_avg = {}
            user_std = {}
            
        df['amount_to_avg_ratio'] = df.apply(lambda x: x['amount'] / (user_avg.get(x['customer_id'], x['amount']) + 1e-5), axis=1)
        df['amount_zscore'] = df.apply(lambda x: (x['amount'] - user_avg.get(x['customer_id'], 0)) / (user_std.get(x['customer_id'], 1) + 1e-5), axis=1)
        
        # 2. Velocity & Frequency
        if 'txn_count_last_1h' not in df.columns: df['txn_count_last_1h'] = 0
        df['txn_count_last_1h'] = df['txn_count_last_1h'].fillna(0)
        
        if 'txn_count_last_24h' not in df.columns: df['txn_count_last_24h'] = 0
        df['txn_count_last_24h'] = df['txn_count_last_24h'].fillna(0)
        
        if 'amount_sum_last_24h' not in df.columns: df['amount_sum_last_24h'] = df['amount']
        df['amount_sum_last_24h'] = df['amount_sum_last_24h'].fillna(df['amount'])

        # 3. Geolocation & Mobility
        if 'lat' not in df.columns: df['lat'] = 0.0
        df['lat'] = df['lat'].fillna(0.0)
        
        if 'lon' not in df.columns: df['lon'] = 0.0
        df['lon'] = df['lon'].fillna(0.0)
        
        if 'prev_lat' not in df.columns: df['prev_lat'] = df['lat']
        df['prev_lat'] = df['prev_lat'].fillna(df['lat'])
        
        if 'prev_lon' not in df.columns: df['prev_lon'] = df['lon']
        df['prev_lon'] = df['prev_lon'].fillna(df['lon'])
        
        if 'prev_date_time' not in df.columns: df['prev_date_time'] = df['date_time']
        
        def calc_distance(row):
            return haversine(row['lat'], row['lon'], row['prev_lat'], row['prev_lon'])
            
        df['haversine_distance_km'] = df.apply(calc_distance, axis=1)
        
        def calc_velocity(row):
            try:
                dt = (row['date_time'] - row['prev_date_time']).total_seconds() / 3600.0
                if dt <= 0: return 0.0
                return row['haversine_distance_km'] / dt
            except:
                return 0.0
            
        df['travel_speed_kmh'] = df.apply(calc_velocity, axis=1)
        
        # 4. Device & Spatial Signals
        if 'is_new_device' not in df.columns: df['is_new_device'] = 0
        df['is_new_device'] = df['is_new_device'].fillna(0).astype(int)
        
        if 'is_new_location' not in df.columns: df['is_new_location'] = 0
        df['is_new_location'] = df['is_new_location'].fillna(0).astype(int)
        
        if 'device_frequency' not in df.columns: df['device_frequency'] = 1
        df['device_frequency'] = df['device_frequency'].fillna(1)
        
        # 5. Temporal Behavioral Indicators
        if 'date_time' in df.columns:
            df['hour_of_day'] = df['date_time'].dt.hour
            df['day_of_week'] = df['date_time'].dt.dayofweek
            df['is_night_transaction'] = df['hour_of_day'].apply(lambda x: 1 if (x >= 23 or x <= 5) else 0)
        else:
            df['hour_of_day'] = 12
            df['day_of_week'] = 0
            df['is_night_transaction'] = 0
            
        # 6. Categorical specific handling (payment_method, merchant) will be encoded in pipeline.py
        # But we ensure they are string
        if 'payment_method' in df.columns:
            df['payment_method'] = df['payment_method'].fillna('UNKNOWN').astype(str)
        if 'merchant' in df.columns:
            df['merchant'] = df['merchant'].fillna('UNKNOWN').astype(str)
        if 'transaction_type' in df.columns:
            df['transaction_type'] = df['transaction_type'].fillna('UNKNOWN').astype(str)
        if 'device_info' in df.columns:
            df['device_info'] = df['device_info'].fillna('UNKNOWN').astype(str)
            
        # 7. Profile Context
        if 'account_age_days' not in df.columns: df['account_age_days'] = 365
        df['account_age_days'] = df['account_age_days'].fillna(365)
        
        if 'merchant_risk_score' not in df.columns: df['merchant_risk_score'] = 0.5
        df['merchant_risk_score'] = df['merchant_risk_score'].fillna(0.5)
        
        # We drop cols that can't be numeric inputs (unless pipeline encodes them)
        # pipeline.py will handle drop logic for customer_id, transaction_id, etc.
        
        return df
