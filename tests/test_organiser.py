import logging
from file_organizer.main import fileOrganiser


def test_backup_file(tmp_path):

    # 1. 创建临时测试目录
    inbox_dir = tmp_path / "Inbox"
    backup_dir = tmp_path / "Backups"

    inbox_dir.mkdir()
    backup_dir.mkdir()

    # 2. 创建测试文件
    file_path = inbox_dir / "test.py"
    file_path.write_text("print('hello')", encoding="utf-8")

    # 3. 实例化 FileOrganizer
    organizer = fileOrganiser(
        inbox_dir=inbox_dir,
        backup_dir=backup_dir,
        file_rules={},
        dir_map={},
        logger=logging.getLogger("test_backup")
    )

    # 4. 调用你自己编写的备份方法
    organizer._backup_file(file_path)

    # 5. 获取备份文件路径
    backup_file = backup_dir / "test.py"

    # 6. 检查原文件是否仍然存在
    assert file_path.exists()

    # 7. 检查备份文件是否创建成功
    assert backup_file.exists()

    # 8. 检查两个文件内容是否一致
    assert (
        file_path.read_text(encoding="utf-8")
        == backup_file.read_text(encoding="utf-8")
    )

    # 9. 检查备份内容是否符合预期
    assert backup_file.read_text(encoding="utf-8") == "print('hello')"