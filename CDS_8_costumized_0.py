import tkinter as tk
from tkinter import ttk, messagebox
import math
from tkinter import font as tkfont

def clear_results():
    """清除所有輸出和備註欄位"""
    # 第二欄
    # 第三欄
    lbl_source_dist_val.config(text="---")
    lbl_width_val.config(text="---")
    lbl_bs_diam_val.config(text="---")
    lbl_f_val.config(text="---")
    lbl_distance_val.config(text="---")
    lbl_resolution_val.config(text="---")
    lbl_magnification_val.config(text="---")
    lbl_pr_outer_diam_val.config(text="---")
    lbl_pr_inner_diam_val.config(text="---")
    lbl_source_size_val.config(text="---")
    lbl_zp_diameter_val.config(text="---")
    
def calculate():
    """
    根據輸入的 a, L, Distance, ZP diam, Source size，使用數值方法反向計算 b, WD 及其他參數
    """
    try:
        # 1. 讀取輸入值
        # --- 1. Read all inputs from UI ---
        a = float(entry_a.get())
        L = float(entry_L.get())
        b = float(entry_b.get())
        wd = float(entry_wd.get())
        r_in = float(entry_rin.get())
        r_out = float(entry_rout.get())
        na1_mrad = float(entry_na1.get())
        na2_mrad = float(entry_na2.get())
        zp_diameter_um = float(entry_zp_diameter.get())
        delta_r_nm = float(entry_delta_r.get())
        energy_ev = float(entry_energy.get())
        detector_dist_mm = float(entry_detector.get())

        # --- 2. Convert units and perform basic validation ---
        na1 = na1_mrad / 1000.0
        na2 = na2_mrad / 1000.0

        if not (a > 0 and L > 0 and b > 0 and wd > 0 and r_in > 0 and r_out > 0 and na1 > 0 and zp_diameter_um > 0 and delta_r_nm > 0 and energy_ev > 0 and detector_dist_mm > 0):
            messagebox.showwarning("輸入警告", "為獲得有效計算結果，所有輸入值應為正數。")
        if a <= b:
            messagebox.showerror("參數錯誤", "橢圓半長軸 'a' 必須大於半短軸 'b'。")
            clear_results()
            return
        if b <= r_in or b <= r_out:
            messagebox.showwarning("參數警告", "橢圓半短軸 'b' 通常應大於入口半徑 'r_in' 和出口半徑 'r_out'。")

        # --- 3. Calculate all "Remark" values based on inputs ---

        # Ellipse properties
        c = math.sqrt(a**2 - b**2)
        source_dist_mm = 2 * c

        # Illumination properties
        width = (na1 - na2) / na1 if na1 != 0 else 0
        
        # Beam Stop
        bs_diameter_um = 2 * r_out * 1000

        # FZP and X-ray properties
        lambda_nm = 1239.84244 / energy_ev
        f_mm = (zp_diameter_um * delta_r_nm) / (lambda_nm * 1000.0)
        
        # Magnification and related
        magnification = 0
        distance = 0
        if f_mm > 0:
            C = detector_dist_mm / f_mm
            if C >= 4:
                magnification = ((C - 2) + math.sqrt(C**2 - 4*C)) / 2
                if magnification > 0:
                    distance = f_mm * (magnification + 1) / magnification
        
        # Resolution and other FZP params
        resolution_nm = lambda_nm / (2 * na1) if na1 > 0 else float('inf')
        N = (zp_diameter_um * 1000.0) / (4 * delta_r_nm)
        fzp_na_mrad = (lambda_nm / (2 * delta_r_nm)) * 1000.0
        
        # Phase Ring
        pr_outer_diam_um = na1 * f_mm * 1000
        pr_inner_diam_um = na2 * f_mm * 1000
        
        # Source size
        source_size_um = r_in * 2000.0

        # --- 4. Update remark labels ---
        # 第三欄
        lbl_source_dist_val.config(text=f"{source_dist_mm:.0f}")
        lbl_width_val.config(text=f"{width * 100:.1f} %")
        lbl_bs_diam_val.config(text=f"{bs_diameter_um:.2f}")
        lbl_lambda_val.config(text=f"{lambda_nm:.5f}")
        lbl_f_val.config(text=f"{f_mm:.3f}") # FZP focal length
        lbl_distance_val.config(text=f"{distance:.3f}" if distance > 0 else '---') # FZP sample distance
        lbl_N_val.config(text=f"{N:.0f}") # FZP total rings
        lbl_fzp_na_val.config(text=f"{fzp_na_mrad:.4f}") # FZP NA
        lbl_resolution_val.config(text=f"{resolution_nm:.3f}") # Theoretical resolution
        lbl_magnification_val.config(text=f"{magnification:.2f}" if magnification > 0 else '---') # Magnification
        lbl_pr_outer_diam_val.config(text=f"{pr_outer_diam_um:.2f}") # Phase Ring outer diameter
        lbl_pr_inner_diam_val.config(text=f"{pr_inner_diam_um:.2f}") # Phase Ring inner diameter
        lbl_source_size_val.config(text=f"{source_size_um:.2f}")
        lbl_zp_diameter_val.config(text=f"{zp_diameter_um:.2f}") # Mirror input

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
root.geometry("1500x700") # Adjusted height
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
frame_input = ttk.LabelFrame(main_container, text="輸入 (所有值皆為手動輸入)", padding=(10, 10))

