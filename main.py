import json
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

BASE = Path(__file__).parent
MENU = BASE / "menu.json"
SALES = BASE / "sales.json"
BILLS = BASE / "bills"

TAX = .05
DISCOUNT = .10
LIMIT = 1000

# Official Swiggy-style palette
ORANGE = "#FF5200"
SALT = "#FFEDE3"
WHITE = "#FFFFFF"
DARK = "#202020"
GRAY = "#686868"
BORDER = "#E8E8E8"
GREEN = "#27864B"


def load(file, default):
    try:
        with open(file, encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def save(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("DineFlow - Restaurant Billing System")
        self.geometry("1100x680")
        self.configure(bg=SALT)

        self.menu = load(MENU, [])
        self.sales = load(SALES, [])
        self.cart = {}

        self.search = tk.StringVar()
        self.category = tk.StringVar(value="All")
        self.customer = tk.StringVar(value="Guest")

        self.create_ui()
        self.show_menu()

    def create_ui(self):

        # HEADER
        header = tk.Frame(self, bg=ORANGE, height=72)
        header.pack(fill="x")

        tk.Label(
            header, text="DineFlow",
            font=("Arial", 23, "bold"),
            fg=WHITE, bg=ORANGE
        ).pack(side="left", padx=25)

        tk.Label(
            header, text="Restaurant Billing System",
            font=("Arial", 10),
            fg=WHITE, bg=ORANGE
        ).pack(side="left")

        tk.Button(
            header, text="Sales Dashboard",
            command=self.dashboard,
            bg=WHITE, fg=ORANGE,
            relief="flat", padx=15, pady=7
        ).pack(side="right", padx=20)

        main = tk.Frame(self, bg=SALT)
        main.pack(fill="both", expand=True, padx=20, pady=18)

        # MENU
        left = tk.Frame(main, bg=SALT)
        left.pack(side="left", fill="both", expand=True)

        top = tk.Frame(left, bg=SALT)
        top.pack(fill="x")

        tk.Label(
            top, text="Menu",
            font=("Arial", 20, "bold"),
            fg=DARK, bg=SALT
        ).pack(side="left")

        search = tk.Entry(
            top, textvariable=self.search,
            width=23, relief="solid", bd=1
        )
        search.pack(side="right", ipady=6)

        self.search.trace_add(
            "write", lambda *x: self.show_menu()
        )

        # CATEGORIES
        cats = ["All"] + sorted(
            set(x["category"] for x in self.menu)
        )

        bar = tk.Frame(left, bg=SALT)
        bar.pack(fill="x", pady=12)

        for cat in cats:
            tk.Button(
                bar, text=cat,
                command=lambda x=cat: self.set_category(x),
                bg=ORANGE if cat == "All" else WHITE,
                fg=WHITE if cat == "All" else DARK,
                relief="flat",
                padx=13, pady=6
            ).pack(side="left", padx=3)

        self.menu_frame = tk.Frame(left, bg=SALT)
        self.menu_frame.pack(fill="both", expand=True)

        # CART
        right = tk.Frame(
            main, bg=WHITE, width=330,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        right.pack(side="right", fill="y", padx=(20, 0))
        right.pack_propagate(False)

        tk.Label(
            right, text="Your Order",
            font=("Arial", 18, "bold"),
            fg=DARK, bg=WHITE
        ).pack(anchor="w", padx=18, pady=16)

        tk.Entry(
            right,
            textvariable=self.customer,
            relief="solid", bd=1
        ).pack(fill="x", padx=18)

        self.tree = ttk.Treeview(
            right,
            columns=("item", "qty", "amount"),
            show="headings",
            height=13
        )

        for c in ("item", "qty", "amount"):
            self.tree.heading(c, text=c.title())

        self.tree.column("item", width=145)
        self.tree.column("qty", width=45)
        self.tree.column("amount", width=85)

        self.tree.pack(fill="x", padx=18, pady=15)

        self.total = tk.Label(
            right,
            text="Subtotal: Rs.0.00\n"
                 "Discount: Rs.0.00\n"
                 "Tax: Rs.0.00",
            justify="right",
            font=("Arial", 10),
            fg=GRAY, bg=WHITE
        )
        self.total.pack(fill="x", padx=18)

        self.grand = tk.Label(
            right,
            text="TOTAL  Rs.0.00",
            font=("Arial", 18, "bold"),
            fg=ORANGE, bg=WHITE
        )
        self.grand.pack(anchor="e", padx=18, pady=12)

        tk.Button(
            right, text="REMOVE ITEM",
            command=self.remove,
            bg=SALT, fg=ORANGE,
            relief="flat", pady=7
        ).pack(fill="x", padx=18, pady=3)

        tk.Button(
            right, text="CHECKOUT",
            command=self.checkout,
            bg=ORANGE, fg=WHITE,
            font=("Arial", 11, "bold"),
            relief="flat", pady=11
        ).pack(fill="x", padx=18, pady=7)

    def set_category(self, cat):
        self.category.set(cat)
        self.show_menu()

    def show_menu(self):

        for x in self.menu_frame.winfo_children():
            x.destroy()

        q = self.search.get().lower()
        cat = self.category.get()

        # Different icon for different foods
        icons = {
            "pizza": "🍕",
            "burger": "🍔",
            "biryani": "🍛",
            "rice": "🍚",
            "chicken": "🍗",
            "noodles": "🍜",
            "pasta": "🍝",
            "sandwich": "🥪",
            "fries": "🍟",
            "ice cream": "🍦",
            "cake": "🍰",
            "dessert": "🍰",
            "coffee": "☕",
            "tea": "🍵",
            "juice": "🧃",
            "drink": "🥤",
            "cold drink": "🥤",
            "salad": "🥗",
            "soup": "🍲"
        }

        items = [
            x for x in self.menu
            if (cat == "All" or x["category"] == cat)
            and q in x["name"].lower()
        ]

        for i, item in enumerate(items):

            name = item["name"].lower()
            icon = next(
                (v for k, v in icons.items() if k in name),
                "🍽️"
            )

            card = tk.Frame(
                self.menu_frame,
                bg=WHITE,
                highlightbackground=BORDER,
                highlightthickness=1
            )

            card.grid(
                row=i // 2,
                column=i % 2,
                sticky="ew",
                padx=5, pady=5
            )

            tk.Label(
                card, text=icon,
                font=("Arial", 28),
                bg=WHITE
            ).pack(anchor="w", padx=14, pady=(10, 2))

            tk.Label(
                card, text=item["name"],
                font=("Arial", 12, "bold"),
                fg=DARK, bg=WHITE
            ).pack(anchor="w", padx=14)

            tk.Label(
                card,
                text=f"{item['category']}   •   Rs.{item['price']}",
                fg=GRAY, bg=WHITE
            ).pack(anchor="w", padx=14, pady=3)

            tk.Button(
                card, text="+ Add",
                command=lambda x=item: self.add(x),
                bg=ORANGE, fg=WHITE,
                relief="flat"
            ).pack(fill="x", padx=10, pady=9)

        self.menu_frame.columnconfigure(0, weight=1)
        self.menu_frame.columnconfigure(1, weight=1)

    def add(self, item):

        i = item["id"]

        if i not in self.cart:
            self.cart[i] = [item, 0]

        self.cart[i][1] += 1
        self.update()

    def remove(self):

        selected = self.tree.selection()

        if not selected:
            return

        i = int(selected[0])
        self.cart[i][1] -= 1

        if self.cart[i][1] <= 0:
            del self.cart[i]

        self.update()

    def update(self):

        for x in self.tree.get_children():
            self.tree.delete(x)

        subtotal = 0

        for i, data in self.cart.items():

            item, qty = data
            amount = item["price"] * qty
            subtotal += amount

            self.tree.insert(
                "", "end",
                iid=str(i),
                values=(
                    item["name"],
                    qty,
                    f"Rs.{amount}"
                )
            )

        discount = subtotal * DISCOUNT if subtotal >= LIMIT else 0
        tax = (subtotal - discount) * TAX
        total = subtotal - discount + tax

        self.total.config(
            text=f"Subtotal: Rs.{subtotal:.2f}\n"
                 f"Discount: Rs.{discount:.2f}\n"
                 f"Tax: Rs.{tax:.2f}"
        )

        self.grand.config(
            text=f"TOTAL  Rs.{total:.2f}"
        )

    def checkout(self):

        if not self.cart:
            messagebox.showwarning(
                "Empty Order",
                "Please add items first."
            )
            return

        subtotal = 0
        lines = []

        for item, qty in self.cart.values():

            amount = item["price"] * qty
            subtotal += amount

            lines.append(
                f"{item['name']} x {qty} = Rs.{amount}"
            )

        discount = subtotal * DISCOUNT if subtotal >= LIMIT else 0
        tax = (subtotal - discount) * TAX
        total = subtotal - discount + tax

        invoice = datetime.now().strftime(
            "INV-%Y%m%d-%H%M%S"
        )

        bill = [
            "DINEFLOW RESTAURANT",
            "-" * 35,
            f"Invoice: {invoice}",
            f"Customer: {self.customer.get()}",
            "-" * 35
        ] + lines + [
            "-" * 35,
            f"Subtotal: Rs.{subtotal:.2f}",
            f"Discount: Rs.{discount:.2f}",
            f"Tax: Rs.{tax:.2f}",
            f"TOTAL: Rs.{total:.2f}",
            "-" * 35,
            "Thank you for visiting!"
        ]

        BILLS.mkdir(exist_ok=True)

        with open(
            BILLS / f"{invoice}.txt",
            "w", encoding="utf-8"
        ) as f:
            f.write("\n".join(bill))

        self.sales.append({
            "invoice": invoice,
            "customer": self.customer.get(),
            "total": round(total, 2),
            "date": datetime.now().strftime(
                "%d-%m-%Y %H:%M"
            )
        })

        save(SALES, self.sales)

        messagebox.showinfo(
            "Payment Successful",
            f"Invoice: {invoice}\n\n"
            f"Total: Rs.{total:.2f}"
        )

        self.cart.clear()
        self.customer.set("Guest")
        self.update()

    def dashboard(self):

        sales = load(SALES, [])
        revenue = sum(x.get("total", 0) for x in sales)

        win = tk.Toplevel(self)
        win.title("DineFlow - Sales")
        win.geometry("650x450")
        win.configure(bg=SALT)

        tk.Label(
            win,
            text="Sales Dashboard",
            font=("Arial", 21, "bold"),
            fg=DARK, bg=SALT
        ).pack(pady=20)

        tk.Label(
            win,
            text=f"Orders: {len(sales)}     "
                 f"Revenue: Rs.{revenue:.2f}",
            font=("Arial", 13, "bold"),
            fg=ORANGE, bg=WHITE,
            padx=25, pady=18
        ).pack()

        table = ttk.Treeview(
            win,
            columns=("invoice", "customer", "total"),
            show="headings"
        )

        for c in ("invoice", "customer", "total"):
            table.heading(c, text=c.title())

        for x in reversed(sales):
            table.insert(
                "", "end",
                values=(
                    x["invoice"],
                    x["customer"],
                    f"Rs.{x['total']:.2f}"
                )
            )

        table.pack(
            fill="both",
            expand=True,
            padx=20, pady=20
        )


if __name__ == "__main__":
    App().mainloop()