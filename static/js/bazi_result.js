// 获取URL参数
function getQueryParam(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// 格式化八字数据
function formatBaziData(data) {
    if (!data) return "暂无数据";
    return `${data.year_gz} ${data.month_gz} ${data.day_gz} ${data.hour_gz}`;
}

// 检查字段是否为空或默认值
function isEmptyOrDefault(value) {
    return !value || value === "分析生成中..." || value === "暂无";
}

// 显示分析结果
function showAnalysisResult(data) {
    // 显示基本信息
    document.getElementById('name').textContent = data.name || "匿名用户";
    document.getElementById('gender').textContent = data.gender === "male" ? "男" : "女";
    document.getElementById('birthdate').textContent = data.birthdate || "未知";
    document.getElementById('birthtime').textContent = data.birthtime || "未知";
    document.getElementById('bazi').textContent = formatBaziData(data.bazi_data);
    
    // 显示分析状态
    const analysisStatus = data.analysisStatus || "pending";
    const analysisProgress = data.analysisProgress || 0;
    
    // 更新分析状态显示
    updateAnalysisStatus(analysisStatus, analysisProgress);
    
    // 显示分析结果
    if (data.analysis) {
        console.log("收到分析数据:", Object.keys(data.analysis));
        const analysis = data.analysis;
        
        // 输出调试信息
        console.log("父母情况:", analysis.parents);
        console.log("近五年运势:", analysis.future);
        console.log("人生规划建议:", analysis.lifePlan);
        
        // 核心分析部分
        displayAnalysisSection('coreAnalysis', analysis.coreAnalysis);
        displayAnalysisSection('fiveElements', analysis.fiveElements);
        displayAnalysisSection('shenShaAnalysis', analysis.shenShaAnalysis);
        displayAnalysisSection('keyPoints', analysis.keyPoints);
        
        // 生活各方面分析
        displayAnalysisSection('personality', analysis.personality);
        displayAnalysisSection('health', analysis.health);
        displayAnalysisSection('career', analysis.career);
        displayAnalysisSection('wealth', analysis.wealth);
        displayAnalysisSection('relationship', analysis.relationship);
        displayAnalysisSection('education', analysis.education);
        displayAnalysisSection('children', analysis.children);
        displayAnalysisSection('parents', analysis.parents);
        displayAnalysisSection('social', analysis.social);
        
        // 近五年运势和人生规划建议
        if (analysis.future && !isEmptyOrDefault(analysis.future)) {
            displayAnalysisSection('future', analysis.future);
        } else {
            // 尝试从social字段中提取近五年运势内容
            const futureMatch = /近五年运势(?:\s*\([^)]*\))?([\s\S]+?)(?=---|\Z)/i.exec(analysis.social);
            if (futureMatch && futureMatch[1]) {
                displayAnalysisSection('future', futureMatch[1].trim());
            } else {
                displayAnalysisSection('future', "分析生成中...");
            }
        }
        
        displayAnalysisSection('overall', analysis.overall);
        displayAnalysisSection('lifePlan', analysis.lifePlan);
        
        // 检查是否所有分析都已完成
        checkAnalysisCompletion(analysis);
    }
}

// 显示分析部分
function displayAnalysisSection(sectionId, content) {
    const sectionElement = document.getElementById(sectionId);
    if (sectionElement) {
        console.log(`显示 ${sectionId} 内容:`, content?.substring(0, 50) + "...");
        
        // 检查内容是否为空或默认值
        if (isEmptyOrDefault(content)) {
            sectionElement.innerHTML = `<p class="analysis-loading">分析生成中...</p>`;
        } else {
            // 处理内容中的换行
            const formattedContent = content
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // 处理加粗
            sectionElement.innerHTML = formattedContent;
        }
    } else {
        console.error(`未找到元素: ${sectionId}`);
    }
}

// 检查分析是否全部完成
function checkAnalysisCompletion(analysis) {
    // 检查是否所有分析都已完成
    const analysisCompleted = !Object.values(analysis).some(value => 
        value === "分析生成中..." || value === "暂无"
    );
    
    console.log("分析完成状态:", analysisCompleted);
    
    if (analysisCompleted) {
        // 所有分析都已完成，隐藏加载提示
        document.getElementById('analysisProgress').style.display = 'none';
        document.getElementById('analysisStatus').textContent = '分析已完成';
    }
}

// 更新分析状态显示
function updateAnalysisStatus(status, progress) {
    const statusElement = document.getElementById('analysisStatus');
    const progressElement = document.getElementById('analysisProgress');
    const progressBar = document.getElementById('progressBar');
    
    console.log(`更新分析状态: ${status}, 进度: ${progress}%`);
    
    if (status === 'completed' || progress === 100) {
        statusElement.textContent = '分析已完成';
        progressElement.style.display = 'none';
    } else if (status === 'failed') {
        statusElement.textContent = '分析失败，请重试';
        progressElement.style.display = 'none';
    } else {
        statusElement.textContent = 'AI正在生成八字分析结果，这可能需要30-60秒';
        progressElement.style.display = 'block';
        progressBar.style.width = `${progress}%`;
        progressBar.textContent = `${progress}%`;
    }
}

// 轮询获取分析结果
function pollAnalysisResult(resultId) {
    const checkInterval = 3000; // 3秒检查一次
    
    function checkResult() {
        console.log(`轮询获取结果: ${resultId}`);
        
        fetch(`/api/bazi/result/${resultId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log("API返回成功:", data.result.analysisStatus, data.result.analysisProgress);
                    showAnalysisResult(data.result);
                    
                    // 如果分析仍在进行中，继续轮询
                    const analysisStatus = data.result.analysisStatus || "pending";
                    const analysisProgress = data.result.analysisProgress || 0;
                    
                    if (analysisStatus !== 'completed' && analysisStatus !== 'failed' && analysisProgress < 100) {
                        setTimeout(checkResult, checkInterval);
                    }
                } else {
                    console.error("获取分析结果失败:", data.message);
                    document.getElementById('analysisStatus').textContent = '获取分析结果失败，请刷新页面重试';
                }
            })
            .catch(error => {
                console.error("API请求错误:", error);
                document.getElementById('analysisStatus').textContent = '网络错误，请检查连接后重试';
            });
    }
    
    // 开始轮询
    checkResult();
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log("页面加载完成，开始初始化");
    
    const resultId = getQueryParam('id');
    if (resultId) {
        console.log(`找到结果ID: ${resultId}`);
        // 开始轮询获取结果
        pollAnalysisResult(resultId);
    } else {
        console.error("未找到结果ID");
        document.getElementById('analysisStatus').textContent = '未找到分析ID，请返回首页重新提交';
    }
}); 