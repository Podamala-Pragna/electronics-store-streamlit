import os
from typing import Optional, Dict, Any
import pandas as pd
from datetime import datetime
from slugify import slugify

DATA_DIR = "data"
UPLOAD_DIR = "uploads"

# ---- SAFETY: ensure folders exist even if files with same name existed
def _ensure_dir(path: str):
    if os.path.exists(path) and not os.path.isdir(path):
        os.remove(path)
    os.makedirs(path, exist_ok=True)

_ensure_dir(DATA_DIR)
_ensure_dir(UPLOAD_DIR)

FILES = {
    "products": "products.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv",
    "repairs": "repairs.csv",
    "users": "users.csv",
    "sell_requests": "sell_requests.csv",
    "payments": "payments.csv",
}

SCHEMAS = {
    "products": [
        "id","name","brand","category","condition","price","stock","warranty_months",
        "image_path","desc","slug","created_at","updated_at","created_by"
    ],
    "orders": ["order_id","email","status","total","payment_id","payment_method","created_at"],
    "order_items": ["order_id","product_id","qty","price"],
    "repairs": ["ticket","email","device","issue","status","created_at"],
    # users now includes password_hash (bcrypt)
    "users": ["email","password_hash","role","created_at"],
    "sell_requests": [
        "req_id","email","device","brand","condition","exp_price","desc","image_path",
        "status","created_at"
    ],
    "payments": ["payment_id","order_id","amount","method","details","status","created_at"],
}

def _path(name): return os.path.join(DATA_DIR, FILES[name])

def _ensure_file(name):
    p = _path(name)
    if not os.path.exists(p):
        pd.DataFrame(columns=SCHEMAS[name]).to_csv(p, index=False)

def _load(name):
    _ensure_file(name)
    df = pd.read_csv(_path(name))
    # auto-migrate users.csv if password_hash missing (older versions)
    if name == "users" and "password_hash" not in df.columns:
        df["password_hash"] = ""
        if "role" not in df.columns:
            df["role"] = "customer"
        if "created_at" not in df.columns:
            df["created_at"] = datetime.now()
        df = df[SCHEMAS["users"]]  # reorder
        df.to_csv(_path("users"), index=False)
    return df

def _save(name, df):
    df.to_csv(_path(name), index=False)

# ---------- Users (password-aware) ----------
def create_user(email: str, password_hash: str, role: str = "customer") -> bool:
    if not email: return False
    df = _load("users")
    if (df["email"] == email).any():
        return False  # already exists
    new = pd.DataFrame([{
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "created_at": datetime.now()
    }])
    _save("users", pd.concat([df, new], ignore_index=True))
    return True

def get_user(email: str) -> Optional[Dict[str, Any]]:
    if not email: return None
    df = _load("users")
    row = df[df["email"] == email]
    if row.empty: return None
    r = row.iloc[0].to_dict()
    return r

def set_role(email: str, role: str) -> bool:
    df = _load("users")
    m = df["email"] == email
    if not m.any(): return False
    df.loc[m, "role"] = role
    _save("users", df)
    return True

def get_role(email: str) -> str:
    u = get_user(email)
    return u.get("role", "customer") if u else "customer"

def set_password_hash(email: str, password_hash: str) -> bool:
    df = _load("users")
    m = df["email"] == email
    if not m.any(): return False
    df.loc[m, "password_hash"] = password_hash
    _save("users", df)
    return True

# ---------- Uploads ----------
def save_upload(uploader_file) -> str:
    if not uploader_file: return ""
    name = slugify(uploader_file.name, lowercase=False)
    path = os.path.join(UPLOAD_DIR, f"{int(datetime.now().timestamp())}-{name}")
    with open(path, "wb") as f:
        f.write(uploader_file.getbuffer())
    return path

# ---------- Products ----------
def _next_id(df, col="id"):
    if df.empty: return 1
    return int(df[col].astype(int).max()) + 1

def add_product(data: Dict[str, Any]) -> int:
    df = _load("products")
    pid = _next_id(df)
    now = datetime.now()
    slug = slugify(f"{data['name']}-{pid}")
    rec = {
        "id": pid,
        "name": data["name"],
        "brand": data.get("brand",""),
        "category": data.get("category","Other"),
        "condition": data.get("condition","Good"),
        "price": float(data["price"]),
        "stock": int(data.get("stock",0)),
        "warranty_months": int(data.get("warranty_months",3)),
        "image_path": data.get("image_path",""),
        "desc": data.get("desc",""),
        "slug": slug,
        "created_at": now,
        "updated_at": now,
        "created_by": data.get("created_by","system"),
    }
    _save("products", pd.concat([df, pd.DataFrame([rec])], ignore_index=True))
    return pid

def update_product(pid: int, **fields):
    df = _load("products")
    m = df["id"] == pid
    if not m.any(): return False
    for k, v in fields.items():
        if k in df.columns:
            df.loc[m, k] = v
    df.loc[m, "updated_at"] = datetime.now()
    _save("products", df)
    return True

def update_stock(product_id: int, change: int):
    df = _load("products")
    m = df["id"] == product_id
    if not m.any(): return False
    new_stock = max(0, int(df.loc[m, "stock"].iloc[0]) + change)
    df.loc[m, "stock"] = new_stock
    df.loc[m, "updated_at"] = datetime.now()
    _save("products", df)
    return True

