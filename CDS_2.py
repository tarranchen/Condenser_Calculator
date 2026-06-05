import tkinter as tk
from tkinter import ttk, messagebox
import math

def calculate():
    """
    根據輸入的 a, L, NA1, r_in，使用數值方法反向計算 b, WD 及其他參數
    """
    try:
        # 1. 讀取輸入值
        a = float(entry_a.get())
        L = float(entry_L.get())
        na1 = float(entry_na1_in.get())
        r_in = float(entry_r_in_in.get())

        # 2. 基礎防呆檢查
        if not (a > 0 and L > 0):
            messagebox.showerror("參數錯誤", "半長軸 (a) 與長度 (Length) 必須大於 0")
            return
        if not (0 < na1 < 1):
            messagebox.showerror("參數錯誤", "數值孔徑 (NA1) 必須介於 0 和 1 之間")
            return
        if not (0 < r_in < a):
            messagebox.showerror("參數錯誤", "入口半徑 (Entrance R) 必須大於 0 且小於半長軸 (a)")
            return

        # 3. 數值求解半短軸 b
        # --------------------------------------------------------------------
        # 理論:
        # 我們有兩個獨立的方程式可以導出工作距離 WD，兩者都與未知的 b (或 c) 有關。
        # 我們需要找到一個 b 值，使得兩個方程式算出的 WD 相等。
        # 這可以轉換為一個尋根問題：Error(b) = WD1(b) - WD2(b) = 0
        # 我們使用二分法來尋找 b 的根。

        K = math.tan(math.asin(na1))

        def error_func(b):
            if a**2 < b**2: return float('inf') # b 不可大於 a
            c = math.sqrt(a**2 - b**2)

            # 從 NA1 推導的 WD1
            # (a^2*K^2+b^2)*WD^2 - 2*c*b^2*WD - b^4 = 0
            # 解二次方程式取正根
            wd1_discriminant = (2*c*b**2)**2 + 4*(a**2*K**2 + b**2)*b**4
            wd1 = (2*c*b**2 + math.sqrt(wd1_discriminant)) / (2 * (a**2*K**2 + b**2))

            # 從 r_in 推導的 WD2
            # (c - WD - L)^2 = a^2 * (1 - r_in^2 / b^2)
            if b**2 < r_in**2: return float('inf') # b 必須大於 r_in
            sqrt_term = a * math.sqrt(1 - r_in**2 / b**2)
            # x_ent = c - WD - L，通常 x_ent > 0
            wd2 = c - L - sqrt_term

            return wd1 - wd2

        # 使用二分法尋找 b
        b_low = r_in
        b_high = a
        
        # 檢查解是否存在於區間內
        try:
            err_low = error_func(b_low)
            err_high = error_func(b_high)
            if err_low * err_high >= 0:
                messagebox.showerror("無解", "無法找到滿足條件的解，請檢查輸入參數。")
                return
        except ValueError:
            messagebox.showerror("計算錯誤", "在邊界條件下計算出錯，請檢查輸入參數。")
            return

        for _ in range(100): # 迭代 100 次以獲得足夠精度
            b_mid = (b_low + b_high) / 2
            err_mid = error_func(b_mid)
            if err_mid == float('inf'): # 處理 b_mid 超出定義域的情況
                b_high = b_mid
                continue
            if err_low * err_mid < 0:
                b_high = b_mid
            else:
                b_low = b_mid
                err_low = err_mid
        
        b = (b_low + b_high) / 2
        # --------------------------------------------------------------------

        # 4. 使用找到的 b 計算所有輸出參數
        c = math.sqrt(a**2 - b**2)
        wd = c - L - a/b * math.sqrt(b**2 - r_in**2)

        if wd <= 0:
            messagebox.showerror("計算結果無效", "計算出的工作距離 (WD) 為負值或零，此組輸入參數無物理意義。")
            return

        r_out = b * math.sqrt(1 - ((c - wd)/a)**2)
        na2 = math.sin(math.atan(r_in / (wd + L)))
        width = (na1 - na2) / na1

        # 5. 更新輸出介面 (強制顯示 8 位小數)
        lbl_b_val.config(text=f"{b:.8f}")
        lbl_wd_val.config(text=f"{wd:.8f}")
        lbl_r_out_val.config(text=f"{r_out:.8f}")
        lbl_na2_val.config(text=f"{na2:.8f}")
        lbl_width_val.config(text=f"{width:.8f}")

    except ValueError:
        messagebox.showerror("格式錯誤", "請輸入有效的數值 (不含文字或空白)")
    except Exception as e:
        messagebox.showerror("未知錯誤", f"發生預期外的錯誤: {e}")

