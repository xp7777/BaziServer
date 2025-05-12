const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const baziResultSchema = new Schema({
  userId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  orderId: {
    type: Schema.Types.ObjectId,
    ref: 'Order',
    required: true
  },
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
  focusAreas: [String],
  baziData: {
    yearPillar: {
      heavenlyStem: String,
      earthlyBranch: String,
      element: String
    },
    monthPillar: {
      heavenlyStem: String,
      earthlyBranch: String,
      element: String
    },
    dayPillar: {
      heavenlyStem: String,
      earthlyBranch: String,
      element: String
    },
    hourPillar: {
      heavenlyStem: String,
      earthlyBranch: String,
      element: String
    },
    fiveElements: {
      wood: Number,
      fire: Number,
      earth: Number,
      metal: Number,
      water: Number
    },
    flowingYears: [{
      year: Number,
      heavenlyStem: String,
      earthlyBranch: String,
      element: String
    }]
  },
  aiAnalysis: {
    health: String,
    wealth: String,
    career: String,
    relationship: String,
    children: String,
    overall: String
  },
  pdfUrl: String,
  createTime: {
    type: Date,
    default: Date.now
  }
}, { timestamps: true });

module.exports = mongoose.model('BaziResult', baziResultSchema);
