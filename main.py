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
    body = db.Column(db.Text(120))
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
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        redirect('/login')
    
    


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users = users)

    

@app.route('/blog', methods=[ 'POST','GET']) #this handler has a GET method because it sends a get request to the database. No data is posted.
def blog():
    if session:
        owner = User.query.filter_by(username = session['username']).first()
    blog_id = request.args.get('id')
    user_id = request.args.get('id')
    if blog_id == None:
        posts = Blog.query.filter_by(id = blog_id).all() #this line will query the blog entries by ID from the database
        
        return render_template('main_blog.html', posts=posts, blog_id=blog_id) #This line renders the main blog page along with the posts.
    elif user_id==None:
        
        posts=Blog.query.filter_by(owner_id = user_id).all()
        return render_template('main_blog.html', posts=posts)
    else:
        posts = Blog.query.get(blog_id)
        return render_template('individual_entry.html', posts=posts)

    
    
     
    
   

@app.route('/new_post', methods=[ 'POST', 'GET'])#This route gest both get and post, because it posts to the database, and it gets the form to load. 
def new_post():
    
    blog_name = ""
    entry = ""
    name_error = ""
    body_error = ""
    
    if request.method == 'POST':

        blog_name = request.form['new']
        entry = request.form['blog']            #This if statement gets the data from the form and creates an object from the Blog class.
        owner = User.query.filter_by(username=session['username'].first())
        
       
        if not blog_name:
            name_error = "This field cannot be empty"
        if not entry:
            body_error = "This field cannot be empty"
        if not name_error and not body_error:
            new_entry = Blog(blog_name, entry, owner)

        
            db.session.add(new_entry)  #These lines add and commit the data to the database. 
            db.session.commit()
            blog_id=Blog.query.order_by(Blog.id.desc()).first()
            user = owner
            return redirect('/blog?id={}&user={}'.format(new_entry.id, user.username)) #After adding the data to databse, it redirects back to the main blog page.
        
        
    return render_template('new_blog.html', title="Add a new blog", blog_name=blog_name, entry=entry,name_error = name_error,body_error=body_error)




@app.route('/login', methods=['POST' ,'GET'])
def login():
    username = " "
    username_error=""
    password_error = ""
    incorrect_username=""
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        
   
        user = User.query.filter_by(username=username).first()#this line verifies the user password to log the user in.
        if not user:
            incorrect_username= "User does not exist"
            if username==" ":
                username_error="This field cannot be empty"
        if not password:
            password_error="This field cannot be empty"
        if user and user.password != password:
            password_error= "You entered the wrong password"

       
        if user and user.password == password:#this conditional checks if the user is in the system's database.
            session['username'] = username #the session object is used to store data to be remebered by the databse
            #flash("Logged in")
            return redirect('/new_post')
   

    return render_template('login.html', username=username,username_error=username_error,password_error=password_error,incorrect_username=incorrect_username)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username = " "
    username_error=""
    password_error = ""
    verify_error=""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify_pass']
       
       
        current_user = User.query.filter_by(username=username).first()
        
        if len(username)<3:
            username_error="The username must be longer than 3 characters"
            if username==" ":
                username_error="This field cannot be blank"
        if password !=verify:
            password_error="Passwords do not match"
            verify_error="Passwords do not match"
        if len(password)<3:
            password_error="Password must be longer than 3 characters"
            if password ==" ":
                password_error="Field cannot be blank"
        if password != verify:
            password_error="Passwords do not match"
            verify_error="Passwords do not match"
        if not username_error and not password_error and not verify_error:
            if not current_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username']=username
                return redirect('/new_post')
            else:
                username_error="This username is already taken"
        
            
            
    return render_template('signup.html', username=username,username_error=username_error, password_error=password_error,verify_error=verify_error)
    

@app.route('/logout') 
def logout():
    del session['username']
    return redirect('/blog')   

 



if __name__ == '__main__':
    app.run()

    