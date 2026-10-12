from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INBOX_DIR = BASE_DIR / "Inbox"

INBOX_DIR.mkdir(exist_ok=True)

test_files = [
    "test.py",
    "hello.txt",
    "student.csv",
    "config.json",
    "photo.jpg",
    "program.cpp",
    "main.c",
    "unknown.xyz"
]

for filename in test_files:
    file_path = INBOX_DIR / filename
    file_path.touch(exist_ok=True)

print("测试文件生成完成")