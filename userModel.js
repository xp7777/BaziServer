const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const userSchema = new Schema({
  phone: {
    type: String,
    required: true,
    unique: true
  },
  passwordHash: {
    type: String
  },
  createTime: {
    type: Date,
    default: Date.now
  },
  lastLoginTime: {
    type: Date,
    default: Date.now
  },
  status: {
    type: String,
    enum: ['active', 'inactive', 'banned'],
    default: 'active'
  }
}, { timestamps: true });

module.exports = mongoose.model('User', userSchema);
