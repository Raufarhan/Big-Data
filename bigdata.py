import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time

URL = 'https://kurs.web.id/'

def get_kurs_data():
    try:
        print("🌐 Mengakses situs kurs.web.id...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Temukan tabel kurs utama
        table = soup.find('table')
        if not table:
            print("❌ Tabel kurs tidak ditemukan.")
            return None

        kurs_data = []
        rows = table.find_all('tr')[1:]  # Skip header

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                bank = cols[0].get_text(strip=True)
                beli = cols[1].get_text(strip=True).replace('.', '').replace(',', '.')
                jual = cols[2].get_text(strip=True).replace('.', '').replace(',', '.')
                kurs_data.append([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), bank, beli, jual])
        
        return kurs_data
    except Exception as e:
        print(f"❌ Gagal mengambil data: {e}")
        return None

def save_to_csv(data, filename='kurs_data.csv'):
    header = ['Timestamp', 'Bank', 'Kurs Beli', 'Kurs Jual']
    try:
        file_exists = False
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                file_exists = True
        except FileNotFoundError:
            pass
        
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header)
            writer.writerows(data)
        print(f"✅ Data berhasil disimpan ke {filename}")
    except Exception as e:
        print(f"❌ Gagal menyimpan data: {e}")

def main():
    print("🔄 Mulai pengambilan data kurs dari kurs.web.id setiap 5 menit. Tekan Ctrl+C untuk berhenti.")
    while True:
        data = get_kurs_data()
        if data:
            save_to_csv(data)
        time.sleep(300)  # Tunggu 5 menit

if __name__ == '__main__':
    main()
