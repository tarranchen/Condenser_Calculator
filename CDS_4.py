import tkinter as tk
from tkinter import ttk, messagebox
import math

def clear_results():
    """清除所有輸出和備註欄位"""
    # 第二欄
    lbl_b_val.config(text="---")
    lbl_wd_val.config(text="---")
    lbl_na2_val.config(text="---")
    lbl_r_out_val.config(text="---")
    lbl_width_val.config(text="---")
    # 第三欄
    lbl_source_dist_val.config(text="---")
    lbl_zp_diam_val.config(text="---")
    lbl_cs_diam_val.config(text="---")
    lbl_source_size_val.config(text="---")
    lbl_bs_diam_val.config(text="---")

def calculate():
    """
    根據輸入的 a, L, Distance, NA1, r_in，使用數值方法反向計算 b, WD 及其他參數
    """
    try:
        # 1. 讀取輸入值
        a = float(entry_a.get())
        L = float(entry_L.get())
        distance = float(entry_distance.get())
        na1 = float(entry_na1_in.get())
        r_in = float(entry_r_in_in.get())

        # 2. 基礎防呆檢查
        if not (a > 0 and L > 0 and distance > 0):
            messagebox.showerror("參數錯誤", "橢圓半長軸 a, Condenser 長度 Length, 波帶片樣品距離 Distance 皆必須大於 0")
            clear_results()
            return
        if not (0 < na1 < 1):
            messagebox.showerror("參數錯誤", "數值孔徑 (NA1) 必須介於 0 和 1 之間")
            clear_results()
            return
        if not (0 < r_in < a):
            messagebox.showerror("參數錯誤", "入口半徑 (Entrance R) 必須大於 0 且小於半長軸 (a)")
            clear_results()
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
                clear_results()
                return
        except ValueError:
            messagebox.showerror("計算錯誤", "在邊界條件下計算出錯，請檢查輸入參數。")
            clear_results()
            return

        for _ in range(200): # 增加迭代次數以獲得更高精度
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
            clear_results()
            return

        r_out = b * math.sqrt(1 - ((c - wd)/a)**2)
        na2 = math.sin(math.atan(r_in / (wd + L)))
        width = (na1 - na2) / na1 if na1 != 0 else 0

        # 5. 計算備註欄參數
        source_dist_mm = 2 * c
        zp_diameter_um = 2 * na1 * distance * 1000
        cs_diameter_um = 2 * na2 * distance * 1000
        source_size_um = 2 * r_in * 1000
        bs_diameter_um = 2 * r_out * 1000

        # 6. 更新輸出介面
        # 第二欄
        lbl_b_val.config(text=f"{b:.8f}")
        lbl_wd_val.config(text=f"{wd:.2f}")
        lbl_na2_val.config(text=f"{na2:.10f}")
        lbl_r_out_val.config(text=f"{r_out:.8f}")
        lbl_width_val.config(text=f"{width:.8f}")

        # 第三欄
        lbl_source_dist_val.config(text=f"{source_dist_mm:.0f}")
        lbl_zp_diam_val.config(text=f"{zp_diameter_um:.0f}")
        lbl_cs_diam_val.config(text=f"{cs_diameter_um:.0f}")
        lbl_source_size_val.config(text=f"{source_size_um:.0f}")
        lbl_bs_diam_val.config(text=f"{bs_diameter_um:.0f}")

    except ValueError as e:
        if 'math domain error' in str(e):
            messagebox.showerror("計算錯誤", "參數組合無物理意義，無法對負數開根號。")
        else:
            messagebox.showerror("格式錯誤", "請輸入有效的數值 (不含文字或空白)")
        clear_results()
    except Exception as e:
        messagebox.showerror("未知錯誤", f"發生預期外的錯誤: {e}")
        clear_results()

# --- 建立主視窗 ---
root = tk.Tk()
root.title("Condenser Calculator")
root.geometry("960x350")
root.resizable(False, False)

style = ttk.Style()
style.theme_use('clam')

# --- 主容器 ---
main_container = ttk.Frame(root, padding=(10, 10))
main_container.pack(fill="both", expand=True)

# Get required height from an Entry widget to align rows.
# This ensures that rows in all columns have the same height, matching the
# taller Entry widgets in the first column.
temp_entry = ttk.Entry(main_container)
entry_row_height = temp_entry.winfo_reqheight()
temp_entry.destroy()

