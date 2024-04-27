@app.route('/download_predictions')
def download_predictions():
    # Lakukan proses prediksi seperti yang dilakukan pada fungsi /upload
    # Misalnya:
    predictions = index()

    # Simpan hasil prediksi ke dalam DataFrame
    predictions_df = pd.DataFrame(predictions, columns=['Prediction'])

    # Simpan DataFrame sebagai file xlsx
    predictions_file_path = 'predictions.xlsx'
    predictions_df.to_excel(predictions_file_path, index=False)

    # Kemudian kembalikan file tersebut
    return send_file(predictions_file_path, as_attachment=True)
