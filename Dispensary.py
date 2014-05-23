# all the imports
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flaskext.mysql import MySQL
from config import config
import datetime
 
mysql = MySQL()
# create our little application :)
app = Flask(__name__)

for key in config:
    app.config[key] = config[key]

mysql.init_app(app)
app.config.from_object(__name__)


def get_cursor():
    return mysql.connect().cursor()

@app.teardown_appcontext
def close_db():
    """Closes the database again at the end of the request."""
    mysql.connect().close()

@app.route('/')
def screen():
    return render_template('screen.html') #show_entries

@app.route('/register')
def register():
    return render_template('show_entries.html')

@app.route('/add', methods=['POST']) #add
def add():
    db = get_cursor()
    sno=request.form['Sno']
    regno= request.form['Regno']
    fname=request.form['FirstName']
    mname=request.form['MiddleName']
    lname=request.form['LastName']
    bgroup=request.form['BloodGroup']
    dob=request.form['dateofbirth']
    year=int(dob[0:4])
    month=int(dob[5:7])
    date=int(dob[8:10])
    dob=datetime.date(year,month,date)
    age=request.form['Age']
    typ=request.form['Type']
    phn=request.form['phno']
    address=request.form['address']
    email=request.form['emailid']
    gender=request.form['sex']
    uname=request.form['uname']
    password=request.form['pwd']
    sql='insert into Users \
    (Sno, RegNo, FirstName, MiddleName,LastName, BloodGroup, DateofBirth, Age, Type, Phonenumber, Address,\
     email,gender) values (%s,%s,"%s","%s","%s","%s","%s",%s,%s,"%s","%s","%s","%s")'
    db.execute(sql%(sno,regno,fname,mname,lname,bgroup,dob,age,typ,phn,address,email,gender))
    db.execute("COMMIT")
    db.execute("insert into Login values('%s','%s','%s',%s)"%(regno,uname,password,typ))
    db.execute("COMMIT")
    flash('New user '+ regno + ' registered')
    return redirect(url_for('screen'))#show_entriesreturn render_template(url_for('show_entries.html'))

# @app.route('/reg', methods=['POST']) #reg
# def add_user():
#     if not session.get('logged_in'):
#         abort(401)
#     db = get_cursor()
#     db.execute('insert into Users (Sno, RegNo, First Name, Middle Name,Last Name, Blood Group, Date of Birth, Age, Type, Phone number, Address, email) values (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
#         [request.form['Sno'], request.form['RegNo'],request.form['FirstName'],request.form['MiddleName'],request.form['LastName'],request.form['BloodGroup'],request.form['DateOfBirth'],request.form['Age'],request.form['Type'],request.form['PhoneNumber'],request.form['text'],request.form['email']])

#     db.commit()
#     flash('New entry was successfully posted')
#     return redirect(url_for('show_entries'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    db=get_cursor()
    if request.method == 'POST':
        uname=str(request.form['username'])
        pwd=str(request.form['password'])
        sql='select Count(*) from Login where UserName="%s" and Password="%s"'%(uname,pwd)
        db.execute(sql)
        data = db.fetchone()[0]
        if data ==0:
            error='Invalid username/password'
        else:
            session['logged_in'] = True
            app.config['USERNAME'] = uname
            flash('You were logged in ')
        return redirect(url_for('screen'))
    return render_template('login.html', error=error) #login.html

t=0
@app.route('/inventory')
def inventory():
    db=get_cursor()
    db.execute('select * from Pharmacy order by Sno')
    entries = db.fetchall()
    db.execute('commit')
    return render_template('pharmventory.html',entries = entries)

@app.route('/insert',methods=['GET','POST'])
def insert():
    global t
    db=get_cursor()
    db.execute('select Count(1) from Pharmacy')
    t=db.fetchone()[0]
    if request.form['btn'] == 'insert':
        sno = (request.form['Sno'])
        name = (request.form['Name'])
        quantity = (request.form['qty'])
        batchno = request.form['bno']
        mfg =datetime.datetime.strptime(request.form['mfgdate'],"%d/%m/%Y")
        exp =datetime.datetime.strptime(request.form['expdate'],"%d/%m/%Y")
        sql = 'insert into Pharmacy values(%s,"%s",%s,%s,"%s","%s")'
        db.execute(sql%(sno,name,quantity,batchno,mfg,exp))
        db.execute("COMMIT")
        flash('New entry successfully inserted')
        return redirect(url_for('inventory'))
    else:
        flash('Record not inserted')
    return redirect(url_for('inventory'))

