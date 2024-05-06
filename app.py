# Load modul
from flask import Flask, request, render_template, redirect, send_file
import pandas as pd
import numpy as np
import pickle
from tensorflow.keras.models import load_model
import io

app = Flask(__name__)

# Load scaler dan model
with open('src/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
model = load_model('src/model.h5')

# list caption output
caption = ["Calm", "Light air", "Light breeze", "Gentle breeze", "Moderate breeze", "Fresh breeze", "Strong breeze"]

# list categorical to numeric for DD
DD_capt={'Calm, no wind' : 0, 
         'Wind blowing from the east' : 1,
         'Wind blowing from the east-northeast' : 2,
         'Wind blowing from the east-southeast' : 3,
         'Wind blowing from the north' : 4, 
         'Wind blowing from the north-east' : 5,
         'Wind blowing from the north-northeast' : 6,
         'Wind blowing from the north-northwest' : 7,
         'Wind blowing from the north-west' : 8,
         'Wind blowing from the south' : 9,
         'Wind blowing from the south-east' : 10,
         'Wind blowing from the south-southeast' : 11,
         'Wind blowing from the south-southwest' : 12,
         'Wind blowing from the south-west' : 13,
         'Wind blowing from the west' : 14,
         'Wind blowing from the west-northwest' : 15,
         'Wind blowing from the west-southwest' : 16, 
         'nan' : -1}

# Fungsi untuk mendapatkan kunci berdasarkan nilai untuk
def get_key(val):
    for key, value in DD_capt.items():
        if val == value:
            return key

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # ambil value dari inputan
        T = float(request.form['T'])
        P = float(request.form['P'])
        DD = request.form['DD']
        Td = float(request.form['Td'])


        # normalisasi data dengan minmax scaler
        scaled_input = scaler.transform([[T, P, DD, Td]])

        # prediksi dengan model 
        prediction = model.predict(scaled_input)

        # mengkombinasikan hasil prediksi dengan string keterangan cth : 2 ---> 2 m/s Light breeze
        result = f"{np.argmax(prediction)} m/s ({caption[np.argmax(prediction)]})"

        DD_int=int(DD)

        global df

        # membuat output table
        df = pd.DataFrame({'T': [T], 'P': [P], 'DD': [get_key(DD_int)], 'Td': [Td], 'result': [result]})

        # convert DataFrame sebagai list ke dalam template HTML
        output_list = df.values.tolist()

        return render_template('home.html', table=output_list)

    return render_template('home.html')

@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        # Get uploaded file
        file = request.files['file']

        #default delimiter
        delimiter = ','
        first_line = file.stream.readline().decode()
        if ';' in first_line:
            delimiter = ';'

        global df

        # Read CSV file
        file.stream.seek(0)  # Reset file pointer to beginning
        df = pd.read_csv(file, delimiter=delimiter)

        # df = pd.read_csv(file,  delimiter=delimiter)

        # mengubah dari dataframe ke numpy array
        data=df.values

        # merubah DD categorical ke numeric
        # for i in range(0,data.shape[0]):
        #     temp=data[i][2]
        #     data[i][2]=DD_capt[data[i][2]]
        for i in range(data.shape[0]):
            data[i][2] = DD_capt.get(data[i][2])


        # normalisasi data dengan minmax scaler
        scaled_input = scaler.transform(data)

        # prediksi dengan model
        predictions = model.predict(scaled_input)

        # menyimpan hasil prediksi
        df["result"]=np.argmax(predictions, axis=1)

        # mengkombinasikan hasil prediksi dengan string keterangan cth : 2 ---> 2 m/s Light breeze
        for i in range(0,df.shape[0]):
            temp=f"{df.loc[i,'result']} m/s ({caption[df.loc[i,'result']]})"
            df.loc[i,'result']=temp
        
        # convert DataFrame sebagai list ke dalam template HTML
        output_list = df.values.tolist()
        
        return render_template('home.html', table=output_list)

    return render_template('home.html')

@app.route('/downloadcsv', methods=['POST'])
def download_table():
    csv_data = df.to_csv(index=False)

    with open('hasil_prediksi.csv', 'w') as f:
        f.write(csv_data)

    return send_file('hasil_prediksi.csv', as_attachment=True)

@app.route('/downloadxlsx', methods=['POST'])
def download_table_xlsx():

    df.to_excel('hasil_prediksi.xlsx', index=False)

    return send_file('hasil_prediksi.xlsx', as_attachment=True)

@app.route('/reset_prediction', methods=['POST'])
def reset_prediction():
    # Logika untuk menghapus data prediksi
    # Anda mungkin perlu menambahkan lebih banyak kode di sini
    df_prediction = pd.DataFrame(columns=['T', 'P', 'DD', 'Td', 'result'])
    return redirect('/')  # Redirect ke halaman utama setelah mereset prediksi

@app.route('/download_template', methods=['POST'])
def download_template():
    template_path = 'src/template_data.csv'  # Ganti dengan path ke file template Anda
    return send_file(template_path, as_attachment=True)
    
if __name__ == '__main__':
    app.run(debug=True)