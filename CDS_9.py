import tkinter as tk
from tkinter import ttk, messagebox
import math
from tkinter import font as tkfont

# --- 物理常數與轉換因子 ---
EV_NM_CONVERSION_FACTOR = 1239.84244  # E(eV) * lambda(nm)
UM_PER_MM = 1000.0


def clear_results():
    """清除所有輸出和備註欄位"""
    # 第二欄
    lbl_b_val.config(text="---")
    lbl_wd_val.config(text="---")
    lbl_na1_val.config(text="---")
    lbl_na2_val.config(text="---")
    lbl_rin_val.config(text="---")
    lbl_rout_val.config(text="---")
    # 第三欄
    lbl_source_dist_val.config(text="---")
    lbl_width_val.config(text="---")
    lbl_bs_diam_val.config(text="---")
    lbl_lambda_val.config(text="---")
    lbl_f_val.config(text="---")
    lbl_N_val.config(text="---")
    lbl_fzp_na_val.config(text="---")
    lbl_distance_val.config(text="---")
    lbl_resolution_val.config(text="---")
    lbl_magnification_val.config(text="---")
    lbl_pr_outer_diam_val.config(text="---")
    lbl_pr_inner_diam_val.config(text="---")

def _solve_for_b(a, r_in, na1, L):
    """
    使用二分法求解橢圓半短軸 b。
    尋找一個 b 值，使得由 NA1 推導出的 WD 和由 r_in 推導出的 WD 相等。
    """
    K = math.tan(math.asin(na1))

    def error_func(b):
        """計算兩個 WD 推導方式之間的誤差。"""
        if not (r_in <= b <= a): return float('inf')
        try:
            c = math.sqrt(a**2 - b**2)

            # 從 NA1 推導的 WD1: (a^2*K^2+b^2)*WD^2 - 2*c*b^2*WD - b^4 = 0
            wd1_discriminant = (2*c*b**2)**2 + 4*(a**2*K**2 + b**2)*b**4
            wd1 = (2*c*b**2 + math.sqrt(wd1_discriminant)) / (2 * (a**2*K**2 + b**2))

            # 從 r_in 推導的 WD2: (c - WD - L)^2 = a^2 * (1 - r_in^2 / b^2)
            sqrt_term = a * math.sqrt(1 - r_in**2 / b**2)
            wd2 = c - L - sqrt_term

            return wd1 - wd2
        except ValueError: # 捕獲 math domain error
            return float('inf')

    b_low, b_high = r_in, a
    
    err_low = error_func(b_low)
    err_high = error_func(b_high)

    # 如果在邊界上無解或解不跨越零點，則拋出錯誤
    if err_low == float('inf') or err_high == float('inf') or err_low * err_high >= 0:
        raise ValueError("無法在邊界條件下找到解。")

    for _ in range(200): # 迭代求解
        b_mid = (b_low + b_high) / 2
        if b_mid == b_low or b_mid == b_high: # 達到浮點數精度極限
            break
        
        err_mid = error_func(b_mid)

        if err_mid == float('inf'): # 處理 b_mid 超出定義域的情況
            b_high = b_mid
            continue

        if err_low * err_mid < 0:
            b_high = b_mid
        else:
            b_low = b_mid
            err_low = err_mid
    
    return (b_low + b_high) / 2

