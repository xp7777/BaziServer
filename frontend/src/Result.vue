<template>
  <div class="result-container">
    <van-nav-bar title="分析结果" />
    
    <!-- 步骤面包屑 -->
    <div class="step-breadcrumb">
      <div class="step completed" style="color: #000000;">
        <van-icon name="passed" class="step-icon" />
        <span class="step-text">填写信息</span>
      </div>
      <div class="step-line completed"></div>
      <div class="step completed" style="color: #000000;">
        <van-icon name="passed" class="step-icon" />
        <span class="step-text">确认支付</span>
      </div>
      <div class="step-line completed"></div>
      <div class="step active" style="color: #000000;">
        <van-icon name="description" class="step-icon" />
        <span class="step-text">查看结果</span>
      </div>
    </div>
    
    <!-- 路径面包屑 -->
    <div class="breadcrumb">
      <router-link to="/" class="breadcrumb-item">
        <van-icon name="home-o" size="14" />
        首页
      </router-link>
      <van-icon name="arrow" class="breadcrumb-arrow" />
      <router-link to="/bazi-service" class="breadcrumb-item">
        <van-icon name="balance-o" size="14" />
        八字服务
      </router-link>
      <van-icon name="arrow" class="breadcrumb-arrow" />
      <span class="breadcrumb-item current" style="color: #000000;">
        <van-icon name="description" size="14" />
        分析结果
      </span>
    </div>
    
    <!-- 快捷操作 -->
    <div class="quick-actions">
      <van-button 
        type="primary" 
        size="large" 
        @click="goToBaziService"
        class="action-button"
      >
        <van-icon name="replay" />
        重新测算
      </van-button>
    </div>
    
    <!-- 现有结果内容 -->
    <van-nav-bar
      title="八字分析结果"
      left-text="返回"
      left-arrow
      @click-left="onClickLeft"
    />
    
    <div class="result-header">
      <h2>您的八字命盘分析</h2>
      <p>基于您的出生信息，AI为您提供的个性化人生指导</p>
    </div>
    
    <!-- 添加全局分析状态提示 -->
    <van-notice-bar
      v-if="analysisStatus === 'pending' && !isAnalysisContentLoaded()"
      color="#1989fa"
      background="#ecf9ff"
      left-icon="info-o"
      :scrollable="false"
      class="analysis-progress-notice"
    >
      <div class="analysis-progress">
        <p>正在生成AI分析结果，这可能需要30-60秒</p>
        <van-progress :percentage="analysisProgress" :show-pivot="false" color="#1989fa" />
      </div>
    </van-notice-bar>
    
    <!-- 添加手动刷新按钮 -->
    <div v-if="showManualRefresh" class="manual-refresh-container">
      <van-empty description="获取分析结果失败" />
      <van-button type="primary" size="normal" @click="manualRefresh">手动刷新</van-button>
      <p class="refresh-tip">如果多次刷新仍然失败，请联系客服</p>
    </div>
    
    <van-tabs v-model="activeTab" sticky v-if="!showManualRefresh">
      <van-tab title="命盘信息">
        <div class="bazi-chart">
          <h3>八字命盘</h3>
          <div v-if="baziChart && baziChart.yearPillar && baziChart.monthPillar && baziChart.dayPillar && baziChart.hourPillar" class="four-pillars">
            <!-- 年柱 -->
            <div class="pillar">
              <div class="stem">{{ baziChart.yearPillar.heavenlyStem }}</div>
              <div class="branch">{{ baziChart.yearPillar.earthlyBranch }}</div>
              <div class="label">年柱</div>
              <div class="nayin">{{ baziChart.yearPillar.naYin }}</div>
              <div class="shishen">{{ baziChart.yearPillar.shiShen }}</div>
              <div class="wangshuai">{{ baziChart.yearPillar.wangShuai }}</div>
            </div>
            
            <!-- 月柱 -->
            <div class="pillar">
              <div class="stem">{{ baziChart.monthPillar.heavenlyStem }}</div>
              <div class="branch">{{ baziChart.monthPillar.earthlyBranch }}</div>
              <div class="label">月柱</div>
              <div class="nayin">{{ baziChart.monthPillar.naYin }}</div>
              <div class="shishen">{{ baziChart.monthPillar.shiShen }}</div>
              <div class="wangshuai">{{ baziChart.monthPillar.wangShuai }}</div>
            </div>
            
            <!-- 日柱 -->
            <div class="pillar">
              <div class="stem">{{ baziChart.dayPillar.heavenlyStem }}</div>
              <div class="branch">{{ baziChart.dayPillar.earthlyBranch }}</div>
              <div class="label">日柱</div>
              <div class="nayin">{{ baziChart.dayPillar.naYin }}</div>
              <div class="shishen">{{ baziChart.dayPillar.shiShen }}</div>
              <div class="wangshuai">{{ baziChart.dayPillar.wangShuai }}</div>
            </div>
            
            <!-- 时柱 -->
            <div class="pillar">
              <div class="stem">{{ baziChart.hourPillar.heavenlyStem }}</div>
              <div class="branch">{{ baziChart.hourPillar.earthlyBranch }}</div>
              <div class="label">时柱</div>
              <div class="nayin">{{ baziChart.hourPillar.naYin }}</div>
              <div class="shishen">{{ baziChart.hourPillar.shiShen }}</div>
              <div class="wangshuai">{{ baziChart.hourPillar.wangShuai }}</div>
            </div>
          </div>
          <div v-else class="error-message">
            <van-empty description="八字数据加载失败，请重试" />
            <van-button type="primary" size="small" @click="reloadBaziData">重新加载</van-button>
          </div>
          
          <h3>五行分布</h3>
          <div class="five-elements" v-if="baziChart && baziChart.fiveElements">
            <div class="element" v-for="(value, element) in baziChart.fiveElements" :key="element">
              <div class="element-name">{{ getElementName(element) }}</div>
              <div class="element-value">{{ value }}</div>
            </div>
          </div>
          <div class="five-elements" v-else>
            <div class="element" v-for="element in ['wood', 'fire', 'earth', 'metal', 'water']" :key="element">
              <div class="element-name">{{ getElementName(element) }}</div>
              <div class="element-value">--</div>
            </div>
          </div>
          
          <!-- 添加神煞显示 -->
          <h3>神煞信息</h3>
          <div class="shen-sha-info" v-if="baziChart && baziChart.shenSha">
            <!-- AI神煞分析优先显示 -->
            <div v-if="aiAnalysis.shenShaAnalysis && aiAnalysis.shenShaAnalysis !== '暂无' && aiAnalysis.shenShaAnalysis !== '分析生成中...'" class="ai-shen-sha-analysis">
              <div class="markdown-content" v-html="renderMarkdown(aiAnalysis.shenShaAnalysis)"></div>
            </div>
            
            <!-- 传统神煞信息（当AI分析存在时作为补充，当AI分析不存在时作为主要显示） -->
            <div class="traditional-shen-sha" v-if="!aiAnalysis.shenShaAnalysis || aiAnalysis.shenShaAnalysis === '暂无' || aiAnalysis.shenShaAnalysis === '分析生成中...'">
              <div class="shen-sha-content">
                <div class="shen-sha-item">
                  <span class="label">日冲</span>
                  <span class="value">{{ baziChart.shenSha.dayChong }}</span>
                </div>
                <div class="shen-sha-item">
                  <span class="label">值神</span>
                  <span class="value">{{ baziChart.shenSha.zhiShen }}</span>
                </div>
                <div class="shen-sha-item">
                  <span class="label">喜神</span>
                  <span class="value">{{ baziChart.shenSha.xiShen }}</span>
                </div>
                <div class="shen-sha-item">
                  <span class="label">福神</span>
                  <span class="value">{{ baziChart.shenSha.fuShen }}</span>
                </div>
                <div class="shen-sha-item">
                  <span class="label">财神</span>
                  <span class="value">{{ baziChart.shenSha.caiShen }}</span>
                </div>
              </div>
              
              <!-- 本命神煞 -->
              <div class="ben-ming-sha" v-if="baziChart.shenSha.benMing && baziChart.shenSha.benMing.length > 0">
                <h4>本命神煞</h4>
                <div class="ben-ming-list">
                  <span v-for="(sha, index) in baziChart.shenSha.benMing" :key="index" class="ben-ming-item">
                    {{ sha }}
                  </span>
                </div>
              </div>
              
              <!-- 其他神煞分类 -->
              <div class="other-shen-sha" v-if="baziChart.shenSha.yearGan && baziChart.shenSha.yearGan.length > 0">
                <h4>年干神煞</h4>
                <div class="ben-ming-list">
                  <span v-for="(sha, index) in baziChart.shenSha.yearGan" :key="index" class="ben-ming-item">
                    {{ sha }}
                  </span>
                </div>
              </div>
              
              <div class="other-shen-sha" v-if="baziChart.shenSha.yearZhi && baziChart.shenSha.yearZhi.length > 0">
                <h4>年支神煞</h4>
                <div class="ben-ming-list">
                  <span v-for="(sha, index) in baziChart.shenSha.yearZhi" :key="index" class="ben-ming-item">
                    {{ sha }}
                  </span>
                </div>
              </div>
              
              <div class="other-shen-sha" v-if="baziChart.shenSha.dayGan && baziChart.shenSha.dayGan.length > 0">
                <h4>日干神煞</h4>
                <div class="ben-ming-list">
                  <span v-for="(sha, index) in baziChart.shenSha.dayGan" :key="index" class="ben-ming-item">
                    {{ sha }}
                  </span>
                </div>
              </div>
              
              <div class="other-shen-sha" v-if="baziChart.shenSha.dayZhi && baziChart.shenSha.dayZhi.length > 0">
                <h4>日支神煞</h4>
                <div class="ben-ming-list">
                  <span v-for="(sha, index) in baziChart.shenSha.dayZhi" :key="index" class="ben-ming-item">
                    {{ sha }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div class="shen-sha-info" v-else>
            <van-cell-group inset>
              <van-cell title="神煞信息" value="暂无数据" />
            </van-cell-group>
          </div>
          
          <!-- 添加大运显示 -->
          <h3>大运信息</h3>
          <div class="da-yun-info" v-if="baziChart && baziChart.daYun">
            <div class="qi-yun-info">
              <p>起运年龄: {{ baziChart.daYun.startAge }}岁</p>
              <p>起运年份: {{ baziChart.daYun.startYear }}年</p>
              <p>大运顺序: {{ baziChart.daYun.isForward ? '顺行' : '逆行' }}</p>
            </div>
            
            <!-- 大运列表 -->
            <div class="da-yun-table">
              <table class="custom-table">
                <thead>
                  <tr>
                    <th>年龄</th>
                    <th>年份</th>
                    <th>天干</th>
                    <th>地支</th>
                    <th>纳音</th>
                    <th>吉凶</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(yun, index) in baziChart.daYun.daYunList" :key="index">
                    <td>{{ yun.startAge }}-{{ yun.endAge }}</td>
                    <td>{{ yun.startYear }}-{{ yun.endYear }}</td>
                    <td>{{ yun.heavenlyStem }}</td>
                    <td>{{ yun.earthlyBranch }}</td>
                    <td>{{ yun.naYin }}</td>
                    <td>{{ yun.jiXiong }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="da-yun-info" v-else>
            <van-cell-group inset>
              <van-cell title="大运信息" value="暂无数据" />
            </van-cell-group>
          </div>
          
          <h3>流年信息</h3>
          <div class="liu-nian-info" v-if="baziChart && baziChart.flowingYears && baziChart.flowingYears.length">
            <table class="custom-table">
              <thead>
                <tr>
                  <th>年份</th>
                  <th>年龄</th>
                  <th>天干</th>
                  <th>地支</th>
                  <th>五行</th>
                  <th>神煞</th>
                  <th>吉凶</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(year, index) in baziChart.flowingYears" :key="index">
                  <td>{{ year.year }}</td>
                  <td>{{ year.age }}</td>
                  <td>{{ year.heavenlyStem }}</td>
                  <td>{{ year.earthlyBranch }}</td>
                  <td>{{ getElementName(year.ganElement) }}/{{ getElementName(year.zhiElement) }}</td>
                  <td>{{ year.shenSha && Array.isArray(year.shenSha) ? year.shenSha.join(', ') : '无' }}</td>
                  <td>{{ year.jiXiong || '未知' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="liu-nian-info" v-else>
            <van-empty description="流年数据暂无" />
          </div>
        </div>
      </van-tab>
      
      <van-tab title="AI分析结果">
        <div class="ai-analysis">
          <div v-if="userAge !== null && userAge < 0" class="age-notice">
            <van-notice-bar
              color="#1989fa"
              background="#ecf9ff"
              left-icon="info-o"
            >
              此分析针对未来出生的宝宝，重点关注性格特点、天赋才能和健康发展趋势。
            </van-notice-bar>
          </div>
          <div v-else-if="userAge !== null && userAge < 6" class="age-notice">
            <van-notice-bar
              color="#1989fa"
              background="#ecf9ff"
              left-icon="info-o"
            >
              此分析针对婴幼儿({{userAge}}岁)，重点关注性格特点、天赋才能和健康发展趋势。
            </van-notice-bar>
          </div>
          <div v-else-if="userAge !== null && userAge < 18" class="age-notice">
            <van-notice-bar
              color="#1989fa"
              background="#ecf9ff"
              left-icon="info-o"
            >
              此分析针对未成年人({{userAge}}岁)，重点关注性格特点、学业发展和健康状况。
            </van-notice-bar>
          </div>
          
                   
          <!-- 核心分析 -->
          <div class="analysis-section">
            <h3>八字命局核心分析</h3>
            <template v-if="!aiAnalysis.coreAnalysis || aiAnalysis.coreAnalysis === '暂无' || aiAnalysis.coreAnalysis === '分析生成中...' || aiAnalysis.coreAnalysis.includes('分析生成中')">
              <div class="loading-content">
                <van-loading size="24px" vertical>分析生成中...</van-loading>
              </div>
            </template>
            <div v-else v-html="renderMarkdown(aiAnalysis.coreAnalysis)" class="markdown-content"></div>
          </div>
          
          <!-- 五行旺衰与用神 -->
          <div class="analysis-section">
            <h3>五行旺衰与用神</h3>
            <template v-if="!aiAnalysis.fiveElements || aiAnalysis.fiveElements === '暂无' || aiAnalysis.fiveElements === '分析生成中...' || aiAnalysis.fiveElements.includes('分析生成中')">
              <div class="loading-content">
                <van-loading size="24px" vertical>分析生成中...</van-loading>
              </div>
            </template>
            <div v-else v-html="renderMarkdown(aiAnalysis.fiveElements)" class="markdown-content"></div>
          </div>
          
          <!-- 神煞解析 -->
          <div class="analysis-section">
            <h3>神煞解析</h3>
            <template v-if="!aiAnalysis.shenShaAnalysis || aiAnalysis.shenShaAnalysis === '暂无' || aiAnalysis.shenShaAnalysis === '分析生成中...'">
              <div class="loading-content">
                <van-loading size="24px" vertical>分析生成中...</van-loading>
              </div>
            </template>
            <div v-else v-html="renderMarkdown(aiAnalysis.shenShaAnalysis)" class="markdown-content"></div>
          </div>
          
          <!-- 大运与流年关键节点 -->
          <div class="analysis-section">
            <h3>大运与流年关键节点</h3>
            <template v-if="!aiAnalysis.keyPoints || aiAnalysis.keyPoints === '暂无' || aiAnalysis.keyPoints === '分析生成中...'">
              <div class="loading-content">
                <van-loading size="24px" vertical>分析生成中...</van-loading>
              </div>
            </template>
            <div v-else v-html="renderMarkdown(aiAnalysis.keyPoints)" class="markdown-content"></div>
          </div>
          
          <!-- 婚姻感情 -->
          <div class="analysis-section">
            <h3>{{ userAge !== null && userAge >= 18 ? '婚姻感情' : '未来感情发展' }}</h3>
            <template v-if="!aiAnalysis.relationship || aiAnalysis.relationship === '暂无' || aiAnalysis.relationship === '分析生成中...'">
              <div class="loading-content">
                <van-loading size="24px" vertical>分析生成中...</van-loading>
              </div>
            </template>
            <div v-else>
              <!-- 如果有追问分析结果，优先显示追问分析 -->
              <div v-if="followupAnalysis.relationship || followupAnalysis.marriage" class="enhanced-analysis">
                <div v-html="renderMarkdown(followupAnalysis.relationship || followupAnalysis.marriage)" class="markdown-content"></div>
                <div class="analysis-source">
                  <van-tag type="primary" size="medium">深度分析</van-tag>
                </div>
              </div>
              <div v-else v-html="renderMarkdown(aiAnalysis.relationship)" class="markdown-content"></div>
            </div>
          </div>
          
          <!-- 事业财运 -->
          <div class="analysis-section">
            <h3>{{ userAge !== null && userAge >= 18 ? '事业财运' : '未来事业财运' }}</h3>
            <template v-if="!aiAnalysis.career || aiAnalysis.career === '暂无' || aiAnalysis.career === '分析生成中...'">
              <div class="loading-content">
                <van-loading size="24px" vertical>分析生成中...</van-loading>
              </div>
            </template>
            <div v-else>
              <!-- 如果有追问分析结果，优先显示追问分析 -->
              <div v-if="followupAnalysis.career || followupAnalysis.work || followupAnalysis.money || followupAnalysis.wealth" class="enhanced-analysis">
                <div v-html="renderMarkdown(followupAnalysis.career || followupAnalysis.work || followupAnalysis.money || followupAnalysis.wealth)" class="markdown-content"></div>
                <div class="analysis-source">
                  <van-tag type="primary" size="medium">深度分析</van-tag>
                </div>
              </div>
              <div v-else v-html="renderMarkdown(aiAnalysis.career)" class="markdown-content"></div>
            </div>
          </div>
          
          <!-- 子女情况 -->
          <div class="analysis-section">
            <h3>{{ userAge !== null && userAge >= 18 ? '子女情况' : '未来子女缘分' }}</h3>
            <template v-if="!aiAnalysis.children || aiAnalysis.children === '暂无' || aiAnalysis.children === '分析生成中...'">
              <div class="loading-content">
                <van-loading size="24px" vertical>分析生成中...</van-loading>
              </div>
            </template>
            <div v-else>
              <!-- 如果有追问分析结果，优先显示追问分析 -->
              <div v-if="followupAnalysis.children || followupAnalysis.family" class="enhanced-analysis">
                <div v-html="renderMarkdown(followupAnalysis.children || followupAnalysis.family)" class="markdown-content"></div>
                <div class="analysis-source">
                  <van-tag type="primary" size="medium">深度分析</van-tag>
                </div>
              </div>
              <div v-else v-html="renderMarkdown(aiAnalysis.children)" class="markdown-content"></div>
            </div>
          </div>
          
          <!-- 父母情况 -->
          <div class="analysis-section">
            <h3>父母情况</h3>
            <template v-if="!aiAnalysis.parents || aiAnalysis.parents === '暂无' || aiAnalysis.parents === '分析生成中...'">
              <div class="loading-content">
                <van-loading size="24px" vertical>分析生成中...</van-loading>
              </div>
            </template>
            <div v-else>
              <!-- 如果有追问分析结果，优先显示追问分析 -->
              <div v-if="followupAnalysis.parents" class="enhanced-analysis">
                <div v-html="renderMarkdown(followupAnalysis.parents)" class="markdown-content"></div>
                <div class="analysis-source">
                  <van-tag type="primary" size="medium">深度分析</van-tag>
                </div>
              </div>
              <div v-else v-html="renderMarkdown(aiAnalysis.parents)" class="markdown-content"></div>
            </div>
          </div>
          
          <!-- 身体健康 -->
          <div class="analysis-section">
            <h3>身体健康</h3>
            <template v-if="!aiAnalysis.health || aiAnalysis.health === '暂无' || aiAnalysis.health === '分析生成中...'">
              <div class="loading-content">
                <van-loading size="24px" vertical>分析生成中...</van-loading>
              </div>
            </template>
            <div v-else>
              <!-- 如果有追问分析结果，优先显示追问分析 -->
              <div v-if="followupAnalysis.health" class="enhanced-analysis">
                <div v-html="renderMarkdown(followupAnalysis.health)" class="markdown-content"></div>
                <div class="analysis-source">
                  <van-tag type="primary" size="medium">深度分析</van-tag>
                </div>
              </div>
              <div v-else v-html="renderMarkdown(aiAnalysis.health)" class="markdown-content"></div>
            </div>
          </div>
          
          <!-- 学业 -->
          <div class="analysis-section">
            <h3>学业</h3>
            <template v-if="!aiAnalysis.education || aiAnalysis.education === '暂无' || aiAnalysis.education === '分析生成中...'">
              <div class="loading-content">
                <van-loading size="24px" vertical>分析生成中...</van-loading>
              </div>
            </template>
            <div v-else>
              <!-- 如果有追问分析结果，优先显示追问分析 -->
              <div v-if="followupAnalysis.education || followupAnalysis.study" class="enhanced-analysis">
                <div v-html="renderMarkdown(followupAnalysis.education || followupAnalysis.study)" class="markdown-content"></div>
                <div class="analysis-source">
                  <van-tag type="primary" size="medium">深度分析</van-tag>
                </div>
              </div>
              <div v-else v-html="renderMarkdown(aiAnalysis.education)" class="markdown-content"></div>
            </div>
          </div>
          
          <!-- 人际关系 -->
          <div class="analysis-section">
            <h3>人际关系</h3>
            <template v-if="!aiAnalysis.social || aiAnalysis.social === '暂无' || aiAnalysis.social === '分析生成中...'">
              <div class="loading-content">
                <van-loading size="24px" vertical>分析生成中...</van-loading>
              </div>
            </template>
            <div v-else>
              <!-- 如果有追问分析结果，优先显示追问分析 -->
              <div v-if="followupAnalysis.social || followupAnalysis.relationship || followupAnalysis.friends" class="enhanced-analysis">
                <div v-html="renderMarkdown(followupAnalysis.social || followupAnalysis.relationship || followupAnalysis.friends)" class="markdown-content"></div>
                <div class="analysis-source">
                  <van-tag type="primary" size="medium">深度分析</van-tag>
                </div>
              </div>
              <div v-else v-html="renderMarkdown(aiAnalysis.social)" class="markdown-content"></div>
            </div>
          </div>
          
          <!-- 近五年运势 -->
          <div class="analysis-section">
            <h3>近五年运势</h3>
            <template v-if="!aiAnalysis.future || aiAnalysis.future === '暂无' || aiAnalysis.future === '分析生成中...'">
              <div class="loading-content">
                <van-loading size="24px" vertical>分析生成中...</van-loading>
              </div>
            </template>
            <div v-else>
              <!-- 如果有追问分析结果，优先显示追问分析 -->
              <div v-if="followupAnalysis.future || followupAnalysis.fiveYears" class="enhanced-analysis">
                <div v-html="renderMarkdown(followupAnalysis.future || followupAnalysis.fiveYears)" class="markdown-content"></div>
                <div class="analysis-source">
                  <van-tag type="primary" size="medium">深度分析</van-tag>
                </div>
              </div>
              <div v-else v-html="renderMarkdown(aiAnalysis.future)" class="markdown-content"></div>
            </div>
          </div>
        </div>
      </van-tab>
    </van-tabs>
    
    <div class="action-buttons">
      <van-button type="primary" block @click="downloadPDF">
        下载PDF报告
      </van-button>
               
      <!-- 调试按钮 -->
      <van-button plain type="warning" 
                  block 
                  style="margin-top: 10px;" 
                  @click="reloadBaziData">
        重新加载分析数据
      </van-button>
    </div>
    
    <!-- 添加追问部分 -->
    <div class="followup-section" v-if="baziChart && !loading">
      <h2 class="section-title">深度分析</h2>
      <p class="section-desc">选择您感兴趣的领域，进行深度分析</p>
      
      <div class="followup-options">
        <div 
          v-for="option in followupOptions" 
          :key="option.id" 
          class="followup-option" 
          style="color: #000000;"
          :class="{ 'paid': option.paid }"
          @click="selectFollowupOption(option)"
        >
          <div class="option-content">
            <span class="option-name" style="color: #000000;">{{ option.name }}</span>
            <span class="option-status" v-if="option.paid" style="color: #000000;">已解锁</span>
            <span class="option-status" v-else>￥9.9</span>
          </div>
        </div>
      </div>
      
      <!-- 已支付的追问分析结果展示 -->
      <div v-if="currentFollowup && currentFollowup.paid" class="followup-result">
        <h3>{{ currentFollowup.name }}分析</h3>
        <div v-if="isLoadingFollowup" class="loading-content">
          <van-loading size="24px" vertical>分析加载中...</van-loading>
        </div>
        <div v-else-if="!followupAnalysis[currentFollowup.id]" class="loading-content">
          <van-empty description="分析结果尚未生成，请稍后刷新页面" />
          <van-button type="primary" size="small" @click="reloadFollowupAnalysis(currentFollowup.id)">
            刷新分析
          </van-button>
        </div>
        <div v-else class="analysis-content" v-html="renderMarkdown(followupAnalysis[currentFollowup.id])"></div>
      </div>
    </div>
    
    <!-- 追问支付对话框 -->
    <van-dialog
      v-model:show="showFollowupDialog"
      title="深度分析"
      confirm-button-text="支付 ￥9.9"
      show-cancel-button
      cancel-button-text="取消"
      @confirm="payForFollowup"
      :before-close="() => !isLoadingFollowup"
      style="color: #000000;"
    >
      <div class="followup-dialog-content">
        <p style="color: #000000;">您选择了「{{ currentFollowup?.name }}」深度分析</p>
        <p style="color: #000000;">支付后，AI将根据您的八字和流年运势，为您提供专业的命理分析</p>
      </div>
    </van-dialog>
  </div>
  <!-- 在 template 部分添加支付二维码弹窗 -->
  <van-popup :show="showQRCode" @update:show="showQRCode = $event" round>
    <div class="qrcode-container">
      <h3 style="color: #000000;">请扫码支付</h3>
      <div class="qrcode">
        <img v-if="qrCodeUrl && qrCodeUrl.startsWith('data:')" :src="qrCodeUrl" alt="支付二维码" />
        <iframe v-else-if="qrCodeUrl" :src="qrCodeUrl" frameborder="0" width="200" height="200"></iframe>
        <div v-else class="qrcode-placeholder">
          <p>正在加载支付二维码...</p>
        </div>
      </div>
      <p style="color: #000000;">支付金额: ¥9.90</p>
      <van-button type="primary" block @click="checkPaymentStatus">
        我已完成支付
      </van-button>
      <van-button plain block @click="showQRCode = false" style="margin-top: 10px">
        取消
      </van-button>
    </div>
  </van-popup>
</template>

<script setup>
import { ref, onMounted, reactive, computed, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Toast, Dialog } from 'vant';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';
import axios from 'axios';
import MarkdownIt from 'markdown-it';  // 添加markdown-it导入

// 创建markdown解析器实例
const md = new MarkdownIt({
  html: true,
  breaks: true,
  linkify: true,
  typographer: true
});

const route = useRoute();
const router = useRouter();
const resultId = ref(route.params.id || route.query.resultId);
const activeTab = ref(0);
const loading = ref(false);

// 添加分析状态相关变量
const isAnalyzing = ref(false);
const analyzeProgress = ref(0);
const analyzeTimer = ref(null);

// 渲染Markdown内容
const renderMarkdown = (content) => {
  if (!content) return '';
  try {
    // 检查内容是否已经是HTML
    if (content.includes('<') && content.includes('>') && content.includes('<div') || content.includes('<p>')) {
      // 如果已经含有HTML标签，可能已经被渲染过，直接返回
      return content;
    }

    // 预处理八字分析特殊格式
    let processedContent = content;
    
    // 处理加粗文本 **文本**
    processedContent = processedContent.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // 处理分隔符 --
    processedContent = processedContent.replace(/\s*--\s*/g, '<hr>');
    
    // 处理标题（以#开头的行）
    processedContent = processedContent.replace(/^(#+)\s+(.*?)$/gm, (match, hashes, text) => {
      const level = Math.min(hashes.length, 6);
      return `<h${level}>${text}</h${level}>`;
    });
    
    // 处理列表（以-或数字开头的行）
    processedContent = processedContent.replace(/^- (.*?)$/gm, '<li>$1</li>');
    processedContent = processedContent.replace(/^(\d+)\. (.*?)$/gm, '<li>$1. $2</li>');
    
    // 将连续的<li>元素包装在<ul>或<ol>中
    if (processedContent.includes('<li>')) {
      // 简单检测是否含有数字列表
      const hasNumberList = /^<li>\d+\./.test(processedContent);
      const listTag = hasNumberList ? 'ol' : 'ul';
      
      // 将连续的<li>元素包装在列表标签中
      processedContent = processedContent.replace(/(<li>.*?<\/li>\n*)+/g, match => {
        return `<${listTag}>${match}</${listTag}>`;
      });
    }
    
    // 处理段落
    if (!processedContent.includes('<p>')) {
      const paragraphs = processedContent.split('\n\n');
      processedContent = paragraphs.map(p => {
        // 如果段落不是以HTML标签开头，则添加<p>标签
        if (p.trim() && !p.trim().startsWith('<')) {
          return `<p>${p}</p>`;
        }
        return p;
      }).join('\n');
    }
    
    // 最后使用markdown-it处理任何剩余的Markdown标记
    return md.render(processedContent);
  } catch (e) {
    console.error('Markdown渲染失败:', e);
    return content; // 如果渲染失败，返回原始内容
  }
};

// 用户年龄，从URL参数或localStorage获取
const userAge = ref(null);
// 尝试从URL参数获取年龄
if (route.query.age && !isNaN(parseInt(route.query.age))) {
  userAge.value = parseInt(route.query.age);
} 
// 如果URL参数中没有年龄，尝试从localStorage获取
else if (localStorage.getItem('userAge') && !isNaN(parseInt(localStorage.getItem('userAge')))) {
  userAge.value = parseInt(localStorage.getItem('userAge'));
}
// 记录用户年龄到控制台，便于调试
console.log('用户年龄:', userAge.value);

// 从分析文本中提取特定部分内容
const getAnalysisContent = (sectionName) => {
  try {
    // 如果是性格特点或学业发展，直接从对应字段获取
    if (sectionName === '性格特点' && aiAnalysis.value.personality) {
      return aiAnalysis.value.personality;
    }
    
    if (sectionName === '学业发展' && aiAnalysis.value.education) {
      return aiAnalysis.value.education;
    }
    
    // 处理健康分析文本，尝试提取学业、性格等内容
    if (aiAnalysis.value.health) {
      const healthText = aiAnalysis.value.health;
      
      // 查找各部分的标记
      const sectionMatch = healthText.match(new RegExp(`###\\s*${sectionName}([\\s\\S]*?)(?=###|$)`, 'i'));
      if (sectionMatch && sectionMatch[1]) {
        return sectionMatch[1].trim();
      }
      
      // 如果是未来发展，尝试从overall中提取
      if (sectionName === '未来发展' && aiAnalysis.value.overall) {
        const futureMatch = aiAnalysis.value.overall.match(/未来(\d+)年[：:]([\s\S]*?)(?=（本分析|$)/i);
        if (futureMatch && futureMatch[2]) {
          return futureMatch[2].trim();
        }
      }
    }
    
    // 如果没有找到对应部分或提取失败，返回空字符串
    return '';
  } catch (e) {
    console.error(`提取${sectionName}内容时出错:`, e);
    return '';
  }
};

// 修改数据初始化
const focusAreas = ref([]);
const analysisResult = ref({});

// 检查分析内容是否已经加载
const isAnalysisContentLoaded = () => {
  if (!aiAnalysis.value) return false;
  
  // 检查核心分析部分是否已加载
  const hasCore = aiAnalysis.value.coreAnalysis && 
                 !aiAnalysis.value.coreAnalysis.includes('分析生成中') &&
                 aiAnalysis.value.coreAnalysis !== '暂无';
                 
  // 检查五行分析部分是否已加载
  const hasFiveElements = aiAnalysis.value.fiveElements && 
                         !aiAnalysis.value.fiveElements.includes('分析生成中') &&
                         aiAnalysis.value.fiveElements !== '暂无';
  
  // 如果核心分析和五行分析都已加载，认为分析内容已就绪
  return hasCore && hasFiveElements;
};

// 初始化八字数据
const baziData = ref({
  yearPillar: { 
    heavenlyStem: '', 
    earthlyBranch: '',
    naYin: '',
    shiShen: '',
    wangShuai: ''
  },
  monthPillar: { 
    heavenlyStem: '', 
    earthlyBranch: '',
    naYin: '',
    shiShen: '',
    wangShuai: ''
  },
  dayPillar: { 
    heavenlyStem: '', 
    earthlyBranch: '',
    naYin: '',
    shiShen: '',
    wangShuai: ''
  },
  hourPillar: { 
    heavenlyStem: '', 
    earthlyBranch: '',
    naYin: '',
    shiShen: '',
    wangShuai: ''
  },
  fiveElements: {},
  flowingYears: [],
  shenSha: {
    dayChong: '',
    zhiShen: '',
    xiShen: '',
    fuShen: '',
    caiShen: '',
    benMing: [],
    yearGan: [],
    yearZhi: [],
    dayGan: [],
    dayZhi: []
  },
  daYun: {
    startAge: 0,
    startYear: 0,
    isForward: true,
    daYunList: []
  },
  birthDate: null,
  birthTime: null,
  gender: null
});

// 初始化分析数据
const aiAnalysis = ref({
  health: '',
  career: '',
  relationship: '',
  children: '',
  social: '',
  future: '',
  parents: '',
  education: '',
  // 新增字段
  coreAnalysis: '',
  fiveElements: '',
  shenShaAnalysis: '',
  keyPoints: ''
});

const testApiConnection = async () => {
  try {
    Toast.loading('正在测试API连接...');
    // 使用配置好的http实例
    const response = await axios.get('/');
    console.log('API根路径响应:', response.data);
    Toast.success('API连接成功');
    return true;
  } catch (error) {
    console.error('API连接测试失败:', error);
    Toast.fail('API连接失败，请检查后端服务');
    return false;
  }
};

onMounted(async () => {
  // 先测试API连接
  const isApiConnected = await testApiConnection();
  if (!isApiConnected) {
    console.warn('API连接失败，将使用模拟数据');
    loading.value = false;
    return;
  }
  
  console.log('结果页面加载，URL参数中的ID:', resultId.value);
  
  // 如果没有resultId，尝试从本地存储获取
  const localResultId = localStorage.getItem('resultId');
  if (!resultId.value && localResultId) {
    console.log('从本地存储获取ID:', localResultId);
    // 更新resultId为从本地存储获取的值
    resultId.value = localResultId;
  }
  
  // 确保resultId是字符串类型，不是布尔值或其他数据类型
  if (resultId.value === true || resultId.value === false) {
    console.error('resultId不应该是布尔值:', resultId.value);
    resultId.value = localResultId || route.query.resultId || '';
  }
  
  console.log('最终使用的resultId:', resultId.value);
  
  // 如果resultId为空或无效，显示错误并尝试从URL查询参数获取
  if (!resultId.value) {
    console.error('缺少结果ID，无法获取分析结果');
    
    // 尝试从URL查询参数获取备选ID
    const urlResultId = route.query.resultId;
    if (urlResultId) {
      console.log('从URL查询参数获取备选ID:', urlResultId);
      resultId.value = urlResultId;
    } else {
      Toast.fail('缺少结果ID，无法获取分析结果');
      loading.value = false;
      return;
    }
  }
  
  // 存储确认的resultId到本地存储
  localStorage.setItem('resultId', resultId.value);
  
  // 显示加载提示
  Toast.loading({
    message: '正在加载八字分析结果，请稍候...',
    duration: 0,
    forbidClick: true
  });
  
  // 调用getBaziResult函数获取结果
  await getBaziResult();
  
  // 检查分析是否完成
  const stillAnalyzing = Object.values(aiAnalysis.value).some(
    value => typeof value === 'string' && value.includes('正在分析')
  );
  
  if (stillAnalyzing) {
    console.log('检测到分析仍在进行中...');
    Toast.loading({
      message: '正在生成八字分析结果，这可能需要30-60秒...',
      duration: 0
    });
    
    // 设置分析状态为进行中
    analysisStatus.value = 'pending';
    
    // 启动轮询
    await pollAnalysisStatus(resultId.value);
    Toast.success('分析完成');
    
    // 分析完成后更新状态
    analysisStatus.value = 'completed';
    analysisProgress.value = 100;
  }
  
  // 关闭加载提示
  Toast.clear();
});

const getElementName = (element) => {
  if (!element) return '--';
  
  const elementNames = {
    'wood': '木',
    'fire': '火',
    'earth': '土',
    'metal': '金',
    'water': '水',
    '木': '木',
    '火': '火',
    '土': '土',
    '金': '金',
    '水': '水'
  };
  
  return elementNames[element] || element;
};

const onClickLeft = () => {
  router.push('/');
};

// 修改后的直接流下载函数，适应后端始终返回文件流
const downloadPDFAsStream = async () => {
  Toast.loading({
    message: '正在生成PDF并下载报告...',
    duration: 0,
    position: 'middle',
    forbidClick: true
  });
  
  if (!resultId.value) {
    Toast.clear();
    Toast.fail('缺少结果ID，无法下载报告');
    return false;
  }
  
  try {
    console.log('直接下载报告, 结果ID:', resultId.value);
    
    // 创建下载链接，添加时间戳避免缓存问题和force参数强制重新生成
    const timestamp = new Date().getTime();
    // 默认启用markdown解析
    const downloadUrl = `/api/bazi/pdf/${resultId.value}?t=${timestamp}&force=true&parseMarkdown=true`;
    console.log('下载URL:', downloadUrl);
    
    // 使用fetch API获取文件流
    const response = await fetch(downloadUrl, {
      method: 'GET',
      cache: 'no-cache',
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
    
    // 检查错误
    if (!response.ok) {
      let errorMsg = `下载失败: HTTP错误 ${response.status}`;
      try {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const errorData = await response.json();
          errorMsg = errorData.message || errorMsg;
        } else {
          // 如果不是JSON格式的错误，尝试获取文本错误信息
          const errorText = await response.text();
          if (errorText) {
            errorMsg = `下载失败: ${errorText.substring(0, 100)}`;
          }
        }
      } catch (e) {
        console.error('解析错误响应失败:', e);
      }
      throw new Error(errorMsg);
    }
    
    // 检查内容类型
    const contentType = response.headers.get('content-type');
    const disposition = response.headers.get('content-disposition');
    
    console.log('响应内容类型:', contentType);
    console.log('响应内容处置:', disposition);
    
    // 确定文件名和扩展名
    let filename = `八字命理分析_${resultId.value}.pdf`;
    if (disposition && disposition.includes('filename=')) {
      const filenameMatch = disposition.match(/filename=["']?([^"']+)["']?/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1];
      }
    }
    
    // 确定文件类型
    const fileExtension = contentType && contentType.includes('html') ? 'html' : 'pdf';
    if (!filename.endsWith(fileExtension)) {
      filename = `八字命理分析_${resultId.value}.${fileExtension}`;
    }
    
    // 转换为Blob对象
    const blob = await response.blob();
    console.log('PDF Blob大小:', blob.size, '字节');
    
    // 检查Blob大小 - 注意：当浏览器接管下载时，可能会导致blob.size为0
    // 因此，如果有Content-Disposition头部，我们应该认为下载已经开始
    const isDownloadStarted = disposition && disposition.includes('attachment');
    if (blob.size === 0 && !isDownloadStarted) {
      throw new Error('下载的文件为空');
    }
    
    // 对于小文件，我们可以验证文件内容
    // 但对于大文件或浏览器接管的下载，跳过验证
    if (blob.size > 0 && blob.size < 1024*1024 && contentType && contentType.includes('pdf')) {
      try {
        // 读取文件头部以验证是否为有效的PDF
        const fileReader = new FileReader();
        const headerPromise = new Promise((resolve, reject) => {
          fileReader.onloadend = (e) => resolve(e.target.result);
          fileReader.onerror = (e) => reject(e);
        });
        fileReader.readAsArrayBuffer(blob.slice(0, 5));
        
        const header = await headerPromise;
        const headerView = new Uint8Array(header);
        const headerString = String.fromCharCode.apply(null, headerView);
        
        if (!headerString.startsWith('%PDF')) {
          console.error('无效的PDF文件头:', headerString);
          throw new Error('下载的不是有效的PDF文件');
        } else {
          console.log('PDF文件头验证通过');
        }
      } catch (e) {
        console.error('验证PDF文件失败:', e);
        // 如果是浏览器接管下载导致的验证失败，我们不抛出错误
        if (!isDownloadStarted) {
          throw new Error('验证PDF文件失败: ' + e.message);
        } else {
          console.warn('浏览器接管了下载，跳过PDF验证');
        }
      }
    }
    
    // 不管浏览器是否已经接管下载，我们都手动创建一个下载链接
    try {
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      console.log('创建Blob URL:', url);
      
      // 使用iframe方式下载，避免某些浏览器的下载拦截
      const iframe = document.createElement('iframe');
      iframe.style.display = 'none';
      document.body.appendChild(iframe);
      
      // 创建a标签并触发下载
      const a = document.createElement('a');
      a.href = url;
      a.download = `八字命理分析_${resultId.value}.pdf`; // 强制使用自定义文件名
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      
      // 在iframe中添加a标签并点击
      iframe.contentWindow.document.body.appendChild(a);
      console.log('触发下载, 文件名:', a.download);
      a.click();
      
      // 清理
      setTimeout(() => {
        window.URL.revokeObjectURL(url);
        document.body.removeChild(iframe);
        console.log('清理下载资源完成');
      }, 1000); // 增加延时确保下载开始
    } catch (e) {
      console.error('创建下载链接失败:', e);
      
      // 尝试使用window.open直接打开PDF
      try {
        console.log('尝试使用window.open方法下载');
        const pdfWindow = window.open(downloadUrl, '_blank');
        if (!pdfWindow) {
          console.warn('弹出窗口被阻止，尝试其他方法');
          // 提示用户直接打开链接
          Dialog.alert({
            title: '下载提示',
            message: '系统无法自动下载PDF，请点击确定后手动保存文件',
            confirmButtonText: '确定',
          }).then(() => {
            window.open(downloadUrl, '_blank');
          });
        }
      } catch (openError) {
        console.error('使用window.open下载失败:', openError);
        throw new Error('下载失败，请尝试使用其他浏览器');
      }
    }
    
    Toast.clear();
    Toast.success('报告下载成功');
    return true;
  } catch (error) {
    console.error('直接下载PDF出错:', error);
    Toast.clear();
    
    // 检查是否是因为浏览器已经接管了下载而导致的错误
    if (error.message && (
        error.message.includes('下载的文件为空') || 
        error.message.includes('验证PDF文件失败')
      )) {
      // 如果是这类错误，可能是浏览器已经开始下载，我们不显示错误
      console.log('可能是浏览器已经接管了下载，不显示错误');
      Toast.success('报告下载已开始，请等待浏览器完成下载');
      return true;
    }
    
    // 显示错误信息
    Toast.fail(error.message || '下载失败，请稍后重试');
    return false;
  }
};

// 修改主下载函数，添加重试逻辑
const downloadPDF = async () => {
  Toast.loading({
    message: '正在准备生成PDF报告...',
    duration: 5000,
    position: 'middle'
  });
  
  if (!resultId.value) {
    Toast.fail('缺少结果ID，无法生成报告');
    return;
  }
  
  try {
    // 先重新加载最新的数据，确保PDF包含最新的追问分析结果
    Toast.loading({
      message: '正在同步最新数据...',
      duration: 5000
    });
    
    // 获取最新的基础分析结果
    await getBaziResult();
    
    // 获取最新的追问分析结果
    await loadFollowupResults();
    
    Toast.loading({
      message: '正在生成并下载PDF报告...',
      duration: 5000
    });
    
    // 最多尝试3次下载
    let attempts = 0;
    let success = false;
    
    while (attempts < 3 && !success) {
      attempts++;
      
      if (attempts > 1) {
        console.log(`尝试第${attempts}次下载...`);
        Toast.loading({
          message: `尝试第${attempts}次下载...`,
          duration: 2000
        });
        // 在重试之前等待一段时间
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
      
      // 使用流式下载模式，并处理返回值
      success = await downloadPDFAsStream();
      
      // 如果流式下载成功，直接返回，不再尝试其他方法
      if (success === true) {
        return;
      }
    }
    
    // 如果多次尝试后仍然失败，提示用户
    if (!success) {
      Toast.clear();
      Dialog.alert({
        title: 'PDF下载失败',
        message: '下载PDF报告失败，请稍后再试。如果问题持续存在，请联系客服。',
      });
    }
  } catch (error) {
    console.error('下载PDF过程中发生错误:', error);
    Toast.clear();
    Toast.fail('生成PDF报告失败: ' + (error.message || '未知错误'));
  }
};

// 本地生成PDF的函数
const generatePDFLocally = async () => {
  console.log('使用客户端jsPDF库生成PDF');
  
  // 获取内容元素
  const element = document.querySelector('.result-container');
  if (!element) {
    throw new Error('找不到要转换的内容元素');
  }
  
  Toast.loading({
    message: '正在捕获页面内容...',
    duration: 5000
  });
  
  try {
    // 在捕获内容前先应用Markdown格式（临时）
    const sections = document.querySelectorAll('.analysis-section');
    const originalContents = [];
    
    // 确保所有Markdown内容都已经被渲染为HTML
    sections.forEach((section, index) => {
      const contentElement = section.querySelector('p, .markdown-content');
      if (contentElement && !contentElement.classList.contains('markdown-content')) {
        originalContents.push({
          element: contentElement,
          content: contentElement.innerHTML
        });
        
        // 如果内容中有Markdown语法但尚未渲染，则渲染它
        if (contentElement.textContent.includes('**') || 
            contentElement.textContent.includes('##') ||
            contentElement.textContent.includes('--') ||
            contentElement.textContent.includes('- ')) {
          contentElement.innerHTML = md.render(contentElement.textContent);
          contentElement.classList.add('markdown-content-temp');
        }
      }
    });
    
    // 使用html2canvas捕获内容
    const canvas = await html2canvas(element, {
      scale: 1,
      useCORS: true,
      logging: false,
      windowWidth: document.documentElement.offsetWidth,
      windowHeight: document.documentElement.offsetHeight,
    });
    
    Toast.loading({
      message: '正在生成PDF文件...',
      duration: 5000
    });
        
    // 创建PDF文档
    const pdf = new jsPDF('p', 'mm', 'a4');
        
    // 计算尺寸和比例
    const imgData = canvas.toDataURL('image/png');
    const imgWidth = 210; // A4宽度，单位mm
    const pageHeight = 297; // A4高度，单位mm
    const imgHeight = canvas.height * imgWidth / canvas.width;
    let heightLeft = imgHeight;
    let position = 0;
          
    // 添加首页
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;
    
    // 如果内容超过一页，添加更多页
    while (heightLeft > 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }
    
    // 添加页脚
    const pageCount = pdf.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
      pdf.setPage(i);
      pdf.setFontSize(10);
      pdf.setTextColor(150);
      pdf.text(`八字命理AI分析报告 - 页 ${i} / ${pageCount}`, pdf.internal.pageSize.getWidth() / 2, pdf.internal.pageSize.getHeight() - 10, { align: 'center' });
    }
    
    // 恢复原始内容
    originalContents.forEach(item => {
      if (item && item.element) {
        item.element.innerHTML = item.content;
        item.element.classList.remove('markdown-content-temp');
      }
    });
    
    // 保存PDF
    pdf.save(`八字命理分析_${resultId.value}.pdf`);
    
    return true;
  } catch (error) {
    console.error('本地PDF生成错误:', error);
    throw error;
  }
};

const shareResult = () => {
  Toast.success('分享功能开发中');
};

// 处理本地PDF生成
const handleLocalPDFGeneration = async () => {
  try {
    Toast.loading({
      message: '正在本地生成PDF...',
      duration: 0,
      forbidClick: true
    });
    
    // 确保所有内容都已经渲染Markdown
    const sections = document.querySelectorAll('.analysis-section');
    const originalContents = [];
    let needsRendering = false;
    
    // 检查是否有内容需要渲染
    sections.forEach((section) => {
      const contentElement = section.querySelector('p:not(.markdown-content)');
      if (contentElement) {
        needsRendering = true;
      }
    });
    
    // 如果需要渲染，先将所有内容进行Markdown渲染
    if (needsRendering) {
      console.log('检测到需要渲染Markdown内容');
      sections.forEach((section) => {
        const contentElements = section.querySelectorAll('p:not(.markdown-content)');
        contentElements.forEach((element) => {
          const text = element.textContent;
          if (text && (
            text.includes('**') || 
            text.includes('#') || 
            text.includes('-') || 
            text.includes('1.') ||
            text.includes('\n')
          )) {
            originalContents.push({
              element: element,
              content: element.innerHTML
            });
            element.innerHTML = md.render(text);
            element.classList.add('markdown-content');
            element.classList.add('temp-rendered');
          }
        });
      });
    }
    
    // 生成PDF
    await generatePDFLocally();
    
    // 恢复原始内容
    if (needsRendering) {
      document.querySelectorAll('.temp-rendered').forEach((element) => {
        const original = originalContents.find(item => item.element === element);
        if (original) {
          element.innerHTML = original.content;
          element.classList.remove('markdown-content');
          element.classList.remove('temp-rendered');
        }
      });
    }
    
    Toast.clear();
    Toast.success('本地PDF生成成功');
  } catch (error) {
    console.error('本地PDF生成失败:', error);
    Toast.clear();
    Toast.fail('本地PDF生成失败: ' + (error.message || '未知错误'));
  }
};

// 添加分析状态检查函数
const checkAnalysisStatus = async (resultId) => {
  try {
    console.log('检查分析状态:', resultId);
    const response = await axios.get(`/api/bazi/result/${resultId}`);
    
    if (response.data.code === 200) {
      // 检查AI分析是否已经生成
      const aiAnalysisData = response.data.data.aiAnalysis || {};
      
      // 统计已完成和正在分析的项目
      let totalItems = 0;
      let completedItems = 0;
      
      Object.entries(aiAnalysisData).forEach(([key, value]) => {
        totalItems++;
        if (!(typeof value === 'string' && value.includes('正在分析'))) {
          completedItems++;
        }
      });
      
      // 更新进度
      if (totalItems > 0) {
        analyzeProgress.value = Math.floor((completedItems / totalItems) * 100);
      }
      
      // 检查是否还有"正在分析"的内容
      const stillAnalyzing = Object.values(aiAnalysisData).some(
        value => typeof value === 'string' && value.includes('正在分析')
      );
      
      isAnalyzing.value = stillAnalyzing;
      
      if (stillAnalyzing) {
        console.log('分析仍在进行中...', `完成度: ${analyzeProgress.value}%`);
        return false;
      } else {
        console.log('分析已完成');
        return true;
      }
    }
    return false;
  } catch (error) {
    console.error('检查分析状态出错:', error);
    return false;
  }
};

// 轮询检查分析状态
const pollAnalysisStatus = async (resultId) => {
  let attempts = 0;
  const maxAttempts = 30; // 最多轮询30次，约60秒
  
  // 启动模拟进度条
  if (!analyzeTimer.value) {
    let progress = analysisProgress.value || 0;
    analyzeTimer.value = setInterval(() => {
      if (progress < 95) { // 最多到95%，留5%给实际完成时
        progress += Math.random() * 3;
        if (progress > 95) progress = 95;
        analysisProgress.value = Math.floor(progress);
      }
    }, 1000);
  }
  
  // 检查分析状态
  const checkAnalysisStatus = async (resultId) => {
    try {
      const response = await axios.get(`/api/bazi/result/${resultId}`);
      if (response.data.code === 200) {
        const data = response.data.data;
        
        // 更新AI分析结果
        if (data.aiAnalysis) {
          aiAnalysis.value = {
            ...aiAnalysis.value,
            ...data.aiAnalysis
          };
        }
        
        // 检查分析状态
        const status = data.analysisStatus || 'completed';
        const progress = data.analysisProgress || 0;
        
        // 更新状态和进度
        analysisStatus.value = status;
        analysisProgress.value = progress;
        
        // 检查是否完成
        if (status === 'completed' || progress >= 100) {
          return true;
        }
        
        // 检查分析内容是否已加载，如果已加载则认为已完成
        if (isAnalysisContentLoaded()) {
          analysisStatus.value = 'completed';
          analysisProgress.value = 100;
          return true;
        }
        
        // 检查内容是否已生成（即使状态未更新）
        const allGenerated = !Object.values(aiAnalysis.value).some(
          value => typeof value === 'string' && value.includes('正在分析')
        );
        
        return allGenerated;
      }
      return false;
    } catch (error) {
      console.error('检查分析状态失败:', error);
      return false;
    }
  };
  
  return new Promise((resolve) => {
    const checkInterval = setInterval(async () => {
      attempts++;
      const isComplete = await checkAnalysisStatus(resultId);
      
      if (isComplete || attempts >= maxAttempts) {
        clearInterval(checkInterval);
        
        // 清除模拟进度定时器
        if (analyzeTimer.value) {
          clearInterval(analyzeTimer.value);
          analyzeTimer.value = null;
        }
        
        if (isComplete) {
          // 如果完成，确保进度显示100%
          analysisProgress.value = 100;
          setTimeout(() => {
            analysisStatus.value = 'completed';
          }, 1000); // 短暂显示100%后隐藏进度条
        }
        
        await getBaziResult(); // 最后再获取一次完整结果
        Toast.clear();
        resolve(isComplete);
      }
    }, 2000); // 每2秒检查一次
  });
};

// 重新加载八字数据
const reloadBaziData = async () => {
  try {
    Toast.loading({
      message: '正在加载现有分析结果...',
      duration: 0,
      forbidClick: true
    });
    
    const response = await axios.get(`/api/bazi/result/${resultId.value}`);
    
    if (response.data.code === 200) {
      // 更新八字数据
      if (response.data.data.baziChart) {
        baziChart.value = response.data.data.baziChart;
      }
      
      // 更新AI分析结果
      if (response.data.data.aiAnalysis) {
        aiAnalysis.value = response.data.data.aiAnalysis;
      }
      
      // 更新用户信息
      if (response.data.data.gender) {
        userGender.value = response.data.data.gender === 'male' ? '男' : '女';
      }
      
      if (response.data.data.birthTime) {
        userBirthTime.value = response.data.data.birthTime;
      }
      
      // 更新分析状态
      analysisStatus.value = response.data.data.analysisStatus || 'completed';
      analysisProgress.value = response.data.data.analysisProgress || 100;
      
      // 检查分析内容是否已加载，如果已加载则强制更新状态为completed
      if (isAnalysisContentLoaded()) {
        analysisStatus.value = 'completed';
        analysisProgress.value = 100;
      }
      
      console.log('分析状态:', analysisStatus.value);
      console.log('分析进度:', analysisProgress.value);
      console.log('AI分析结果更新:', aiAnalysis.value);
      
      // 重新加载追问分析结果
      console.log('重新加载追问分析结果...');
      await loadFollowupResults();
      
      // 遍历所有已支付的追问选项，强制重新获取分析结果
      const paidOptions = followupOptions.value.filter(option => option.paid);
      if (paidOptions.length > 0) {
        console.log('发现已支付的追问选项，强制重新获取:', paidOptions.map(o => o.id));
        for (const option of paidOptions) {
          await getFollowupAnalysis(option.id);
        }
      }
      
      Toast.success('数据刷新成功');
    } else {
      Toast.fail(response.data.message || '加载失败');
    }
  } catch (error) {
    console.error('重新加载失败:', error);
    Toast.fail('加载失败: ' + (error.message || '未知错误'));
  }
};

// 追问相关状态
const followupOptions = ref([
  { id: 'marriage', name: '婚姻感情', selected: false, paid: false },
  { id: 'career', name: '事业财运', selected: false, paid: false },
  { id: 'children', name: '子女情况', selected: false, paid: false },
  { id: 'parents', name: '父母情况', selected: false, paid: false },
  { id: 'health', name: '身体健康', selected: false, paid: false },
  { id: 'education', name: '学业', selected: false, paid: false },
  { id: 'relationship', name: '人际关系', selected: false, paid: false },
  { id: 'fiveYears', name: '近五年运势', selected: false, paid: false }
]);

const currentFollowup = ref(null);
const showFollowupDialog = ref(false);
const followupAnalysis = ref({});
const isLoadingFollowup = ref(false);

// 选择追问选项
const selectFollowupOption = async (option) => {
  // 设置当前选择的追问选项
  currentFollowup.value = option;
  
  // 如果已经支付过，直接显示结果
  if (option.paid) {
    console.log(`选择已支付的追问: ${option.id}`);
    
    // 如果已有分析结果，直接显示
    if (followupAnalysis.value[option.id]) {
      console.log(`已有${option.id}分析结果，直接显示`);
      return;
    }
    
    // 如果没有分析结果，尝试获取
    console.log(`尝试获取${option.id}分析结果`);
    Toast.loading({
      message: '正在加载分析结果...',
      duration: 0
    });
    
    try {
      // 尝试获取分析结果
      const analysis = await getFollowupAnalysis(option.id);
      if (analysis && typeof analysis === 'string' && analysis.length > 0) {
        Toast.success('加载成功');
        console.log(`成功获取${option.id}分析结果，长度: ${analysis.length}`);
      } else {
        Toast.fail('分析结果尚未生成完成，请稍后再试');
        console.warn(`获取${option.id}分析结果失败或为空`);
      }
    } catch (error) {
      console.error(`获取${option.id}分析失败:`, error);
      Toast.fail('获取分析失败，请重试');
    } finally {
      Toast.clear();
    }
    
    return;
  }
  
  // 否则显示支付对话框
  showFollowupDialog.value = true;
};

// 在 script setup 部分添加弹窗状态
const showQRCode = ref(false);
const qrCodeUrl = ref('');
let followupPaymentInterval = null; // 添加轮询定时器变量

// 监听二维码显示状态，自动启动轮询
watch(showQRCode, (newVal) => {
  if (newVal) {
    // 显示二维码时，启动轮询
    startFollowupPaymentPolling();
  } else if (followupPaymentInterval) {
    // 隐藏二维码时，停止轮询
    clearInterval(followupPaymentInterval);
  }
});

// 组件卸载时清除定时器
onUnmounted(() => {
  if (followupPaymentInterval) {
    clearInterval(followupPaymentInterval);
  }
});

// 添加轮询支付状态的函数
const startFollowupPaymentPolling = () => {
  // 每3秒查询一次支付状态
  followupPaymentInterval = setInterval(async () => {
    try {
      const followupOrderId = window.currentFollowupOrderId;
      if (!followupOrderId) return;
      
      console.log('自动轮询追问支付状态:', followupOrderId);
      const statusResponse = await axios.get(`/api/order/query/${followupOrderId}`);
      
      if (statusResponse.data.code === 200) {
        const orderStatus = statusResponse.data.data.status;
        console.log(`支付状态查询结果: ${orderStatus}`, statusResponse.data);
        
        if (orderStatus === 'paid') {
          // 支付成功，停止轮询并处理
          clearInterval(followupPaymentInterval);
          followupPaymentInterval = null;
          
          // 关闭二维码弹窗
          showQRCode.value = false;
          
          // 执行支付成功后的操作
          Toast.success('支付成功');
          
          // 更新UI，将当前追问项标记为已付费
          const index = followupOptions.value.findIndex(o => o.id === currentFollowup.value.id);
          if (index !== -1) {
            followupOptions.value[index].paid = true;
            followupOptions.value = [...followupOptions.value];
          }
          
          // 加载分析结果
          Toast.loading({
            message: '正在生成分析结果，这可能需要30-60秒...',
            forbidClick: true,
            duration: 0
          });
          
          await pollFollowupStatus();
        }
      }
    } catch (error) {
      console.error('轮询追问支付状态失败:', error);
    }
  }, 3000);
};

// 修改支付追问费用函数
const payForFollowup = async () => {
  if (!currentFollowup.value) return;
  
  try {
    isLoadingFollowup.value = true;
    
    // 第一步：创建订单
    Toast.loading({
      message: '正在创建订单...',
      forbidClick: true,
      duration: 0
    });
    
    // 创建追问订单
    const orderResponse = await axios.post('/api/order/create/followup', {
      resultId: resultId.value,
      area: currentFollowup.value.id
    });
    
    if (orderResponse.data.code === 200) {
      const followupOrderId = orderResponse.data.data.orderId;
      window.currentFollowupOrderId = followupOrderId; // 保存订单ID
      console.log('追问订单创建成功:', followupOrderId);
      
      // 调用微信支付
      Toast.loading({
        message: '正在获取支付二维码...',
        forbidClick: true,
        duration: 0
      });
      
      // 获取微信支付参数
      const paymentResponse = await axios.post(`/api/order/create/payment/${followupOrderId}`, {
        paymentMethod: 'wechat',
        deviceType: 'pc',
        returnQrCode: true
      });
      
      if (paymentResponse.data.code === 200) {
        Toast.clear();
        
        // 解析支付二维码返回数据
        if (paymentResponse.data.data.qr_image) {
          // 直接使用Base64二维码图片
          qrCodeUrl.value = paymentResponse.data.data.qr_image;
          showQRCode.value = true;
        } else if (paymentResponse.data.data.code_url) {
          // 生成二维码图片
          qrCodeUrl.value = paymentResponse.data.data.code_url;
          showQRCode.value = true;
        } else {
          Toast.fail('未获取到支付二维码');
        }
      } else {
        Toast.clear();
        Toast.fail(paymentResponse.data.message || '获取支付参数失败');
      }
    } else {
      Toast.fail('创建订单失败');
    }
  } catch (error) {
    console.error('追问支付过程出错:', error);
    Toast.fail('处理失败，请重试');
  } finally {
    isLoadingFollowup.value = false;
  }
};

// 添加检查支付状态函数
const checkPaymentStatus = async () => {
  if (!currentFollowup.value) return;
  
  try {
    Toast.loading({
      message: '正在确认支付结果...',
      forbidClick: true,
      duration: 0
    });
    
    // 这里需要获取当前的订单ID，可能需要在支付时保存
    // 暂时使用一个临时变量存储
    const followupOrderId = window.currentFollowupOrderId;
    
    if (!followupOrderId) {
      Toast.fail('订单信息丢失，请重新支付');
      return;
    }
    
    // 轮询检查支付结果
    let checkCount = 0;
    const maxChecks = 10;
    let isPaid = false;
    
    while (checkCount < maxChecks && !isPaid) {
      try {
        // 使用不需要认证的query接口替代status接口
        const statusResponse = await axios.get(`/api/order/query/${followupOrderId}`);
        
        if (statusResponse.data.code === 200) {
          const orderStatus = statusResponse.data.data.status;
          console.log(`支付状态查询结果: ${orderStatus}`, statusResponse.data);
          
          if (orderStatus === 'paid') {
            isPaid = true;
            break;
          }
        }
      } catch (error) {
        console.error('检查支付状态出错:', error);
      }
      
      await new Promise(resolve => setTimeout(resolve, 2000));
      checkCount++;
    }
    
    Toast.clear();
    
    if (isPaid) {
      Toast.success('支付成功');
      showQRCode.value = false;
      
      // 更新UI，将当前追问项标记为已付费
      const index = followupOptions.value.findIndex(o => o.id === currentFollowup.value.id);
      if (index !== -1) {
        followupOptions.value[index].paid = true;
        followupOptions.value = [...followupOptions.value];
      }
      
      // 加载分析结果
      Toast.loading({
        message: '正在生成分析结果，这可能需要30-60秒...',
        forbidClick: true,
        duration: 0
      });
      
      await pollFollowupStatus();
    } else {
      Toast.fail('未检测到支付完成，请稍后再试');
    }
  } catch (error) {
    console.error('支付处理出错:', error);
    Toast.fail('支付处理出错，请重试');
  }
};

// 自定义轮询检查追问分析状态
const pollFollowupStatus = async () => {
  const area = currentFollowup.value.id;
  console.log(`开始轮询追问分析状态: ${area}`);
  
  // 开始计时
  const startTime = new Date().getTime();
  const timeoutMs = 120000; // 120秒超时
  let attempts = 0;
  const maxAttempts = 60; // 最多等待120秒（60次 * 2秒）
  let isComplete = false;
  
  // 首先，主动触发追问分析
  try {
    console.log(`主动触发追问分析: ${resultId.value}, 领域: ${area}`);
    const triggerResponse = await axios.post(`/api/bazi/followup/${resultId.value}`, {
      area: area
    });
    
    if (triggerResponse.data.code === 200) {
      console.log('成功触发追问分析:', triggerResponse.data);
    } else {
      console.warn('触发追问分析返回非200状态:', triggerResponse.data);
    }
  } catch (error) {
    // 如果是404错误，可能是API路径不对，尝试另一个路径
    if (error.response && error.response.status === 404) {
      try {
        console.log(`尝试备用API路径触发追问分析: ${resultId.value}/${area}`);
        const backupResponse = await axios.post(`/api/bazi/followup/${resultId.value}/${area}`, {});
        console.log('备用API触发结果:', backupResponse.data);
      } catch (backupError) {
        console.warn('备用API触发也失败:', backupError);
      }
    } else {
      console.error('触发追问分析失败:', error);
    }
  }
  
  // 等待几秒，让后端有时间开始处理
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  while (attempts < maxAttempts && !isComplete) {
    attempts++;
    try {
      // 等待2秒
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 检查是否超时
      const currentTime = new Date().getTime();
      if (currentTime - startTime > timeoutMs) {
        console.warn(`轮询追问分析状态超时: ${area}`);
        break;
      }
      
      // 检查追问分析结果
      console.log(`尝试第${attempts}次获取追问分析: ${area}`);
      const response = await axios.get(`/api/bazi/followup/${resultId.value}/${area}`);
      
      if (response.data.code === 200 && response.data.data) {
        console.log(`获取到追问分析响应:`, response.data);
        
        // 检查分析内容是否为"正在分析"
        let analysis = null;
        if (response.data.data.analysis) {
          analysis = response.data.data.analysis;
        } else if (typeof response.data.data === 'string') {
          analysis = response.data.data;
        } else if (response.data.data[area]) {
          analysis = response.data.data[area];
        }
        
        if (analysis && typeof analysis === 'string' && !analysis.includes('正在分析')) {
          console.log(`成功获取追问分析结果: ${area}, 内容长度: ${analysis.length}`);
          isComplete = true;
          followupAnalysis.value[area] = analysis;
          break;
        } else {
          console.log(`追问分析结果还在生成中: ${area}, 当前内容:`, analysis ? analysis.substring(0, 50) + '...' : '无内容');
        }
      }
    } catch (error) {
      // 只有非404错误才打印详细信息
      if (!error.response || error.response.status !== 404) {
        console.error('检查追问分析状态出错:', error);
      }
      
      // 如果遇到404错误，表示追问分析尚未创建完毕
      if (error.response && error.response.status === 404) {
        console.log('追问分析尚未创建完毕，继续等待...');
      } else if (attempts >= maxAttempts / 2) {
        // 如果尝试次数超过一半且仍然失败，不要退出轮询，但记录错误
        console.warn(`获取分析数据失败(${attempts}/${maxAttempts})，继续尝试...`);
      }
    }
  }
  
  // 无论是否完成，都尝试获取最终结果
  console.log(`轮询完成，最终尝试获取追问分析: ${area}`);
  try {
    const finalResult = await getFollowupAnalysis(area);
    console.log(`最终获取追问分析结果: ${finalResult ? '成功' : '失败'}`);
    
    // 更新UI
    Toast.clear();
    if (finalResult) {
      Toast.success('分析已完成');
      
      // 支付成功且分析完成后，切换到AI分析结果标签页显示结果
      activeTab.value = 1; // 切换到AI分析结果标签
      
      // 滚动到相应分析部分
      setTimeout(() => {
        const sectionMap = {
          'relationship': '婚姻感情',
          'marriage': '婚姻感情',
          'career': '事业财运',
          'work': '事业财运',
          'money': '事业财运',
          'wealth': '事业财运',
          'children': '子女情况',
          'family': '子女情况',
          'parents': '父母情况',
          'health': '身体健康',
          'education': '学业',
          'study': '学业',
          'social': '人际关系',
          'friends': '人际关系',
          'future': '近五年运势',
          'fiveYears': '近五年运势',
          'lifePlan': '人生规划建议'
        };
        
        const targetTitle = sectionMap[currentFollowup.value.id];
        if (targetTitle) {
          // 查找并滚动到对应的分析部分
          const sections = document.querySelectorAll('.analysis-section h3');
          for (let i = 0; i < sections.length; i++) {
            if (sections[i].textContent.includes(targetTitle)) {
              sections[i].scrollIntoView({ behavior: 'smooth', block: 'center' });
              
              // 高亮显示该部分
              const section = sections[i].parentElement;
              section.classList.add('highlight-section');
              setTimeout(() => {
                section.classList.remove('highlight-section');
              }, 3000);
              
              break;
            }
          }
        }
      }, 500);
    } else {
      Toast.success('正在生成分析，请稍后刷新查看');
    }
    
    showFollowupDialog.value = false;
    
    return finalResult;
  } catch (error) {
    console.error('获取最终追问分析结果失败:', error);
    Toast.clear();
    Toast.fail('分析生成失败，请稍后刷新页面');
    
    // 如果分析结果仍然不可用，显示友好的错误信息
    followupAnalysis.value[area] = "分析正在处理中，请稍后刷新页面查看。";
    return null;
  }
};

// 获取追问分析结果
const getFollowupAnalysis = async (area) => {
  loading.value = true;
  try {
    console.log(`开始获取[${area}]追问分析，结果ID: ${resultId.value}`);
    const response = await axios.get(`/api/bazi/followup/${resultId.value}/${area}`);
    
    if (response.data.code === 200) {
      console.log('获取追问分析成功，响应数据:', response.data);
      console.log('响应data字段详情:', JSON.stringify(response.data.data));
      
      // 处理分析结果为null或空的情况
      if (!response.data.data) {
        console.warn(`追问分析结果data为空: ${area}`);
        const defaultMessage = `${followupOptions.value.find(o => o.id === area)?.name || area}分析正在生成中，请稍后刷新页面查看。`;
        followupAnalysis.value[area] = defaultMessage;
        return defaultMessage;
      }
      
      // 提取分析内容，处理不同的响应格式
      let analysisContent = null;
      
      if (response.data.data.analysis) {
        // 标准格式：{area, analysis}
        analysisContent = response.data.data.analysis;
        console.log(`获取到标准格式分析结果, 类型: ${typeof analysisContent}, 长度: ${analysisContent ? analysisContent.length : 0}`);
      } else if (typeof response.data.data === 'string') {
        // 直接字符串格式
        analysisContent = response.data.data;
        console.log(`获取到字符串格式分析结果, 长度: ${analysisContent.length}`);
      } else if (response.data.data[area]) {
        // 对象格式：{area1: "分析1", area2: "分析2"}
        analysisContent = response.data.data[area];
        console.log(`获取到对象格式分析结果, 长度: ${analysisContent ? analysisContent.length : 0}`);
      } else {
        // 尝试遍历所有属性，看是否有匹配的内容
        console.log('尝试查找匹配内容，data的所有键:', Object.keys(response.data.data));
        for (const key in response.data.data) {
          if (key.toLowerCase() === area.toLowerCase() || 
             (area === 'fiveYears' && key === 'future') ||
             (area === 'future' && key === 'fiveYears') ||
             (area === 'lifePlan' && key === 'lifePlan')) {
            analysisContent = response.data.data[key];
            console.log(`找到匹配的键[${key}]，内容长度: ${analysisContent ? analysisContent.length : 0}`);
            break;
          }
        }
      }
      
      // 检查分析结果是否为null或空
      if (!analysisContent) {
        console.warn(`无法从响应中提取有效分析内容: ${area}`);
        const defaultMessage = `${followupOptions.value.find(o => o.id === area)?.name || area}分析尚未生成，请稍后刷新页面查看。`;
        followupAnalysis.value[area] = defaultMessage;
        return defaultMessage;
      }
      
      // 检查分析结果是否是空字符串
      if (typeof analysisContent === 'string' && analysisContent.trim() === '') {
        console.warn(`追问分析结果为空字符串: ${area}`);
        const defaultMessage = `${followupOptions.value.find(o => o.id === area)?.name || area}分析正在生成中，请稍后刷新页面查看。`;
        followupAnalysis.value[area] = defaultMessage;
        return defaultMessage;
      }
      
      // 记录有效的分析结果
      console.log(`获取到有效的[${area}]分析结果，长度: ${analysisContent.length}`);
      
      // 存储并返回分析结果
      followupAnalysis.value[area] = analysisContent;
      return analysisContent;
    } else {
      console.error('获取追问分析失败:', response.data);
      const errorMessage = `获取分析失败: ${response.data.message || '未知错误'}`;
      followupAnalysis.value[area] = errorMessage;
      return errorMessage;
    }
  } catch (error) {
    console.error('获取追问分析出错:', error);
    const errorMessage = `获取分析出错: ${error.message || '请稍后重试'}`;
    followupAnalysis.value[area] = errorMessage;
    return errorMessage;
  } finally {
    loading.value = false;
  }
};

// 检查已支付的追问
const checkPaidFollowups = async () => {
  try {
    const response = await axios.get(`/api/bazi/followup/list/${resultId.value}`);
    
    if (response.data.code === 200 && response.data.data.followups) {
      const paidFollowups = response.data.data.followups;
      
      // 更新已支付的追问选项
      followupOptions.value = followupOptions.value.map(option => {
        const isPaid = paidFollowups.some(f => f.area === option.id);
        if (isPaid) {
          // 如果已支付，获取分析结果
          getFollowupAnalysis(option.id);
        }
        return { ...option, paid: isPaid };
      });
    }
  } catch (error) {
    console.error('检查已支付追问出错:', error);
  }
};

// 获取八字分析结果
const getBaziResult = async () => {
  loading.value = true;
  error.value = '';
  
  // 添加重试机制
  let retryCount = 0;
  const maxRetries = 3;
  let success = false;
  
  while (retryCount < maxRetries && !success) {
    try {
      console.log(`获取八字分析结果 (尝试 ${retryCount + 1}/${maxRetries})，ID: ${resultId.value}`);
      const response = await axios.get(`/api/bazi/result/${resultId.value}`);
      
      if (response.data.code === 200) {
        // 将结果数据赋值给响应变量
        const result = response.data.data;
        
        // 更新八字图数据
        if (result.baziChart) {
          baziChart.value = result.baziChart;
          
          // 计算年龄
          if (result.baziChart.birthDate) {
            const birthYear = parseInt(result.baziChart.birthDate.split('-')[0]);
            const currentYear = new Date().getFullYear();
            userAge.value = currentYear - birthYear;
            console.log('用户年龄:', userAge.value);
          }
        }
        
        // 更新AI分析结果
        if (result.aiAnalysis) {
          aiAnalysis.value = result.aiAnalysis;
        }
        
        // 更新用户信息
        if (result.gender) {
          userGender.value = result.gender === 'male' ? '男' : '女';
        }
        
        if (result.birthTime) {
          userBirthTime.value = result.birthTime;
        }
        
        // 更新分析状态
        analysisStatus.value = result.analysisStatus || 'completed';
        analysisProgress.value = result.analysisProgress || 100;
        
        // 检查分析内容是否已加载，如果已加载则强制更新状态为completed
        if (isAnalysisContentLoaded()) {
          analysisStatus.value = 'completed';
          analysisProgress.value = 100;
        }
        
        // 更新订单ID
        orderId.value = result.orderId || '';
        
        // 标记为成功
        success = true;
        loading.value = false;
        
        // 检查是否有神煞数据
        if (result.baziChart && result.baziChart.shenSha) {
          shenShaData.value = result.baziChart.shenSha;
        }
        
        // 检查是否有大运数据
        if (result.baziChart && result.baziChart.daYun) {
          daYunData.value = result.baziChart.daYun;
        }
        
        // 检查是否有流年数据
        if (result.baziChart && result.baziChart.flowingYears) {
          flowingYearsData.value = result.baziChart.flowingYears;
        }
        
        return true;
      } else {
        console.error('获取八字分析结果失败:', response.data.message);
        error.value = response.data.message || '获取分析结果失败';
        retryCount++;
        await new Promise(resolve => setTimeout(resolve, 1000)); // 等待1秒后重试
      }
    } catch (e) {
      console.error('获取八字分析结果出错:', e);
      error.value = e.message || '获取分析结果出错';
      
      // 如果是404错误，可能是结果记录还未创建，尝试手动更新订单状态
      if (e.response && e.response.status === 404) {
        console.log('结果记录不存在，尝试手动更新订单状态');
        
        // 从resultId中提取orderId
        let orderId = '';
        if (resultId.value.startsWith('RES')) {
          orderId = 'BZ' + resultId.value.substring(3);
          console.log('从resultId提取的orderId:', orderId);
          
          try {
            // 尝试手动更新订单状态
            const manualResponse = await axios.get(`/api/order/manual_update/${orderId}`);
            console.log('手动更新响应:', manualResponse.data);
            
            if (manualResponse.data.code === 200) {
              console.log('手动更新成功，等待2秒后重试获取结果');
              // 等待2秒后重试，给后端时间创建记录
              await new Promise(resolve => setTimeout(resolve, 2000));
            }
          } catch (manualError) {
            console.error('手动更新失败:', manualError);
          }
        }
      }
      
      retryCount++;
      await new Promise(resolve => setTimeout(resolve, 1000)); // 等待1秒后重试
    }
  }
  
  if (!success) {
    loading.value = false;
    
    // 如果所有重试都失败，显示手动刷新按钮
    showManualRefresh.value = true;
    
    return false;
  }
  
  return true;
};

// 添加缺失的函数
// 初始化追问选项
const initFollowupOptions = () => {
  // 根据用户年龄调整追问选项
  if (userAge.value !== null) {
    if (userAge.value < 6) {
      // 为婴幼儿调整选项
      followupOptions.value = followupOptions.value.filter(option => 
        ['health', 'personality', 'education', 'parents'].includes(option.id)
      );
    } else if (userAge.value < 18) {
      // 为未成年人调整选项
      followupOptions.value = followupOptions.value.filter(option => 
        !['marriage', 'career'].includes(option.id)
      );
    }
  }
  
  console.log('初始化追问选项完成:', followupOptions.value);
};

// 加载已支付的追问分析结果
const loadFollowupResults = async () => {
  try {
    // 检查是否有结果ID
    if (!resultId.value) {
      console.warn('缺少结果ID，无法加载追问分析');
      return;
    }
    
    console.log('开始加载追问分析结果列表:', resultId.value);
    
    // 调用API获取已支付的追问列表
    const response = await axios.get(`/api/bazi/followup/list/${resultId.value}`);
    
    if (response.data.code === 200 && response.data.data.followups) {
      const paidFollowups = response.data.data.followups;
      console.log('获取到的追问列表:', paidFollowups);
      
      // 更新已支付的追问选项
      followupOptions.value = followupOptions.value.map(option => {
        // 检查是否有匹配的追问分析
        const isPaid = paidFollowups.some(f => {
          // 尝试多种匹配方式
          if (typeof f === 'object') {
            // 对象格式：检查area字段
            return f.area === option.id;
          } else if (typeof f === 'string') {
            // 字符串格式：直接比较
            return f === option.id;
          }
          return false;
        });
        
        if (isPaid) {
          console.log(`发现已支付的追问: ${option.id}`);
          // 如果已支付，获取分析结果
          getFollowupAnalysis(option.id);
        }
        
        return { ...option, paid: isPaid };
      });
      
      console.log('更新后的追问选项:', followupOptions.value);
    } else {
      console.warn('获取追问列表失败或返回空列表');
    }
  } catch (error) {
    console.error('加载追问分析结果出错:', error);
    // 出错时不显示错误提示，静默失败
  }
};

// 解析八字数据
const parseBaZiData = (data) => {
  if (!data) return null;
  
  return {
    yearPillar: data.yearPillar || { heavenlyStem: '未知', earthlyBranch: '未知' },
    monthPillar: data.monthPillar || { heavenlyStem: '未知', earthlyBranch: '未知' },
    dayPillar: data.dayPillar || { heavenlyStem: '未知', earthlyBranch: '未知' },
    hourPillar: data.hourPillar || { heavenlyStem: '未知', earthlyBranch: '未知' },
    shenSha: data.shenSha || {
      dayChong: '未知',
      zhiShen: '未知',
      pengZuGan: '未知',
      pengZuZhi: '未知',
      xiShen: '未知',
      fuShen: '未知',
      caiShen: '未知',
      benMing: [],
      yearGan: [],
      yearZhi: [],
      dayGan: [],
      dayZhi: []
    },
    daYun: data.daYun || {
      startAge: 0,
      startYear: 0,
      isForward: true,
      daYunList: []
    },
    flowingYears: data.flowingYears || []
  };
};

// 添加分析状态检测函数
const isAnalysisItemLoading = (key) => {
  if (!aiAnalysis.value) return true;
  const value = aiAnalysis.value[key];
  return !value || value === '暂无' || (value.includes && value.includes('正在分析'));
};

// 清理组件时移除定时器
onUnmounted(() => {
  if (analyzeTimer.value) {
    clearInterval(analyzeTimer.value);
    analyzeTimer.value = null;
  }
});

// 刷新特定追问的分析结果
const reloadFollowupAnalysis = async (area) => {
  if (!area) return;
  
  try {
    isLoadingFollowup.value = true;
    Toast.loading({
      message: '正在刷新分析结果...',
      duration: 0
    });
    
    console.log(`刷新${area}分析结果`);
    const analysis = await getFollowupAnalysis(area);
    
    if (analysis && typeof analysis === 'string' && analysis.length > 0) {
      Toast.success('刷新成功');
      console.log(`成功刷新${area}分析结果，长度: ${analysis.length}`);
    } else {
      Toast.fail('分析结果尚未生成完成');
      console.warn(`刷新${area}分析结果失败或为空`);
    }
  } catch (error) {
    console.error(`刷新${area}分析失败:`, error);
    Toast.fail('刷新失败，请重试');
  } finally {
    isLoadingFollowup.value = false;
    Toast.clear();
  }
};

// 在data部分添加showManualRefresh变量
const showManualRefresh = ref(false);

// 添加手动刷新函数
const manualRefresh = async () => {
  showManualRefresh.value = false;
  Toast.loading({
    message: '正在重新获取分析结果...',
    duration: 0,
    forbidClick: true
  });
  
  // 从resultId中提取orderId
  let orderId = '';
  if (resultId.value.startsWith('RES')) {
    orderId = 'BZ' + resultId.value.substring(3);
    console.log('从resultId提取的orderId:', orderId);
    
    try {
      // 尝试手动更新订单状态
      const manualResponse = await axios.get(`/api/order/manual_update/${orderId}`);
      console.log('手动更新响应:', manualResponse.data);
      
      if (manualResponse.data.code === 200) {
        console.log('手动更新成功，等待2秒后重试获取结果');
        // 等待2秒后重试，给后端时间创建记录
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // 重新获取结果
        const success = await getBaziResult();
        if (success) {
          Toast.success('分析结果加载成功');
        } else {
          Toast.fail('获取分析结果失败，请稍后再试');
        }
      } else {
        Toast.fail('手动更新失败: ' + (manualResponse.data.message || '未知错误'));
      }
    } catch (error) {
      console.error('手动更新失败:', error);
      Toast.fail('手动更新失败，请稍后再试');
    }
  } else {
    // 直接重试获取结果
    const success = await getBaziResult();
    if (success) {
      Toast.success('分析结果加载成功');
    } else {
      Toast.fail('获取分析结果失败，请稍后再试');
    }
  }
  
  Toast.clear();
};

// 在data部分添加error变量
const error = ref('');

// 添加所有需要的变量定义
const baziChart = ref({});
const analysisStatus = ref('completed');
const analysisProgress = ref(100);
const orderId = ref('');
const userGender = ref('');
const userBirthTime = ref('');
const shenShaData = ref({});
const daYunData = ref({});
const flowingYearsData = ref([]);
</script>

<style scoped>
.result-container {
  padding-bottom: 20px;
  background-color: #ffffff; /* 添加白色背景 */
  min-height: 100vh; /* 确保全屏白色 */
}

.value {
  color: #000000;
}

.result-header {
  text-align: center;
  padding: 20px 0;
  background-color: #f2f3f5;
}

.result-header h2 {
  margin: 0;
  font-size: 20px;
  color: #323233;
}

.result-header p {
  margin: 10px 0 0;
  font-size: 14px;
  color: #969799;
}

.bazi-chart {
  padding: 20px 16px;
}

.bazi-chart h3 {
  margin: 20px 0 10px;
  color: #323233;
}

.four-pillars {
  display: flex;
  justify-content: space-around;
  margin: 20px 0;
}

.pillar {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f5f7fa;
  padding: 10px;
  border-radius: 8px;
  width: 80px;
}

.stem, .branch {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  margin: 4px 0;
  border-radius: 4px;
}

.stem {
  background: #1989fa;
  color: white;
}

.branch {
  background: #07c160;
  color: white;
}

.label {
  font-size: 12px;
  color: #646566;
  margin-top: 4px;
}

.nayin, .shishen, .wangshuai {
  font-size: 12px;
  color: #323233;
  margin-top: 4px;
}

.five-elements {
  display: flex;
  justify-content: space-between;
  margin: 10px 0;
}

.element {
  text-align: center;
  flex: 1;
}

.element-name {
  font-size: 14px;
  color: #323233;
}

.element-value {
  font-size: 18px;
  font-weight: bold;
  color: #1989fa;
  margin-top: 5px;
}

.flowing-years {
  margin: 20px 0;
}

.ai-analysis {
  padding: 20px 16px;
}

.analysis-section {
  margin-bottom: 20px;
}

.analysis-section h3 {
  margin: 0 0 10px;
  color: #323233;
}

.analysis-section p {
  margin: 0;
  font-size: 14px;
  color: #646566;
  line-height: 1.6;
}

.action-buttons {
  padding: 20px 16px;
}

.age-notice {
  margin-bottom: 20px;
}

.shen-sha-info {
  margin-bottom: 20px;
}

.da-yun-info {
  margin-bottom: 20px;
}

.qi-yun-info {
  margin: 0 0 10px;
  font-size: 14px;
  color: #646566;
}

.da-yun-table {
  margin-top: 10px;
}

.placeholder {
  background-color: #f2f3f5;
  color: #969799;
}

/* 追问部分样式 */
.followup-section {
  margin-top: 20px;
  padding: 15px;
  background-color: #fff;
  border-radius: 8px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.section-desc {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
}

.followup-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.followup-option {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.followup-option:hover {
  background-color: #e8f0fe;
}

.followup-option.paid {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
}

.option-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.option-name {
  font-size: 15px;
  font-weight: 500;
}

.option-status {
  font-size: 13px;
  color: #ff6b00;
}

.followup-option.paid .option-status {
  color: #52c41a;
}

.followup-result {
  margin-top: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #1989fa;
}

.followup-result h3 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #333;
}

.analysis-content {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
}

.followup-dialog-content {
  padding: 15px;
  text-align: center;
}

/* 添加表格样式 */
.custom-table {
  width: 100%;
  border-collapse: collapse;
  border-spacing: 0;
  margin: 10px 0;
  background-color: #fff;
  color: #323233;
  font-size: 14px;
}

.custom-table th,
.custom-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #ebedf0;
  text-align: center;
}

.custom-table th {
  font-weight: 500;
  background-color: #f7f8fa;
  color: #646566;
}

.custom-table tr:hover {
  background-color: #f2f3f5;
}

/* 添加分析状态相关样式 */
.analysis-progress-notice {
  margin: 10px 16px;
  border-radius: 8px;
}

.analysis-progress {
  width: 100%;
}

.analysis-progress p {
  margin-bottom: 10px;
  font-size: 14px;
  color: #1989fa;
}

.loading-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
  background-color: #f7f8fa;
  border-radius: 8px;
  margin: 10px 0;
}

.enhanced-analysis {
  margin-bottom: 10px;
  padding: 10px;
  border-left: 3px solid #1989fa;
  background-color: #f8f9ff;
  border-radius: 4px;
}

.enhanced-analysis p {
  color: #333;
  line-height: 1.6;
  white-space: pre-wrap;
  margin-bottom: 8px;
}

.analysis-source {
  text-align: right;
  margin-top: 8px;
}

/* 高亮效果 */
@keyframes highlight-pulse {
  0% { box-shadow: 0 0 0 0 rgba(25, 137, 250, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(25, 137, 250, 0); }
  100% { box-shadow: 0 0 0 0 rgba(25, 137, 250, 0); }
}

.highlight-section {
  animation: highlight-pulse 1.5s ease-in-out;
  background-color: rgba(25, 137, 250, 0.08);
  border-radius: 8px;
  transition: background-color 0.5s ease;
}

.markdown-content {
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 14px;
  color: #333;
}

.markdown-content h1, 
.markdown-content h2, 
.markdown-content h3, 
.markdown-content h4, 
.markdown-content h5, 
.markdown-content h6 {
  margin-top: 1em;
  margin-bottom: 0.5em;
  font-weight: bold;
  color: #333;
}

.markdown-content h1 {
  font-size: 1.8em;
}

.markdown-content h2 {
  font-size: 1.5em;
}

.markdown-content h3 {
  font-size: 1.3em;
}

.markdown-content h4 {
  font-size: 1.1em;
}

.markdown-content p {
  margin-bottom: 1em;
}

.markdown-content ul, 
.markdown-content ol {
  margin-left: 2em;
  margin-bottom: 1em;
}

.markdown-content ul {
  list-style-type: disc;
}

.markdown-content ol {
  list-style-type: decimal;
}

.markdown-content li {
  margin-bottom: 0.5em;
}

.markdown-content strong {
  font-weight: bold;
}

.markdown-content em {
  font-style: italic;
}

.markdown-content blockquote {
  border-left: 4px solid #ddd;
  padding-left: 1em;
  margin-left: 0;
  color: #666;
}

.markdown-content hr {
  height: 1px;
  background-color: #ddd;
  border: none;
  margin: 1.5em 0;
}

/* 添加手动刷新按钮样式 */
.manual-refresh-container {
  padding: 20px;
  text-align: center;
}
.refresh-tip {
  margin-top: 10px;
  color: #999;
  font-size: 14px;
}

/* 在 style 部分添加二维码样式 */
.qrcode-container {
  padding: 20px;
  text-align: center;
}

.qrcode {
  margin: 20px 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

.qrcode img,
.qrcode iframe {
  border: 1px solid #eee;
  border-radius: 8px;
}

.qrcode-placeholder {
  width: 200px;
  height: 200px;
  border: 1px dashed #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}

.step-text{
  color: #000000;
}

</style>