def list_products(filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    df = _load("products")
    if filters:
        if filters.get("brand"):
            df = df[df["brand"].str.contains(filters["brand"], case=False, na=False)]
        if filters.get("q"):
            q = filters["q"].lower()
            df = df[df["name"].str.lower().str.contains(q) | df["desc"].str.lower().str.contains(q, na=False)]
        if filters.get("category") and filters["category"] != "All":
            df = df[df["category"] == filters["category"]]
        if filters.get("condition") and filters["condition"] != "All":
            df = df[df["condition"] == filters["condition"]]
    return df.sort_values("created_at", ascending=False)

# ---------- Orders & Payments ----------
def _next_pay_id() -> str:
    return f"PAY-{int(datetime.now().timestamp())}"

def create_order(email: str, items: Dict[int,int], method: str, details: str) -> str:
    if not items: raise ValueError("Cart is empty")
    dfp = _load("products")
    total = 0.0; rows = []
    for pid, qty in items.items():
        row = dfp[dfp["id"] == pid]
        if row.empty: continue
        price = float(row.iloc[0]["price"])
        total += price * qty
        rows.append({"product_id": int(pid), "qty": int(qty), "price": price})
    order_id = f"ORD-{int(datetime.now().timestamp())}"
    pay_id = _next_pay_id()
    pay_status = "Pending" if method == "COD" else "Success"

    p = _load("payments")
    p = pd.concat([p, pd.DataFrame([{
        "payment_id": pay_id, "order_id": order_id, "amount": total,
        "method": method, "details": details, "status": pay_status,
        "created_at": datetime.now()
    }])], ignore_index=True)
    _save("payments", p)

    o = _load("orders")
    o = pd.concat([o, pd.DataFrame([{
        "order_id": order_id, "email": email, "status":"Paid" if pay_status=="Success" else "Pending",
        "total": total, "payment_id": pay_id, "payment_method": method, "created_at": datetime.now()
    }])], ignore_index=True)
    _save("orders", o)

    oi = _load("order_items")
    for r in rows: r["order_id"] = order_id
    oi = pd.concat([oi, pd.DataFrame(rows)], ignore_index=True)
    _save("order_items", oi)

    for r in rows: update_stock(r["product_id"], -r["qty"])
    return order_id

def list_orders(email: Optional[str] = None) -> pd.DataFrame:
    o = _load("orders")
    if email: o = o[o["email"] == email]
    return o.sort_values("created_at", ascending=False)

def update_order_status(order_id: str, status: str):
    o = _load("orders")
    m = o["order_id"] == order_id
    if not m.any(): return False
    o.loc[m, "status"] = status
    _save("orders", o)
    return True

# ---------- Repairs ----------
def create_repair(email: str, device: str, issue: str) -> str:
    t = f"R-{int(datetime.now().timestamp())}"
    df = _load("repairs")
    df = pd.concat([df, pd.DataFrame([{
        "ticket": t, "email": email, "device": device, "issue": issue,
        "status": "In Progress", "created_at": datetime.now()
    }])], ignore_index=True)
    _save("repairs", df)
    return t

def list_repairs(email: Optional[str] = None) -> pd.DataFrame:
    df = _load("repairs")
    if email: df = df[df["email"] == email]
    return df.sort_values("created_at", ascending=False)

# ---------- Sell device ----------
def create_sell_request(email: str, device: str, brand: str, condition: str, exp_price: float, desc: str, image_path: str) -> str:
    df = _load("sell_requests")
    req_id = f"SR-{int(datetime.now().timestamp())}"
    df = pd.concat([df, pd.DataFrame([{
        "req_id": req_id, "email": email, "device": device, "brand": brand,
        "condition": condition, "exp_price": float(exp_price), "desc": desc,
        "image_path": image_path, "status": "Pending", "created_at": datetime.now()
    }])], ignore_index=True)
    _save("sell_requests", df)
    return req_id

def list_sell_requests(status: Optional[str] = None) -> pd.DataFrame:
    df = _load("sell_requests")
    if status and status != "All":
        df = df[df["status"] == status]
    return df.sort_values("created_at", ascending=False)

def update_sell_request(req_id: str, status: str):
    df = _load("sell_requests")
    m = df["req_id"] == req_id
    if not m.any(): return False
    df.loc[m, "status"] = status
    _save("sell_requests", df)
    return True

def convert_sell_request_to_product(req_id: str, price: float, stock:int=1, warranty:int=3, created_by:str="staff") -> int | None:
    df = _load("sell_requests")
    row = df[df["req_id"] == req_id]
    if row.empty: return None
    pid = add_product({
        "name": row.iloc[0]["device"],
        "brand": row.iloc[0]["brand"],
        "category": "Phone",
        "condition": row.iloc[0]["condition"],
        "price": price,
        "stock": stock,
        "warranty_months": warranty,
        "desc": row.iloc[0]["desc"],
        "image_path": row.iloc[0]["image_path"],
        "created_by": created_by,
    })
    update_sell_request(req_id, "Converted")
    return pid
