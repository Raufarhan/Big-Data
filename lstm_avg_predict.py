import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from datetime import timedelta

# ========== 1. Load dan Agregasi Data ==========
df = pd.read_csv('kurs_data.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Filter hanya data valid dengan kurs di bawah 20
df = df[(df['Kurs Beli'] < 20) & (df['Kurs Jual'] < 20)]

# Hitung rata-rata kurs beli dan jual untuk setiap waktu
df_avg = df.groupby('Timestamp')[['Kurs Beli', 'Kurs Jual']].mean().reset_index()
df_avg = df_avg.sort_values('Timestamp')

# ========== 2. Normalisasi ==========
data_values = df_avg[['Kurs Beli', 'Kurs Jual']].values
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data_values)

# ========== 3. Buat Dataset Time Series ==========
X, y = [], []
window_size = 30
for i in range(window_size, len(scaled_data)):
    X.append(scaled_data[i-window_size:i])
    y.append(scaled_data[i])
X = np.array(X)
y = np.array(y)

# ========== 4. Split Train dan Test ==========
split_index = int(len(X) * 0.8)
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

# ========== 5. Bangun dan Latih Model ==========
model = Sequential([
    LSTM(64, return_sequences=False, input_shape=(X.shape[1], X.shape[2])),
    Dense(2)
])
model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X_train, y_train, epochs=50, batch_size=16, validation_data=(X_test, y_test))

# ========== 6. Visualisasi Prediksi ==========
predicted = model.predict(X_test)
predicted_rescaled = scaler.inverse_transform(predicted)
actual_rescaled = scaler.inverse_transform(y_test)

plt.figure(figsize=(12, 6))
plt.plot(actual_rescaled[:, 0], label='Kurs Beli Aktual', linestyle='-')
plt.plot(predicted_rescaled[:, 0], label='Kurs Beli Prediksi', linestyle='--')
plt.plot(actual_rescaled[:, 1], label='Kurs Jual Aktual', linestyle='-')
plt.plot(predicted_rescaled[:, 1], label='Kurs Jual Prediksi', linestyle='--')
plt.title('Prediksi Rata-rata Kurs Beli & Jual (Pasar)')
plt.xlabel('Waktu (index)')
plt.ylabel('Nilai Kurs')
plt.legend()
plt.tight_layout()
plt.savefig('prediksi_kurs_rata_beli_jual.png')
plt.show()

# ========== 7. Prediksi 7 Hari ke Depan ==========
last_window = scaled_data[-window_size:]
future = []
for _ in range(7):
    pred = model.predict(np.expand_dims(last_window, axis=0))[0]
    future.append(pred)
    last_window = np.vstack([last_window[1:], pred])

future_rescaled = scaler.inverse_transform(future)
start_date = df_avg['Timestamp'].max() + timedelta(days=1)
dates = [start_date + timedelta(days=i) for i in range(7)]

future_df = pd.DataFrame(future_rescaled, columns=['Kurs Beli Rata-rata Pred', 'Kurs Jual Rata-rata Pred'])
future_df['Tanggal'] = dates

# ========== 8. Simpan Hasil ==========
future_df.to_csv('prediksi_kurs_rata.csv', index=False)
print("\n✅ Prediksi 7 hari ke depan (rata-rata pasar) disimpan ke prediksi_kurs_rata.csv")