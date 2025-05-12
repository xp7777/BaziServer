/**
 * 八字命理计算工具
 * 用于计算用户的八字和流年大运信息
 */

// 天干
const HEAVENLY_STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'];
// 地支
const EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥'];
// 五行
const FIVE_ELEMENTS = {
  '甲': 'wood', '乙': 'wood',
  '丙': 'fire', '丁': 'fire',
  '戊': 'earth', '己': 'earth',
  '庚': 'metal', '辛': 'metal',
  '壬': 'water', '癸': 'water',
  '子': 'water', '丑': 'earth',
  '寅': 'wood', '卯': 'wood',
  '辰': 'earth', '巳': 'fire',
  '午': 'fire', '未': 'earth',
  '申': 'metal', '酉': 'metal',
  '戌': 'earth', '亥': 'water'
};

/**
 * 计算八字
 * @param {Object} birthTime 出生时间对象，包含年、月、日、时
 * @param {Boolean} isLunar 是否农历
 * @param {String} gender 性别，'male'或'female'
 * @returns {Object} 八字数据
 */
function calculateBazi(birthTime, isLunar, gender) {
  // 实际项目中，这里应该使用真实的万年历数据和真太阳时计算
  // 为了演示，我们使用简化的计算方法
  
  // 如果是农历，转换为公历
  // 实际项目中，这里应该调用农历转公历的函数
  const solarDate = isLunar ? convertLunarToSolar(birthTime) : birthTime;
  
  // 计算年柱
  const yearStem = HEAVENLY_STEMS[(solarDate.year - 4) % 10];
  const yearBranch = EARTHLY_BRANCHES[(solarDate.year - 4) % 12];
  
  // 计算月柱
  // 实际项目中，这里应该根据节气计算
  const monthIndex = solarDate.month - 1;
  const monthStem = HEAVENLY_STEMS[(yearStem === '甲' || yearStem === '己' ? 0 : 
                     yearStem === '乙' || yearStem === '庚' ? 2 :
                     yearStem === '丙' || yearStem === '辛' ? 4 :
                     yearStem === '丁' || yearStem === '壬' ? 6 : 8) + monthIndex % 10];
  const monthBranch = EARTHLY_BRANCHES[(monthIndex + 2) % 12];
  
  // 计算日柱
  // 实际项目中，这里应该使用甲子纳音表计算
  const dayIndex = Math.floor((new Date(solarDate.year, solarDate.month - 1, solarDate.day).getTime() / 86400000) + 49) % 60;
  const dayStem = HEAVENLY_STEMS[dayIndex % 10];
  const dayBranch = EARTHLY_BRANCHES[dayIndex % 12];
  
  // 计算时柱
  // 实际项目中，这里应该根据真太阳时计算
  const hourIndex = Math.floor(solarDate.hour / 2);
  const hourStem = HEAVENLY_STEMS[(dayIndex % 10 * 2 + hourIndex) % 10];
  const hourBranch = EARTHLY_BRANCHES[hourIndex % 12];
  
  // 计算五行分布
  const fiveElements = {
    wood: 0,
    fire: 0,
    earth: 0,
    metal: 0,
    water: 0
  };
  
  // 统计天干地支的五行
  [yearStem, monthStem, dayStem, hourStem, yearBranch, monthBranch, dayBranch, hourBranch].forEach(char => {
    fiveElements[FIVE_ELEMENTS[char]]++;
  });
  
  // 计算大运流年
  // 实际项目中，这里应该根据性别和月柱计算大运
  const flowingYears = [];
  const startYear = new Date().getFullYear();
  
  for (let i = 0; i < 10; i++) {
    const year = startYear + i;
    const stemIndex = (year - 4) % 10;
    const branchIndex = (year - 4) % 12;
    
    flowingYears.push({
      year,
      heavenlyStem: HEAVENLY_STEMS[stemIndex],
      earthlyBranch: EARTHLY_BRANCHES[branchIndex],
      element: FIVE_ELEMENTS[HEAVENLY_STEMS[stemIndex]]
    });
  }
  
  return {
    yearPillar: {
      heavenlyStem: yearStem,
      earthlyBranch: yearBranch,
      element: FIVE_ELEMENTS[yearStem]
    },
    monthPillar: {
      heavenlyStem: monthStem,
      earthlyBranch: monthBranch,
      element: FIVE_ELEMENTS[monthStem]
    },
    dayPillar: {
      heavenlyStem: dayStem,
      earthlyBranch: dayBranch,
      element: FIVE_ELEMENTS[dayStem]
    },
    hourPillar: {
      heavenlyStem: hourStem,
      earthlyBranch: hourBranch,
      element: FIVE_ELEMENTS[hourStem]
    },
    fiveElements,
    flowingYears
  };
}

/**
 * 农历转公历
 * 实际项目中，这里应该使用真实的万年历数据
 * 为了演示，我们使用简化的转换方法
 * @param {Object} lunarDate 农历日期对象
 * @returns {Object} 公历日期对象
 */
function convertLunarToSolar(lunarDate) {
  // 实际项目中，这里应该使用真实的万年历数据进行转换
  // 为了演示，我们简单地返回原日期
  return {
    year: lunarDate.year,
    month: lunarDate.month,
    day: lunarDate.day,
    hour: lunarDate.hour
  };
}

module.exports = {
  calculateBazi
};
