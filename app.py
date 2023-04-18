from flask import Flask, render_template, request, g, jsonify
import sqlite3

app = Flask(__name__)

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
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = request.form['date']
        category = request.form['category']
        amount = request.form['amount']

        # 插入数据到数据库
        db = get_db()
        db.execute("INSERT INTO bills (date, category, amount) VALUES (?, ?, ?)", (date, category, amount))
        db.commit()


    return render_template('index.html')

# 获取数据并返回JSON格式数据
@app.route('/data')
def get_data():
    db = get_db()
    cur = db.execute("SELECT category, SUM(amount) AS total, date FROM bills WHERE date BETWEEN date('now', 'start of month') AND date('now', 'start of month', '+1 month', '-1 day') GROUP BY category ORDER BY date")
    data = cur.fetchall()
    labels = []
    values = []
    for row in data:
        labels.append(row['category'])
        values.append(row['total'])
    time_range = f'{data[0][2]}至{data[-1][2]}'
    # response = {
    #     "time_range": time_range,
    #     "data": {
    #         "labels": labels,
    #         "values": values
    #     }
    # }
    return jsonify(labels=labels, values=values, time_range=time_range)

if __name__ == '__main__':
    app.run(debug=True)