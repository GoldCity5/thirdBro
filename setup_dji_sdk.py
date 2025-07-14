#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DJI Thermal SDK 自动设置脚本
帮助用户下载和安装DJI Thermal SDK
"""

import os
import sys
import zipfile
import requests
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class DJISDKSetup:
    """DJI SDK安装助手"""
    
    def __init__(self):
        self.sdk_url = "https://dl.djicdn.com/downloads/dji_assistant/20220929/dji_thermal_sdk_v1.4_20220929.zip"
        self.project_dir = Path.cwd()
        self.temp_dir = self.project_dir / "temp_sdk"
        
    def check_existing_sdk(self) -> bool:
        """检查是否已安装SDK"""
        if sys.platform == "win32":
            dll_path = self.project_dir / "libdirp.dll"
            return dll_path.exists()
        else:
            so_path = Path("/usr/local/lib/libdirp.so")
            local_so = self.project_dir / "libdirp.so"
            return so_path.exists() or local_so.exists()
    
    def download_sdk(self) -> str:
        """下载DJI SDK"""
        logger.info("🔄 正在下载DJI Thermal SDK...")
        logger.info(f"📁 下载地址: {self.sdk_url}")
        
        # 创建临时目录
        self.temp_dir.mkdir(exist_ok=True)
        
        zip_path = self.temp_dir / "dji_thermal_sdk.zip"
        
        try:
            response = requests.get(self.sdk_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r📥 下载进度: {progress:.1f}%", end='', flush=True)
            
            print()  # 新行
            logger.info("✅ 下载完成")
            return str(zip_path)
            
        except requests.RequestException as e:
            logger.error(f"❌ 下载失败: {e}")
            logger.info("💡 您可以手动下载SDK并将libdirp.dll放入项目目录")
            logger.info(f"   手动下载地址: {self.sdk_url}")
            return None
    
    def extract_sdk(self, zip_path: str) -> bool:
        """解压SDK"""
        logger.info("📦 正在解压SDK...")
        
        try:
            extract_dir = self.temp_dir / "extracted"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            logger.info("✅ 解压完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 解压失败: {e}")
            return False
    
    def install_sdk(self) -> bool:
        """安装SDK文件"""
        logger.info("🔧 正在安装SDK...")
        
        extract_dir = self.temp_dir / "extracted"
        
        if sys.platform == "win32":
            # Windows系统
            dll_files = list(extract_dir.rglob("libdirp.dll"))
            
            if not dll_files:
                logger.error("❌ 未找到libdirp.dll文件")
                return False
            
            dll_source = dll_files[0]
            dll_dest = self.project_dir / "libdirp.dll"
            
            try:
                import shutil
                shutil.copy2(dll_source, dll_dest)
                logger.info(f"✅ 已复制 libdirp.dll 到项目目录")
                return True
                
            except Exception as e:
                logger.error(f"❌ 复制文件失败: {e}")
                return False
                
        else:
            # Linux/macOS系统
            so_files = list(extract_dir.rglob("libdirp.so"))
            
            if not so_files:
                logger.error("❌ 未找到libdirp.so文件")
                return False
            
            so_source = so_files[0]
            
            # 尝试复制到系统目录
            try:
                import shutil
                shutil.copy2(so_source, "/usr/local/lib/libdirp.so")
                logger.info("✅ 已安装到 /usr/local/lib/")
                return True
                
            except PermissionError:
                # 如果没有权限，复制到项目目录
                so_dest = self.project_dir / "libdirp.so"
                shutil.copy2(so_source, so_dest)
                logger.info("✅ 已复制到项目目录")
                return True
                
            except Exception as e:
                logger.error(f"❌ 安装失败: {e}")
                return False
    
    def cleanup(self):
        """清理临时文件"""
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            logger.info("🧹 已清理临时文件")
        except Exception:
            pass
    
    def verify_installation(self) -> bool:
        """验证安装"""
        logger.info("🔍 验证安装...")
        
        try:
            from dji_thermal_converter import DJIThermalConverter
            converter = DJIThermalConverter()
            
            if converter.is_initialized:
                logger.info("✅ DJI Thermal SDK 安装成功并已初始化")
                return True
            else:
                logger.warning("⚠️ SDK文件已复制，但未能成功初始化")
                logger.info("💡 请检查文件权限或重启程序")
                return False
                
        except Exception as e:
            logger.error(f"❌ 验证失败: {e}")
            return False
    
    def run_setup(self):
        """运行完整安装流程"""
        logger.info("🚀 开始DJI Thermal SDK安装流程")
        
        # 检查是否已安装
        if self.check_existing_sdk():
            logger.info("✅ DJI SDK已安装")
            if self.verify_installation():
                return True
            else:
                logger.info("🔄 重新安装SDK...")
        
        try:
            # 下载SDK
            zip_path = self.download_sdk()
            if not zip_path:
                return False
            
            # 解压SDK
            if not self.extract_sdk(zip_path):
                return False
            
            # 安装SDK
            if not self.install_sdk():
                return False
            
            # 验证安装
            success = self.verify_installation()
            
            return success
            
        finally:
            # 清理临时文件
            self.cleanup()


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("🔥 DJI Thermal SDK 自动安装工具")
    logger.info("=" * 50)
    
    try:
        setup = DJISDKSetup()
        success = setup.run_setup()
        
        if success:
            logger.info("\n🎉 安装完成！")
            logger.info("现在您可以使用以下命令测试：")
            logger.info("  python main.py --check-requirements")
            logger.info("  python gui.py")
        else:
            logger.info("\n❌ 安装失败")
            logger.info("请尝试手动安装：")
            logger.info("1. 下载 DJI Thermal SDK")
            logger.info("2. 解压后将 libdirp.dll 复制到项目目录")
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ 用户取消安装")
    except Exception as e:
        logger.error(f"\n💥 安装过程出错: {e}")


if __name__ == "__main__":
    main() 