def calculate():
    """
    根據輸入的 a, L, Distance, ZP diam, Source size，使用數值方法反向計算 b, WD 及其他參數
    """
    try:
        # 1. 讀取輸入值
        a = float(entry_a.get())
        L = float(entry_L.get())
        zp_diameter_um = float(entry_zp_diameter.get())
        source_size_um = float(entry_source_size.get())
        energy_ev = float(entry_energy.get())
        delta_r_nm = float(entry_delta_r.get())
        detector_dist_mm = float(entry_detector.get())

        # 1.5. 從新輸入計算求解器所需的參數
        if energy_ev <= 0:
            messagebox.showerror("參數錯誤", "光源能量 Energy 必須大於 0")
            clear_results()
            return
        lambda_nm = EV_NM_CONVERSION_FACTOR / energy_ev

        if lambda_nm <= 0 or delta_r_nm <= 0 or zp_diameter_um <= 0:
            messagebox.showerror("參數錯誤", "波長、最外層厚度或 FZP 直徑不能為零或負數。")
            clear_results()
            return
        f_mm = (zp_diameter_um * delta_r_nm) / (lambda_nm * UM_PER_MM)

        C = detector_dist_mm / f_mm
        if C < 4:
            messagebox.showerror("無解", f"無法計算放大倍率 M (D/f = {C:.2f} < 4)。\n偵測器距離(D)必須至少是焦距(f)的4倍。")
            clear_results()
            return

        magnification = ((C - 2) + math.sqrt(C**2 - 4*C)) / 2
        if magnification == 0:
            messagebox.showerror("計算錯誤", "放大倍率 M 為 0，無法計算樣品距離。")
            clear_results()
            return
        distance = f_mm * (magnification + 1) / magnification

        # r_in in mm from source_size_um in um
        r_in = source_size_um / (2.0 * UM_PER_MM)
        # na1 in rad from zp_diameter_um in um and distance in mm
        na1 = zp_diameter_um / (2.0 * distance * UM_PER_MM)

        # 2. 基礎防呆檢查
        if not (a > 0 and L > 0 and detector_dist_mm > 0):
            messagebox.showerror("參數錯誤", "橢圓半長軸 a, Condenser 長度 Length, 偵測器樣品距離 Detector 皆必須大於 0")
            clear_results()
            return
        if not (0 < na1 < 1): # 驗證計算出的 na1
            messagebox.showerror("參數錯誤", f"計算出的數值孔徑 NA1 ({na1:.4f} rad) 無效，必須介於 0 和 1 之間。請檢查波帶片直徑和距離。")
            clear_results()
            return
        if not (0 < r_in < a): # 驗證計算出的 r_in
            messagebox.showerror("參數錯誤", f"計算出的入口半徑 R ({r_in:.4f} mm) 無效，必須大於 0 且小於半長軸 a。請檢查光源大小。")
            clear_results()
            return

        # 3. 數值求解半短軸 b
        try:
            b = _solve_for_b(a, r_in, na1, L)
        except ValueError as e:
            messagebox.showerror("無解", f"無法找到滿足條件的解: {e}\n請檢查輸入參數。")
            clear_results()
            return
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
        bs_diameter_um = 2 * r_out * UM_PER_MM
        pr_outer_diam_um = 2 * na1 * f_mm * UM_PER_MM
        pr_inner_diam_um = 2 * na2 * f_mm * UM_PER_MM
        N = (zp_diameter_um * UM_PER_MM) / (4 * delta_r_nm)
        fzp_na_mrad = (lambda_nm / (2 * delta_r_nm)) * 1000.0 # 單位轉換為 mrad，保留 1000

        if na1 > 0:
            resolution_nm = lambda_nm / (2 * na1)
        else:
            resolution_nm = float('inf')

        # 6. 更新輸出介面
        # 第二欄
        lbl_b_val.config(text=f"{b:.5f}")
        lbl_na1_val.config(text=f"{na1 * 1000:.4f}")
        lbl_na2_val.config(text=f"{na2 * 1000:.4f}")
        lbl_rin_val.config(text=f"{r_in:.5f}")
        lbl_rout_val.config(text=f"{r_out:.5f}")
        lbl_wd_val.config(text=f"{wd:.2f}")

        # 第三欄
        lbl_source_dist_val.config(text=f"{source_dist_mm:.0f}")
        lbl_width_val.config(text=f"{width * 100:.1f} %")
        lbl_bs_diam_val.config(text=f"{bs_diameter_um:.0f}")
        lbl_lambda_val.config(text=f"{lambda_nm:.5f}")
        lbl_f_val.config(text=f"{f_mm:.3f}")
        lbl_distance_val.config(text=f"{distance:.3f}")
        lbl_N_val.config(text=f"{N:.0f}")
        lbl_fzp_na_val.config(text=f"{fzp_na_mrad:.4f}")
        lbl_resolution_val.config(text=f"{resolution_nm:.3f}")
        lbl_magnification_val.config(text=f"{magnification:.3f}")
        lbl_pr_outer_diam_val.config(text=f"{pr_outer_diam_um:.2f}")
        lbl_pr_inner_diam_val.config(text=f"{pr_inner_diam_um:.2f}")

    except ValueError as e:
        if 'math domain error' in str(e).lower():
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
root.geometry("1200x650")
root.resizable(False, False)

style = ttk.Style()
style.theme_use('clam')

# --- Create custom fonts for highlighting ---
default_font = tkfont.nametofont("TkDefaultFont")

font_blue_bold = default_font.copy()
font_blue_bold.configure(weight="bold")

font_purple_bold = default_font.copy()
font_purple_bold.configure(weight="bold")

font_green_bold = default_font.copy()
font_green_bold.configure(weight="bold")

font_brown_bold = default_font.copy()
font_brown_bold.configure(weight="bold")

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
entry_zp_diameter = ttk.Entry(frame_input, width=18)
entry_zp_diameter.insert(0, "300")
entry_source_size = ttk.Entry(frame_input, width=18)
entry_source_size.insert(0, "989.395")
entry_energy = ttk.Entry(frame_input, width=18)
entry_energy.insert(0, "8000")
entry_delta_r = ttk.Entry(frame_input, width=18)
entry_delta_r.insert(0, "25")
entry_detector = ttk.Entry(frame_input, width=18)
entry_detector.insert(0, "1900")

# -- 第二欄：輸出 --
frame_output = ttk.LabelFrame(main_container, text="輸出", padding=(10, 10))
lbl_b_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))
lbl_wd_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))
lbl_na1_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))
lbl_na2_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))
lbl_rin_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))
lbl_rout_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))

# -- 第三欄：備註 --
frame_remarks = ttk.LabelFrame(main_container, text="備註", padding=(10, 10))
lbl_source_dist_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_width_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_bs_diam_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_lambda_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_f_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_distance_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_N_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_fzp_na_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_resolution_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_magnification_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_pr_outer_diam_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))
lbl_pr_inner_diam_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))

