import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
import random
import time
import copy
import os
import glob

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKY_PATH = os.path.join(BASE_DIR, "sky.png")

# Automatically find a .ttf font in the folder
ttf_files = glob.glob(os.path.join(BASE_DIR, "*.ttf"))
if ttf_files:
    FONT_PATH = ttf_files[0]
    print(f"Using font file: {FONT_PATH}")
else:
    FONT_PATH = None
    print("No .ttf font file found! Using default system font.")

# Tkinter Setup
root = tk.Tk()
root.title("Gridoku")
root.geometry("500x650")
root.resizable(False, False)

# Load custom TTF font
if FONT_PATH and os.path.exists(FONT_PATH):
    try:
        from tkinter import font as tkFont
        # Use internal font family name
        PixelFont = tkFont.Font(root=root, family="Press Start 2P", size=12)
        print("Loaded font from TTF successfully.")
    except:
        PixelFont = tkFont.Font(root=root, size=12)
        print("Failed to load TTF font; using default font.")
else:
    PixelFont = tkFont.Font(root=root, size=12)
    print("No TTF font found; using default font.")

# Font settings
TITLE_FONT = (PixelFont.actual("family"), 22)
MENU_FONT  = (PixelFont.actual("family"), 12)
TIMER_FONT = (PixelFont.actual("family"), 10)
CELL_FONT  = (PixelFont.actual("family"), 14)
WIN_FONT   = (PixelFont.actual("family"), 16)

# Themes
THEMES = {"easy": "#A8E6A3", "medium": "#D1B3FF", "hard": "#FFCC99"}
current_theme = THEMES["medium"]
current_difficulty = 45

# Game State
solution_board = None
game_active = True
start_time = time.time()
grid = []

