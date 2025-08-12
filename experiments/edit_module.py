import os
import re
from typing import List

FILE_PATH = "~/miniforge3/envs/tc_env/lib/python3.12/site-packages/tensorcircuit/cloud/tencent.py"

def remove_measure_commands() -> None:
    """
    从 tencent.py 文件中删除之前添加的 measure 命令
    """
    file_path = os.path.expanduser(FILE_PATH)
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 查找并删除测量命令行
    # 模式匹配：包含 "s += 'measure q[数字];\n'" 的行
    measure_pattern = re.compile(r"\s*s \+= 'measure q\[\d+\];\\n'\s*\n")
    
    filtered_lines = []
    removed_count = 0
    
    for line in lines:
        if measure_pattern.match(line):
            removed_count += 1
            continue  # 跳过匹配的行
        filtered_lines.append(line)
    
    if removed_count > 0:
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(filtered_lines)
        
        print(f"成功删除了 {removed_count} 个测量命令")
    else:
        print("没有找到需要删除的测量命令")

def add_measure_commands(qubits: list[int]) -> None:
    """
    在 tencent.py 文件的第217行开始添加 measure 命令
    
    Parameters:
    -----------
    qubits : list[int]
        要添加的测量量子比特
    """

    remove_measure_commands()

    file_path = os.path.expanduser(FILE_PATH)
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 生成要插入的测量命令
    measure_commands = []
    for i in qubits:
        measure_commands.append(f"                    s += 'measure q[{i}];\\n'\n")
    
    # 在第216行（索引215）后插入测量命令
    target_line = 215  # 0-based index for line 216
    
    # 确保目标行存在
    if target_line < len(lines):
        # 在目标行后插入测量命令
        lines[target_line+1:target_line+1] = measure_commands
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"成功添加了 {len(qubits)} 个测量命令到 tencent.py 文件第 {target_line+2} 行开始")
    else:
        print(f"错误：文件只有 {len(lines)} 行，无法在第 {target_line+1} 行后插入")

def backup_file() -> str:
    """
    创建原文件的备份
    
    Returns:
    --------
    str: 备份文件的路径
    """
    import shutil
    from datetime import datetime
    
    file_path = os.path.expanduser(FILE_PATH)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    
    shutil.copy2(file_path, backup_path)
    print(f"备份文件已创建：{backup_path}")
    return backup_path

def show_context_around_line(line_number: int, context: int = 5) -> None:
    """
    显示指定行号周围的代码上下文
    
    Parameters:
    -----------
    line_number : int
        要查看的行号（1-based）
    context : int
        显示前后多少行的上下文
    """
    file_path = os.path.expanduser(FILE_PATH)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    start = max(0, line_number - 1 - context)
    end = min(len(lines), line_number + context)
    
    print(f"\n文件第 {start+1} 到 {end} 行的内容：")
    print("-" * 50)
    
    for i in range(start, end):
        marker = ">>>" if i == line_number - 1 else "   "
        print(f"{marker} {i+1:3d}: {lines[i].rstrip()}")
    
    print("-" * 50)

if __name__ == "__main__":
    # 示例用法
    print("选择操作：")
    print("1. 查看第217行附近的代码")
    print("2. 备份文件")
    print("3. 添加测量命令")
    print("4. 删除测量命令")
    
    choice = input("请输入选择 (1-4): ").strip()
    
    if choice == "1":
        show_context_around_line(217)
    elif choice == "2":
        backup_file()
    elif choice == "3":
        try:
            n = int(input("请输入量子比特数量: "))
            backup_file()  # 先备份
            add_measure_commands(list(range(n)))
        except ValueError:
            print("请输入有效的整数")
    elif choice == "4":
        backup_file()  # 先备份
        remove_measure_commands()
    else:
        print("无效选择")
