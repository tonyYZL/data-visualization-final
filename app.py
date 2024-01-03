from flask import Flask, request, render_template, make_response, redirect, url_for
import time, uuid, requests, json
from ast import literal_eval

app = Flask(__name__, static_url_path='/static')

dbBaseUrl = "http://localhost:3000"
webBaseUrl = "http://127.0.0.1:5001"
# dbBaseUrl = "JSON_SERVER_URL"
# webBaseUrl = "WEBSITE_URL"


# 首頁
@app.route('/')
def home():
    return render_template('home.html', title='首頁', page='home')


# 問卷頁面
@app.route('/form')
def form():
    return render_template('form.html', title='問卷', page='form')

# 問卷提交
@app.route('/submit', methods=['POST'])
def submit():
    if request.method=='POST':
        form_data = request.form

        new_data = {
            "id": request.cookies.get('SERIALNUM'),
            "gender": form_data['gender'],
            "age": form_data['age'],
            "ever_married": form_data['ever_married'],
            "Residence_type": form_data['Residence_type'],
            "bmi": form_data['bmi'],
            "smoking_status": form_data['smoking_status'],
            "stroke": form_data['stroke'],
            "email": form_data['q6_email6'] or ""
        }

        params = {}

        c = request.cookies.get('SERIALNUM')
        
        
        if c == None:
            gen_uuid = str(uuid.uuid4())
            new_data['id'] = gen_uuid

            url = dbBaseUrl + "/response"

            try:
                result = requests.post(url, params=params, json=new_data)
            except:
                return redirect(webBaseUrl + "/analytics")

            if result.status_code != 201:
                return "Submit failed"
            
            resp = make_response(redirect(webBaseUrl + "/analytics"))  
            resp.set_cookie(key='SERIALNUM', value=gen_uuid, expires=time.time() + 10*60)    
            return resp
        else:
            url = dbBaseUrl + f"/response/{c}"

            try:
                result = requests.get(url)
            except:
                return redirect(webBaseUrl + "/analytics")

            if result.status_code == 200:
                update_res = requests.put(url, params=params, data=new_data)
                if update_res.status_code != 200:
                    return "Update failed"
            else:
                url = dbBaseUrl + f"/response"
                result = requests.post(url, params=params, json=new_data)
                if result.status_code != 201:
                    return "Submit failed"
            
            return redirect(webBaseUrl + "/analytics")



# 圖表頁面
@app.route('/analytics')
def analytics():
    c = request.cookies.get('SERIALNUM')
    if c == None:
        return render_template('analytics.html', title='分析', page='analytics', form_response={})

    url = dbBaseUrl + f"/response/{c}"
    try:
        result = requests.get(url)
    except:
        return render_template('analytics.html', title='分析', page='analytics', form_response={})

    if result.status_code != 200:
        return render_template('analytics.html', title='分析', page='analytics', form_response={})

    data = literal_eval(result.content.decode('utf-8'))

    return render_template('analytics.html', title='分析', page='analytics', form_response=json.dumps(data))

@app.errorhandler(400)
def bad_request(error):
    return redirect(webBaseUrl)

@app.errorhandler(404)
def not_found(error):
    return redirect(webBaseUrl)

@app.errorhandler(405)
def method_not_allow(error):
    return redirect(webBaseUrl)

app.run(port=5001)