from flask import Flask,render_template
app = Flask(__name__)

@app.route('/users/<name>')
def hello_world(name):
	newsfeed = ['physics', 'chemistry', 'dog', 'cat']
	mazare = "de ce"
	return render_template('user.html', name=name, newsfeed=newsfeed)

if __name__ == '__main__':
	app.run(debug=True)
