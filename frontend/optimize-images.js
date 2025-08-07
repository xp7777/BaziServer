#!/usr/bin/env node

/**
 * 图片优化脚本
 * 自动压缩和转换图片格式以提升加载速度
 */

const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

// 配置参数
const CONFIG = {
  inputDir: './src/assets',
  outputDir: './src/assets/optimized',
  formats: ['webp', 'jpeg'], // 生成的格式
  quality: 85, // 压缩质量
  maxWidth: 1920, // 最大宽度
  maxHeight: 1080, // 最大高度
};

// 创建输出目录
if (!fs.existsSync(CONFIG.outputDir)) {
  fs.mkdirSync(CONFIG.outputDir, { recursive: true });
}

// 支持的图片格式
const SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'];

/**
 * 获取文件大小
 */
function getFileSize(filePath) {
  const stats = fs.statSync(filePath);
  return {
    bytes: stats.size,
    kb: Math.round(stats.size / 1024 * 100) / 100,
    mb: Math.round(stats.size / 1024 / 1024 * 100) / 100
  };
}

/**
 * 压缩并转换图片
 */
async function optimizeImage(inputPath, outputPath, format, options = {}) {
  try {
    const image = sharp(inputPath);
    const metadata = await image.metadata();
    
    // 调整尺寸
    let resizeOptions = {
      width: CONFIG.maxWidth,
      height: CONFIG.maxHeight,
      fit: 'inside',
      withoutEnlargement: true
    };

    image.resize(resizeOptions);

    // 根据格式设置压缩选项
    switch (format) {
      case 'webp':
        image.webp({ quality: CONFIG.quality, effort: 6 });
        break;
      case 'jpeg':
        image.jpeg({ quality: CONFIG.quality, progressive: true });
        break;
      case 'png':
        image.png({ quality: CONFIG.quality, compressionLevel: 9 });
        break;
    }

    await image.toFile(outputPath);
    
    return {
      success: true,
      originalSize: getFileSize(inputPath),
      optimizedSize: getFileSize(outputPath),
      reduction: 0
    };
  } catch (error) {
    console.error(`处理失败: ${inputPath}`, error.message);
    return { success: false, error: error.message };
  }
}

/**
 * 处理单个文件
 */
async function processFile(filePath) {
  const fileName = path.basename(filePath, path.extname(filePath));
  const results = [];

  console.log(`处理: ${path.basename(filePath)}`);

  for (const format of CONFIG.formats) {
    const outputFileName = `${fileName}.${format}`;
    const outputPath = path.join(CONFIG.outputDir, outputFileName);
    
    const result = await optimizeImage(filePath, outputPath, format);
    
    if (result.success) {
      result.reduction = Math.round(
        (1 - result.optimizedSize.bytes / result.originalSize.bytes) * 100
      );
      console.log(`  ${format.toUpperCase()}: ${result.originalSize.kb}KB → ${result.optimizedSize.kb}KB (${result.reduction}% 减少)`);
    }
    
    results.push({ format, ...result });
  }

  return results;
}

/**
 * 生成响应式图片
 */
async function generateResponsiveImages(inputPath) {
  const fileName = path.basename(inputPath, path.extname(inputPath));
  const widths = [320, 768, 1024, 1440, 1920];
  
  console.log(`生成响应式图片: ${path.basename(inputPath)}`);
  
  for (const width of widths) {
    const outputFileName = `${fileName}-${width}w.webp`;
    const outputPath = path.join(CONFIG.outputDir, 'responsive', outputFileName);
    
    // 确保响应式目录存在
    const responsiveDir = path.join(CONFIG.outputDir, 'responsive');
    if (!fs.existsSync(responsiveDir)) {
      fs.mkdirSync(responsiveDir, { recursive: true });
    }
    
    try {
      await sharp(inputPath)
        .resize(width, null, { 
          fit: 'inside',
          withoutEnlargement: true 
        })
        .webp({ quality: CONFIG.quality })
        .toFile(outputPath);
      
      console.log(`  ${width}w: 完成`);
    } catch (error) {
      console.error(`  ${width}w: 失败 - ${error.message}`);
    }
  }
}

/**
 * 主处理函数
 */
async function main() {
  console.log('🖼️  图片优化开始...\n');
  
  try {
    // 获取所有图片文件
    const files = fs.readdirSync(CONFIG.inputDir)
      .filter(file => {
        const ext = path.extname(file).toLowerCase();
        return SUPPORTED_FORMATS.includes(ext) && file.startsWith('banner');
      })
      .map(file => path.join(CONFIG.inputDir, file));

    if (files.length === 0) {
      console.log('未找到需要优化的图片文件');
      return;
    }

    console.log(`找到 ${files.length} 个图片文件\n`);

    let totalOriginalSize = 0;
    let totalOptimizedSize = 0;

    // 处理每个文件
    for (const filePath of files) {
      const results = await processFile(filePath);
      
      // 统计结果
      results.forEach(result => {
        if (result.success) {
          totalOriginalSize += result.originalSize.bytes;
          totalOptimizedSize += result.optimizedSize.bytes;
        }
      });

      // 生成响应式版本
      await generateResponsiveImages(filePath);
    }

    // 打印总结
    const totalReduction = Math.round(
      (1 - totalOptimizedSize / totalOriginalSize) * 100
    );

    console.log('\n📊 优化完成!');
    console.log(`原始总大小: ${Math.round(totalOriginalSize / 1024 / 1024 * 100) / 100}MB`);
    console.log(`优化后总大小: ${Math.round(totalOptimizedSize / 1024 / 1024 * 100) / 100}MB`);
    console.log(`总减少: ${totalReduction}%`);
    console.log(`\n优化后的文件保存在: ${CONFIG.outputDir}`);

  } catch (error) {
    console.error('优化过程中出错:', error.message);
  }
}

/**
 * 生成HTML使用示例
 */
function generateUsageExample() {
  const optimizedFiles = fs.readdirSync(CONFIG.outputDir)
    .filter(file => file.endsWith('.webp'))
    .filter(file => !file.includes('-')); // 排除响应式图片

  let html = `<!-- 优化后的图片使用示例 -->\n`;
  
  optimizedFiles.forEach(file => {
    const name = path.basename(file, '.webp');
    html += `<!-- ${name} -->\n`;
    html += `<picture>\n`;
    html += `  <source srcset="./assets/optimized/${name}.webp" type="image/webp">\n`;
    html += `  <source srcset="./assets/optimized/${name}.jpg" type="image/jpeg">\n`;
    html += `  <img src="./assets/${name}.png" alt="${name}" loading="lazy">\n`;
    html += `</picture>\n\n`;
  });

  fs.writeFileSync(
    path.join(CONFIG.outputDir, 'usage-example.html'),
    html
  );

  console.log('\n📄 使用示例已生成: usage-example.html');
}

// 运行主程序
if (require.main === module) {
  main().then(() => {
    generateUsageExample();
  });
}

module.exports = {
  optimizeImage,
  processFile,
  CONFIG
};