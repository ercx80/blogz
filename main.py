from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:Password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app) #this creates a database object to pass data

class Blog(db.Model): #the class represents the data that will be stored in the database. We create this class so that SQL alchemy can create the tables.
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    

    def __init__(self, title, body): #this is the class constructor
        self.title = title
        self.body = body

@app.route('/blog', methods=[ 'GET']) #this handler has a GET method because it sends a get request to the database. No data is posted.
def index():

    

    
    blog = Blog.query.all() #this line will query the blog entries from the database
     
    
    return render_template('main_blog.html', blog=blog) #This line renders the main blog page along with the posts.

@app.route('/new_post', methods=[ 'POST', 'GET'])#This route gest both get and post, because it posts to the database, and it gets the form to load. 
def new_post():
    if request.method == 'POST':
        blog_name = request.form['title']
        entry = request.form['blog']            #This if statement gets the data from the form and creates an object from the Blog class.
        new_entry = Blog(blog_name, entry)
        
        db.session.add(new_entry)  #These lines add and commit the data to the database. 
        db.session.commit()
        return redirect('/blog') #After adding the data to databse, it redirects back to the main blog page.
    else:
        return render_template('new_blog.html') 




if __name__ == '__main__':
    app.run()

    