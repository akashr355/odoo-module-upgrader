import xmlrpc.client


class OdooClient:
    def __init__(self, url, db, username, password, use_http=False):
        if not url.startswith(("http://", "https://")):
            url = f"http://{url}" if use_http else f"https://{url}"
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.models = None

    def connect(self):
        common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        if not self.uid:
            raise ValueError("Authentication failed")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def fetch_modules(self, states=["installed"]):
        modules = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "ir.module.module",
            "search_read",
            [[("state", "in", states)]],
            {"fields": ["name", "state", "summary"], "limit": 1000},
        )
        return sorted(modules, key=lambda m: m["name"].lower())

    def upgrade_modules(self, module_names):
        module_ids = self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "ir.module.module",
            "search",
            [[("name", "in", module_names)]],
        )
        if not module_ids:
            return 0
        self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            "ir.module.module",
            "button_immediate_upgrade",
            [module_ids],
        )
        return len(module_ids)
