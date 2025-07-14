# Windows系统安装说明

## 系统要求

- **操作系统**: Windows 10/11 (64位)
- **Python版本**: Python 3.7 或更高版本
- **内存**: 建议 8GB 以上
- **硬盘空间**: 至少 1GB 可用空间

## 安装步骤

### 1. 安装Python（如果尚未安装）

从 [Python官网](https://www.python.org/downloads/) 下载并安装Python 3.7+

**重要**: 安装时勾选 "Add Python to PATH"

### 2. 下载项目代码

```bash
git clone <repository-url>
cd thirdBro
```

或者直接下载zip文件并解压

### 3. 安装Python依赖

打开命令提示符（cmd）或PowerShell，进入项目目录：

```bash
pip install -r requirements.txt
```

如果安装速度慢，可以使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 下载DJI Thermal SDK

#### 方法1：官方下载
1. 访问 [DJI官网](https://www.dji.com/cn/downloads/softwares/dji-thermal-sdk)
2. 下载 `dji_thermal_sdk_v1.4_20220929.zip` 或更高版本
3. 解压文件

#### 方法2：直接链接（如果可用）
```bash
# 示例链接（实际链接可能会变更）
https://dl.djicdn.com/downloads/dji_assistant/20220929/dji_thermal_sdk_v1.4_20220929.zip
```

### 5. 配置DJI SDK

1. 从下载的SDK中找到 `tsdk-core\lib\release_x64\` 目录
2. 将以下文件复制到项目根目录：
   - `libdirp.dll`
   - `libv_dirp.dll`
   - `libv_girp.dll`
   - `libv_iirp.dll`
   - `libv_list.ini`

**目录结构示例：**
```
thirdBro/
├── main.py
├── dji_thermal_converter.py
├── gui.py
├── config.py
├── requirements.txt
├── README.md
├── libdirp.dll          ← 从DJI SDK复制
├── libv_dirp.dll        ← 从DJI SDK复制
├── libv_girp.dll        ← 从DJI SDK复制
├── libv_iirp.dll        ← 从DJI SDK复制
└── libv_list.ini        ← 从DJI SDK复制
```

### 6. 验证安装

运行系统检查：

```bash
python main.py --check-requirements
```

如果显示所有组件都正常，说明安装成功。

## 使用方法

### 命令行使用

```bash
# 转换单个文件
python main.py -i DJI_thermal.jpg -o output.tiff

# 批量转换
python main.py -i input_folder -o output_folder --batch

# 指定无人机型号
python main.py -i image.jpg -o output.tiff -m H20T
```

### 图形界面使用

```bash
python gui.py
```

## 常见问题解决

### 1. "libdirp.dll not found" 错误

**解决方法：**
- 确保 `libdirp.dll` 文件在项目根目录下
- 检查DLL文件是否为64位版本（对应Windows 64位系统）
- 重新从DJI SDK复制文件

### 2. "DJI SDK未初始化" 错误

**解决方法：**
- 确保所有DJI SDK文件都已正确复制到项目目录
- 检查 `libv_list.ini` 文件是否存在
- 确保文件没有被杀毒软件误删

### 3. "module 'dji_thermal_sdk' has no attribute" 错误

**解决方法：**
```bash
pip uninstall dji_thermal_sdk
pip install dji_thermal_sdk -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. OpenCV相关错误

**解决方法：**
```bash
pip uninstall opencv-python
pip install opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5. 转换速度慢

**优化建议：**
- 确保有足够的内存
- 使用SSD硬盘
- 批量转换时分批处理
- 关闭不必要的程序

## 性能优化建议

1. **内存优化**
   - 建议系统内存8GB以上
   - 批量转换时避免同时处理过多文件

2. **硬盘优化**
   - 输入输出文件存储在SSD上
   - 确保有足够的硬盘空间

3. **系统优化**
   - 关闭不必要的后台程序
   - 使用高性能电源模式

## 支持的文件格式

- **输入格式**: DJI R-JPEG (.jpg, .jpeg)
- **输出格式**: 16位TIFF (.tiff)
- **压缩选项**: LZW, ZIP, 无压缩

## 技术支持

如果遇到问题，请：

1. 首先运行 `python main.py --check-requirements` 检查系统状态
2. 查看错误日志中的详细信息
3. 确保所有依赖都已正确安装
4. 验证DJI SDK文件是否完整

## 更新说明

要更新项目：

1. 备份当前配置
2. 下载最新代码
3. 重新安装依赖：`pip install -r requirements.txt`
4. 重新配置DJI SDK文件

## 许可证

本项目使用MIT许可证。DJI Thermal SDK使用大疆的许可证条款。 