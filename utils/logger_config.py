import logging
import os
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
import glob
import threading
import time

class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """自定义按日期轮转的文件处理器"""
    def __init__(self, filename, when='midnight', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        # 确保目录存在
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc)
    
    def rotation_filename(self, default_name):
        """自定义轮转文件名格式"""
        dirname, basename = os.path.split(default_name)
        prefix, ext = os.path.splitext(basename)
        # 格式: error_2025-01-24.log
        return os.path.join(dirname, f"{prefix}_{datetime.now().strftime('%Y-%m-%d')}{ext}")

def setup_logging():
    """配置日志系统"""
    
    # 创建错误日志目录
    error_log_dir = 'logs/errors'
    os.makedirs(error_log_dir, exist_ok=True)
    
    # 清理旧日志
    cleanup_old_logs()
    
    # 创建根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # 1. 控制台处理器（显示所有级别）注释掉这4行 日志就不输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 2. 错误日志文件处理器（只记录ERROR级别）
    error_handler = CustomTimedRotatingFileHandler(
        filename=os.path.join(error_log_dir, 'error.log'),
        when='midnight',
        interval=1,
        backupCount=90,  # 保留90天
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)  # 只记录ERROR及以上级别
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # 启动定期清理任务
    start_cleanup_scheduler()
    
    logging.info("日志系统初始化完成")
    logging.info(f"错误日志目录: {error_log_dir}")
    logging.info("文件只记录ERROR级别日志，控制台显示所有日志")

def cleanup_old_logs():
    """清理3个月前的错误日志文件"""
    try:
        cutoff_date = datetime.now() - timedelta(days=90)
        
        # 只清理错误日志
        error_files = glob.glob('logs/errors/error_*.log*')
        for error_file in error_files:
            try:
                file_time = datetime.fromtimestamp(os.path.getctime(error_file))
                if file_time < cutoff_date:
                    os.remove(error_file)
                    logging.info(f"已删除旧错误日志文件: {error_file}")
            except Exception as e:
                logging.error(f"删除错误日志文件失败 {error_file}: {str(e)}")
                
    except Exception as e:
        logging.error(f"清理旧日志时出错: {str(e)}")

def start_cleanup_scheduler():
    """启动定期清理调度器"""
    def cleanup_task():
        while True:
            # 每天凌晨2点执行清理
            now = datetime.now()
            next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            
            sleep_seconds = (next_run - now).total_seconds()
            time.sleep(sleep_seconds)
            
            cleanup_old_logs()
    
    # 在后台线程中运行
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