# Sudoku Logic
def is_valid(board, r, c, n):
    for i in range(9):
        if board[r][i] == n or board[i][c] == n:
            return False
    sr, sc = 3 * (r // 3), 3 * (c // 3)
    for i in range(sr, sr + 3):
        for j in range(sc, sc + 3):
            if board[i][j] == n:
                return False
    return True

def solve_sudoku(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for n in nums:
                    if is_valid(board, r, c, n):
                        board[r][c] = n
                        if solve_sudoku(board):
                            return True
                        board[r][c] = 0
                return False
    return True

def generate_sudoku(removed):
    board = [[0]*9 for _ in range(9)]
    solve_sudoku(board)
    global solution_board
    solution_board = copy.deepcopy(board)
    removed_cells = 0
    while removed_cells < removed:
        r, c = random.randint(0, 8), random.randint(0, 8)
        if board[r][c] != 0:
            board[r][c] = 0
            removed_cells += 1
    return board

# UI Helpers
def validate_entry(P):
    return P == "" or (P.isdigit() and 1 <= int(P) <= 9)

def draw_grid_lines():
    canvas.delete("grid")
    for i in range(10):
        thickness = 4 if i % 3 == 0 else 1
        canvas.create_line(i * 50, 0, i * 50, 450, width=thickness, fill="black", tags="grid")
        canvas.create_line(0, i * 50, 450, i * 50, width=thickness, fill="black", tags="grid")

def on_input(event, r, c):
    grid[r][c].config(bg=current_theme)
    check_win()

def check_puzzle():
    if not game_active:
        return
    for r in range(9):
        for c in range(9):
            cell = grid[r][c]
            val = cell.get()
            if cell["state"] == "disabled":
                continue
            cell.config(bg=current_theme)
            if val != "":
                if int(val) != solution_board[r][c]:
                    cell.config(bg="#FF9999")

def check_win():
    global game_active
    if not game_active:
        return
    for r in range(9):
        for c in range(9):
            val = grid[r][c].get()
            if val == "" or int(val) != solution_board[r][c]:
                return
    game_active = False
    win_label.config(text="YOU WIN!")
    disable_grid()

def disable_grid():
    for row in grid:
        for cell in row:
            cell.config(state="disabled")

def create_grid():
    g = []
    vcmd = root.register(validate_entry)
    for r in range(9):
        row = []
        for c in range(9):
            e = tk.Entry(
                canvas, font=CELL_FONT, justify="center", bd=0,
                fg="black", bg=current_theme, disabledforeground="black",
                validate="key", validatecommand=(vcmd, "%P")
            )
            e.place(x=c*50+2, y=r*50+2, width=48, height=48)
            e.bind("<KeyRelease>", lambda event, r=r, c=c: on_input(event, r, c))
            row.append(e)
        g.append(row)
    return g

def display_board(board):
    global game_active
    game_active = True
    win_label.config(text="")
    for r in range(9):
        for c in range(9):
            cell = grid[r][c]
            cell.config(state="normal", bg=current_theme)
            cell.delete(0, tk.END)
            if board[r][c] != 0:
                cell.insert(0, str(board[r][c]))
                cell.config(state="disabled")

# Timer
def reset_timer():
    global start_time
    start_time = time.time()

def update_timer():
    if game_active:
        elapsed = int(time.time() - start_time)
        timer_label.config(text=f"TIME {elapsed//60:02d}:{elapsed%60:02d}")
    root.after(1000, update_timer)

# Game Control
def start_game(removed, mode):
    global current_difficulty, current_theme
    current_difficulty = removed
    current_theme = THEMES[mode]
    menu_canvas.pack_forget()
    game_frame.pack()
    apply_theme()
    draw_grid_lines()
    board = generate_sudoku(current_difficulty)
    display_board(board)
    reset_timer()

def new_game():
    board = generate_sudoku(current_difficulty)
    display_board(board)
    reset_timer()

def back_to_menu():
    game_frame.pack_forget()
    menu_canvas.pack(fill="both", expand=True)

def apply_theme():
    root.config(bg=current_theme)
    game_frame.config(bg=current_theme)
    canvas.config(bg=current_theme)
    control_frame.config(bg=current_theme)
    timer_label.config(bg=current_theme, fg="black")
    win_label.config(bg=current_theme, fg="black")
    for w in control_frame.winfo_children():
        w.config(bg=current_theme, fg="black")

# Menu Setup
menu_canvas = tk.Canvas(root, width=500, height=650, highlightthickness=0)
menu_canvas.pack(fill="both", expand=True)

sky_img_raw = Image.open(SKY_PATH).resize((500, 650))
menu_canvas.sky_bg = ImageTk.PhotoImage(sky_img_raw)
menu_canvas.create_image(0, 0, image=menu_canvas.sky_bg, anchor="nw")

menu_canvas.create_text(250, 100, text="GRIDOKU", font=TITLE_FONT, fill="black")
menu_canvas.create_text(250, 170, text="SELECT MODE", font=MENU_FONT, fill="black")

menu_canvas.create_window(250, 260, window=tk.Button(root, text="EASY", font=MENU_FONT, command=lambda: start_game(35, "easy")))
menu_canvas.create_window(250, 320, window=tk.Button(root, text="MEDIUM", font=MENU_FONT, command=lambda: start_game(45, "medium")))
menu_canvas.create_window(250, 380, window=tk.Button(root, text="HARD", font=MENU_FONT, command=lambda: start_game(55, "hard")))

# Game Frame Setup
game_frame = tk.Frame(root, bg=current_theme)
canvas = tk.Canvas(game_frame, width=450, height=450, bg=current_theme, highlightthickness=0)
canvas.pack(pady=10)
grid = create_grid()
draw_grid_lines()

control_frame = tk.Frame(game_frame, bg=current_theme)
control_frame.pack()

timer_label = tk.Label(control_frame, font=TIMER_FONT)
timer_label.grid(row=0, column=0, padx=6)
tk.Button(control_frame, text="NEW", font=MENU_FONT, command=new_game).grid(row=0, column=1, padx=6)
tk.Button(control_frame, text="CHECK", font=MENU_FONT, command=check_puzzle).grid(row=0, column=2, padx=6)
tk.Button(control_frame, text="MENU", font=MENU_FONT, command=back_to_menu).grid(row=0, column=3, padx=6)

win_label = tk.Label(game_frame, font=WIN_FONT, fg="black", bg=current_theme)
win_label.pack(pady=10)

update_timer()
root.mainloop()
