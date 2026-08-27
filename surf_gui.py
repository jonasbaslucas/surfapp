import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk


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

        import math

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

        sock_length = min(
            width * 0.13,
            height * 0.20
        )

        sock_width = sock_length * 0.28

        self.windsock_radius = sock_length * 0.85

        # ====================================================
        # WIND SPEED
        #
        # Convert 0–40 knots into 0.0–1.0
        # ====================================================

        wind_fraction = max(
            0.0,
            min(
                self.wind_speed / MAX_WIND_SPEED,
                1.0
            )
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

        direction_index = directions.index(
            self.wind_direction
        )

        # ====================================================
        # WIND DIRECTION
        #
        # Wind comes FROM self.wind_direction.
        # Windsock points AWAY from it.
        # ====================================================

        wind_from_degrees = direction_index * 22.5

        sock_degrees = (
                               wind_from_degrees + 180
                       ) % 360

        # Convert compass angle to canvas angle

        wind_angle = math.radians(
            sock_degrees - 90
        )

        # ====================================================
        # DRAW ATTACHMENT RING
        # ====================================================

        ring_radius = sock_width * 0.42

        self.canvas.create_oval(
            base_x - ring_radius,
            base_y - ring_radius,
            base_x + ring_radius,
            base_y + ring_radius,
            fill="#5B371A",
            outline="#E0B365",
            width=2,
            tags="windsock"
        )

        # ====================================================
        # COLOURS
        # ====================================================

        colors = [
            "#D64532",
            "#F4E6D0",
            "#D64532",
            "#F4E6D0",
            "#D64532"
        ]

        segments = 5

        segment_length = sock_length / segments

        # ====================================================
        # CALCULATE WINDSOCK PATH
        #
        # At 0 kt:
        # every segment points downward.
        #
        # At 40 kt:
        # every segment points completely in
        # the wind direction.
        #
        # In between:
        # the windsock gradually curves.
        # ====================================================

        points = []

        current_x = base_x
        current_y = base_y

        for i in range(segments + 1):

            if i == 0:
                points.append(
                    (current_x, current_y)
                )

                continue

            # ------------------------------------------------
            # Position along the windsock
            #
            # The end reacts more strongly to the wind
            # than the beginning.
            # ------------------------------------------------

            position_fraction = i / segments

            local_wind_effect = (
                    wind_fraction
                    * (
                            0.35
                            + 0.65 * position_fraction
                    )
            )

            # ------------------------------------------------
            # DOWNWARD DIRECTION
            # ------------------------------------------------

            down_angle = math.radians(90)

            # ------------------------------------------------
            # INTERPOLATE BETWEEN DOWN AND WIND DIRECTION
            #
            # Using sine/cosine interpolation avoids
            # problems with compass angles crossing 0°.
            # ------------------------------------------------

            down_x = math.cos(down_angle)
            down_y = math.sin(down_angle)

            wind_x = math.cos(wind_angle)
            wind_y = math.sin(wind_angle)

            direction_x = (
                    down_x * (1 - local_wind_effect)
                    + wind_x * local_wind_effect
            )

            direction_y = (
                    down_y * (1 - local_wind_effect)
                    + wind_y * local_wind_effect
            )

            # Normalize

            magnitude = math.sqrt(
                direction_x ** 2
                + direction_y ** 2
            )

            direction_x /= magnitude
            direction_y /= magnitude

            # Move along windsock

            current_x += (
                    direction_x
                    * segment_length
            )

            current_y += (
                    direction_y
                    * segment_length
            )

            points.append(
                (current_x, current_y)
            )

        # ====================================================
        # DRAW EACH WINDSOCK SEGMENT
        # ====================================================

        for i in range(segments):
            start_x, start_y = points[i]
            end_x, end_y = points[i + 1]

            # Direction of this segment

            dx = end_x - start_x
            dy = end_y - start_y

            length = math.sqrt(
                dx ** 2 + dy ** 2
            )

            # Perpendicular direction

            perp_x = -dy / length
            perp_y = dx / length

            # Tapering

            start_width = (
                    sock_width
                    * (
                            1
                            - 0.45 * (i / segments)
                    )
            )

            end_width = (
                    sock_width
                    * (
                            1
                            - 0.45 * ((i + 1) / segments)
                    )
            )

            # Four corners

            p1 = (
                start_x
                + perp_x * start_width / 2,

                start_y
                + perp_y * start_width / 2
            )

            p2 = (
                end_x
                + perp_x * end_width / 2,

                end_y
                + perp_y * end_width / 2
            )

            p3 = (
                end_x
                - perp_x * end_width / 2,

                end_y
                - perp_y * end_width / 2
            )

            p4 = (
                start_x
                - perp_x * start_width / 2,

                start_y
                - perp_y * start_width / 2
            )

            self.canvas.create_polygon(
                p1,
                p2,
                p3,
                p4,
                fill=colors[i],
                outline="#7A3B2E",
                width=1,
                tags="windsock"
            )

        # ====================================================
        # OPEN END
        # ====================================================

        end_x, end_y = points[-1]

        last_x, last_y = points[-2]

        dx = end_x - last_x
        dy = end_y - last_y

        length = math.sqrt(
            dx ** 2 + dy ** 2
        )

        perp_x = -dy / length
        perp_y = dx / length

        end_width = sock_width * 0.55

        end_top = (
            end_x
            + perp_x * end_width / 2,

            end_y
            + perp_y * end_width / 2
        )

        end_bottom = (
            end_x
            - perp_x * end_width / 2,

            end_y
            - perp_y * end_width / 2
        )

        self.canvas.create_line(
            end_top,
            end_bottom,
            fill="#7A3B2E",
            width=2,
            tags="windsock"
        )

        # ====================================================
        # LABEL
        # ====================================================

        self.canvas.create_text(
            self.windsock_x,
            self.windsock_y + sock_length * 1.15,
            text=(
                f"WIND: {self.wind_direction}\n"
                f"{self.wind_speed:.1f} kt"
            ),
            fill="#FFF0CF",
            font=("Arial", 12, "bold"),
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

        # ====================================================
        # SLIDER POSITION
        #
        # Place it LEFT of the windsock.
        #
        # Change these values later if necessary.
        # ====================================================

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

        # ====================================================
        # WIND SPEED VALUE
        # ====================================================

        self.canvas.create_text(
            rail_x,
            rail_top - 28,
            text=f"{self.wind_speed:.1f} kt",
            fill=TEXT_LIGHT,
            font=("Arial", 12, "bold"),
            tags="wind_slider"
        )

        # ====================================================
        # BAMBOO SHADOW
        # ====================================================

        self.canvas.create_line(
            rail_x + 3,
            rail_top,
            rail_x + 3,
            rail_bottom,
            fill=BAMBOO_DARK,
            width=11,
            capstyle=tk.ROUND,
            tags="wind_slider"
        )

        # ====================================================
        # BAMBOO MAIN
        # ====================================================

        self.canvas.create_line(
            rail_x,
            rail_top,
            rail_x,
            rail_bottom,
            fill=BAMBOO,
            width=8,
            capstyle=tk.ROUND,
            tags="wind_slider"
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
            tags="wind_slider"
        )

        # ====================================================
        # BAMBOO JOINTS
        # ====================================================

        for joint_fraction in (0.25, 0.50, 0.75):
            y = (
                    rail_top
                    + joint_fraction
                    * (rail_bottom - rail_top)
            )

            self.canvas.create_line(
                rail_x - 6,
                y,
                rail_x + 6,
                y,
                fill=BAMBOO_DARK,
                width=4,
                capstyle=tk.ROUND,
                tags="wind_slider"
            )

        # ====================================================
        # WIND SPEED MARKERS
        # ====================================================

        marker_values = [0, 10, 20, 30, 40]

        for value in marker_values:
            marker_fraction = value / MAX_WIND_SPEED

            marker_y = (
                    rail_bottom
                    - marker_fraction
                    * (rail_bottom - rail_top)
            )

            # Small marker

            self.canvas.create_line(
                rail_x + 10,
                marker_y,
                rail_x + 16,
                marker_y,
                fill=TEXT_LIGHT,
                width=2,
                tags="wind_slider"
            )

            # Number

            self.canvas.create_text(
                rail_x + 21,
                marker_y,
                text=str(value),
                anchor="w",
                fill=TEXT_LIGHT,
                font=("Arial", 8, "bold"),
                tags="wind_slider"
            )

        # ====================================================
        # HANDLE SHADOW
        # ====================================================

        self.canvas.create_oval(
            rail_x - 13,
            knob_y - 13,
            rail_x + 13,
            knob_y + 13,
            fill="#4A2B16",
            outline="",
            tags="wind_slider"
        )

        # ====================================================
        # HANDLE
        # ====================================================

        self.canvas.create_oval(
            rail_x - 10,
            knob_y - 10,
            rail_x + 10,
            knob_y + 10,
            fill="#E4572E",
            outline=TEXT_LIGHT,
            width=2,
            tags="wind_slider"
        )

        # ====================================================
        # LABEL
        # ====================================================

        self.canvas.create_text(
            rail_x,
            rail_bottom + 25,
            text="WIND",
            fill=TEXT_LIGHT,
            font=("Arial", 9, "bold"),
            tags="wind_slider"
        )

        # Keep slider visible

        self.canvas.tag_raise("wind_slider")

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

        # Redraw

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

        self.draw_windsock()

        self.draw_wind_slider()

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