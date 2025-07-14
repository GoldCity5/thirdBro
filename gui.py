#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from pathlib import Path
import logging

# 导入DJI转换器
try:
    from dji_thermal_converter import DJIThermalConverter
    DJI_CONVERTER_AVAILABLE = True
except ImportError:
    DJI_CONVERTER_AVAILABLE = False

class ThermalConverterGUI:
    """DJI热红外图像转换器GUI界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("大疆无人机热红外图像转换器")
        self.root.geometry("600x500")
        
        # 设置日志
        self.setup_logging()
        
        # 创建界面
        self.create_widgets()
        
        # 初始化变量
        self.converter = None
        self.is_converting = False
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="大疆无人机热红外图像转换器", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 无人机型号选择
        ttk.Label(main_frame, text="无人机型号:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value="M30T")
        model_combo = ttk.Combobox(main_frame, textvariable=self.model_var, 
                                  values=["M30T", "H20T", "H30T", "M2EA"], 
                                  state="readonly", width=15)
        model_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 输入文件/目录选择
        ttk.Label(main_frame, text="输入路径:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.input_var = tk.StringVar()
        input_entry = ttk.Entry(main_frame, textvariable=self.input_var, width=50)
        input_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(main_frame, text="浏览", command=self.browse_input).grid(row=2, column=2, pady=5)
        
        # 输出信息显示
        output_info_frame = ttk.LabelFrame(main_frame, text="输出设置", padding="10")
        output_info_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        from pathlib import Path
        output_dir = Path.cwd() / "output"
        output_info = ttk.Label(output_info_frame, 
                               text=f"📁 自动输出到: {output_dir}",
                               foreground="blue")
        output_info.grid(row=0, column=0, sticky=tk.W)
        
        note_label = ttk.Label(output_info_frame, 
                             text="💡 提示: 文件将自动保存到项目的output文件夹中",
                             font=('Arial', 9), foreground="gray")
        note_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # 选项
        options_frame = ttk.LabelFrame(main_frame, text="转换选项", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # 批量转换
        self.batch_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="批量转换", variable=self.batch_var).grid(row=0, column=0, sticky=tk.W)
        
        # 递归处理
        self.recursive_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="递归处理子目录", variable=self.recursive_var).grid(row=0, column=1, sticky=tk.W)
        
        # 压缩选项
        ttk.Label(options_frame, text="压缩方式:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.compression_var = tk.StringVar(value="lzw")
        compression_combo = ttk.Combobox(options_frame, textvariable=self.compression_var,
                                        values=["lzw", "zip", "none"], state="readonly", width=10)
        compression_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 转换按钮
        self.convert_button = ttk.Button(main_frame, text="开始转换", command=self.start_conversion)
        self.convert_button.grid(row=5, column=0, columnspan=3, pady=20)
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 日志框
        log_frame = ttk.LabelFrame(main_frame, text="转换日志", padding="5")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def browse_input(self):
        """浏览输入文件/目录"""
        if self.batch_var.get():
            # 批量模式 - 选择目录
            path = filedialog.askdirectory(title="选择输入目录")
        else:
            # 单文件模式 - 选择文件
            path = filedialog.askopenfilename(
                title="选择输入文件",
                filetypes=[("JPG files", "*.jpg"), ("JPEG files", "*.jpeg"), ("All files", "*.*")]
            )
        
        if path:
            self.input_var.set(path)
            
    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def start_conversion(self):
        """开始转换"""
        if self.is_converting:
            messagebox.showwarning("警告", "转换正在进行中...")
            return
            
        # 验证输入
        input_path = self.input_var.get().strip()
        
        if not input_path:
            messagebox.showerror("错误", "请选择输入文件或目录")
            return
            
        # 检查DJI转换器是否可用
        if not DJI_CONVERTER_AVAILABLE:
            messagebox.showerror("错误", "DJI转换器不可用\n请确保已安装 dji_thermal_sdk")
            return
        
        # 显示输出信息
        from pathlib import Path
        output_dir = Path.cwd() / "output"
        self.log_message(f"📁 输出目录: {output_dir}")
        self.log_message("开始转换...")
            
        # 在单独线程中运行转换
        self.is_converting = True
        self.convert_button.config(text="转换中...", state="disabled")
        self.progress.start()
        
        thread = threading.Thread(target=self.convert_images)
        thread.daemon = True
        thread.start()
        
    def convert_images(self):
        """转换图像（在单独线程中运行）"""
        try:
            # 创建DJI转换器
            self.log_message("初始化DJI转换器...")
            converter = DJIThermalConverter()
            
            if not converter.is_initialized:
                self.log_message("错误: DJI SDK未初始化")
                self.log_message("请确保libdirp.dll文件在程序目录下")
                return
                
            self.log_message("DJI SDK初始化成功")
            
            input_path = self.input_var.get().strip()
            
            # 自动生成输出路径
            from pathlib import Path
            project_dir = Path.cwd()
            output_dir = project_dir / "output"
            
            # 确保output目录存在
            output_dir.mkdir(exist_ok=True)
            
            if self.batch_var.get():
                # 批量转换模式
                self.log_message(f"开始批量转换: {input_path}")
                
                input_dir = Path(input_path)
                
                # 查找所有JPG文件
                if self.recursive_var.get():
                    pattern = "**/*.jpg"
                else:
                    pattern = "*.jpg"
                
                image_files = list(input_dir.glob(pattern))
                image_files.extend(input_dir.glob(pattern.replace('.jpg', '.JPG')))
                
                if not image_files:
                    self.log_message("未找到JPG文件")
                    return
                    
                self.log_message(f"找到 {len(image_files)} 个图像文件")
                
                success_count = 0
                for i, image_file in enumerate(image_files):
                    try:
                        # 生成输出文件名
                        relative_path = image_file.relative_to(input_dir)
                        output_file = output_dir / relative_path.with_suffix('.tiff')
                        
                        # 确保输出目录存在
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        
                        self.log_message(f"转换 ({i+1}/{len(image_files)}): {image_file.name}")
                        
                        # 转换图像
                        if converter.convert_rjpeg_to_tiff(str(image_file), str(output_file)):
                            success_count += 1
                            self.log_message(f"✅ 转换成功: {image_file.name}")
                        else:
                            self.log_message(f"❌ 转换失败: {image_file.name}")
                        
                    except Exception as e:
                        self.log_message(f"转换失败 {image_file.name}: {str(e)}")
                
                self.log_message(f"批量转换完成: {success_count}/{len(image_files)} 个文件成功")
                
            else:
                # 单文件转换模式
                self.log_message(f"开始转换: {input_path}")
                
                # 生成输出文件名
                input_file = Path(input_path)
                output_file = output_dir / (input_file.stem + '.tiff')
                
                # 转换图像
                if converter.convert_rjpeg_to_tiff(input_path, str(output_file)):
                    self.log_message(f"✅ 转换完成: {output_file}")
                else:
                    self.log_message(f"❌ 转换失败: {input_path}")
                
        except Exception as e:
            self.log_message(f"转换失败: {str(e)}")
            
        finally:
            # 重置UI状态
            self.is_converting = False
            self.convert_button.config(text="开始转换", state="normal")
            self.progress.stop()

def main():
    """主函数"""
    root = tk.Tk()
    app = ThermalConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 