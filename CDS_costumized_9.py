import tkinter as tk
from tkinter import ttk, messagebox
import math
from tkinter import font as tkfont

def clear_results():
    """清除所有輸出和備註欄位"""
    # 第二欄
    lbl_b_val.config(text="---")
    lbl_L_val.config(text="---")
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
    lbl_source_size_val.config(text="---")

def calculate():
    """
    根據輸入的 a, NA1, NA2, WD，使用數值方法反向計算 b, L, Ent R, Ext R 及其他參數
    """
    try:
        # 1. 讀取輸入值
        a = float(entry_a.get())
        wd = float(entry_wd.get())
        na1_mrad = float(entry_na1.get())
        na2_mrad = float(entry_na2.get())
        zp_diameter_um = float(entry_zp_diameter.get())
        energy_ev = float(entry_energy.get())
        delta_r_nm = float(entry_delta_r.get())
        detector_dist_mm = float(entry_detector.get())

        na1 = na1_mrad / 1000.0
        na2 = na2_mrad / 1000.0

        # 1.5. 從新輸入計算求解器所需的參數
        if energy_ev <= 0:
            messagebox.showerror("參數錯誤", "光源能量 Energy 必須大於 0")
            clear_results()
            return
        lambda_nm = 1239.84244 / energy_ev

        if lambda_nm <= 0 or delta_r_nm <= 0 or zp_diameter_um <= 0:
            messagebox.showerror("參數錯誤", "波長、最外層厚度或 FZP 直徑不能為零或負數。")
            clear_results()
            return
        f_mm = (zp_diameter_um * delta_r_nm) / (lambda_nm * 1000.0)

        C = detector_dist_mm / f_mm
        if C < 4:
            messagebox.showerror("無解", f"無法計算放大倍率 M (D/f = {C:.2f} < 4)。\n偵測器距離(D)必須至少是焦距(f)的4倍。")
            clear_results()
            return

        # 根據物像距 p+q (detector_dist_mm) 與焦距 f (f_mm) 計算放大率 M
        # 由透鏡公式 1/f = 1/p + 1/q 和 M = q/p, 且 p+q = detector_dist_mm (D)
        # 可推導出二次方程式: M^2 + (2 - D/f)M + 1 = 0
        # 解 M 可得: M = ((D/f - 2) +/- sqrt((D/f)^2 - 4*(D/f))) / 2
        # 此處 C = D/f，且取正解對應放大影像。
        magnification = ((C - 2) + math.sqrt(C**2 - 4*C)) / 2
        if magnification == 0:
            messagebox.showerror("計算錯誤", "放大倍率 M 為 0，無法計算樣品距離。")
            clear_results()
            return
        distance = f_mm * (magnification + 1) / magnification

        # 2. 基礎防呆檢查 (a, wd, na1, na2)
        if not (a > 0 and wd > 0):
            messagebox.showerror("參數錯誤", "橢圓半長軸 a, 工作距離 WD 皆必須大於 0")
            clear_results()
            return
        if not (0 < na1 < 1 and 0 < na2 < 1):
            messagebox.showerror("參數錯誤", f"數值孔徑 NA1/NA2 ({na1:.4f}/{na2:.4f} rad) 無效，必須介於 0 和 1 之間。")
            clear_results()
            return
        if na1 <= na2:
            messagebox.showerror("參數錯誤", "外數值孔徑 NA1 必須大於內數值孔徑 NA2。")
            clear_results()
            return

        # 3. 根據輸入解出 r_out, b, c, L, r_in
        # --------------------------------------------------------------------
        # 3.1. 從 NA1 和 WD 解出 r_out
        K1 = math.tan(math.asin(na1))
        r_out = wd * K1

        # 3.2. 數值求解半短軸 b
        # 理論: 從橢圓方程式 x = a/b * sqrt(b^2-r^2) 和幾何關係 x_exit = c - wd
        # 可得: sqrt(a^2 - b^2) - a/b * sqrt(b^2 - r_out^2) - wd = 0
        # 我們使用二分法來尋找 b 的根。

        def error_func(b):
            if not (r_out <= b <= a): return float('inf')
            return math.sqrt(a**2 - b**2) - (a/b) * math.sqrt(b**2 - r_out**2) - wd

        # 使用二分法尋找 b
        b_low = r_out
        b_high = a

        # 檢查解是否存在於區間內
        try:
            err_low = error_func(b_low)
            err_high = error_func(b_high)
            if err_low * err_high >= 0:
                messagebox.showerror("無解", f"無法找到橢圓半短軸 b 的解。\n邊界誤差: f({b_low:.3f})={err_low:.3f}, f({b_high:.3f})={err_high:.3f}\n請檢查輸入參數 a, WD, NA1。")
                clear_results()
                return
        except ValueError:
            messagebox.showerror("計算錯誤", "在邊界條件下計算出錯，請檢查輸入參數。")
            clear_results()
            return

        for _ in range(200):
            b_mid = (b_low + b_high) / 2
            err_mid = error_func(b_mid)
            if err_mid == float('inf'):
                b_high = b_mid
                continue
            if err_low * err_mid < 0:
                b_high = b_mid
            else:
                b_low = b_mid
                err_low = err_mid

        b = (b_low + b_high) / 2
        c = math.sqrt(a**2 - b**2)

        # 3.3. 從 b, c, NA2, WD 解出 L 和 r_in
        # 理論: 聯立以下兩式解出 L 和 r_in
        # (A) r_in = (WD + L) * tan(asin(NA2))
        # (B) r_in = b * sqrt(1 - ((c - WD - L)/a)^2)
        # 可得 Y = WD + L 的二次方程式: (K2^2 + b^2/a^2)Y^2 - (2b^2c/a^2)Y - b^4/a^2 = 0
        K2 = math.tan(math.asin(na2))
        A_quad = K2**2 + b**2/a**2
        B_quad = -2*b**2*c/a**2
        C_quad = -b**4/a**2

        discriminant = B_quad**2 - 4*A_quad*C_quad
        if discriminant < 0:
            messagebox.showerror("無解", "無法計算 Condenser 長度 L (判別式為負)，請檢查 NA2。")
            clear_results()
            return

        Y = (-B_quad + math.sqrt(discriminant)) / (2*A_quad)
        L = Y - wd
        r_in = Y * K2

        # --------------------------------------------------------------------

        # 4. 檢查計算結果
        if L <= 0 or r_in <= 0:
            messagebox.showwarning("計算結果警告", f"計算出的 Condenser 長度 L ({L:.2f}) 或入口半徑 r_in ({r_in:.4f}) 為負值或零。")

        # 5. 計算備註欄參數
        width = (na1 - na2) / na1 if na1 != 0 else 0
        source_dist_mm = 2 * c
        bs_diameter_um = 2 * r_out * 1000
        pr_outer_diam_um = 2 * na1 * f_mm * 1000  # 修正: 計算直徑 (Diameter = 2 * Radius)
        pr_inner_diam_um = 2 * na2 * f_mm * 1000  # 修正: 計算直徑 (Diameter = 2 * Radius)
        N = (zp_diameter_um * 1000.0) / (4 * delta_r_nm)
        fzp_na_mrad = (lambda_nm / (2 * delta_r_nm)) * 1000.0
        source_size_um = r_in * 2000.0

        if na1 > 0:
            resolution_nm = lambda_nm / (2 * na1)
        else:
            resolution_nm = float('inf')

        # 6. 更新輸出介面
        # 第二欄
        lbl_b_val.config(text=f"{b:.5f}")
        lbl_L_val.config(text=f"{L:.3f}")
        lbl_rin_val.config(text=f"{r_in:.5f}")
        lbl_rout_val.config(text=f"{r_out:.5f}")

        # 第三欄
        lbl_source_dist_val.config(text=f"{source_dist_mm:.0f}")
        lbl_width_val.config(text=f"{width * 100:.2f} %")
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
        lbl_source_size_val.config(text=f"{source_size_um:.2f}")

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
entry_wd = ttk.Entry(frame_input, width=18)
entry_wd.insert(0, "180")
entry_na1 = ttk.Entry(frame_input, width=18)
entry_na1.insert(0, "2.62")
entry_na2 = ttk.Entry(frame_input, width=18)
entry_na2.insert(0, "2.43")
entry_zp_diameter = ttk.Entry(frame_input, width=18)
entry_zp_diameter.insert(0, "300")
entry_energy = ttk.Entry(frame_input, width=18)
entry_energy.insert(0, "8000")
entry_delta_r = ttk.Entry(frame_input, width=18)
entry_delta_r.insert(0, "25")
entry_detector = ttk.Entry(frame_input, width=18)
entry_detector.insert(0, "1900")

