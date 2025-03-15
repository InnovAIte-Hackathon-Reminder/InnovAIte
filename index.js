require('ejs');
require('dotenv').config();

const express = require('express');
const bodyParser = require('body-parser');
const session = require('express-session');
const mongoose = require('mongoose');
const path = require('path');
const axios = require('axios');
const UserSchema = require('./models/user');

const app = express();
const PORT = 80;

app.set('json spaces', 1);
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.set('trust proxy', 1);

app.use(bodyParser.json());
app.use('/static', express.static('static'));
app.use('/node_modules', express.static(path.join(__dirname, 'node_modules')));
app.use(
	session({
		secret: 'BISAD2025',
		resave: true,
		saveUninitialized: true,
	}),
);

mongoose.connect(process.env.DB);

app.get('/', (req, res) => {
	if (!req.session.user) {
		return res.redirect('/auth');
	}
	res.render('index', { user: (req.session.user) });
});

// Authentication
app.get('/auth', (req, res) => {
	res.render('auth');
});

app.post('/auth', async (req, res) => {
	const { email, password } = req.body;
	let user = await UserSchema.findOne({ email: email });
	if (!user) {
		user = new UserSchema({ email, password });
		await user.save();
	} else if (user.password !== password) {
		return res.status(401).json({ message: 'Incorrect password' });
	}

	req.session.user = user.toObject();
	console.log(req.session.user);
	return res.status(200).json({ message: 'Login successful' });
});

app.post('/submit', async (req) => {
	// Take the server and make a request to it
	// The request will send the two arrays: the deadline one and the action one
	// The difference in the two arrays will be calculated by checking if 'allDay' is set to true or false
	// If false then it is the deadline...
	// The AI response is then put back to the DB
	// Khalas, finito, done
	const { deadlineArray, actionArray } = req.body;
	const serverUrl = 'to be done';
	// our commrade didn't do the server (and needs help with arranging it)
	try {

		const deadlines = deadlineArray.filter(item => item.allDay === false);
		const actions = actionArray.filter(item => item.allDay === true);

		const response = await axios.post(serverUrl, { deadlines, actions });
		await app.saveResponse(response.data);
		console.log('AI response saved successfully:', response.data);
	} catch (error) {
		console.error('Error processing deadlines:', error);
	}
});

app.listen(PORT, () => {
	console.log(`Server running on http://localhost:${PORT}`);
});