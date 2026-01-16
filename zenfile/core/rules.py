class RuleMatcher:
    def __init__(self, config):
        self.rules = config.get("rules", {})
        # 新增：关键词规则
        self.keyword_rules = config.get("keyword_rules", {})
        self.ignore_exts = config.get("ignore_exts", [])

    def match(self, file_path):
        """
        根据规则匹配目标文件夹
        返回: (是否忽略, 目标文件夹名)
        """
        filename = file_path.name.lower()

        # 1. 检查忽略后缀
        if file_path.suffix.lower() in self.ignore_exts:
            return True, None

        # 2. 优先匹配关键词 (Smart Match)
        for keyword, folder in self.keyword_rules.items():
            if keyword.lower() in filename:
                return False, folder

        # 3. 匹配后缀名 (Extension Match)
        ext = file_path.suffix.lower()
        for folder, ext_list in self.rules.items():
            if ext in ext_list:
                return False, folder

        # 4. 默认归类
        return False, "99_其他"