# -- 第二欄：輸出 --
frame_output = ttk.LabelFrame(main_container, text="輸出", padding=(10, 10))
lbl_b_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))
lbl_L_val = ttk.Label(frame_output, text="---", font=("Consolas", 10))
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
lbl_source_size_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))

# --- 介面佈局 (Widget Layout) ---

# -- 第一欄：輸入 --
frame_input.grid(row=0, column=0, padx=10, pady=5, sticky="ns")
ttk.Label(frame_input, text="橢圓半長軸 a (mm):", font=font_blue_bold, foreground="navy").grid(row=0, column=0, sticky="w", pady=5, padx=5)
entry_a.grid(row=0, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="工作距離 WD (mm):", font=font_purple_bold, foreground="purple").grid(row=1, column=0, sticky="w", pady=5, padx=5)
entry_wd.grid(row=1, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="外數值孔徑 NA1 (mrad):", font=font_green_bold, foreground="dark green").grid(row=2, column=0, sticky="w", pady=5, padx=5)
entry_na1.grid(row=2, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="內數值孔徑 NA2 (mrad):", font=font_green_bold, foreground="dark green").grid(row=3, column=0, sticky="w", pady=5, padx=5)
entry_na2.grid(row=3, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="FZP 直徑 (μm):").grid(row=4, column=0, sticky="w", pady=5, padx=5)
entry_zp_diameter.grid(row=4, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="X光能量 Energy (eV):").grid(row=5, column=0, sticky="w", pady=5, padx=5)
entry_energy.grid(row=5, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="FZP 最外層厚 delta r (nm):").grid(row=6, column=0, sticky="w", pady=5, padx=5)
entry_delta_r.grid(row=6, column=1, pady=5, padx=5)
ttk.Label(frame_input, text="樣品-偵測器總距 (p+q) (mm):").grid(row=7, column=0, sticky="w", pady=5, padx=5)
entry_detector.grid(row=7, column=1, pady=5, padx=5)

