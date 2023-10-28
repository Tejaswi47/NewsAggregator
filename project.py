import json
from flask_mail import Mail,Message
import smtplib
from datetime import date
import requests
from flask import Flask,redirect,url_for,render_template,request,flash,session,abort
from flask_session import Session
from itsdangerous import URLSafeTimedSerializer
import mysql.connector
from cmail import sendmail
from token_1 import token
from key import salt1,secret_key,key
GENDER_OPTIONS = ['Male', 'Female', 'Prefer not to say']
Data_base=mysql.connector.connect(host='localhost',user='root',password='Teja@2003',db='data')
project=Flask(__name__,template_folder='template')
project.secret_key=secret_key
project.config['SESSION_TYPE']='filesystem'
Session(project)
project.config['MAIL_SERVER'] = 'smtp.gmail.com'
project.config['MAIL_PORT'] = 465
project.config['MAIL_USE_TLS'] = False
project.config['MAIL_USE_SSL'] = True
project.config['MAIL_USERNAME'] = 'bodapatitejaswipratap8@gmail.com'
project.config['MAIL_PASSWORD'] = 'jnmvxfxwvvozcoza'
mail = Mail(project)
@project.route('/',methods=['GET','POST'])
@project.route('/')
def home():
    logged_in= session.get('user') is not None
    return render_template('home.html', logged_in=logged_in)
@project.route('/results',methods=['GET','POST'])
def search_results():
    query = request.args.get('query')
    relevant_urls = {
        'business': 'http://127.0.0.1:5000/business',
        'science': 'http://127.0.0.1:5000/science',
        'health': 'http://127.0.0.1:5000/health',
        'general': 'http://127.0.0.1:5000/general',
        'technology': 'http://127.0.0.1:5000/technology',
        'entertainment': 'http://127.0.0.1:5000/entertainment',
        'sports': 'http://127.0.0.1:5000/sports'
    }
    relevant_url = relevant_urls.get(query.lower()) 
    
    if relevant_url:
        return redirect(relevant_url)
    else:
       return render_template('error.html'), 404
@project.route('/about_us', methods=['GET'])
def about_us():
    cursor = Data_base.cursor(buffered=True)
    if 'user' in session:
        email = session['user'] 
        cursor.execute('SELECT fullname FROM details WHERE email = %s', [email])
        fullname = cursor.fetchone()[0]
        cursor.close()
        return render_template('about_us.html', user={'email': email, 'fullname': fullname})
    else:
        return render_template('about_us.html', user=None)
@project.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        Name = request.form['name']
        Email = request.form['email']
        Message = request.form['message']
        cursor = Data_base.cursor(buffered=True)
        try:
            cursor.execute('INSERT INTO contact (name, email, message) VALUES (%s, %s, %s)', (Name, Email, Message))
        except mysql.connector.IntegrityError as e:
            flash('Error: {}'.format(str(e)))
            return redirect(url_for('contact_us'))
        else:
            Data_base.commit()
            cursor.close()
            flash('Thank you for your complaint')
            return redirect(url_for('contact_us'))
    return render_template('contact.html')
@project.route('/business')
def business():
    response1=requests.get("https://newsapi.org/v2/top-headlines?country=in", params={'apikey':key, 'category':'business'}).json()
    return response1
@project.route('/entertainment')
def entertainment():
    response2=requests.get("https://newsapi.org/v2/top-headlines?country=in", params={'apikey':key, 'category':'entertainment'}).json()
    return response2
@project.route('/science')
def science():
    response3=requests.get("https://newsapi.org/v2/top-headlines?country=in", params={'apikey':key, 'category':'science'}).json()
    return response3
@project.route('/general')
def general():
    response4=requests.get("https://newsapi.org/v2/top-headlines?country=in", params={'apikey':key, 'category':'general'}).json()
    return response4
@project.route('/technology')
def technology():
    response5=requests.get("https://newsapi.org/v2/top-headlines?country=in", params={'apikey':key, 'category':'technology'}).json()
    return response5
@project.route('/health')
def health():
    response6=requests.get("https://newsapi.org/v2/top-headlines?country=in", params={'apikey':key, 'category':'health'}).json()
    return response6
@project.route('/sports')
def sports():
    response7=requests.get("https://newsapi.org/v2/top-headlines?country=in", params={'apikey':key, 'category':'sports'}).json()
    return response7