# --- 介面元件定義 (Widget Definitions) ---

# -- 第一欄：輸入 --
frame_input = ttk.LabelFrame(main_container, text="輸入", padding=(10, 10))
entry_a = ttk.Entry(frame_input, width=18)
entry_a.insert(0, "950")
entry_L = ttk.Entry(frame_input, width=18)
entry_L.insert(0, "120")
entry_distance = ttk.Entry(frame_input, width=18)
entry_distance.insert(0, "50")
entry_na1_in = ttk.Entry(frame_input, width=18)
entry_na1_in.insert(0, "0.003")
entry_r_in_in = ttk.Entry(frame_input, width=18)
entry_r_in_in.insert(0, "0.5")

# -- 第二欄：輸出 --
frame_output = ttk.LabelFrame(main_container, text="輸出", padding=(10, 10))
lbl_b_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))
lbl_wd_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))
lbl_na2_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))
lbl_r_out_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))
lbl_width_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))

# -- 第三欄：備註 --
frame_remarks = ttk.LabelFrame(main_container, text="備註", padding=(10, 10))
lbl_source_dist_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_zp_diam_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_cs_diam_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_source_size_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_bs_diam_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))

# --- 介面佈局 (Widget Layout) ---

# -- 第一欄：輸入 --
frame_input.grid(row=0, column=0, padx=10, pady=5, sticky="ns")
ttk.Label(frame_input, text="橢圓半長軸 a (mm):").grid(row=0, column=0, sticky="w", pady=5, padx=5)
entry_a.grid(row=0, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="外數值孔徑 NA1 (rad):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
entry_na1_in.grid(row=1, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="波帶片樣品距離 Distance (mm):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
entry_distance.grid(row=2, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="入口半徑 Entrance R (mm):").grid(row=3, column=0, sticky="w", pady=5, padx=5)
entry_r_in_in.grid(row=3, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="Condenser 長度 Length (mm):").grid(row=4, column=0, sticky="w", pady=5, padx=5)
entry_L.grid(row=4, column=1, pady=5, padx=5)

# -- 第二欄：輸出 --
frame_output.grid(row=0, column=1, padx=10, pady=5, sticky="ns")
for i in range(5):
    frame_output.rowconfigure(i, minsize=entry_row_height)

ttk.Label(frame_output, text="橢圓半短軸 b (mm):").grid(row=0, column=0, sticky="w", pady=5, padx=5)
lbl_b_val.grid(row=0, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_output, text="內數值孔徑 NA2 (rad):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
lbl_na2_val.grid(row=1, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_output, text="環寬 Width:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
lbl_width_val.grid(row=2, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_output, text="出口半徑 Exit R (mm):").grid(row=3, column=0, sticky="w", pady=5, padx=5)
lbl_r_out_val.grid(row=3, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_output, text="工作距離 WD (mm):").grid(row=4, column=0, sticky="w", pady=5, padx=5)
lbl_wd_val.grid(row=4, column=1, sticky="w", pady=6, padx=5)

# -- 第三欄：備註 --
frame_remarks.grid(row=0, column=2, padx=10, pady=5, sticky="ns")
for i in range(5):
    frame_remarks.rowconfigure(i, minsize=entry_row_height)

ttk.Label(frame_remarks, text="二次光源距樣品 (mm):").grid(row=0, column=0, sticky="w", pady=5, padx=5)
lbl_source_dist_val.grid(row=0, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="波帶片直徑 (μm):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
lbl_zp_diam_val.grid(row=1, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="波帶片 Central Stop 直徑 (μm):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
lbl_cs_diam_val.grid(row=2, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="光源大小 (μm):").grid(row=3, column=0, sticky="w", pady=5, padx=5)
lbl_source_size_val.grid(row=3, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="Beam Stop 直徑 (μm):").grid(row=4, column=0, sticky="w", pady=5, padx=5)
lbl_bs_diam_val.grid(row=4, column=1, sticky="w", pady=6, padx=5)

# --- 計算按鈕 ---
btn_calc = ttk.Button(main_container, text="Calculate", command=calculate)
btn_calc.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")

# 啟動時自動計算一次預設值
calculate()

# 啟動主迴圈
root.mainloop()