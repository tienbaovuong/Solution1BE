import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler, StandardScaler

# Load models
with open("ml_models/dt_model.pkl", "rb") as f:
    dt_bundle = pickle.load(f)
dt_model = dt_bundle['model']
with open("ml_models/xgb_model.pkl", "rb") as f:
    xgb_bundle = pickle.load(f)
xgb_model = xgb_bundle['model']
with open("ml_models/gbr_model.pkl", "rb") as f:
    gbr_bundle = pickle.load(f)
gbr_model = gbr_bundle['model']

def ip_to_binary(ip):
    try:
        ip_str = str(ip)
        parts = ip_str.split('.')
        if len(parts) != 4:
            return None
        return ''.join([format(int(part), '08b') for part in parts])
    except:
        return None
    
def label_decoder(label):
    if label == 0:
        return "Attack"
    elif label == 1:
        return "CC"
    elif label == 2:
        return "DDoS"
    elif label == 3:
        return "PartofAHorizontalPortScan"
    else:
        return "Benign"

def get_prediction(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = ["timestamp", "uid", "origin_host", "origin_port", "response_host", "response_port",
                  "protocol", "service", "duration", "original_bytes", "response_bytes", "connection_state",
                  "local_origin", "local_response", "missed_bytes", "history", "original_packets",
                  "original_ip_bytes", "response_packets", "response_ip_bytes", "tunnel_parents"]
    
    timestamp_copy = df['timestamp'].copy()
    # df.drop('detailed_label', axis=1, inplace=True)
    # df.drop('label', axis=1, inplace=True)
    
    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
    df['year'] = df['timestamp'].dt.year
    df['month'] = df['timestamp'].dt.month
    df['day'] = df['timestamp'].dt.day
    df['hour'] = df['timestamp'].dt.hour
    df.drop('timestamp', axis=1, inplace=True)

    #Replace '-' with NaN
    df.replace('-', np.nan, inplace=True)

    # Select only required features from the dataset
    required_columns = ['year', 'month', 'day','hour', 'origin_host', 'origin_port', 'response_host', 'response_port',
                    'protocol', 'service', 'duration', 'original_bytes', 'original_packets',
                    'response_bytes', 'response_packets', 'connection_state', 'missed_bytes',
                    'history']
    # New Dataframe with required features
    df_selected = df[required_columns].copy()

    df_selected['original_bytes'] = df_selected['original_bytes'].fillna(0).astype(int)
    df_selected['response_bytes'] = df_selected['response_bytes'].fillna(0).astype(int)
    df_selected['service'] = df_selected['service'].fillna('unknown')
    df_selected['history'] = df_selected['history'].fillna('unknown')

    # Checking for duplicates
    duplicate_mask = df_selected.duplicated(subset=['year', 'month', 'day', 'hour', 'origin_host', 'response_host', 'origin_port', 'response_port', 'protocol', 'duration', 'original_bytes', 'response_bytes'], keep=False)
    df_selected.drop(columns=['duration'], inplace=True)

    # Numeric columns
    numeric_columns = ['origin_port', 'response_port', 'original_bytes', 'original_packets',
                    'response_bytes', 'response_packets', 'missed_bytes']
    for col in numeric_columns:
        df_selected[col] = pd.to_numeric(df_selected[col], errors='coerce').fillna(0).astype(int)

    # Categorical columns
    categorical_columns = ['protocol', 'service', 'connection_state', 'history']
    for col in categorical_columns:
        df_selected[col] = df_selected[col].astype('category')

    # Convert IP to binary
    df_selected['origin_host_binary'] = df_selected['origin_host'].apply(ip_to_binary)
    df_selected['response_host_binary'] = df_selected['response_host'].apply(ip_to_binary)

    # Drop column contains None (invalid IP)
    df_selected.dropna(subset=['origin_host_binary', 'response_host_binary'], inplace=True)

    # Convert binary string to integer
    df_selected['origin_host_binary'] = df_selected['origin_host_binary'].apply(lambda x: int(x, 2))
    df_selected['response_host_binary'] = df_selected['response_host_binary'].apply(lambda x: int(x, 2))

    # Drop original IP column
    df_selected.drop(columns=['origin_host', 'response_host'], inplace=True)

    # Feature Scaling using Robust Scaler to minimize impact of outliers
    robust_scaler = RobustScaler()
    df_selected[numeric_columns] = robust_scaler.fit_transform(df_selected[numeric_columns])

    # One-hot Encoding
    df_encoded = pd.get_dummies(df_selected, columns=['protocol', 'service', 'connection_state', 'history'], prefix=['proto', 'serv', 'conn_state', 'hist'])
    encoded_columns = df_encoded.columns.difference(df_selected.columns)
    df_encoded_features = df_encoded[encoded_columns]

    df_dropped = df_selected.drop(columns=['connection_state', 'protocol', 'history', 'service'])

    df_combined = pd.concat([df_dropped, df_encoded_features], axis=1)

    # Finalising the dataframe with selected categorical and numerical features
    selected_features = ['hist_S', 'conn_state_RSTO', 'proto_udp', 'conn_state_S2', 'hist_ShAa', 'serv_dns', 'proto_tcp', 'hist_ShAr', 'hist_Sr', 'hist_D', 'conn_state_SF', 'conn_state_REJ', 'hist_unknown', 'proto_icmp', 'hist_Dd']
    df_selected_features = df_combined[list(selected_features)]
    df_final = pd.concat([df_dropped, df_selected_features], axis=1)

    # Ensure all columns are numeric
    df_final = df_final.replace({True: 1, False: 0})
    for col in df_final.select_dtypes(include=['object']).columns:
        df_final[col] = pd.to_numeric(df_combined[col], errors='coerce').fillna(0).astype(int)

    # XGB input
    df_xgb = df_final.copy()
    xgb_features = ['month', 'day', 'hour', 'origin_port', 'response_port',
       'original_bytes', 'original_packets', 'response_bytes',
       'response_packets', 'origin_host_binary', 'response_host_binary',
       'hist_S', 'conn_state_SF']
    X_xgb = df_xgb[xgb_features]

    # GBR input
    df_gbr = df_final.select_dtypes(include=[np.number]).dropna().copy()
    scaler = StandardScaler()
    X_gbr_scaled = pd.DataFrame(scaler.fit_transform(df_gbr), columns=df_gbr.columns)

    # Make predictions
    dt_preds = dt_model.predict(df_final)
    xgb_preds = xgb_model.predict(X_xgb)
    gbr_preds = gbr_model.predict(X_gbr_scaled)

    # Create result df
    result_df = pd.DataFrame(columns=["timestamp", "detection", "classifier", "severity"])
    result_df['timestamp'] = timestamp_copy
    result_df['detection'] = dt_preds
    result_df['severity'] = gbr_preds
    
    xgb_counter = 0
    for i in range(len(result_df)):
        if result_df.loc[i, 'detection'] == 0:
            result_df.loc[i, 'classifier'] = 'Benign'
        else:
            result_df.loc[i, 'classifier'] = label_decoder(int(xgb_preds[xgb_counter]))
            xgb_counter += 1

    return result_df