@project.route('/login',methods=['GET','POST'])
@project.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method == 'POST':
        Email = request.form['Email']
        Password = request.form['Password']
        Remember = request.form.get('Remember')
        cursor = Data_base.cursor(buffered=True)
        cursor.execute('SELECT COUNT(*) FROM details WHERE email = %s', [Email])
        count = cursor.fetchone()[0]
        if count == 1:
            cursor.execute('SELECT COUNT(*) FROM details WHERE email = %s AND password = %s', [Email, Password])
            p_count = cursor.fetchone()[0]
            if p_count == 1:
                if Remember == '1':
                    session['remember'] = True
                    session['email'] = Email
                else:
                    session.pop('remember', None)
                    session.pop('email', None)
                session['user'] = Email
                cursor.execute('SELECT email_status FROM details WHERE email = %s', [Email])
                status = cursor.fetchone()[0]
                cursor.close()
                if status != 'confirmed':
                    flash('Your email is not confirmed. Please confirm your email.')
                    return redirect(url_for('home'))
                else:
                    return redirect(url_for('home'))
            else:
                cursor.close()
                flash('Invalid password')
                return render_template('login.html')
        else:
            cursor.close()
            flash('Invalid email')
            return render_template('login.html')
    return render_template('login.html')
@project.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))
@project.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        Fullname=request.form['Fullname']
        Username=request.form['Username']
        Phonenumber=request.form['Phonenumber']
        Email=request.form['Email']
        Password=request.form['Password']
        gender=request.form['gender']
        cursor=Data_base.cursor(buffered=True)
        try:
           cursor.execute('insert into details (fullname,username,phonenumber,email,password,gender) values(%s,%s,%s,%s,%s,%s)',(Fullname,Username,Phonenumber,Email,Password,gender))
        except mysql.connector.IntegrityError:
            flash('Username or email is already in use')
            return render_template('signup.html', gender_options=GENDER_OPTIONS)
        else:
            Data_base.commit()
            cursor.close()
            subject='Email Confirmation'
            confirm_link=url_for('confirm',token=token(Email,salt1),_external=True)
            body=f"Thanks for signing up.Follow this link-\n\n{confirm_link}"
            sendmail(to=Email,body=body,subject=subject)
            flash('Confirmation link sent check your email')
            return render_template('signup.html', gender_options=GENDER_OPTIONS)
    return render_template('signup.html', gender_options=GENDER_OPTIONS)
@project.route('/confirm/<token>')
def confirm(token):
    try:
        serializer=URLSafeTimedSerializer(secret_key)
        Email=serializer.loads(token,salt=salt1,max_age=120)
    except Exception as e:
        abort(404,'Link expired')
    else:
        cursor=Data_base.cursor(buffered=True)
        cursor.execute('select email_status from details where email=%s',[Email])
        status=cursor.fetchone()[0]
        cursor.close()
        if status=='confirmed':
            flash('Email already confirmed')
            return redirect(url_for('login'))
        else:
            cursor=Data_base.cursor(buffered=True)
            cursor.execute("update details set email_status='confirmed' where email=%s",[Email])
            Data_base.commit()
            flash('Email confirmation success')
            return redirect(url_for('login'))
@project.route('/send_newsletter', methods=['GET', 'POST'])
def send_newsletter():
    api_key = key  
    api_endpoint = 'https://newsapi.org/v2/top-headlines'
    params = {
        'country': 'in',
        'apiKey': api_key
    }
    response = requests.get(api_endpoint, params=params)
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get('articles', [])
    else:
        return 'Failed to retrieve news data'
    newsletter_html = render_template('newsletter.html', articles=articles)
    if session.get('user'):
        cursor = Data_base.cursor(buffered=True)  
        cursor.execute('SELECT email FROM details WHERE email=%s', [session['user']])
        client = cursor.fetchone()[0]
        cursor.close()
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login('bodapatitejaswipratap8@gmail.com', 'jnmvxfxwvvozcoza')  
        subject = f"Daily Newsletter - {date.today()}"
        message = Message(subject=subject, sender=project.config['MAIL_USERNAME'], recipients=[client])
        message.html = newsletter_html
        mail.send(message)
        server.quit()
        return 'Newsletter sent successfully'
    else:
        return 'User not logged in'
project.run(debug=True, use_reloader=True)
