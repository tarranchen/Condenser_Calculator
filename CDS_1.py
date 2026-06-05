import tkinter as tk
from tkinter import ttk, messagebox
import math

def calculate():
    try:
        # 1. 讀取輸入值
        a = float(entry_a.get())
        b = float(entry_b.get())
        L = float(entry_L.get())
        WD = float(entry_WD.get())

        # 基礎防呆檢查
        if a <= b:
            messagebox.showerror("參數錯誤", "半長軸 (a) 必須大於半短軸 (b)")
            return
        if WD <= 0 or L <= 0:
            messagebox.showerror("參數錯誤", "工作距離 (WD) 與長度 (Length) 必須大於 0")
            return

        # 2. 幾何參數計算
        c = math.sqrt(a**2 - b**2)
        x_exit = c - WD
        x_ent = c - WD - L

        # 檢查座標是否超出橢球範圍
        if abs(x_exit) > a or abs(x_ent) > a:
            messagebox.showerror("範圍錯誤", "毛細管座標超出橢球範圍，請檢查長度或工作距離設定。")
            return

        # 3. 半徑運算
        r_out = b * math.sqrt(1 - (x_exit/a)**2)
        r_in = b * math.sqrt(1 - (x_ent/a)**2)

        # 4. 數值孔徑運算 (NA1 = NA_out, NA2 = NA_in)
        na1 = math.sin(math.atan(r_out / WD))
        na2 = math.sin(math.atan(r_in / (WD + L)))

        # 5. 空心錐寬度運算
        width = (na1 - na2) / na1

        # 6. 更新輸出介面 (強制顯示 8 位小數)
        lbl_na1_val.config(text=f"{na1:.8f}")
        lbl_na2_val.config(text=f"{na2:.8f}")
        lbl_width_val.config(text=f"{width:.8f}")
        lbl_r_in_val.config(text=f"{r_in:.8f}")
        lbl_r_out_val.config(text=f"{r_out:.8f}")

    except ValueError:
        messagebox.showerror("格式錯誤", "請輸入有效的數值 (不含文字或空白)")

# --- 建立主視窗 ---
root = tk.Tk()
root.title("毛細管聚光鏡光學計算器")
root.geometry("380x500")
root.resizable(False, False)

# 套用現代化外觀
style = ttk.Style()
style.theme_use('clam')

# --- 輸入區 (Input Frame) ---
frame_input = ttk.LabelFrame(root, text="輸入參數 (Inputs)", padding=(10, 10))
frame_input.pack(padx=15, pady=10, fill="x")

# 輸入框排列設計
ttk.Label(frame_input, text="半長軸 a:").grid(row=0, column=0, sticky="e", pady=5, padx=5)
entry_a = ttk.Entry(frame_input, width=15)
entry_a.insert(0, "1000")
entry_a.grid(row=0, column=1, pady=5)

ttk.Label(frame_input, text="半短軸 b:").grid(row=1, column=0, sticky="e", pady=5, padx=5)
entry_b = ttk.Entry(frame_input, width=15)
entry_b.insert(0, "0.3572")
entry_b.grid(row=1, column=1, pady=5)

ttk.Label(frame_input, text="工作距離 WD:").grid(row=2, column=0, sticky="e", pady=5, padx=5)
entry_WD = ttk.Entry(frame_input, width=15)
entry_WD.insert(0, "60")
entry_WD.grid(row=2, column=1, pady=5)

ttk.Label(frame_input, text="毛細管長度 Length:").grid(row=3, column=0, sticky="e", pady=5, padx=5)
entry_L = ttk.Entry(frame_input, width=15)
entry_L.insert(0, "150")
entry_L.grid(row=3, column=1, pady=5)

# --- 計算按鈕 ---
btn_calc = ttk.Button(root, text="執行計算 (Calculate)", command=calculate)
btn_calc.pack(pady=5)

# --- 輸出區 (Output Frame) ---
frame_output = ttk.LabelFrame(root, text="輸出結果 (Outputs)", padding=(10, 10))
frame_output.pack(padx=15, pady=10, fill="x")

# 輸出標籤排列設計
ttk.Label(frame_output, text="外數值孔徑 (NA1):").grid(row=0, column=0, sticky="e", pady=5, padx=5)
lbl_na1_val = ttk.Label(frame_output, text="0.00000000", font=("Consolas", 10, "bold"), foreground="blue")
lbl_na1_val.grid(row=0, column=1, sticky="w", pady=5)

ttk.Label(frame_output, text="內數值孔徑 (NA2):").grid(row=1, column=0, sticky="e", pady=5, padx=5)
lbl_na2_val = ttk.Label(frame_output, text="0.00000000", font=("Consolas", 10, "bold"), foreground="blue")
lbl_na2_val.grid(row=1, column=1, sticky="w", pady=5)

ttk.Label(frame_output, text="照明寬度 (Width):").grid(row=2, column=0, sticky="e", pady=5, padx=5)
lbl_width_val = ttk.Label(frame_output, text="0.00000000", font=("Consolas", 10, "bold"), foreground="purple")
lbl_width_val.grid(row=2, column=1, sticky="w", pady=5)

ttk.Label(frame_output, text="入口半徑 (Entrance R):").grid(row=3, column=0, sticky="e", pady=5, padx=5)
lbl_r_in_val = ttk.Label(frame_output, text="0.00000000", font=("Consolas", 10))
lbl_r_in_val.grid(row=3, column=1, sticky="w", pady=5)

ttk.Label(frame_output, text="出口半徑 (Exit R):").grid(row=4, column=0, sticky="e", pady=5, padx=5)
lbl_r_out_val = ttk.Label(frame_output, text="0.00000000", font=("Consolas", 10))
lbl_r_out_val.grid(row=4, column=1, sticky="w", pady=5)

# 啟動時自動計算一次預設值
calculate()

# 啟動主迴圈
root.mainloop()