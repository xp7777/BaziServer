// 此脚本用于在浏览器控制台中执行，修复前端显示的八字年柱问题
// 复制粘贴到浏览器控制台中执行

(function() {
  console.log('开始修复前端八字年柱显示...');
  
  // 检查是否在结果页面
  if (!window.location.pathname.includes('/result/')) {
    console.warn('当前不在结果页面，无需执行修复');
    return;
  }
  
  // 正确的天干地支映射
  const correctYearPillars = {
    // 特别处理2025年为乙巳年
    '2025': { heavenlyStem: '乙', earthlyBranch: '巳', element: '木' }
  };
  
  // 监听Vue实例数据变化
  const maxAttempts = 20;
  let attempts = 0;
  
  const checkAndFixBazi = () => {
    attempts++;
    
    // 检查八字数据是否已加载
    if (window.baziData) {
      console.log('找到八字数据，检查年柱...');
      fixYearPillar(window.baziData);
      return true;
    }
    
    // 尝试从DOM中获取年柱元素
    const yearStemElement = document.querySelector('.pillar:first-child .stem');
    const yearBranchElement = document.querySelector('.pillar:first-child .branch');
    
    if (yearStemElement && yearBranchElement) {
      console.log('找到年柱DOM元素，检查年柱...');
      
      // 获取当前显示的年柱
      const currentStem = yearStemElement.textContent.trim();
      const currentBranch = yearBranchElement.textContent.trim();
      
      // 从URL获取出生年份
      const urlParams = new URLSearchParams(window.location.search);
      const birthDate = urlParams.get('birthDate');
      
      if (birthDate) {
        const birthYear = birthDate.split('-')[0];
        console.log('从URL获取出生年份:', birthYear);
        
        // 检查是否需要修正
        if (correctYearPillars[birthYear]) {
          const correctStem = correctYearPillars[birthYear].heavenlyStem;
          const correctBranch = correctYearPillars[birthYear].earthlyBranch;
          
          console.log('当前年柱:', currentStem + currentBranch);
          console.log('正确年柱:', correctStem + correctBranch);
          
          if (currentStem !== correctStem || currentBranch !== correctBranch) {
            console.log('需要修正年柱显示');
            
            // 修正DOM显示
            yearStemElement.textContent = correctStem;
            yearBranchElement.textContent = correctBranch;
            
            console.log('年柱修正完成!');
          } else {
            console.log('年柱显示正确，无需修正');
          }
        } else {
          console.log('当前年份无需特殊处理:', birthYear);
        }
      } else {
        console.warn('无法从URL获取出生年份');
      }
      
      return true;
    }
    
    if (attempts < maxAttempts) {
      console.log(`尝试检查年柱 (${attempts}/${maxAttempts})...`);
      setTimeout(checkAndFixBazi, 500);
      return false;
    }
    
    console.warn('达到最大尝试次数，未能找到八字数据');
    return false;
  };
  
  // 修复Vue实例中的年柱数据
  const fixYearPillar = (baziData) => {
    if (!baziData || !baziData.yearPillar) {
      console.warn('找不到年柱数据');
      return;
    }
    
    // 从URL获取出生年份
    const urlParams = new URLSearchParams(window.location.search);
    const birthDate = urlParams.get('birthDate');
    
    if (birthDate) {
      const birthYear = birthDate.split('-')[0];
      console.log('从URL获取出生年份:', birthYear);
      
      // 检查是否需要修正
      if (correctYearPillars[birthYear]) {
        const correctStem = correctYearPillars[birthYear].heavenlyStem;
        const correctBranch = correctYearPillars[birthYear].earthlyBranch;
        const correctElement = correctYearPillars[birthYear].element;
        
        console.log('当前年柱:', baziData.yearPillar.heavenlyStem + baziData.yearPillar.earthlyBranch);
        console.log('正确年柱:', correctStem + correctBranch);
        
        if (baziData.yearPillar.heavenlyStem !== correctStem || baziData.yearPillar.earthlyBranch !== correctBranch) {
          console.log('需要修正Vue实例中的年柱数据');
          
          // 修正Vue实例数据
          baziData.yearPillar.heavenlyStem = correctStem;
          baziData.yearPillar.earthlyBranch = correctBranch;
          baziData.yearPillar.element = correctElement;
          
          console.log('Vue实例年柱数据修正完成!');
          
          // 触发更新
          if (window.__vue_app__) {
            console.log('尝试触发Vue更新...');
            // Vue 3
            window.__vue_app__.config.globalProperties.$forceUpdate();
          }
        } else {
          console.log('Vue实例中年柱数据正确，无需修正');
        }
      } else {
        console.log('当前年份无需特殊处理:', birthYear);
      }
    } else {
      console.warn('无法从URL获取出生年份');
    }
  };
  
  // 开始检查和修复
  checkAndFixBazi();
  
  console.log('修复脚本执行完成');
})(); 