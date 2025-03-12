import os 
import re
from typing import Optional, List

class FileManager:
    """文件操作管理器"""
    
    def __init__(self, logger=None):
        self.logger = logger
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """获取单个文件的大小（字节）"""
        if os.path.isfile(file_path):
            return os.path.getsize(file_path)
        else:
            if self.logger:
                self.logger.warning(f"文件 {file_path} 不存在")
            return None

    def find_matching_unittest_files(self, directory: str, target_str: str) -> List[str]:
        """查找目录中符合特定命名规则的文件"""
        pattern = re.compile(
            rf'.*{re.escape(target_str)}(_\d+)?\.txt$',
            flags=re.IGNORECASE
        )
        
        matching_files = []
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            if os.path.isfile(filepath) and pattern.fullmatch(filename):
                matching_files.append(filename)
        
        return matching_files
    

    def find_matching_md_file(self, directory: str, filename: str) -> List[str]:
        """在指定目录及其子目录中递归查找文件"""
        found_files = []
        
        if not os.path.exists(directory):
            if self.logger:
                self.logger.warning(f"目录 '{directory}' 不存在")
            return found_files
        
        for root, dirs, files in os.walk(directory):
            if filename in files:
                file_path = os.path.join(root, filename)
                found_files.append(file_path)
        
        return found_files

    def find_clean_doc(self, root_directory: str, function_name: str) -> Optional[str]:
        """
        查找指定函数名的 HTML 文件
        
        Args:
            function_name: 要查找的函数名，例如 "bondAccr"
            root_directory: 开始搜索的根目录
            
        Returns:
            找到的文件的完整路径，如果没找到则返回 None
        """
        if not os.path.exists(root_directory):
            print(f"警告: 目录 '{root_directory}' 不存在")
            return None
        
        for root, dirs, files in os.walk(root_directory):
            # 检查当前目录中的所有文件
            for filename in files:
                # 检查是否匹配任一可能的文件名
                if filename == f"{function_name}.txt":
                    # 返回完整的文件路径
                    return os.path.join(root, filename)
        
        # 如果没有找到匹配的文件
        return None
        

    def find_function_html_file(root_directory: str, function_name: str) -> Optional[str]:
        """
        递归查找指定函数名的 HTML 文件
        
        Args:
            function_name: 要查找的函数名，例如 "bondAccr"
            root_directory: 开始搜索的根目录
            
        Returns:
            找到的文件的完整路径，如果没找到则返回 None
        """
        # 生成可能的文件名变体

        # 特殊处理一些函数
        if function_name == "valueAtRisk": return "./docs/funcs/v/var_0.html"
        if function_name == "condValueAtRisk": return "./docs/funcs/c/cvar.html"

        possible_filenames = [
            f"{function_name}.html",              # 原始名称
            f"{function_name.lower()}.html"       # 全小写
        ]
        
        # 检查根目录是否存在
        if not os.path.exists(root_directory):
            print(f"警告: 目录 '{root_directory}' 不存在")
            return None
        
        # 递归遍历目录
        for root, dirs, files in os.walk(root_directory):
            # 检查当前目录中的所有文件
            for filename in files:
                # 检查是否匹配任一可能的文件名
                if filename in possible_filenames:
                    # 返回完整的文件路径
                    return os.path.join(root, filename)
        
        # 如果没有找到匹配的文件
        return None


    def find_all_function_html_files(function_name: str, root_directory: str) -> List[str]:
        """
        递归查找指定函数名的所有 HTML 文件
        
        Args:
            function_name: 要查找的函数名，例如 "bondAccr"
            root_directory: 开始搜索的根目录
            
        Returns:
            找到的所有文件的完整路径列表，如果没找到则返回空列表
        """
        # 生成可能的文件名变体
        possible_filenames = [
            f"{function_name}.html",              # 原始名称
            f"{function_name.lower()}.html"       # 全小写
        ]
        
        found_files = []
        
        # 检查根目录是否存在
        if not os.path.exists(root_directory):
            print(f"警告: 目录 '{root_directory}' 不存在")
            return found_files
        
        # 递归遍历目录
        for root, dirs, files in os.walk(root_directory):
            # 检查当前目录中的所有文件
            for filename in files:
                # 检查是否匹配任一可能的文件名
                if filename in possible_filenames:
                    # 添加完整的文件路径到结果列表
                    found_files.append(os.path.join(root, filename))
        
        return found_files

    def read_with_limit(self, file_path: str, limit_kb: int = 2) -> Optional[str]:
        """读取文件内容，超过指定大小时截断"""
        limit_bytes = limit_kb * 1024
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(limit_bytes + 1)
                
                if len(content) > limit_bytes:
                    content = content[:limit_bytes]
                    if self.logger:
                        self.logger.warning(f"文件超过{limit_kb}KB，已截断")
                
                return content
        except UnicodeDecodeError:
            if self.logger:
                self.logger.error(f"文件 {file_path} 不是有效的文本文件")
            return None

