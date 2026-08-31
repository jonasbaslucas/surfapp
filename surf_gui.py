import tkinter as tk
import math
from tkinter import ttk
import customtkinter as ctk
from PIL import Image, ImageTk

from surf_logic import evaluate_conditions
from surf_spots import SURF_SPOTS


# ============================================================
# SETTINGS
# ============================================================

BACKGROUND_FILES = {
    1: "backgrounds/wave_01.png",
    2: "backgrounds/wave_02.png",
    3: "backgrounds/wave_03.png",
}

START_WIDTH = 1400
START_HEIGHT = 850

MIN_WIDTH = 1000
MIN_HEIGHT = 650

MAX_SWELL = 3.0
MAX_WIND_SPEED = 40.0

ctk.set_appearance_mode("light")


# ============================================================
# COLOURS
# ============================================================

BAMBOO_DARK = "#65401F"
BAMBOO = "#B77B36"
BAMBOO_LIGHT = "#E0B365"

SURFBOARD = "#D9A441"
SURFBOARD_DARK = "#174A56"

TEXT_LIGHT = "#FFF0CF"

PANEL_DARK = "#10242D"
PANEL = "#274554"
PANEL_EDGE = "#E0B365"
PANEL_SHADOW = "#0D1B22"
PANEL_TEXT = "#FFF6E2"
PANEL_ACCENT = "#E4572E"
PANEL_SOFT = "#F8E4B1"


# ============================================================
# APPLICATION
# ============================================================

class SurfApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("🏄 Surf's Up — Dutch Coast")

        self.geometry(
            f"{START_WIDTH}x{START_HEIGHT}"
        )

        self.minsize(
            MIN_WIDTH,
            MIN_HEIGHT
        )

        self.resizable(
            True,
            True
        )

        # ----------------------------------------------------
        # Current swell
        # ----------------------------------------------------

        self.swell = 0.8

        # ----------------------------------------------------
        # Current swell direction
        # ----------------------------------------------------

        self.swell_direction = "NW"

        # ----------------------------------------------------
        # Current wind direction
        # ----------------------------------------------------

        self.wind_direction = "E"

        # ----------------------------------------------------
        # Current wind speed in knots
        # ----------------------------------------------------

        self.wind_speed = 12.0

        # ----------------------------------------------------
        # Current period in seconds
        # ----------------------------------------------------

        self.period = 9.0

        # ----------------------------------------------------
        # Surf spot selection
        # ----------------------------------------------------

        self.spot_order = list(SURF_SPOTS.keys())
        self.spot_name_to_key = {
            spot["name"]: key
            for key, spot in SURF_SPOTS.items()
        }
        self.selected_spot_key = self.spot_order[0]
        self.selected_spot_name = SURF_SPOTS[
            self.selected_spot_key
        ]["name"]

        # ----------------------------------------------------
        # Wind animation
        # ----------------------------------------------------

        self.wind_pulse_phase = 0.0
        self.wind_animation_job = None

        # ----------------------------------------------------
        # Load the three backgrounds
        # ----------------------------------------------------

        self.background_images = {}

        for state, filename in BACKGROUND_FILES.items():

            self.background_images[state] = (
                Image.open(filename)
                .convert("RGB")
            )

        # ----------------------------------------------------
        # ONE CANVAS
        #
        # The background and slider are drawn on the same
        # canvas.
        #
        # This means there is NO ugly transparent/white box.
        # ----------------------------------------------------

        self.canvas = tk.Canvas(
            self,
            highlightthickness=0,
            bd=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        self.background_photo = None
        self.background_id = None

        # ----------------------------------------------------
        # UI styles and dropdown
        # ----------------------------------------------------

        self.configure_widget_styles()
        self.create_spot_selector()

        # ----------------------------------------------------
        # Mouse interaction
        # ----------------------------------------------------

        self.canvas.bind(
            "<Button-1>",
            self.canvas_click
        )

        self.canvas.bind(
            "<B1-Motion>",
            self.canvas_drag
        )

        # ----------------------------------------------------
        # Resize
        # ----------------------------------------------------

        self.bind(
            "<Configure>",
            self.on_resize
        )

        self.after(
            100,
            self.update_scene
        )

    # ========================================================
    # SHAPE HELPERS
    # ========================================================

    def draw_rounded_rect(
        self,
        x1,
        y1,
        x2,
        y2,
        radius,
        **kwargs
    ):

        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]

        return self.canvas.create_polygon(
            *points,
            smooth=True,
            splinesteps=24,
            **kwargs
        )

    def draw_capsule(
        self,
        x1,
        y1,
        x2,
        y2,
        radius,
        **kwargs
    ):

        return self.draw_rounded_rect(
            x1,
            y1,
            x2,
            y2,
            radius,
            **kwargs
        )

    def configure_widget_styles(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Surf.TCombobox",
            fieldbackground=PANEL,
            background=PANEL,
            foreground=PANEL_TEXT,
            arrowcolor=PANEL_SOFT,
            bordercolor=PANEL_EDGE,
            lightcolor=PANEL_EDGE,
            darkcolor=PANEL_SHADOW,
            padding=(10, 8),
            relief="flat"
        )

        style.map(
            "Surf.TCombobox",
            fieldbackground=[
                ("readonly", PANEL),
                ("active", PANEL),
            ],
            foreground=[
                ("readonly", PANEL_TEXT),
                ("active", PANEL_TEXT),
            ],
            background=[
                ("readonly", PANEL),
                ("active", PANEL),
            ],
        )

    def create_spot_selector(self):

        self.spot_selector_frame = tk.Frame(
            self.canvas,
            bg=PANEL
        )

        self.spot_selector_var = tk.StringVar(
            value=self.selected_spot_name
        )

        self.spot_selector = ttk.Combobox(
            self.spot_selector_frame,
            textvariable=self.spot_selector_var,
            values=[
                SURF_SPOTS[key]["name"]
                for key in self.spot_order
            ],
            state="readonly",
            style="Surf.TCombobox",
            width=28
        )

        self.spot_selector.bind(
            "<<ComboboxSelected>>",
            self.on_spot_selected
        )

        self.spot_selector.pack(
            fill="x",
            padx=2,
            pady=2
        )

        self.spot_selector_window_id = None

    def get_selected_spot(self):

        return SURF_SPOTS[self.selected_spot_key]

    def get_condition_summary(self):

        spot = self.get_selected_spot()

        return evaluate_conditions(
            spot,
            self.wind_direction,
            self.swell_direction,
            self.swell,
            self.period
        )

    def on_spot_selected(self, event=None):

        selected_name = self.spot_selector_var.get()

        self.selected_spot_key = self.spot_name_to_key[
            selected_name
        ]

        self.selected_spot_name = selected_name

        self.draw_verdict_card()

    def draw_wind_cluster_panel(self):

        width = self.winfo_width()
        height = self.winfo_height()

        panel_left = width * 0.53
        panel_right = width * 0.92
        panel_top = height * 0.53
        panel_bottom = height * 0.91

        glow = 4 + 2 * (0.5 + 0.5 * math.sin(self.wind_pulse_phase))

        self.draw_rounded_rect(
            panel_left + glow,
            panel_top + glow,
            panel_right + glow,
            panel_bottom + glow,
            34,
            fill=PANEL_SHADOW,
            outline="",
            tags="wind_cluster"
        )

        self.draw_rounded_rect(
            panel_left,
            panel_top,
            panel_right,
            panel_bottom,
            34,
            fill=PANEL,
            outline=PANEL_EDGE,
            width=2,
            tags="wind_cluster"
        )

        self.canvas.create_text(
            panel_left + 28,
            panel_top + 28,
            text="WIND",
            anchor="w",
            fill=PANEL_TEXT,
            font=("Arial", 14, "bold"),
            tags="wind_cluster"
        )

        self.canvas.create_text(
            panel_left + 28,
            panel_top + 52,
            text="Direction and strength",
            anchor="w",
            fill=PANEL_SOFT,
            font=("Arial", 9, "italic"),
            tags="wind_cluster"
        )

    def draw_spot_card(self):

        width = self.winfo_width()
        height = self.winfo_height()

        card_left = width * 0.03
        card_top = height * 0.05
        card_right = width * 0.28
        card_bottom = height * 0.16

        self.draw_rounded_rect(
            card_left + 5,
            card_top + 6,
            card_right + 5,
            card_bottom + 6,
            24,
            fill=PANEL_SHADOW,
            outline="",
            tags="ui_panels"
        )

        self.draw_rounded_rect(
            card_left,
            card_top,
            card_right,
            card_bottom,
            24,
            fill=PANEL,
            outline=PANEL_EDGE,
            width=2,
            tags="ui_panels"
        )

        self.canvas.create_text(
            card_left + 22,
            card_top + 24,
            text="SURF SPOT",
            anchor="w",
            fill=PANEL_SOFT,
            font=("Arial", 9, "bold"),
            tags="ui_panels"
        )

        self.canvas.create_text(
            card_left + 22,
            card_top + 46,
            text="Choose a beach to score",
            anchor="w",
            fill=PANEL_TEXT,
            font=("Arial", 11, "bold"),
            tags="ui_panels"
        )

        selector_x = card_left + 18
        selector_y = card_top + 62
        selector_w = card_right - card_left - 36
        selector_h = 30

        self.draw_rounded_rect(
            selector_x - 2,
            selector_y - 2,
            selector_x + selector_w + 2,
            selector_y + selector_h + 2,
            14,
            fill="#12252E",
            outline="",
            tags="ui_panels"
        )

        if self.spot_selector_window_id is None:

            self.spot_selector_window_id = self.canvas.create_window(
                selector_x,
                selector_y,
                anchor="nw",
                window=self.spot_selector_frame,
                width=selector_w,
                height=selector_h,
                tags="ui_panels"
            )

        else:

            self.canvas.coords(
                self.spot_selector_window_id,
                selector_x,
                selector_y
            )

            self.canvas.itemconfig(
                self.spot_selector_window_id,
                width=selector_w,
                height=selector_h
            )

        self.canvas.tag_raise("ui_panels")
        self.spot_selector_frame.lift()

    def draw_verdict_card(self):

        width = self.winfo_width()
        height = self.winfo_height()

        card_width = width * 0.28
        card_height = height * 0.18
        card_left = width * 0.35
        card_top = height * 0.04

        summary = self.get_condition_summary()
        spot = self.get_selected_spot()

        self.canvas.delete("verdict_card")

        self.draw_rounded_rect(
            card_left + 6,
            card_top + 7,
            card_left + card_width + 6,
            card_top + card_height + 7,
            28,
            fill=PANEL_SHADOW,
            outline="",
            tags="verdict_card"
        )

        self.draw_rounded_rect(
            card_left,
            card_top,
            card_left + card_width,
            card_top + card_height,
            28,
            fill=PANEL,
            outline=PANEL_EDGE,
            width=2,
            tags="verdict_card"
        )

        self.canvas.create_text(
            card_left + 24,
            card_top + 24,
            text=spot["name"],
            anchor="w",
            fill=PANEL_TEXT,
            font=("Arial", 13, "bold"),
            tags="verdict_card"
        )

        self.canvas.create_text(
            card_left + 24,
            card_top + 48,
            text=summary["verdict"],
            anchor="w",
            fill=PANEL_SOFT,
            font=("Arial", 18, "bold"),
            tags="verdict_card"
        )

        score_text = f"{summary['total_score']} / 100"
        self.canvas.create_text(
            card_left + card_width - 24,
            card_top + 24,
            text=score_text,
            anchor="e",
            fill="#F8E4B1",
            font=("Arial", 18, "bold"),
            tags="verdict_card"
        )

        self.canvas.create_text(
            card_left + card_width - 24,
            card_top + 48,
            text=f"Period {self.period:.1f}s",
            anchor="e",
            fill=PANEL_TEXT,
            font=("Arial", 9, "bold"),
            tags="verdict_card"
        )

        stat_y = card_top + 85
        stats = [
            ("Wind", summary["wind_quality"]),
            ("Swell", summary["swell_direction_quality"]),
            ("Height", summary["swell_height_quality"]),
            ("Period", summary["period_quality"]),
        ]

        stat_width = (card_width - 60) / 4

        for index, (label, value) in enumerate(stats):
            stat_left = card_left + 18 + index * stat_width
            self.draw_rounded_rect(
                stat_left,
                stat_y,
                stat_left + stat_width - 8,
                stat_y + 40,
                14,
                fill="#12252E",
                outline="",
                tags="verdict_card"
            )
            self.canvas.create_text(
                stat_left + 10,
                stat_y + 11,
                text=label,
                anchor="w",
                fill=PANEL_SOFT,
                font=("Arial", 8, "bold"),
                tags="verdict_card"
            )
            self.canvas.create_text(
                stat_left + 10,
                stat_y + 26,
                text=value,
                anchor="w",
                fill=PANEL_TEXT,
                font=("Arial", 9, "bold"),
                tags="verdict_card"
            )

        self.canvas.tag_raise("verdict_card")

    # ========================================================
    # DETERMINE BACKGROUND
    # ========================================================

    def get_background_state(self):

        if self.swell <= 1.0:
            return 1

        elif self.swell <= 2.0:
            return 2

        else:
            return 3

    # ========================================================
    # CREATE BACKGROUND
    # ========================================================

    def create_background(self):

        width = self.winfo_width()
        height = self.winfo_height()

        if width < 10 or height < 10:
            return

        # ----------------------------------------------------
        # Select ONE background
        # ----------------------------------------------------

        state = self.get_background_state()

        image = self.background_images[state].copy()

        original_width, original_height = image.size

        # ----------------------------------------------------
        # Scale to fill window
        # ----------------------------------------------------

        scale = max(
            width / original_width,
            height / original_height
        )

        new_width = int(
            original_width * scale
        )

        new_height = int(
            original_height * scale
        )

        image = image.resize(
            (
                new_width,
                new_height
            ),
            Image.Resampling.LANCZOS
        )

        # ----------------------------------------------------
        # Crop
        # ----------------------------------------------------

        left = (
            new_width - width
        ) // 2

        top = (
            new_height - height
        ) // 2

        image = image.crop(
            (
                left,
                top,
                left + width,
                top + height
            )
        )

        # ----------------------------------------------------
        # Display background
        # ----------------------------------------------------

        self.background_photo = ImageTk.PhotoImage(
            image
        )

        if self.background_id is None:

            self.background_id = (
                self.canvas.create_image(
                    0,
                    0,
                    image=self.background_photo,
                    anchor="nw",
                    tags="background"
                )
            )

        else:

            self.canvas.itemconfig(
                self.background_id,
                image=self.background_photo
            )

        # Always keep background at the very back

        self.canvas.tag_lower(
            self.background_id
        )

    # ========================================================
    # DRAW SLIDER ON SURFBOARD
    # ========================================================

    def draw_slider(self):

        # Delete only slider elements.
        # The background stays untouched.

        self.canvas.delete(
            "swell_slider"
        )

        width = self.winfo_width()
        height = self.winfo_height()

        if width < 100 or height < 100:
            return

        # ====================================================
        # POSITION
        #
        # Based on your actual screenshot:
        # the surfboard occupies roughly the left 10%.
        #
        # The slider is deliberately kept INSIDE it.
        # ====================================================

        rail_x = width * 0.058

        rail_top = height * 0.30
        rail_bottom = height * 0.76

        # ====================================================
        # CURRENT SURFBOARD POSITION
        #
        # 0 m = bottom
        # 3 m = top
        # ====================================================

        fraction = (
            self.swell
            / MAX_SWELL
        )

        knob_y = (
            rail_bottom
            - fraction
            * (
                rail_bottom - rail_top
            )
        )

        # ====================================================
        # BAMBOO RAIL SHADOW
        # ====================================================

        self.canvas.create_line(
            rail_x + 3,
            rail_top,
            rail_x + 3,
            rail_bottom,
            fill=BAMBOO_DARK,
            width=11,
            capstyle=tk.ROUND,
            tags="swell_slider"
        )

        # ====================================================
        # BAMBOO RAIL
        # ====================================================

        self.canvas.create_line(
            rail_x,
            rail_top,
            rail_x,
            rail_bottom,
            fill=BAMBOO,
            width=8,
            capstyle=tk.ROUND,
            tags="swell_slider"
        )

        # ====================================================
        # BAMBOO HIGHLIGHT
        # ====================================================

        self.canvas.create_line(
            rail_x - 2,
            rail_top + 3,
            rail_x - 2,
            rail_bottom - 3,
            fill=BAMBOO_LIGHT,
            width=2,
            capstyle=tk.ROUND,
            tags="swell_slider"
        )

        # ====================================================
        # BAMBOO JOINTS
        # ====================================================

        for fraction in (
            0.25,
            0.50,
            0.75
        ):

            y = (
                rail_top
                + fraction
                * (
                    rail_bottom - rail_top
                )
            )

            self.canvas.create_line(
                rail_x - 6,
                y,
                rail_x + 6,
                y,
                fill=BAMBOO_DARK,
                width=4,
                capstyle=tk.ROUND,
                tags="swell_slider"
            )

        # ====================================================
        # SMALL CURRENT HANDLE
        #
        # This is TEMPORARY.
        #
        # Later we'll replace this with the tiny surfboard
        # image you want.
        # ====================================================

        self.canvas.create_oval(
            rail_x - 10,
            knob_y - 16,
            rail_x + 10,
            knob_y + 16,
            fill=SURFBOARD_DARK,
            outline="",
            tags="swell_slider"
        )

        self.canvas.create_oval(
            rail_x - 8,
            knob_y - 14,
            rail_x + 8,
            knob_y + 14,
            fill=SURFBOARD,
            outline=SURFBOARD_DARK,
            width=2,
            tags="swell_slider"
        )

        # ====================================================
        # VALUE
        #
        # Put it immediately beside the rail.
        # ====================================================

        self.canvas.create_text(
            rail_x + 17,
            knob_y,
            text=f"{self.swell:.1f} m",
            anchor="w",
            fill=TEXT_LIGHT,
            font=("Arial", 11, "bold"),
            tags="swell_slider"
        )

        # ====================================================
        # SMALL / BIG
        # ====================================================

        self.canvas.create_text(
            rail_x - 14,
            rail_bottom,
            text="SMALL",
            anchor="e",
            fill=TEXT_LIGHT,
            font=("Arial", 8, "bold"),
            tags="swell_slider"
        )

        self.canvas.create_text(
            rail_x - 14,
            rail_top,
            text="3 m",
            anchor="e",
            fill=TEXT_LIGHT,
            font=("Arial", 8, "bold"),
            tags="swell_slider"
        )

        # ====================================================
        # KEEP SLIDER ABOVE BACKGROUND
        # ====================================================

        self.canvas.tag_raise(
            "swell_slider"
        )

    # ========================================================
    # CHECK WHETHER CLICK IS NEAR SLIDER
    # ========================================================

    # ========================================================
    # DRAW SWELL COMPASS
    # ========================================================

    def draw_compass(self):

        # Delete only the old compass
        self.canvas.delete("compass")

        width = self.winfo_width()
        height = self.winfo_height()

        if width < 100 or height < 100:
            return

        # ====================================================
        # COMPASS POSITION
        #
        # Change these later if we want to move it.
        # ====================================================

        self.compass_x = width * 0.18
        self.compass_y = height * 0.84

        radius = min(
            width * 0.055,
            height * 0.11
        )

        self.compass_radius = radius

        # ====================================================
        # COMPASS SHADOW
        # ====================================================

        self.canvas.create_oval(
            self.compass_x - radius + 4,
            self.compass_y - radius + 5,
            self.compass_x + radius + 4,
            self.compass_y + radius + 5,
            fill="#16333A",
            outline="",
            tags="compass"
        )

        # ====================================================
        # OUTER COMPASS
        # ====================================================

        self.canvas.create_oval(
            self.compass_x - radius,
            self.compass_y - radius,
            self.compass_x + radius,
            self.compass_y + radius,
            fill="#D8B56D",
            outline="#5B371A",
            width=4,
            tags="compass"
        )

        # ====================================================
        # INNER COMPASS
        # ====================================================

        inner_radius = radius * 0.88

        self.canvas.create_oval(
            self.compass_x - inner_radius,
            self.compass_y - inner_radius,
            self.compass_x + inner_radius,
            self.compass_y + inner_radius,
            fill="#F3D99A",
            outline="#8B5A2B",
            width=2,
            tags="compass"
        )

        # ====================================================
        # COMPASS DIRECTIONS
        # ====================================================

        directions = [
            "N", "NNE", "NE", "ENE",
            "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW",
            "W", "WNW", "NW", "NNW"
        ]

        import math

        # ====================================================
        # DRAW 16 TICKS
        # ====================================================

        for i in range(16):

            angle = math.radians(i * 22.5 - 90)

            # Major ticks every 45 degrees
            if i % 2 == 0:
                tick_length = radius * 0.16
                tick_width = 3
            else:
                tick_length = radius * 0.09
                tick_width = 1

            outer_x = (
                    self.compass_x
                    + math.cos(angle) * radius * 0.92
            )

            outer_y = (
                    self.compass_y
                    + math.sin(angle) * radius * 0.92
            )

            inner_x = (
                    self.compass_x
                    + math.cos(angle)
                    * (radius * 0.92 - tick_length)
            )

            inner_y = (
                    self.compass_y
                    + math.sin(angle)
                    * (radius * 0.92 - tick_length)
            )

            self.canvas.create_line(
                outer_x,
                outer_y,
                inner_x,
                inner_y,
                fill="#5B371A",
                width=tick_width,
                tags="compass"
            )

        # ====================================================
        # DRAW MAIN DIRECTION LABELS
        # ====================================================

        main_directions = {
            "N": 0,
            "E": 90,
            "S": 180,
            "W": 270
        }

        for direction, degrees in main_directions.items():
            angle = math.radians(
                degrees - 90
            )

            text_x = (
                    self.compass_x
                    + math.cos(angle)
                    * radius * 0.68
            )

            text_y = (
                    self.compass_y
                    + math.sin(angle)
                    * radius * 0.68
            )

            self.canvas.create_text(
                text_x,
                text_y,
                text=direction,
                fill="#264653",
                font=(
                    "Arial",
                    max(9, int(radius * 0.22)),
                    "bold"
                ),
                tags="compass"
            )

        # ====================================================
        # CALCULATE CURRENT ARROW ANGLE
        # ====================================================

        direction_index = directions.index(
            self.swell_direction
        )

        degrees = direction_index * 22.5

        angle = math.radians(
            degrees - 90
        )

        # ====================================================
        # ARROW END
        # ====================================================

        arrow_length = radius * 0.62

        arrow_x = (
                self.compass_x
                + math.cos(angle)
                * arrow_length
        )

        arrow_y = (
                self.compass_y
                + math.sin(angle)
                * arrow_length
        )

        # ====================================================
        # ARROW SHADOW
        # ====================================================

        self.canvas.create_line(
            self.compass_x + 3,
            self.compass_y + 3,
            arrow_x + 3,
            arrow_y + 3,
            fill="#5B371A",
            width=8,
            capstyle=tk.ROUND,
            tags="compass"
        )

        # ====================================================
        # MAIN ARROW
        # ====================================================

        self.canvas.create_line(
            self.compass_x,
            self.compass_y,
            arrow_x,
            arrow_y,
            fill="#E4572E",
            width=5,
            arrow=tk.LAST,
            arrowshape=(
                int(radius * 0.22),
                int(radius * 0.28),
                int(radius * 0.08)
            ),
            capstyle=tk.ROUND,
            tags="compass"
        )

        # ====================================================
        # CENTRE DOT
        # ====================================================

        centre_size = radius * 0.10

        self.canvas.create_oval(
            self.compass_x - centre_size,
            self.compass_y - centre_size,
            self.compass_x + centre_size,
            self.compass_y + centre_size,
            fill="#264653",
            outline="#F3D99A",
            width=2,
            tags="compass"
        )

        # ====================================================
        # CURRENT DIRECTION TEXT
        # ====================================================

        self.canvas.create_text(
            self.compass_x,
            self.compass_y + radius + 25,
            text=f"SWELL: {self.swell_direction}",
            fill="#FFF0CF",
            font=("Arial", 12, "bold"),
            tags="compass"
        )

        # Keep compass above background

        self.canvas.tag_raise("compass")

    # ========================================================
    # DRAW WINDSOCK
    # ========================================================

    # ========================================================
    # DRAW WINDSOCK
    # ========================================================

    # ========================================================
    # DRAW WINDSOCK
    # ========================================================

    def draw_windsock(self):

        # ====================================================
        # DELETE OLD WINDSOCK
        # ====================================================

        self.canvas.delete("windsock")

        width = self.winfo_width()
        height = self.winfo_height()

        if width < 100 or height < 100:
            return

        # ====================================================
        # POSITION
        # ====================================================

        self.windsock_x = width * 0.7
        self.windsock_y = height * 0.84

        base_x = self.windsock_x
        base_y = self.windsock_y

        # ====================================================
        # SIZE
        # ====================================================

        max_length = min(
            width * 0.17,
            height * 0.19
        )

        min_length = max_length * 0.28

        speed_fraction = max(
            0.0,
            min(
                self.wind_speed / MAX_WIND_SPEED,
                1.0
            )
        )

        sock_length = (
            min_length
            + (max_length - min_length)
            * speed_fraction
        )

        sock_width = max(
            20,
            sock_length * 0.36
        )

        pulse = 0.5 + 0.5 * math.sin(self.wind_pulse_phase)

        self.windsock_radius = max_length * 0.82

        # ====================================================
        # COMPASS DIRECTIONS
        # ====================================================

        directions = [
            "N", "NNE", "NE", "ENE",
            "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW",
            "W", "WNW", "NW", "NNW"
        ]

        direction_index = directions.index(
            self.wind_direction
        )

        # Wind comes FROM self.wind_direction.
        # The sock points AWAY from it, like a real windsock.

        wind_from_degrees = direction_index * 22.5
        sock_degrees = (wind_from_degrees + 180) % 360

        # Convert compass angle to canvas angle

        sock_angle = math.radians(sock_degrees - 90)

        direction_x = math.cos(sock_angle)
        direction_y = math.sin(sock_angle)
        perp_x = -direction_y
        perp_y = direction_x

        tip_x = base_x + direction_x * sock_length
        tip_y = base_y + direction_y * sock_length

        # Soft ambient shadow so the control floats above the scene.

        shadow_x = base_x + direction_x * 6 + perp_x * 5
        shadow_y = base_y + direction_y * 6 + perp_y * 5

        self.canvas.create_oval(
            shadow_x - sock_width * (0.58 + pulse * 0.02),
            shadow_y - sock_width * (0.45 + pulse * 0.02),
            shadow_x + sock_length * (0.92 + pulse * 0.02),
            shadow_y + sock_width * (0.48 + pulse * 0.02),
            fill="#1B2D33",
            outline="",
            tags="windsock"
        )

        self.canvas.create_oval(
            base_x - sock_width * (0.68 + pulse * 0.03),
            base_y - sock_width * (0.50 + pulse * 0.03),
            tip_x + sock_width * (0.22 + pulse * 0.03),
            tip_y + sock_width * (0.46 + pulse * 0.03),
            outline="#F2D69A",
            width=1 + pulse * 1.2,
            tags="windsock"
        )

        # Base mount

        mount_radius = max(10, sock_width * 0.18)

        self.canvas.create_oval(
            base_x - mount_radius - 3,
            base_y - mount_radius - 3,
            base_x + mount_radius + 3,
            base_y + mount_radius + 3,
            fill="#2A1810",
            outline="",
            tags="windsock"
        )

        self.canvas.create_oval(
            base_x - mount_radius,
            base_y - mount_radius,
            base_x + mount_radius,
            base_y + mount_radius,
            fill="#8C5A2B",
            outline="#F1D08A",
            width=2,
            tags="windsock"
        )

        self.canvas.create_oval(
            base_x - mount_radius * 0.42,
            base_y - mount_radius * 0.42,
            base_x + mount_radius * 0.42,
            base_y + mount_radius * 0.42,
            fill="#4A2B16",
            outline="",
            tags="windsock"
        )

        # Tether line gives the sock a clean attachment point.

        tether_x = base_x + direction_x * sock_width * 0.28
        tether_y = base_y + direction_y * sock_width * 0.28

        self.canvas.create_line(
            base_x,
            base_y,
            tether_x,
            tether_y,
            fill="#F1D08A",
            width=2 + pulse * 0.6,
            capstyle=tk.ROUND,
            tags="windsock"
        )

        # Main sock body as a polished top-down banner.

        segments = 6
        segment_length = sock_length / segments
        start_width = sock_width
        end_width = max(8, sock_width * 0.38)
        palette = [
            "#B33A2F",
            "#F4E6D0",
            "#C84A37",
            "#F8F1E8",
            "#A8352C",
            "#F0D6BB",
        ]

        for i in range(segments):
            frac0 = i / segments
            frac1 = (i + 1) / segments

            seg_start_x = tether_x + direction_x * segment_length * i
            seg_start_y = tether_y + direction_y * segment_length * i
            seg_end_x = tether_x + direction_x * segment_length * (i + 1)
            seg_end_y = tether_y + direction_y * segment_length * (i + 1)

            width0 = start_width + (end_width - start_width) * frac0
            width1 = start_width + (end_width - start_width) * frac1

            p1 = (
                seg_start_x + perp_x * width0 / 2,
                seg_start_y + perp_y * width0 / 2,
            )
            p2 = (
                seg_end_x + perp_x * width1 / 2,
                seg_end_y + perp_y * width1 / 2,
            )
            p3 = (
                seg_end_x - perp_x * width1 / 2,
                seg_end_y - perp_y * width1 / 2,
            )
            p4 = (
                seg_start_x - perp_x * width0 / 2,
                seg_start_y - perp_y * width0 / 2,
            )

            self.canvas.create_polygon(
                p1,
                p2,
                p3,
                p4,
                fill=palette[i],
                outline="#7A3B2E",
                width=1,
                tags="windsock"
            )

        # A subtle highlight along the upper edge keeps it from feeling flat.

        highlight_start_x = tether_x + perp_x * (start_width * 0.30)
        highlight_start_y = tether_y + perp_y * (start_width * 0.30)
        highlight_end_x = tip_x + perp_x * (end_width * 0.22)
        highlight_end_y = tip_y + perp_y * (end_width * 0.22)

        self.canvas.create_line(
            highlight_start_x,
            highlight_start_y,
            highlight_end_x,
            highlight_end_y,
            fill="#FFF8EE",
            width=1.5 + pulse * 0.5,
            capstyle=tk.ROUND,
            tags="windsock"
        )

        # Rounded tip cap.

        self.canvas.create_oval(
            tip_x - 7,
            tip_y - 7,
            tip_x + 7,
            tip_y + 7,
            fill="#6E271F",
            outline="#F4D8B2",
            width=2,
            tags="windsock"
        )

        self.canvas.create_oval(
            tip_x - 3,
            tip_y - 3,
            tip_x + 3,
            tip_y + 3,
            fill="#FFF5E7",
            outline="",
            tags="windsock"
        )

        # ====================================================
        # LABEL
        # ====================================================

        label_w = 148
        label_h = 48
        label_x = self.windsock_x + width * 0.03
        label_y = self.windsock_y + height * 0.04

        self.draw_rounded_rect(
            label_x - label_w / 2 + 4,
            label_y - label_h / 2 + 4,
            label_x + label_w / 2 + 4,
            label_y + label_h / 2 + 4,
            18,
            fill="#10242D",
            outline="",
            tags="windsock"
        )

        self.draw_rounded_rect(
            label_x - label_w / 2,
            label_y - label_h / 2,
            label_x + label_w / 2,
            label_y + label_h / 2,
            18,
            fill="#274554",
            outline="#E0B365",
            width=2,
            tags="windsock"
        )

        self.canvas.create_text(
            label_x,
            label_y - 8,
            text=(
                f"WIND: {self.wind_direction}\n"
                f"{self.wind_speed:.1f} kt"
            ),
            fill="#FFF6E2",
            font=("Arial", 11, "bold"),
            tags="windsock"
        )

        self.canvas.tag_raise("windsock")

    # ========================================================
    # CHECK WHETHER MOUSE IS NEAR WINDSOCK
    # ========================================================

    def set_wind_direction_from_mouse(self, mouse_x, mouse_y):

        import math

        # ----------------------------------------------------
        # Position relative to the centre of the windsock
        # ----------------------------------------------------

        dx = mouse_x - self.windsock_x
        dy = mouse_y - self.windsock_y

        # Don't do anything if we are exactly in the centre
        if dx == 0 and dy == 0:
            return

        # ----------------------------------------------------
        # Calculate canvas angle
        # ----------------------------------------------------

        angle = math.degrees(
            math.atan2(dy, dx)
        )

        # Convert to compass angle
        #
        # Canvas:
        # right = 0°
        # down  = 90°
        #
        # Compass:
        # north = 0°
        # east  = 90°
        # ----------------------------------------------------

        compass_angle = (
                                angle + 90
                        ) % 360

        # ----------------------------------------------------
        # Convert to one of 16 directions
        # ----------------------------------------------------

        directions = [
            "N", "NNE", "NE", "ENE",
            "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW",
            "W", "WNW", "NW", "NNW"
        ]

        index = int(
            (
                    compass_angle + 11.25
            ) // 22.5
        ) % 16

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # The mouse points in the direction that the
        # windsock should visually point.
        #
        # But self.wind_direction represents where
        # the wind comes FROM.
        #
        # Therefore reverse by 180°.
        # ----------------------------------------------------

        wind_from_index = (
                                  index + 8
                          ) % 16

        self.wind_direction = directions[
            wind_from_index
        ]

        # ----------------------------------------------------
        # Redraw windsock
        # ----------------------------------------------------

        self.draw_windsock()

        # Keep wind slider visible
        self.draw_wind_slider()

    def is_near_windsock(self, x, y):

        distance = (
                           (x - self.windsock_x) ** 2
                           + (y - self.windsock_y) ** 2
                   ) ** 0.5

        return distance <= self.windsock_radius

    # ========================================================
    # SET WIND DIRECTION FROM MOUSE
    # ========================================================

    def set_wind_speed_from_mouse(self, mouse_y):

        mouse_y = max(
            self.wind_slider_top,
            min(
                self.wind_slider_bottom,
                mouse_y
            )
        )

        fraction = (
                           self.wind_slider_bottom - mouse_y
                   ) / (
                           self.wind_slider_bottom
                           - self.wind_slider_top
                   )

        self.wind_speed = (
                fraction
                * MAX_WIND_SPEED
        )

        # Redraw the complete wind widget
        self.draw_windsock()
        self.draw_wind_slider()

    # ========================================================
    # CHECK WHETHER MOUSE IS NEAR COMPASS
    # ========================================================

    def is_near_compass(self, x, y):

        distance = (
                           (x - self.compass_x) ** 2
                           + (y - self.compass_y) ** 2
                   ) ** 0.5

        return distance <= self.compass_radius * 1.3

    # ========================================================
    # DRAW WIND SPEED SLIDER
    # ========================================================

    def draw_wind_slider(self):

        # Delete the previous version of the slider
        self.canvas.delete("wind_slider")

        width = self.winfo_width()
        height = self.winfo_height()

        if width < 100 or height < 100:
            return

        rail_x = self.windsock_x - width * 0.13
        rail_top = self.windsock_y - height * 0.10
        rail_bottom = self.windsock_y + height * 0.10

        # Save the positions for mouse interaction

        self.wind_slider_x = rail_x
        self.wind_slider_top = rail_top
        self.wind_slider_bottom = rail_bottom

        # ====================================================
        # CURRENT HANDLE POSITION
        #
        # 0 kt = bottom
        # 40 kt = top
        # ====================================================

        fraction = self.wind_speed / MAX_WIND_SPEED

        knob_y = (
                rail_bottom
                - fraction
                * (rail_bottom - rail_top)
        )

        pulse = 0.5 + 0.5 * math.sin(self.wind_pulse_phase)

        panel_left = rail_x - 66
        panel_right = rail_x + 58
        panel_top = rail_top - 54
        panel_bottom = rail_bottom + 54

        # Soft floating panel behind the control.

        self.draw_rounded_rect(
            panel_left + 5,
            panel_top + 6,
            panel_right + 5,
            panel_bottom + 6,
            24,
            fill="#12252E",
            outline="",
            tags="wind_slider"
        )

        self.draw_rounded_rect(
            panel_left,
            panel_top,
            panel_right,
            panel_bottom,
            24,
            fill="#28404E",
            outline="#E0B365",
            width=2,
            tags="wind_slider"
        )

        # Title and value badge.

        self.canvas.create_text(
            rail_x,
            rail_top - 36,
            text="WIND SPEED",
            fill="#FFF6E2",
            font=("Arial", 9, "bold"),
            tags="wind_slider"
        )

        self.draw_rounded_rect(
            rail_x - 42,
            rail_top - 26,
            rail_x + 42,
            rail_top - 2,
            12,
            fill="#10242D",
            outline="#E0B365",
            width=1,
            tags="wind_slider"
        )

        self.canvas.create_text(
            rail_x,
            rail_top - 14,
            text=f"{self.wind_speed:.1f} kt",
            fill="#F8E4B1",
            font=("Arial", 11, "bold"),
            tags="wind_slider"
        )

        # Track shadow and fill.

        self.canvas.create_line(
            rail_x + 4,
            rail_top,
            rail_x + 4,
            rail_bottom,
            fill="#0F2028",
            width=14,
            capstyle=tk.ROUND,
            tags="wind_slider"
        )

        self.canvas.create_line(
            rail_x,
            rail_top,
            rail_x,
            rail_bottom,
            fill="#B77B36",
            width=8,
            capstyle=tk.ROUND,
            tags="wind_slider"
        )

        self.canvas.create_line(
            rail_x - 2,
            rail_top + 3,
            rail_x - 2,
            rail_bottom - 3,
            fill="#F2D69A",
            width=2,
            capstyle=tk.ROUND,
            tags="wind_slider"
        )

        # Filled wind column shows intensity.

        fill_top = knob_y

        self.canvas.create_line(
            rail_x,
            fill_top,
            rail_x,
            rail_bottom,
            fill="#E4572E",
            width=7,
            capstyle=tk.ROUND,
            tags="wind_slider"
        )

        # Accent ticks and labels.

        marker_values = [0, 10, 20, 30, 40]

        for value in marker_values:
            marker_fraction = value / MAX_WIND_SPEED

            marker_y = (
                    rail_bottom
                    - marker_fraction
                    * (rail_bottom - rail_top)
            )

            self.canvas.create_line(
                rail_x + 14,
                marker_y,
                rail_x + 22,
                marker_y,
                fill="#F8E4B1",
                width=2,
                tags="wind_slider"
            )

            self.canvas.create_text(
                rail_x + 30,
                marker_y,
                text=str(value),
                anchor="w",
                fill="#FFF6E2",
                font=("Arial", 8, "bold"),
                tags="wind_slider"
            )

        # Thumb shadow and thumb.

        self.canvas.create_oval(
            rail_x - 15 - pulse,
            knob_y - 15 - pulse,
            rail_x + 15 + pulse,
            knob_y + 15 + pulse,
            fill="#1A0F08",
            outline="",
            tags="wind_slider"
        )

        self.canvas.create_oval(
            rail_x - 12,
            knob_y - 12,
            rail_x + 12,
            knob_y + 12,
            fill="#F2B44D",
            outline="#FFF0CF",
            width=2,
            tags="wind_slider"
        )

        self.canvas.create_oval(
            rail_x - 6,
            knob_y - 6,
            rail_x + 6,
            knob_y + 6,
            fill="#E4572E",
            outline="",
            tags="wind_slider"
        )

        self.canvas.create_oval(
            rail_x - 7,
            knob_y - 11,
            rail_x - 1,
            knob_y - 5,
            fill="#FFF3DC",
            outline="",
            tags="wind_slider"
        )

        # Bottom label.

        self.draw_rounded_rect(
            rail_x - 32,
            rail_bottom + 16,
            rail_x + 32,
            rail_bottom + 40,
            12,
            fill="#10242D",
            outline="#E0B365",
            width=1,
            tags="wind_slider"
        )

        self.canvas.create_text(
            rail_x,
            rail_bottom + 28,
            text="WIND",
            fill="#FFF6E2",
            font=("Arial", 9, "bold"),
            tags="wind_slider"
        )

        # Keep slider visible

        self.canvas.tag_raise("wind_slider")

    def animate_wind_cluster(self):

        self.wind_pulse_phase += 0.12

        self.canvas.delete("windsock")
        self.canvas.delete("wind_slider")
        self.canvas.delete("wind_cluster")

        self.draw_wind_cluster_panel()
        self.draw_windsock()
        self.draw_wind_slider()

        self.wind_animation_job = self.after(
            90,
            self.animate_wind_cluster
        )

    # ========================================================
    # CHECK WHETHER MOUSE IS NEAR WIND SLIDER
    # ========================================================

    def is_near_wind_slider(self, x, y):

        horizontal_distance = abs(
            x - self.wind_slider_x
        )

        return (
                horizontal_distance < 45
                and
                self.wind_slider_top - 20
                <= y
                <=
                self.wind_slider_bottom + 20
        )

    # ========================================================
    # SET WIND SPEED FROM MOUSE
    # ========================================================

    def set_wind_speed_from_mouse(self, mouse_y):

        # Keep the handle inside the rail

        mouse_y = max(
            self.wind_slider_top,
            min(
                self.wind_slider_bottom,
                mouse_y
            )
        )

        # Convert mouse position to wind speed

        fraction = (
                           self.wind_slider_bottom - mouse_y
                   ) / (
                           self.wind_slider_bottom
                           - self.wind_slider_top
                   )

        self.wind_speed = (
                fraction
                * MAX_WIND_SPEED
        )

        # Redraw both widgets so the wind indicator updates live

        self.draw_windsock()
        self.draw_wind_slider()

    # ========================================================
    # SET SWELL DIRECTION FROM MOUSE
    # ========================================================

    def set_direction_from_mouse(self, x, y):

        import math

        directions = [
            "N", "NNE", "NE", "ENE",
            "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW",
            "W", "WNW", "NW", "NNW"
        ]

        # Distance from compass centre

        dx = x - self.compass_x
        dy = y - self.compass_y

        # ----------------------------------------------------
        # Calculate angle
        #
        # atan2(dx, -dy) means:
        #
        #       N = 0°
        #       E = 90°
        #       S = 180°
        #       W = 270°
        # ----------------------------------------------------

        angle = math.degrees(
            math.atan2(
                dx,
                -dy
            )
        )

        angle = angle % 360

        # ----------------------------------------------------
        # Snap to nearest 22.5 degrees
        # ----------------------------------------------------

        direction_index = int(
            (angle + 11.25)
            / 22.5
        ) % 16

        self.swell_direction = directions[
            direction_index
        ]

        # Redraw compass only

        self.draw_compass()

    def is_near_slider(self, x, y):

        width = self.winfo_width()
        height = self.winfo_height()

        rail_x = width * 0.058

        rail_top = height * 0.30
        rail_bottom = height * 0.76

        # Give the user a reasonably large touch area
        # around the thin bamboo.

        horizontal_distance = abs(
            x - rail_x
        )

        return (
            horizontal_distance < 45
            and
            rail_top - 20
            <= y
            <=
            rail_bottom + 20
        )

    # ========================================================
    # CLICK
    # ========================================================

    def canvas_click(self, event):

        # SWELL HEIGHT

        if self.is_near_slider(
                event.x,
                event.y
        ):

            self.set_swell_from_mouse(
                event.y
            )

        # SWELL DIRECTION

        elif self.is_near_compass(
                event.x,
                event.y
        ):

            self.set_direction_from_mouse(
                event.x,
                event.y
            )

        # WIND SPEED

        elif self.is_near_wind_slider(
                event.x,
                event.y
        ):

            self.set_wind_speed_from_mouse(
                event.y
            )

        # WIND DIRECTION

        elif self.is_near_windsock(
                event.x,
                event.y
        ):

            self.set_wind_direction_from_mouse(
                event.x,
                event.y
            )

    # ========================================================
    # DRAG
    # ========================================================

    def canvas_drag(self, event):

        # SWELL HEIGHT

        if self.is_near_slider(
                event.x,
                event.y
        ):

            self.set_swell_from_mouse(
                event.y
            )

        # SWELL DIRECTION

        elif self.is_near_compass(
                event.x,
                event.y
        ):

            self.set_direction_from_mouse(
                event.x,
                event.y
            )

        # WIND SPEED

        elif self.is_near_wind_slider(
                event.x,
                event.y
        ):

            self.set_wind_speed_from_mouse(
                event.y
            )

        # WIND DIRECTION

        elif self.is_near_windsock(
                event.x,
                event.y
        ):

            self.set_wind_direction_from_mouse(
                event.x,
                event.y
            )

    # ========================================================
    # MOUSE POSITION → SWELL
    # ========================================================

    def set_swell_from_mouse(self, mouse_y):

        width = self.winfo_width()
        height = self.winfo_height()

        rail_top = height * 0.30
        rail_bottom = height * 0.76

        # ----------------------------------------------------
        # Limit movement
        # ----------------------------------------------------

        mouse_y = max(
            rail_top,
            min(
                rail_bottom,
                mouse_y
            )
        )

        # ----------------------------------------------------
        # Convert position to swell
        #
        # TOP    = 3.0 m
        # BOTTOM = 0.0 m
        # ----------------------------------------------------

        fraction = (
            rail_bottom - mouse_y
        ) / (
            rail_bottom - rail_top
        )

        # IMPORTANT:
        # Keep this continuous.

        self.swell = (
            fraction
            * MAX_SWELL
        )

        # ----------------------------------------------------
        # Background changes if necessary
        # ----------------------------------------------------

        self.create_background()

        # ----------------------------------------------------
        # Redraw slider
        # ----------------------------------------------------

        self.draw_slider()

    # ========================================================
    # UPDATE
    # ========================================================

    def update_scene(self):

        self.create_background()

        self.draw_slider()

        self.draw_compass()

        self.canvas.delete("ui_panels")
        self.spot_selector_window_id = None

        self.draw_wind_cluster_panel()

        self.draw_windsock()

        self.draw_wind_slider()

        self.draw_spot_card()

        self.draw_verdict_card()

        if self.wind_animation_job is None:
            self.animate_wind_cluster()

    # ========================================================
    # RESIZE
    # ========================================================

    def on_resize(self, event):

        if event.widget != self:
            return

        self.after_idle(
            self.update_scene
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app = SurfApp()

    app.mainloop()
