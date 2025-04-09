
from flask import Flask, render_template, request, redirect, url_for, flash, session
import pandas as pd
import os
import json

from llm import analyze_comment 

app = Flask(__name__)
app.secret_key = 'supersecret'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


USERNAME = 'Jacob'
PASSWORD = '2005'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('upload'))
        else:
            flash('用户名或密码错误', 'danger')
    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith(('.csv', '.xlsx')):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            session['file_path'] = filepath
            return redirect(url_for('result'))
        else:
            flash('只支持上传 CSV 或 Excel 文件', 'danger')
    return render_template('upload.html')

@app.route('/result')
def result():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    file_path = session.get('file_path')
    if not file_path or not os.path.exists(file_path):
        flash('未找到上传的文件，请重新上传', 'danger')
        return redirect(url_for('upload'))


    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

   
    if 'comment' not in df.columns:
        flash('文件中必须包含 comment 列', 'danger')
        return redirect(url_for('upload'))

    
    df['Sentiment'] = ''
    df['Category'] = ''
    df['Themes'] = ''

    
    for i, row in df.iterrows():
        comment = row['comment']
        result = analyze_comment(comment)
        if result.startswith('ERROR'):
            df.at[i, 'Sentiment'] = 'Error'
            df.at[i, 'Category'] = 'Error'
            df.at[i, 'Themes'] = result
        else:
            try:
                parsed = json.loads(result)
                df.at[i, 'Sentiment'] = parsed.get('sentiment', '')
                df.at[i, 'Category'] = parsed.get('category', '')
                df.at[i, 'Themes'] = ', '.join(parsed.get('themes', []))
            except Exception:
                
                df.at[i, 'Themes'] = result

    
    save_path = file_path.rsplit('.', 1)[0] + '_processed.csv'
    df.to_csv(save_path, index=False)

    
    table_html = df.to_html(classes='table table-bordered', index=False)
    return render_template('result.html',
                           tables=[table_html],
                           titles=df.columns.values)

if __name__ == '__main__':
    app.run(debug=True)