# -- 第二欄：輸出 --
frame_output.grid(row=0, column=1, padx=10, pady=5, sticky="ns")
for i in range(4):
    frame_output.rowconfigure(i, minsize=entry_row_height)

ttk.Label(frame_output, text="橢圓半短軸 b (mm):", font=font_blue_bold, foreground="navy").grid(row=0, column=0, sticky="w", pady=5, padx=5)
lbl_b_val.grid(row=0, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_output, text="Condenser 長度 L (mm):", font=font_purple_bold, foreground="purple").grid(row=1, column=0, sticky="w", pady=5, padx=5)
lbl_L_val.grid(row=1, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_output, text="入口半徑 Entrance R (mm):", font=font_brown_bold, foreground="saddle brown").grid(row=2, column=0, sticky="w", pady=5, padx=5)
lbl_rin_val.grid(row=2, column=1, sticky="w", pady=6, padx=5)
ttk.Label(frame_output, text="出口半徑 Exit R (mm):", font=font_brown_bold, foreground="saddle brown").grid(row=3, column=0, sticky="w", pady=5, padx=5)
lbl_rout_val.grid(row=3, column=1, sticky="w", pady=6, padx=5)

# -- 第三欄：備註 --
frame_remarks.grid(row=0, column=2, padx=10, pady=5, sticky="ns")
for i in range(13):
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
ttk.Label(frame_remarks, text="光源尺寸 Size (μm):").grid(row=12, column=0, sticky="w", pady=5, padx=5)
lbl_source_size_val.grid(row=12, column=1, sticky="w", pady=6, padx=5)

# --- 計算按鈕 ---
btn_calc = ttk.Button(main_container, text="Calculate", command=calculate)
btn_calc.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")

# 啟動時自動計算一次預設值
calculate()

# 啟動主迴圈
root.mainloop()