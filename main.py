from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app) #this creates a database object to pass data
app.secret_key = 'omegabetaz1' #this secret key is required by sessions to work. For security purposes and session management.

class Blog(db.Model): #the class represents the data that will be stored in the database. We create this class so that SQL alchemy can create the tables.
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))#this property links the Blog model with the User class primary key. It links the user ID to the blog post. 

    

    def __init__(self, title, body, owner): #this is the class constructor
        self.title = title
        self.body = body
        self.owner = owner
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True) #unique avoids users from creating same username. Database will not allow this.
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')#this represents the one-to-many replationship between the blog table and the user, and binding the user with the posts they write.

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        redirect('/login')
    
    


        

@app.route('/')
def index():
    return render_template('index.html')

    

@app.route('/blog', methods=[ 'GET']) #this handler has a GET method because it sends a get request to the database. No data is posted.
def blog():
    blog_id = request.args.get('id')
    if blog_id == None:
        blog = Blog.query.all() #this line will query the blog entries from the database
        return render_template('main_blog.html', blog=blog) #This line renders the main blog page along with the posts.

    else:
        posts = Blog.query.get(blog_id)
        return render_template('individual_entry.html', posts=posts)

    
    
     
    
   

@app.route('/new_post', methods=[ 'POST', 'GET'])#This route gest both get and post, because it posts to the database, and it gets the form to load. 
def new_post():
    if request.method == 'POST':
        blog_name = request.form['new']
        entry = request.form['blog']            #This if statement gets the data from the form and creates an object from the Blog class.
        
        name_error = ""
        body_error = ""
        if not blog_name:
            name_error = "This field cannot be empty"
        if not entry:
            body_error = "This field cannot be empty"
        if not name_error and not body_error:
            new_entry = Blog(blog_name, entry)

        
            db.session.add(new_entry)  #These lines add and commit the data to the database. 
            db.session.commit()
            return redirect('/blog?id={}'.format(new_entry.id)) #After adding the data to databse, it redirects back to the main blog page.
        else:
            return render_template('new_blog.html',name_error=name_error,body_error=body_error,blog_name=blog_name,entry=entry) 
        
    return render_template('new_blog.html')




@app.route('/login', methods=['POST' ,'GET'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(name=name).first()#this line verifies the user password to log the user in
        if user and user.password == password:#this conditional checks if the user is in the system's database.
            session['username'] = name #the session object is used to store data to be remebered by the databse
            #flash("Logged in")
            return redirect('/')
        #else:
            #flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.form == 'POST':
        name = request.form['username']
        passWord = request.form['password']
        verify = request.form['verify_pass']
        current_user = User.query.filter_by(name=name).first()
        if not current_user:
            new_user = User(name, passWord)
            db.session.add(new_user)
            db.session.commit()
            session['username']=name
            return redirect('/new_post')
        
            #TODO return a message
            
    return render_template('signup.html')
    

@app.route('/logout') 
def logout():
    del session['username']
    return redirect('/')   

 



if __name__ == '__main__':
    app.run()

    