# Input Column 1
frame_input_left = ttk.Frame(frame_input)
frame_input_left.grid(row=0, column=0, padx=10)
entry_a = ttk.Entry(frame_input_left, width=18)
entry_a.insert(0, "950")
entry_L = ttk.Entry(frame_input_left, width=18)
entry_L.insert(0, "120")
entry_b = ttk.Entry(frame_input_left, width=18)
entry_b.insert(0, "13.95")
entry_wd = ttk.Entry(frame_input_left, width=18)
entry_wd.insert(0, "30.1")
entry_rin = ttk.Entry(frame_input_left, width=18)
entry_rin.insert(0, "0.49")
entry_rout = ttk.Entry(frame_input_left, width=18)
entry_rout.insert(0, "0.52")

# Input Column 2
frame_input_right = ttk.Frame(frame_input)
frame_input_right.grid(row=0, column=1, padx=10)
entry_na1 = ttk.Entry(frame_input_right, width=18)
entry_na1.insert(0, "3.02")
entry_na2 = ttk.Entry(frame_input_right, width=18)
entry_na2.insert(0, "2.99")
entry_zp_diameter = ttk.Entry(frame_input_right, width=18)
entry_zp_diameter.insert(0, "300")
entry_delta_r = ttk.Entry(frame_input_right, width=18)
entry_delta_r.insert(0, "25")
entry_energy = ttk.Entry(frame_input_right, width=18)
entry_energy.insert(0, "8000")
entry_detector = ttk.Entry(frame_input_right, width=18)
entry_detector.insert(0, "1900")

# -- 第二欄：備註 (由輸入值計算) --
frame_remarks = ttk.LabelFrame(main_container, text="備註 (由輸入值計算)", padding=(10, 10))
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
lbl_zp_diameter_val = ttk.Label(frame_remarks, text="---", font=("Consolas", 10))

# --- 介面佈局 (Widget Layout) ---

# -- 第一欄：輸入 --
frame_input.grid(row=0, column=0, padx=10, pady=5, sticky="ns")

# Layout for left input column
ttk.Label(frame_input_left, text="橢圓半長軸 a (mm):", font=font_blue_bold, foreground="navy").grid(row=0, column=0, sticky="w", pady=5, padx=5)
entry_a.grid(row=0, column=1, pady=5, padx=5)
ttk.Label(frame_input_left, text="Condenser 長度 L (mm):", font=font_purple_bold, foreground="purple").grid(row=1, column=0, sticky="w", pady=5, padx=5)
entry_L.grid(row=1, column=1, pady=5, padx=5)
ttk.Label(frame_input_left, text="橢圓半短軸 b (mm):", font=font_blue_bold, foreground="navy").grid(row=2, column=0, sticky="w", pady=5, padx=5)
entry_b.grid(row=2, column=1, pady=5, padx=5)
ttk.Label(frame_input_left, text="工作距離 WD (mm):", font=font_purple_bold, foreground="purple").grid(row=3, column=0, sticky="w", pady=5, padx=5)
entry_wd.grid(row=3, column=1, pady=5, padx=5)
ttk.Label(frame_input_left, text="入口半徑 R_in (mm):", font=font_brown_bold, foreground="saddle brown").grid(row=4, column=0, sticky="w", pady=5, padx=5)
entry_rin.grid(row=4, column=1, pady=5, padx=5)
ttk.Label(frame_input_left, text="出口半徑 R_out (mm):", font=font_brown_bold, foreground="saddle brown").grid(row=5, column=0, sticky="w", pady=5, padx=5)
entry_rout.grid(row=5, column=1, pady=5, padx=5)

# Layout for right input column
ttk.Label(frame_input_right, text="外數值孔徑 NA1 (mrad):", font=font_green_bold, foreground="dark green").grid(row=0, column=0, sticky="w", pady=5, padx=5)
entry_na1.grid(row=0, column=1, pady=5, padx=5)
ttk.Label(frame_input_right, text="內數值孔徑 NA2 (mrad):", font=font_green_bold, foreground="dark green").grid(row=1, column=0, sticky="w", pady=5, padx=5)
entry_na2.grid(row=1, column=1, pady=5, padx=5)
ttk.Label(frame_input_right, text="FZP 直徑 (μm):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
entry_zp_diameter.grid(row=2, column=1, pady=5, padx=5)
ttk.Label(frame_input_right, text="FZP 最外層厚 Δr (nm):").grid(row=3, column=0, sticky="w", pady=5, padx=5)
entry_delta_r.grid(row=3, column=1, pady=5, padx=5)
ttk.Label(frame_input_right, text="X光能量 Energy (eV):").grid(row=4, column=0, sticky="w", pady=5, padx=5)
entry_energy.grid(row=4, column=1, pady=5, padx=5)
ttk.Label(frame_input_right, text="偵測器樣品距離 D (mm):").grid(row=5, column=0, sticky="w", pady=5, padx=5)
entry_detector.grid(row=5, column=1, pady=5, padx=5)


# -- 第二欄：備註 --
frame_remarks.grid(row=0, column=1, padx=10, pady=5, sticky="ns")
for i in range(14):
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
ttk.Label(frame_remarks, text="[輸入] FZP 直徑 (μm):").grid(row=13, column=0, sticky="w", pady=5, padx=5)
lbl_zp_diameter_val.grid(row=13, column=1, sticky="w", pady=6, padx=5)

# --- 計算按鈕 ---
btn_calc = ttk.Button(main_container, text="Calculate", command=calculate)
btn_calc.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

# 啟動時自動計算一次預設值
calculate()

# 啟動主迴圈
root.mainloop()