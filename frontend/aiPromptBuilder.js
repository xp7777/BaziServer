/**
 * AI提示词模板管理
 * 用于构建专业的八字命理分析提示词
 */

// 基础系统提示词
const SYSTEM_PROMPT = `你是一位专业的八字命理分析师，精通传统命理学和现代心理学。
你需要根据用户提供的八字命盘信息，进行专业、详细且个性化的分析。
分析应该客观、理性，避免过于迷信的表述，同时保留传统命理学的专业性。
请确保分析内容积极向上，给予用户实用的建议和指导。`;

// 健康分析提示词模板
const HEALTH_PROMPT = `
健康分析应考虑以下因素：
1. 五行平衡状况与对应的身体系统
   - 木对应肝胆系统
   - 火对应心脏、小肠、血液循环系统
   - 土对应脾胃、消化系统
   - 金对应肺、大肠、呼吸系统
   - 水对应肾、膀胱、泌尿系统
2. 日主强弱与体质特点
3. 大运流年对健康的影响
4. 具体的养生保健建议

请提供详细的健康状况分析和具体的养生建议，包括饮食、作息、运动等方面。
`;

// 财运分析提示词模板
const WEALTH_PROMPT = `
财运分析应考虑以下因素：
1. 财星、偏财、正财的状态
2. 财库的位置和状态
3. 大运流年对财运的影响
4. 适合的财富管理和投资策略

请提供详细的财运分析和具体的理财建议，包括适合的职业方向、投资策略、财富管理方法等。
`;

// 事业分析提示词模板
const CAREER_PROMPT = `
事业分析应考虑以下因素：
1. 官星、印星的状态
2. 日主与事业宫的关系
3. 大运流年对事业的影响
4. 适合的职业方向和发展策略

请提供详细的事业发展分析和具体的职业规划建议，包括适合的行业、职位、发展方向等。
`;

// 婚姻感情分析提示词模板
const RELATIONSHIP_PROMPT = `
婚姻感情分析应考虑以下因素：
1. 日主与配偶宫的关系
2. 桃花星的状态
3. 大运流年对婚姻感情的影响
4. 婚姻和谐的建议

请提供详细的婚姻感情分析和具体的关系经营建议，包括择偶标准、感情经营、沟通技巧等。
`;

// 子女分析提示词模板
const CHILDREN_PROMPT = `
子女分析应考虑以下因素：
1. 子女宫的状态
2. 日主与子女宫的关系
3. 大运流年对子女的影响
4. 亲子关系和教育方式的建议

请提供详细的子女缘分分析和具体的教育方式建议，包括亲子关系、教育理念、培养方向等。
`;

// 综合分析提示词模板
const OVERALL_PROMPT = `
综合分析应总结用户八字的整体特点，并提供全面的人生指导建议。
请关注以下几点：
1. 八字的整体格局和特点
2. 用户的性格特点和天赋优势
3. 人生发展的关键时期和机遇
4. 全面的人生规划和发展建议

请提供积极、实用、具体的建议，帮助用户更好地规划人生和把握机遇。
`;

/**
 * 构建完整的AI提示词
 * @param {Object} baziData 八字数据
 * @param {Array} focusAreas 关注领域
 * @returns {Object} 包含系统提示词和用户提示词的对象
 */
