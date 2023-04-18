from flask import Flask, render_template, request, g, jsonify, redirect, url_for
import sqlite3
import os
app = Flask(__name__)
if not os.path.exists('myDB.db'):
    conn = sqlite3.connect('myDB.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE bills
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL
                )''')
    conn.commit()
    conn.close()
# 连接数据库
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('myDB.db')
        g.db.row_factory = sqlite3.Row
    return g.db

# 关闭数据库连接
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

# 创建表
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

# 处理表单提交
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # 处理表单提交请求
    # ...
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = request.form['amount']

        # 插入数据到数据库
        db = get_db()
        db.execute("INSERT INTO bills (date, category, amount) VALUES (?, ?, ?)", (date, category, amount))
        db.commit()
        # 返回重定向响应
        return redirect(url_for("index"))

# 获取数据并返回JSON格式数据
@app.route('/data', methods=['POST', 'GET'])
def get_data():
    db = get_db()
    cur = db.execute("SELECT category, SUM(amount) AS total FROM bills GROUP BY category;")
    data = cur.fetchall()
    if not data:
        return jsonify(labels=[], values=[], time_range='')
    labels = []
    values = []
    for row in data:
        labels.append(row['category'])
        values.append(row['total'])
    cur = db.execute("SELECT date FROM bills WHERE date BETWEEN date('now', '-30 days') and date('now') ORDER BY date;")
    data = cur.fetchall()
    dates = []
    for row in data:
        dates.append(row[0])
    time_range = f'{dates[0]} to {dates[-1]}'
    return jsonify(labels=labels, values=values, time_range=time_range)

if __name__ == '__main__':
    app.run(debug=True)