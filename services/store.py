# services/store.py
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
        "image_path","desc","slug","featured","created_at","updated_at","created_by"
    ],
    "orders": ["order_id","email","status","total","payment_id","payment_method","created_at"],
    "order_items": ["order_id","product_id","qty","price"],
    "repairs": [
        "ticket","email","device_type","device","issue","image_path",
        "preferred_time","scheduled_time","status","contacted","staff_notes",
        "assigned_to","created_at","updated_at"
    ],
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

    # ---- migrations / column backfills
    if name == "users":
        if "password_hash" not in df.columns: df["password_hash"] = ""
        if "role" not in df.columns: df["role"] = "customer"
        if "created_at" not in df.columns: df["created_at"] = datetime.now()
        df = df[SCHEMAS["users"]]
        df.to_csv(_path("users"), index=False)

    if name == "products":
        for col, default in [
            ("featured", False),
            ("slug", ""),
            ("created_by", "system"),
            ("updated_at", datetime.now()),
            ("created_at", datetime.now()),
            ("image_path",""),
            ("warranty_months", 3),
        ]:
            if col not in df.columns:
                df[col] = default
        df = df[SCHEMAS["products"]]
        df.to_csv(_path("products"), index=False)

    if name == "repairs":
        defaults = {
            "device_type": "",
            "image_path": "",
            "preferred_time": "",
            "scheduled_time": "",
            "status": "In Progress",
            "contacted": False,
            "staff_notes": "",
            "assigned_to": "",
            "updated_at": datetime.now(),
        }
        for col, default in defaults.items():
            if col not in df.columns:
                df[col] = default
        df = df[SCHEMAS["repairs"]]
        df.to_csv(_path("repairs"), index=False)

    return df

def _save(name, df):
    df.to_csv(_path(name), index=False)

# ---------- Users ----------
def create_user(email: str, password_hash: str, role: str = "customer") -> bool:
    if not email: return False
    df = _load("users")
    if (df["email"] == email).any():
        return False
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
    return None if row.empty else row.iloc[0].to_dict()

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
        "featured": bool(data.get("featured", False)),
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

def list_featured(n: int = 6) -> pd.DataFrame:
    df = _load("products")
    if "featured" in df.columns:
        df = df[df["featured"] == True]  # noqa: E712
    return df.sort_values("updated_at", ascending=False).head(n)

def list_categories() -> list[str]:
    df = _load("products")
    if df.empty: return ["Phone","Laptop","Tablet","Accessory","Other"]
    cats = [c for c in df["category"].dropna().unique().tolist() if c]
    base = ["Phone","Laptop","Tablet","Accessory","Other"]
    out = [c for c in base if c in cats] + [c for c in cats if c not in base]
    return out or base

# ---------- Orders & Payments (with approval workflow) ----------
def _next_pay_id() -> str:
    return f"PAY-{int(datetime.now().timestamp())}"

def create_order(email: str, items: Dict[int,int], method: str, details: str) -> str:
    """
    Creates an order with status 'Pending Approval'.
    Payment record:
      - 'Pending' for COD
      - 'Success' for non-COD (simulated)
    Stock is NOT reduced until approval.
    """
    if not items:
        raise ValueError("Cart is empty")

    dfp = _load("products")
    total = 0.0
    rows = []
    for pid, qty in items.items():
        row = dfp[dfp["id"] == pid]
        if row.empty:
            continue
        price = float(row.iloc[0]["price"])
        total += price * qty
        rows.append({"product_id": int(pid), "qty": int(qty), "price": price})

    order_id = f"ORD-{int(datetime.now().timestamp())}"
    pay_id = _next_pay_id()
    pay_status = "Pending" if method == "COD" else "Success"

    # record payment intent
    p = _load("payments")
    p = pd.concat([p, pd.DataFrame([{
        "payment_id": pay_id, "order_id": order_id, "amount": total,
        "method": method, "details": details, "status": pay_status,
        "created_at": datetime.now()
    }])], ignore_index=True)
    _save("payments", p)

    # create order as Pending Approval (staff gate)
    o = _load("orders")
    o = pd.concat([o, pd.DataFrame([{
        "order_id": order_id, "email": email,
        "status": "Pending Approval",
        "total": total, "payment_id": pay_id,
        "payment_method": method, "created_at": datetime.now()
    }])], ignore_index=True)
    _save("orders", o)

    # store line items (do NOT decrement stock yet)
    oi = _load("order_items")
    for r in rows:
        r["order_id"] = order_id
    oi = pd.concat([oi, pd.DataFrame(rows)], ignore_index=True)
    _save("order_items", oi)

    return order_id

