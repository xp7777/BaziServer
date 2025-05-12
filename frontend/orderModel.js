const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const orderSchema = new Schema({
  userId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  amount: {
    type: Number,
    required: true,
    default: 9.9
  },
  status: {
    type: String,
    enum: ['pending', 'paid', 'failed', 'refunded'],
    default: 'pending'
  },
  paymentMethod: {
    type: String,
    enum: ['wechat', 'alipay'],
    required: true
  },
  createTime: {
    type: Date,
    default: Date.now
  },
  payTime: {
    type: Date
  },
  resultId: {
    type: Schema.Types.ObjectId,
    ref: 'BaziResult'
  },
  orderData: {
    gender: {
      type: String,
      enum: ['male', 'female'],
      required: true
    },
    birthTime: {
      year: Number,
      month: Number,
      day: Number,
      hour: Number,
      isLunar: Boolean
    },
    focusAreas: [String]
  }
}, { timestamps: true });

module.exports = mongoose.model('Order', orderSchema);
