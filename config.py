#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置文件 - 大疆无人机热红外图像转换器
"""

import os
from typing import Dict, List, Tuple

class Config:
    """配置类"""
    
    # 版本信息
    VERSION = "1.0.0"
    
    # 支持的无人机型号配置
    DRONE_MODELS = {
        'M30T': {
            'name': '大疆 M30T',
            'temperature_range': (-20, 400),  # 温度范围 °C
            'resolution': (640, 512),
            'pixel_size': 12.0,  # 像素尺寸 μm
            'format_support': ['jpg', 'jpeg'],
            'spectral_range': (8.0, 14.0),  # 光谱范围 μm
            'thermal_sensitivity': 0.05,  # 热敏感度 °C
            'description': '大疆M30T无人机内置热红外相机'
        },
        'H20T': {
            'name': '大疆 H20T',
            'temperature_range': (-20, 550),
            'resolution': (640, 512),
            'pixel_size': 12.0,
            'format_support': ['jpg', 'jpeg'],
            'spectral_range': (8.0, 14.0),
            'thermal_sensitivity': 0.05,
            'description': '大疆H20T热红外云台相机'
        },
        'H30T': {
            'name': '大疆 H30T',
            'temperature_range': (-20, 1600),
            'resolution': (640, 512),
            'pixel_size': 12.0,
            'format_support': ['jpg', 'jpeg'],
            'spectral_range': (8.0, 14.0),
            'thermal_sensitivity': 0.05,
            'description': '大疆H30T高温热红外云台相机'
        },
        'M2EA': {
            'name': '大疆 御2行业进阶版',
            'temperature_range': (-10, 400),
            'resolution': (640, 512),
            'pixel_size': 17.0,
            'format_support': ['jpg', 'jpeg'],
            'spectral_range': (8.0, 14.0),
            'thermal_sensitivity': 0.1,
            'description': '大疆御2行业进阶版热红外相机'
        }
    }
    
    # 默认设置
    DEFAULT_DRONE_MODEL = 'M30T'
    DEFAULT_COMPRESSION = 'lzw'
    DEFAULT_LOG_LEVEL = 'INFO'
    
    # 文件格式设置
    SUPPORTED_INPUT_FORMATS = ['.jpg', '.jpeg', '.JPG', '.JPEG']
    OUTPUT_FORMAT = '.tiff'
    
    # TIFF设置
    TIFF_COMPRESSION_OPTIONS = {
        'lzw': 'LZW compression (recommended)',
        'zip': 'ZIP compression',
        'none': 'No compression'
    }
    
    # 输出精度设置
    TEMPERATURE_PRECISION = 2  # 小数点后位数
    TEMPERATURE_SCALE_FACTOR = 100  # 温度数据缩放因子
    
    # 日志设置
    LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # GUI设置
    GUI_WINDOW_SIZE = (600, 500)
    GUI_TITLE = "大疆无人机热红外图像转换器"
    
    # 批处理设置
    BATCH_PROGRESS_UPDATE_INTERVAL = 10  # 进度更新间隔（文件数）
    MAX_CONCURRENT_CONVERSIONS = 4  # 最大并发转换数
    
    # 错误处理
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY = 1.0  # 重试延迟（秒）
    
    @classmethod
    def get_model_config(cls, model: str) -> Dict:
        """
        获取指定型号的配置
        
        Args:
            model: 无人机型号
            
        Returns:
            Dict: 配置字典
        """
        model = model.upper()
        if model not in cls.DRONE_MODELS:
            raise ValueError(f"不支持的无人机型号: {model}")
        
        return cls.DRONE_MODELS[model]
    
    @classmethod
    def get_supported_models(cls) -> List[str]:
        """
        获取支持的无人机型号列表
        
        Returns:
            List[str]: 型号列表
        """
        return list(cls.DRONE_MODELS.keys())
    
    @classmethod
    def validate_temperature_range(cls, temperature: float, model: str) -> bool:
        """
        验证温度值是否在有效范围内
        
        Args:
            temperature: 温度值
            model: 无人机型号
            
        Returns:
            bool: 是否有效
        """
        config = cls.get_model_config(model)
        temp_min, temp_max = config['temperature_range']
        return temp_min <= temperature <= temp_max
    
    @classmethod
    def get_temperature_range_string(cls, model: str) -> str:
        """
        获取温度范围字符串表示
        
        Args:
            model: 无人机型号
            
        Returns:
            str: 温度范围字符串
        """
        config = cls.get_model_config(model)
        temp_min, temp_max = config['temperature_range']
        return f"{temp_min}°C ~ {temp_max}°C"
    
    @classmethod
    def is_supported_input_format(cls, filename: str) -> bool:
        """
        检查文件格式是否支持
        
        Args:
            filename: 文件名
            
        Returns:
            bool: 是否支持
        """
        _, ext = os.path.splitext(filename)
        return ext.lower() in [fmt.lower() for fmt in cls.SUPPORTED_INPUT_FORMATS]

# 创建全局配置实例
config = Config() 