@app.route('/updel',methods=['GET','POST'])
def updel():
    global t
    db=get_cursor()
    db.execute('select Count(1) from Pharmacy')
    t=db.fetchone()[0]
    for i in range( 1, t+1):
            r = str(i)
            if request.form['btn1'] == 'update'+r:
                sno=request.form['Sno' + r]
                name=request.form['Name' + r]
                quantity=request.form['qty' + r]
                batchno=request.form['bno' + r]
                mfg =datetime.datetime.strptime(request.form['mfgdate' + r],"%d/%m/%Y")
                exp =datetime.datetime.strptime(request.form['expdate' + r],"%d/%m/%Y")
                query = 'update Pharmacy set Name="%s",Quantity=%s,Batchno=%s,ManufactureDate="%s",ExpiryDate="%s" where Sno=%s'
                db.execute(query%(name,quantity,batchno,mfg,exp,sno))
                db.execute("COMMIT")
                flash('Record '+sno+' updated')
                return redirect(url_for('inventory'))       
            elif request.form['btn1'] == 'delete'+r:
                sno=request.form['Sno' + r]
                query='delete from Pharmacy where Sno='+str(sno)
                db.execute(query)
                db.execute("COMMIT")
                flash('Record '+sno+' deleted')
                return redirect(url_for('inventory'))
            i=i+1
    flash('Nothing occured')
    return redirect(url_for('inventory'))

@app.route('/prescription')
def prescription():
    db = get_cursor()
    db.execute('select * from Prescription order by RegNo asc')
    entries = db.fetchall()
    return render_template('prescription.html',entries = entries)

@app.route('/fileprescription', methods=['GET','POST'])
def fileprescription():
    db = get_cursor()
    docno = request.form['DoctorNo']
    regno = request.form['RegNo']
    cause = request.form['Cause']
    meds = request.form['Medicine']
    qty = request.form['Quantity']
    remark = request.form['Remarks']
    db.execute('insert into Prescription values(%s,"%s","%s","%s",%s,"%s")'%(docno,regno,cause,meds,qty,remark))
    db.execute("COMMIT")
    flash('Prescription for '+regno+' has been given')
    return redirect(url_for('prescription'))

@app.route('/employee',methods=['GET','POST'])
def employee():
    db = get_cursor()
    error=None
    query = 'select EmpID from Login where UserName="%s"'
    db.execute(query%(app.config['USERNAME']))
    data = db.fetchone()
    entries =None
    if data is None:
        error = 'User details not entered properly in the database'
    else:
        db.execute('select * from Users join Employee where Users.RegNo=Employee.RegNo and Users.RegNo=%s',[data[0]])
        entries = db.fetchall()
    return render_template('employee_profile.html',entries = entries)

@app.route('/employeeinfo',methods=['GET','POST'])
def employeeinfo():
    return redirect(url_for('employee'))

@app.route('/student',methods=['GET','POST'])
def student():
    db = get_cursor()
    error=None
    chars=[chr(i) for i in xrange(ord('A'), ord('N')+1)]
    query = 'select EmpID from Login where UserName="%s"'
    db.execute(query%(app.config['USERNAME']))
    data = db.fetchone()
    entries =None
    if data is None:
        error = 'User details not entered properly in the database'
    else:
        db.execute('select * from Users join Student where Users.Regno=Student.Regno and Users.Regno=%s',[data[0]])
        entries = db.fetchall()
    return render_template('student_profile.html',entries = entries,chars=chars)
def years_between(d1):
    d2=datetime.datetime.today()
    d1=datetime.datetime.strptime(str(d1),"%Y-%m-%d")
    return ((d2-d1).days-(d2-d1).seconds/86400.0)/365.2425
@app.route('/studentinfo',methods=['GET','POST'])
def studentinfo():
    db=get_cursor()
    if request.method=="POST":
        lname=request.form['lname']
        fname=request.form['fname']
        mname=request.form['mname']
        regno=request.form['registration_number']
        sex=request.form['gender']
        dob=str(request.form['dob'])
        year=int(dob[0:4])
        month=int(dob[5:7])
        date=int(dob[8:10])
        dob=datetime.date(year,month,date)
        email=request.form['email']
        phno=request.form['phone_number']
        age=int(years_between(dob))
        db.execute('update Users set FirstName="%s",MiddleName="%s",LastName="%s",DateofBirth="%s",Age=%s,Phonenumber="%s",email="%s",gender="%s" where Regno=%s'%(fname,mname,lname,dob,age,phno,email,sex,regno))
        db.execute("COMMIT")
        year_join=int(request.form['year'])
        degree=request.form['course']
        branch=request.form['branch']
        section=request.form['section']
        rno=request.form['roll_number']
        hostelroomno=request.form['room_number']
        db.execute('update Student set Year=%s,Section="%s",Branch="%s",Degree="%s",RollNo="%s" where RegNo="%s"'%(year_join,section,branch,degree,rno,regno))
        db.execute("COMMIT")
        flash('Record '+regno+' updated') 
    return redirect(url_for('student'))

@app.route('/logout')
def logout():
    if session['logged_in']==True:
        session.pop('logged_in', None)
        flash('You were logged out')
    return redirect(url_for('screen'))#show_entries.html

if __name__ == '__main__':
    app.debug = True
    app.secret_key=os.urandom(24)
    app.run()