def list_orders(email: Optional[str] = None, for_customer: bool = False) -> pd.DataFrame:
    """
    Staff view (for_customer=False): ALL orders (optional filter by email).
    Customer view (for_customer=True): ONLY Approved orders for that email.
    """
    o = _load("orders")
    if for_customer:
        if not email:
            return o.iloc[0:0]
        o = o[(o["email"] == email) & (o["status"] == "Approved")]
    else:
        if email:
            o = o[o["email"] == email]
    return o.sort_values("created_at", ascending=False)

def update_order_status(order_id: str, status: str):
    o = _load("orders")
    m = o["order_id"] == order_id
    if not m.any(): return False
    o.loc[m, "status"] = status
    _save("orders", o)
    return True

def approve_order(order_id: str) -> bool:
    """
    Approving:
      - sets order.status = 'Approved'
      - decrements stock per order_items
    """
    if not update_order_status(order_id, "Approved"):
        return False
    oi = _load("order_items")
    items = oi[oi["order_id"] == order_id]
    for _, r in items.iterrows():
        update_stock(int(r["product_id"]), -int(r["qty"]))
    return True

def decline_order(order_id: str) -> bool:
    """
    Declining:
      - sets order.status = 'Declined'
      - leaves stock unchanged
    """
    return update_order_status(order_id, "Declined")

# ---------- Repairs (rich workflow) ----------
def create_repair(email: str, device_type: str, device: str, issue: str,
                  preferred_time: str, image_path: str) -> str:
    """
    Customer creates a repair ticket with optional photo and preferred visit time.
    """
    t = f"R-{int(datetime.now().timestamp())}"
    now = datetime.now()
    df = _load("repairs")
    df = pd.concat([df, pd.DataFrame([{
        "ticket": t,
        "email": email,
        "device_type": device_type,
        "device": device,
        "issue": issue,
        "image_path": image_path or "",
        "preferred_time": preferred_time,
        "scheduled_time": "",
        "status": "In Progress",
        "contacted": False,
        "staff_notes": "",
        "assigned_to": "",
        "created_at": now,
        "updated_at": now,
    }])], ignore_index=True)
    _save("repairs", df)
    return t

def list_repairs(email: Optional[str] = None, all_for_staff: bool = False) -> pd.DataFrame:
    """
    Customer view: only own tickets.
    Staff view: all tickets.
    """
    df = _load("repairs")
    if not all_for_staff and email:
        df = df[df["email"] == email]
    return df.sort_values("created_at", ascending=False)

def update_repair_status(ticket: str, status: str) -> bool:
    df = _load("repairs")
    m = df["ticket"] == ticket
    if not m.any(): return False
    df.loc[m, "status"] = status
    df.loc[m, "updated_at"] = datetime.now()
    _save("repairs", df)
    return True

def schedule_repair_time(ticket: str, scheduled_time: str, staff_notes: str = "") -> bool:
    df = _load("repairs")
    m = df["ticket"] == ticket
    if not m.any(): return False
    df.loc[m, "scheduled_time"] = scheduled_time
    if staff_notes:
        prev = df.loc[m, "staff_notes"].astype(str).fillna("")
        df.loc[m, "staff_notes"] = (prev + ("\n" if prev.iloc[0] else "") + staff_notes).str.strip()
    df.loc[m, "updated_at"] = datetime.now()
    _save("repairs", df)
    return True

def set_repair_contacted(ticket: str, contacted: bool) -> bool:
    df = _load("repairs")
    m = df["ticket"] == ticket
    if not m.any(): return False
    df.loc[m, "contacted"] = bool(contacted)
    df.loc[m, "updated_at"] = datetime.now()
    _save("repairs", df)
    return True

def assign_repair(ticket: str, staff_email: str) -> bool:
    df = _load("repairs")
    m = df["ticket"] == ticket
    if not m.any(): return False
    df.loc[m, "assigned_to"] = staff_email
    df.loc[m, "updated_at"] = datetime.now()
    _save("repairs", df)
    return True

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
        "featured": False,
    })
    update_sell_request(req_id, "Converted")
    return pid
