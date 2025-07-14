#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
大疆无人机热红外图像转换器
主程序入口，提供命令行界面
"""

import argparse
import os
import sys
from pathlib import Path
import logging

# 导入DJI SDK转换器
try:
    from dji_thermal_converter import DJIThermalConverter
    DJI_CONVERTER_AVAILABLE = True
except ImportError:
    DJI_CONVERTER_AVAILABLE = False

def setup_logging(log_level: str = 'INFO'):
    """设置日志记录"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def validate_paths(input_path: str, output_path: str) -> tuple:
    """验证输入和输出路径"""
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    # 验证输入路径
    if not input_path.exists():
        raise FileNotFoundError(f"输入路径不存在: {input_path}")
    
    # 处理输出路径
    if input_path.is_file():
        # 单文件模式
        if output_path.is_dir():
            # 如果输出路径是目录，在目录中创建同名的.tiff文件
            output_filename = input_path.stem + '.tiff'
            output_path = output_path / output_filename
        else:
            # 确保输出文件有.tiff扩展名
            if not output_path.suffix.lower() in ['.tiff', '.tif']:
                output_path = output_path.with_suffix('.tiff')
    else:
        # 批量模式 - 输出应该是目录
        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                # 如果没有权限，使用用户文档目录
                documents_dir = Path.home() / "Documents" / "DJI_Thermal_Output"
                documents_dir.mkdir(parents=True, exist_ok=True)
                output_path = documents_dir
                print(f"⚠️ 权限不足，已切换输出目录到: {output_path}")
    
    # 验证输出目录的写入权限
    if output_path.is_file():
        test_dir = output_path.parent
    else:
        test_dir = output_path
        
    try:
        test_file = test_dir / ".test_write_permission"
        test_file.write_text("test")
        test_file.unlink()
    except (PermissionError, IOError):
        # 如果没有写入权限，使用临时目录
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "DJI_Thermal_Output"
        temp_dir.mkdir(exist_ok=True)
        
        if output_path.is_file():
            output_path = temp_dir / output_path.name
        else:
            output_path = temp_dir
            
        print(f"⚠️ 无写入权限，已切换到临时目录: {output_path}")
    
    return str(input_path), str(output_path)

