from pathlib import Path
from datetime import datetime
import csv
import json
import shutil
import logging

class fileOrganiser:
    def __init__(self,inbox_dir, backup_dir,file_rules, dir_map,logger):
        self.inbox_dir=inbox_dir
        self.backup_dir=backup_dir
        self.file_rules=file_rules
        self.dir_map=dir_map
        self.logger=logger

    def _backup_file(self,file_path):

        shutil.copy2(file_path,self.backup_dir)
        self.logger.info("文件备份成功:%s",file_path.name)

    def _move_file(self,file_path):
        extension=file_path.suffix.lower()
        self.logger.debug(
                    "正在检查文件:%s,后缀:%s",file_path.name,extension
                )
        target_dir=None
        target_name = self.file_rules.get(extension, "OtherDir_Path")
        if extension not in self.file_rules:
            self.logger.warning(
            "未识别文件类型：%s,使用默认分类",extension
            )
        target_dir =self.dir_map.get(target_name,self.dir_map["OtherDir_Path"])
        shutil.move(file_path, target_dir)
        self.logger.info("文件移动成功:%s",file_path.name)
        return target_dir

    def organize_files(self):

        logs=[]
        for file_path in self.inbox_dir.iterdir():
            if not file_path.is_file():
                continue
            extension=file_path.suffix.lower()
            status="success"
            error=''
            target_dir=None
            try:
                self._backup_file(file_path)
                target_dir=self._move_file(file_path)
            except PermissionError as e:
                status='failed'
                error=str(e)
                self.logger.exception("文件处理失败:%s",file_path.name)
            except Exception as e:
                status='failed'
                error=str(e)
                self.logger.exception("文件处理失败:%s",file_path.name)

            log_record = {
                    "filename": file_path.name,
                    "extension": extension,
                    "target_dir": target_dir.name if target_dir is not None else '',
                    "status":status,
                    "error":error,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),                        }
            logs.append(log_record)
        return logs

def create_project_dirs():
    """
    创建项目所需的目录，并返回各目录对应的 Path 对象。
    """

    base_dir = Path(__file__).resolve().parent

    inbox_dir = base_dir / "Inbox"
    sorted_dir = base_dir / "Sorted"
    logs_dir = base_dir / "Logs"
    backups_dir = base_dir / "Backups"

    code_dir = sorted_dir / "CodeDir"
    text_dir = sorted_dir / "TextDir"
    data_dir = sorted_dir / "DataDir"
    image_dir = sorted_dir / "ImageDir"
    other_dir = sorted_dir / "OtherDir"

    # 创建所有目录。
    # parents=True：如果父目录不存在，也一并创建。
    # exist_ok=True：目录已经存在时不报错。
    dirs = [
        inbox_dir,
        sorted_dir,
        logs_dir,
        backups_dir,
        code_dir,
        text_dir,
        data_dir,
        image_dir,
        other_dir,
    ]

    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)

    # 用字典统一管理项目中的路径，
    # 避免函数返回大量变量导致顺序难以维护。
    return {
        "base_dir": base_dir,
        "inbox_dir": inbox_dir,
        "logs_dir": logs_dir,
        "backups_dir": backups_dir,
        "code_dir": code_dir,
        "text_dir": text_dir,
        "data_dir": data_dir,
        "image_dir": image_dir,
        "other_dir": other_dir,
    }


def load_file_rules(base_dir):
    """
    读取文件分类规则。

    如果 file_rules.json 不存在或为空，
    则先自动写入一份默认规则。
    """

    rules_file = base_dir / "file_rules.json"

    default_rules = {
    ".py": "CodeDir_Path",
    ".cpp": "CodeDir_Path",
    ".c": "CodeDir_Path",
    ".jpg": "ImageDir_Path",
    ".txt": "TextDir_Path",
    ".csv": "DataDir_Path",
    ".json": "DataDir_Path",
    }
    # 第一次运行或者配置文件为空时，创建默认配置。
    if not rules_file.exists() or rules_file.stat().st_size == 0:
        with open(rules_file, "w", encoding="utf-8") as file:
            json.dump(default_rules, file, indent=4)

    # 将 JSON 数据读取为 Python 字典。
    with open(rules_file, "r", encoding="utf-8") as file:
        file_rules = json.load(file)

    return file_rules


def create_backup_dir(backups_dir):
    """
    为本次程序运行创建一个独立的备份目录。
    """

    backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backups_dir / f"backup_{backup_time}"

    backup_dir.mkdir(exist_ok=True)

    return backup_dir

def write_logs(logs, logs_dir):
    """
    将本次运行产生的日志追加到 move_log.csv。
    """

    log_file = logs_dir / "move_log.csv"

    # 文件不存在，或者存在但为空，都需要写 CSV 表头。
    is_new_file = (
        not log_file.exists()
        or log_file.stat().st_size == 0
    )


    with open(log_file, "a", newline="", encoding="utf-8") as file:
        fieldnames = [
            "filename",
            "extension",
            "target_dir",
            "status",
            "error",
            "time"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        if is_new_file:
            writer.writeheader()

        writer.writerows(logs)

def setup_logger(logs_dir):
    logger=logging.getLogger("fileOrganiser")
    logger.setLevel(logging.DEBUG)
    console_handler=logging.StreamHandler()
    file_handler=logging.FileHandler(
        logs_dir/"app.log",
        mode="a",
        encoding="utf-8"
    )
    console_handler.setLevel(logging.WARNING)
    file_handler.setLevel(logging.DEBUG)
    formatter=logging.Formatter(
        "%(asctime)s|%(levelname)s|%(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def main():
    """
    程序主流程。

    main() 本身不负责具体功能，
    只负责按照正确顺序调用各个功能函数。
    """

    # 1. 初始化项目目录。
    paths = create_project_dirs()

    # 2. 读取 JSON 中的文件分类规则。
    file_rules = load_file_rules(paths["base_dir"])

    # JSON 中保存的是目录名称字符串，
    # dir_map 负责把字符串转换成真正的 Path 对象。
    dir_map = {
    "CodeDir_Path": paths["code_dir"],
    "TextDir_Path": paths["text_dir"],
    "DataDir_Path": paths["data_dir"],
    "ImageDir_Path": paths["image_dir"],
    "OtherDir_Path": paths["other_dir"],
    }
    backup_dir = create_backup_dir(paths["backups_dir"])

    logger=setup_logger(paths["logs_dir"])
    logger.info("文件整理程序启动")

    organiser=fileOrganiser(paths["inbox_dir"], backup_dir,file_rules, dir_map,logger)
    logs=organiser.organize_files()
    write_logs(logs,paths["logs_dir"])
    # 3. 创建本次运行对应的备份目录。

# 只有直接运行 main.py 时才启动程序。
# 如果以后其他 .py 文件 import main，则不会自动执行整个文件整理流程。
if __name__ == "__main__":
    main()