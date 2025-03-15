const { time } = require('console');
const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
	email: { type: String, required: true },
	password: { type: String, required: true },
	events: {
		type: [{
			title: { type: String, required: true },
			start: { type: String },
			end: { type: String },
			description: { type: String },
			duration: { type: String },
		}],
		default: [],
	},
});

module.exports = mongoose.model('User', UserSchema);