# --- 建立主視窗 ---
root = tk.Tk()
root.title("毛細管聚光鏡光學計算器 (逆向)")
root.geometry("420x520")
root.resizable(False, False)

style = ttk.Style()
style.theme_use('clam')

# --- 輸入區 ---
frame_input = ttk.LabelFrame(root, text="輸入參數 (Inputs)", padding=(10, 10))
frame_input.pack(padx=15, pady=10, fill="x")

ttk.Label(frame_input, text="半長軸 a:").grid(row=0, column=0, sticky="e", pady=5, padx=5)
entry_a = ttk.Entry(frame_input, width=15)
entry_a.insert(0, "1000")
entry_a.grid(row=0, column=1, pady=5)

ttk.Label(frame_input, text="毛細管長度 Length:").grid(row=1, column=0, sticky="e", pady=5, padx=5)
entry_L = ttk.Entry(frame_input, width=15)
entry_L.insert(0, "150")
entry_L.grid(row=1, column=1, pady=5)

ttk.Label(frame_input, text="外數值孔徑 NA1:").grid(row=2, column=0, sticky="e", pady=5, padx=5)
entry_na1_in = ttk.Entry(frame_input, width=15)
entry_na1_in.insert(0, "0.002031")
entry_na1_in.grid(row=2, column=1, pady=5)

ttk.Label(frame_input, text="入口半徑 Entrance R:").grid(row=3, column=0, sticky="e", pady=5, padx=5)
entry_r_in_in = ttk.Entry(frame_input, width=15)
entry_r_in_in.insert(0, "0.21899")
entry_r_in_in.grid(row=3, column=1, pady=5)

# --- 計算按鈕 ---
btn_calc = ttk.Button(root, text="執行計算 (Calculate)", command=calculate)
btn_calc.pack(pady=5)

# --- 輸出區 ---
frame_output = ttk.LabelFrame(root, text="輸出結果 (Outputs)", padding=(10, 10))
frame_output.pack(padx=15, pady=10, fill="x")

ttk.Label(frame_output, text="半短軸 b:").grid(row=0, column=0, sticky="e", pady=5, padx=5)
lbl_b_val = ttk.Label(frame_output, text="0.00000000", font=("Consolas", 10, "bold"), foreground="green")
lbl_b_val.grid(row=0, column=1, sticky="w", pady=5)

ttk.Label(frame_output, text="工作距離 WD:").grid(row=1, column=0, sticky="e", pady=5, padx=5)
lbl_wd_val = ttk.Label(frame_output, text="0.00000000", font=("Consolas", 10, "bold"), foreground="green")
lbl_wd_val.grid(row=1, column=1, sticky="w", pady=5)

ttk.Label(frame_output, text="出口半徑 Exit R:").grid(row=2, column=0, sticky="e", pady=5, padx=5)
lbl_r_out_val = ttk.Label(frame_output, text="0.00000000", font=("Consolas", 10))
lbl_r_out_val.grid(row=2, column=1, sticky="w", pady=5)

ttk.Label(frame_output, text="內數值孔徑 NA2:").grid(row=3, column=0, sticky="e", pady=5, padx=5)
lbl_na2_val = ttk.Label(frame_output, text="0.00000000", font=("Consolas", 10, "bold"), foreground="blue")
lbl_na2_val.grid(row=3, column=1, sticky="w", pady=5)

ttk.Label(frame_output, text="照明寬度 Width:").grid(row=4, column=0, sticky="e", pady=5, padx=5)
lbl_width_val = ttk.Label(frame_output, text="0.00000000", font=("Consolas", 10, "bold"), foreground="purple")
lbl_width_val.grid(row=4, column=1, sticky="w", pady=5)

# 啟動時自動計算一次預設值
calculate()

# 啟動主迴圈
root.mainloop()