def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(
        description="大疆无人机热红外图像转换器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 转换单个R-JPEG文件
  python main.py -i DJI_thermal.jpg -o output.tiff
  
  # 批量转换R-JPEG文件
  python main.py -i input_dir -o output_dir --batch
  
  # 递归转换子目录
  python main.py -i input_dir -o output_dir --batch --recursive
  
支持的无人机型号:
  M30T  - 大疆 M30T (-20°C ~ 400°C)
  H20T  - 大疆 H20T (-20°C ~ 550°C)
  H30T  - 大疆 H30T (-20°C ~ 1600°C)
  M2EA  - 大疆 御2行业进阶版 (-10°C ~ 400°C)
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=False,
        help='输入文件或目录路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=False,
        help='输出文件或目录路径'
    )
    
    parser.add_argument(
        '--sdk-path',
        help='DJI Thermal SDK库文件路径'
    )
    
    parser.add_argument(
        '-m', '--model',
        default='M30T',
        choices=['M30T', 'H20T', 'H30T', 'M2EA'],
        help='无人机型号（默认: M30T）'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='批量转换模式'
    )
    
    parser.add_argument(
        '--recursive',
        action='store_true',
        help='递归处理子目录 (仅在批量模式下有效)'
    )
    
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='日志级别 (默认: INFO)'
    )
    
    parser.add_argument(
        '--compression',
        default='lzw',
        choices=['lzw', 'zip', 'none'],
        help='TIFF压缩方式 (默认: lzw)'
    )
    
    parser.add_argument(
        '--check-requirements',
        action='store_true',
        help='检查系统要求和依赖'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # 检查系统要求
    if args.check_requirements:
        check_system_requirements()
        return
    
    # 验证必需参数
    if not args.input or not args.output:
        logger.error("必须指定输入和输出路径")
        parser.print_help()
        sys.exit(1)
    
    try:
        # 验证输入参数
        input_path, output_path = validate_paths(args.input, args.output)
        
        # 检查DJI转换器是否可用
        if not DJI_CONVERTER_AVAILABLE:
            logger.error("DJI转换器不可用")
            print_installation_guide()
            sys.exit(1)
        
        logger.info("使用DJI Thermal SDK转换器")
        converter = DJIThermalConverter(sdk_path=args.sdk_path)
        
        if not converter.is_initialized:
            logger.error("DJI Thermal SDK未初始化")
            print(converter.get_installation_guide())
            sys.exit(1)
        
        # 执行转换
        run_dji_conversion(converter, input_path, output_path, args)
        
    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        sys.exit(1)

def run_dji_conversion(converter, input_path: str, output_path: str, args):
    """运行DJI SDK转换"""
    logger = logging.getLogger(__name__)
    
    if args.batch:
        # 批量转换模式
        input_dir = Path(input_path)
        output_dir = Path(output_path)
        
        # 查找所有JPG文件
        if args.recursive:
            pattern = "**/*.jpg"
        else:
            pattern = "*.jpg"
        
        image_files = list(input_dir.glob(pattern))
        image_files.extend(input_dir.glob(pattern.replace('.jpg', '.JPG')))
        
        if not image_files:
            logger.warning(f"在目录 {input_path} 中未找到JPG文件")
            return
        
        logger.info(f"找到 {len(image_files)} 个图像文件")
        
        success_count = 0
        for image_file in image_files:
            try:
                # 生成输出文件名
                relative_path = image_file.relative_to(input_dir)
                output_file = output_dir / relative_path.with_suffix('.tiff')
                
                # 确保输出目录存在
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 转换图像
                if converter.convert_rjpeg_to_tiff(str(image_file), str(output_file)):
                    logger.info(f"转换完成: {image_file} -> {output_file}")
                    success_count += 1
                else:
                    logger.error(f"转换失败: {image_file}")
                
            except Exception as e:
                logger.error(f"转换失败 {image_file}: {str(e)}")
        
        logger.info(f"批量转换完成: {success_count}/{len(image_files)} 个文件成功")
        
    else:
        # 单文件转换模式
        if converter.convert_rjpeg_to_tiff(input_path, output_path):
            logger.info(f"转换完成: {input_path} -> {output_path}")
        else:
            logger.error(f"转换失败: {input_path}")

def check_system_requirements():
    """检查系统要求和依赖"""
    print("检查系统要求和依赖...")
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查必需的库
    required_libs = {
        'numpy': '数值计算',
        'cv2': 'OpenCV图像处理',
        'PIL': 'Pillow图像处理',
        'dji_thermal_sdk': 'DJI Thermal SDK',
        'tifffile': 'TIFF文件处理'
    }
    
    for lib, desc in required_libs.items():
        try:
            if lib == 'cv2':
                import cv2
            elif lib == 'PIL':
                from PIL import Image
            else:
                __import__(lib)
            print(f"✅ {desc} ({lib})")
        except ImportError:
            print(f"❌ {desc} ({lib}) - 未安装")
    
    # 检查DJI转换器
    if DJI_CONVERTER_AVAILABLE:
        try:
            from dji_thermal_converter import DJIThermalConverter
            converter = DJIThermalConverter()
            if converter.is_initialized:
                print("✅ DJI Thermal SDK - 已初始化")
            else:
                print("⚠️ DJI Thermal SDK - 未初始化（可能需要DLL文件）")
        except Exception as e:
            print(f"❌ DJI Thermal SDK - 初始化失败: {e}")
    else:
        print("❌ DJI Thermal SDK - 转换器不可用")

def print_installation_guide():
    """打印安装指南"""
    print("""
安装指南:
1. 安装Python依赖:
   pip install dji_thermal_sdk opencv-python numpy pillow tifffile

2. 下载DJI Thermal SDK:
   - 访问: https://www.dji.com/cn/downloads/softwares/dji-thermal-sdk
   - 下载DJI Thermal SDK v1.4或更高版本
   - 将libdirp.dll文件放在程序目录下

3. 系统要求:
   - Windows 10/11 x64
   - Python 3.7+
   - 支持的DJI无人机型号: M30T, H20T, H30T, M2EA
""")

if __name__ == "__main__":
    main() 