from flask import Flask, render_template, request, redirect, url_for
from DAL import DAL

# Serve static files directly from the project root so existing `static/` folder (with css/ and images/) works
app = Flask(__name__, static_folder='.', static_url_path='')

# Initialize Data Access Layer
dal = DAL('projects.db')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/projects')
def projects():
    # Get all active projects from the database
    all_projects = dal.execute_query(
        "SELECT * FROM projects WHERE IsActive = 1 ORDER BY DateCreated DESC"
    )
    # Convert sqlite3.Row objects to dictionaries for easier template access
    projects_list = [dict(project) for project in all_projects]
    return render_template('projects.html', projects=projects_list)


@app.route('/resume')
def resume():
    return render_template('resume.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # In a real site you'd send/store the message. Here we'll just redirect to thanks.
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        return redirect(url_for('thanks'))
    return render_template('contact.html')


@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        image_filename = request.form.get('imagefilename')
        technologies = request.form.get('technologies', '')
        project_url = request.form.get('projecturl', '')
        github_url = request.form.get('githuburl', '')
        
        # Prepare data for insertion
        project_data = {
            'Title': title,
            'Description': description,
            'ImageFileName': image_filename,
            'TechnologiesUsed': technologies,
            'ProjectURL': project_url,
            'GitHubURL': github_url,
            'IsActive': 1
        }
        
        # Insert into database
        dal.insert('projects', project_data)
        
        # Redirect to success page
        return redirect(url_for('project_added'))
    
    return render_template('add_project.html')


@app.route('/project_added')
def project_added():
    return render_template('project_added.html')


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')


if __name__ == '__main__':
    app.run(debug=True)