function buildCompletePrompt(baziData, focusAreas) {
  const { yearPillar, monthPillar, dayPillar, hourPillar, fiveElements, flowingYears } = baziData;
  
  // 构建基础八字信息
  let userPrompt = `请根据以下八字命盘信息，进行专业的命理分析：\n\n`;
  userPrompt += `四柱八字：\n`;
  userPrompt += `年柱：${yearPillar.heavenlyStem}${yearPillar.earthlyBranch}（${yearPillar.element}）\n`;
  userPrompt += `月柱：${monthPillar.heavenlyStem}${monthPillar.earthlyBranch}（${monthPillar.element}）\n`;
  userPrompt += `日柱：${dayPillar.heavenlyStem}${dayPillar.earthlyBranch}（${dayPillar.element}）\n`;
  userPrompt += `时柱：${hourPillar.heavenlyStem}${hourPillar.earthlyBranch}（${hourPillar.element}）\n\n`;
  
  userPrompt += `五行分布：\n`;
  userPrompt += `木：${fiveElements.wood}，火：${fiveElements.fire}，土：${fiveElements.earth}，金：${fiveElements.metal}，水：${fiveElements.water}\n\n`;
  
  userPrompt += `大运流年（未来5年）：\n`;
  flowingYears.slice(0, 5).forEach(year => {
    userPrompt += `${year.year}年：${year.heavenlyStem}${year.earthlyBranch}（${year.element}）\n`;
  });
  
  // 添加关注领域的专业提示
  userPrompt += `\n请重点分析以下方面，每个方面至少提供300字的详细分析：\n\n`;
  
  if (focusAreas.includes('health')) {
    userPrompt += `【健康状况】\n${HEALTH_PROMPT}\n\n`;
  }
  
  if (focusAreas.includes('wealth')) {
    userPrompt += `【财运分析】\n${WEALTH_PROMPT}\n\n`;
  }
  
  if (focusAreas.includes('career')) {
    userPrompt += `【事业发展】\n${CAREER_PROMPT}\n\n`;
  }
  
  if (focusAreas.includes('relationship')) {
    userPrompt += `【婚姻感情】\n${RELATIONSHIP_PROMPT}\n\n`;
  }
  
  if (focusAreas.includes('children')) {
    userPrompt += `【子女缘分】\n${CHILDREN_PROMPT}\n\n`;
  }
  
  // 添加综合分析提示
  userPrompt += `【综合建议】\n${OVERALL_PROMPT}\n\n`;
  
  userPrompt += `请按照以上各个方面分别进行分析，每个部分都应该有明确的标题，并提供详细、具体、实用的建议。特别关注未来2-3年的发展趋势和关键时期。`;
  
  return {
    systemPrompt: SYSTEM_PROMPT,
    userPrompt
  };
}

/**
 * 处理AI响应
 * @param {String} aiResponse AI返回的原始响应
 * @param {Array} focusAreas 关注领域
 * @returns {Object} 结构化的分析结果
 */
function processAIResponse(aiResponse, focusAreas) {
  // 实际项目中，这里应该解析AI的响应，提取各个部分的内容
  // 为了演示，我们返回模拟的分析结果
  
  // 默认分析结果
  const defaultAnalysis = {
    health: '您的八字中火土较旺，木水偏弱。从健康角度看，您需要注意心脑血管系统和消化系统的保养。建议平时多喝水，保持规律作息，避免过度劳累和情绪波动。2025-2026年间需特别注意肝胆健康，可适当增加绿色蔬菜的摄入，定期体检。',
    wealth: '您的财运在2025年有明显上升趋势，特别是在春夏季节。八字中金水相生，适合从事金融、贸易、水利相关行业。投资方面，稳健为主，可考虑分散投资组合。2027年有意外财运，但需谨慎对待，避免投机性强的项目。',
    career: '您的事业宫位较为稳定，具有较强的组织能力和执行力。2025-2026年是事业发展的关键期，有升职或转行的机会。建议提升专业技能，扩展人脉关系。您适合在团队中担任协调或管理角色，发挥沟通才能。',
    relationship: '您的八字中日柱为戊午，感情态度较为务实。2025年下半年至2026年上半年是感情发展的良好时期。已婚者需注意与伴侣的沟通，避免因工作忙碌而忽略家庭。单身者有机会通过社交活动或朋友介绍认识合适的对象。',
    children: '您的子女宫位较为温和，与子女关系和谐。教育方面，建议采用引导式而非强制式的方法，尊重子女的兴趣发展。2026-2027年是子女发展的重要阶段，可能需要您更多的关注和支持。',
    overall: '综合分析您的八字，2025-2027年是您人生的一个上升期，各方面都有良好发展。建议把握这段时间，在事业上积极进取，在健康上注意保养，在人际关系上广结善缘。您的人生态度积极乐观，具有较强的适应能力和抗压能力，这将帮助您度过人生中的各种挑战。'
  };
  
  // 根据用户关注领域过滤结果
  const filteredAnalysis = {};
  focusAreas.forEach(area => {
    if (defaultAnalysis[area]) {
      filteredAnalysis[area] = defaultAnalysis[area];
    }
  });
  
  // 确保总体建议始终包含
  filteredAnalysis.overall = defaultAnalysis.overall;
  
  return filteredAnalysis;
}

module.exports = {
  buildCompletePrompt,
  processAIResponse
};
