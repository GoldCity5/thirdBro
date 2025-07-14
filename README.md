# 大疆无人机热红外图像转换器

一个专门用于将大疆无人机热红外图像从JPG格式转换为TIFF格式的工具。

## 功能特点

- 支持大疆热红外相机的R-JPEG格式图像
- 使用DJI Thermal SDK进行高精度温度数据提取
- 支持多种大疆无人机型号
- 批量转换和递归处理
- 图形化用户界面和命令行界面

## 支持的无人机型号

- **M30T** - 大疆 M30T (-20°C ~ 400°C)
- **H20T** - 大疆 H20T (-20°C ~ 550°C)
- **H30T** - 大疆 H30T (-20°C ~ 1600°C)
- **M2EA** - 大疆 御2行业进阶版 (-10°C ~ 400°C)

## 安装说明

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 下载DJI Thermal SDK

1. 访问 [DJI官网](https://www.dji.com/cn/downloads/softwares/dji-thermal-sdk)
2. 下载 DJI Thermal SDK v1.4 或更高版本
3. 将 `libdirp.dll` 文件放在程序根目录下

### 3. 系统要求

- **操作系统**: Windows 10/11 x64
- **Python**: 3.7+
- **内存**: 建议8GB以上

## 使用方法

### 命令行界面

```bash
# 转换单个文件
python main.py -i DJI_thermal.jpg -o output.tiff

# 批量转换
python main.py -i input_dir -o output_dir --batch

# 递归转换子目录
python main.py -i input_dir -o output_dir --batch --recursive

# 指定无人机型号
python main.py -i image.jpg -o output.tiff -m H20T

# 检查系统要求
python main.py --check-requirements
```

### 图形化界面

```bash
python gui.py
```

## 项目结构

```
thirdBro/
├── main.py                    # 主程序入口
├── dji_thermal_converter.py   # DJI SDK转换器
├── gui.py                     # 图形化界面
├── config.py                  # 配置文件
├── requirements.txt           # 依赖列表
└── README.md                  # 说明文档
```

## 技术说明

### DJI R-JPEG格式

DJI热红外图像采用R-JPEG（Radiometric JPEG）格式，包含：
- 可见光图像数据
- 温度数据
- 相机参数
- 环境参数

### 温度数据提取

使用DJI Thermal SDK提取真实温度数据，精度可达0.1°C。

### 输出格式

- **文件格式**: 16位TIFF
- **温度单位**: 摄氏度（°C）
- **数据精度**: 0.1°C
- **压缩方式**: 可选LZW、ZIP或无压缩

## 故障排除

### 常见问题

1. **DJI SDK未初始化**
   - 确保 `libdirp.dll` 文件在程序目录下
   - 检查DLL文件版本是否匹配

2. **转换失败**
   - 确认输入文件是DJI热红外图像
   - 检查文件格式是否为R-JPEG

3. **性能问题**
   - 批量转换时建议设置合理的文件数量
   - 确保有足够的磁盘空间

### 系统检查

```bash
python main.py --check-requirements
```

## 许可证

MIT License

## 作者

Created for DJI thermal image processing 