# --- 介面佈局 (Widget Layout) ---

# -- 第一欄：輸入 --
frame_input.grid(row=0, column=0, padx=10, pady=5, sticky="ns")
ttk.Label(frame_input, text="橢圓半長軸 a (mm):", font=font_blue_bold, foreground="navy").grid(row=0, column=0, sticky="w", pady=5, padx=5)
entry_a.grid(row=0, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="Condenser 長度 Length (mm):", font=font_purple_bold, foreground="purple").grid(row=1, column=0, sticky="w", pady=5, padx=5)
entry_L.grid(row=1, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="光源尺寸 Size (μm):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
entry_source_size.grid(row=2, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="FZP 直徑 (μm):").grid(row=3, column=0, sticky="w", pady=5, padx=5)
entry_zp_diameter.grid(row=3, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="X光能量 Energy (eV):").grid(row=4, column=0, sticky="w", pady=5, padx=5)
entry_energy.grid(row=4, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="FZP 最外層厚 delta r (nm):").grid(row=5, column=0, sticky="w", pady=5, padx=5)
entry_delta_r.grid(row=5, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="樣品-偵測器總距 (p+q) (mm):").grid(row=6, column=0, sticky="w", pady=5, padx=5)
entry_detector.grid(row=6, column=1, pady=5, padx=5)

# -- 第二欄：輸出 --
frame_output.grid(row=0, column=1, padx=10, pady=5, sticky="ns")
for i in range(11):
    frame_output.rowconfigure(i, minsize=entry_row_height)

ttk.Label(frame_output, text="橢圓半短軸 b (mm):", font=font_blue_bold, foreground="navy").grid(row=0, column=0, sticky="w", pady=5, padx=5)
lbl_b_val.grid(row=0, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_output, text="工作距離 WD (mm):", font=font_purple_bold, foreground="purple").grid(row=1, column=0, sticky="w", pady=5, padx=5)
lbl_wd_val.grid(row=1, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_output, text="外數值孔徑 NA1 (mrad):", font=font_green_bold, foreground="dark green").grid(row=2, column=0, sticky="w", pady=5, padx=5)
lbl_na1_val.grid(row=2, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_output, text="內數值孔徑 NA2 (mrad):", font=font_green_bold, foreground="dark green").grid(row=3, column=0, sticky="w", pady=5, padx=5)
lbl_na2_val.grid(row=3, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_output, text="入口半徑 Entrance R (mm):", font=font_brown_bold, foreground="saddle brown").grid(row=4, column=0, sticky="w", pady=5, padx=5)
lbl_rin_val.grid(row=4, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_output, text="出口半徑 Exit R (mm):", font=font_brown_bold, foreground="saddle brown").grid(row=5, column=0, sticky="w", pady=5, padx=5)
lbl_rout_val.grid(row=5, column=1, sticky="w", pady=6, padx=5)

# -- 第三欄：備註 --
frame_remarks.grid(row=0, column=2, padx=10, pady=5, sticky="ns")
for i in range(12):
    frame_remarks.rowconfigure(i, minsize=entry_row_height)

ttk.Label(frame_remarks, text="二次光源距樣品 2c (mm):").grid(row=0, column=0, sticky="w", pady=5, padx=5)
lbl_source_dist_val.grid(row=0, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="照明環寬 Width (%):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
lbl_width_val.grid(row=1, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="Beam Stop 直徑 (μm):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
lbl_bs_diam_val.grid(row=2, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="X光波長 lambda (nm):").grid(row=3, column=0, sticky="w", pady=5, padx=5)
lbl_lambda_val.grid(row=3, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="FZP 焦距 f (mm):").grid(row=4, column=0, sticky="w", pady=5, padx=5)
lbl_f_val.grid(row=4, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="FZP 樣品距離 Distance (mm):").grid(row=5, column=0, sticky="w", pady=5, padx=5)
lbl_distance_val.grid(row=5, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="理論解析度 Resolution (nm):").grid(row=6, column=0, sticky="w", pady=5, padx=5)
lbl_resolution_val.grid(row=6, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="FZP 總環數 N:").grid(row=7, column=0, sticky="w", pady=5, padx=5)
lbl_N_val.grid(row=7, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="FZP NA (mrad):").grid(row=8, column=0, sticky="w", pady=5, padx=5)
lbl_fzp_na_val.grid(row=8, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="放大倍率 M:").grid(row=9, column=0, sticky="w", pady=5, padx=5)
lbl_magnification_val.grid(row=9, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="Phase Ring 外徑 (µm):").grid(row=10, column=0, sticky="w", pady=5, padx=5)
lbl_pr_outer_diam_val.grid(row=10, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_remarks, text="Phase Ring 內徑 (µm):").grid(row=11, column=0, sticky="w", pady=5, padx=5)
lbl_pr_inner_diam_val.grid(row=11, column=1, sticky="w", pady=6, padx=5)

# --- 計算按鈕 ---
btn_calc = ttk.Button(main_container, text="Calculate", command=calculate)
btn_calc.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")

# 啟動時自動計算一次預設值
calculate()

# 啟動主迴圈
root.mainloop()