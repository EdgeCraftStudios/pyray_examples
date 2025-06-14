"""raylib [text] example - Draw 3d
Example complexity rating: [★★★★] 4/4
NOTE: Draw a 2D text in 3D space, each letter is drawn in a quad (or 2 quads if backface is set)
where the texture coodinates of each quad map to the texture coordinates of the glyphs
inside the font texture.
A more efficient approach, i believe, would be to render the text in a render texture and
map that texture to a plane and render that, or maybe a shader but my method allows more
flexibility...for example to change position of each letter individually to make somethink
like a wavy text effect.
Special thanks to:
     @Nighten for the DrawTextStyle() code https://github.com/NightenDushi/Raylib_DrawTextStyle
     Chris Camacho (codifies - http://bedroomcoders.co.uk/) for the alpha discard shader
Example originally created with raylib 3.5, last time updated with raylib 4.0
Example contributed by Vlad Adrian (@demizdor) and reviewed by Ramon Santamaria (@raysan5)
Example licensed under an unmodified zlib/libpng license, which is an OSI-certified,
BSD-like license that allows static linking with closed source software
Copyright (c) 2021-2025 Vlad Adrian (@demizdor)

This source has been converted from C raylib examples to Python.
"""

import pyray as rl
import math
import random
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent

#--------------------------------------------------------------------------------------
# Globals
#--------------------------------------------------------------------------------------
LETTER_BOUNDRY_SIZE = 0.25
TEXT_MAX_LAYERS = 32
LETTER_BOUNDRY_COLOR = rl.VIOLET

SHOW_LETTER_BOUNDRY = False
SHOW_TEXT_BOUNDRY = False

#--------------------------------------------------------------------------------------
# Data Types definition
#--------------------------------------------------------------------------------------

# Configuration structure for waving the text
class WaveTextConfig:
    def __init__(self):
        self.wave_range = rl.Vector3(0, 0, 0)
        self.wave_speed = rl.Vector3(0, 0, 0)
        self.wave_offset = rl.Vector3(0, 0, 0)

#--------------------------------------------------------------------------------------
# Module Functions Declaration
#--------------------------------------------------------------------------------------
# Draw a codepoint in 3D space
# Update draw_text_codepoint_3d to render both front and back faces
def draw_text_codepoint_3d(font, codepoint, position, font_size, backface, tint):
    # Get the glyph index for the codepoint
    index = rl.get_glyph_index(font, codepoint)
    scale = font_size / font.baseSize

    # Calculate the source rectangle for the glyph
    src_rec = rl.Rectangle(
        font.recs[index].x,
        font.recs[index].y,
        font.recs[index].width,
        font.recs[index].height
    )

    # Calculate the destination rectangle in 3D space
    dest_rec = rl.Rectangle(
        position.x + (font.glyphs[index].offsetX * scale),
        position.y + (font.glyphs[index].offsetY * scale),
        font.recs[index].width * scale,
        font.recs[index].height * scale
    )

    # Draw the glyph texture for both front and back faces
    rl.draw_texture_pro(
        font.texture,
        src_rec,
        dest_rec,
        rl.Vector2(0, 0),  # No rotation offset
        0.0,               # No rotation
        tint
    )

    if backface:
        # Flip the texture for the back face
        flipped_src_rec = rl.Rectangle(
            src_rec.x + src_rec.width,
            src_rec.y,
            -src_rec.width,
            src_rec.height
        )
        rl.draw_texture_pro(
            font.texture,
            flipped_src_rec,
            dest_rec,
            rl.Vector2(0, 0),  # No rotation offset
            0.0,               # No rotation
            tint
        )

# Draw a 2D text in 3D space
def draw_text_3d(font, text, position, font_size, font_spacing, line_spacing, backface, tint):
    offset = rl.Vector3(position.x, position.y, position.z)
    for char in text:
        if char == '\n':
            offset.x = position.x
            offset.z += font_size + line_spacing
            continue
        draw_text_codepoint_3d(font, ord(char), offset, font_size, backface, tint)
        offset.x += font_size + font_spacing

# Draw a 2D text in 3D space and wave the parts that start with `~~` and end with `~~`.
def draw_text_wave_3d(font, text, position, font_size, font_spacing, line_spacing, backface, config, time, tint):
    offset = rl.Vector3(position.x, position.y, position.z)
    wave_active = False
    for char in text:
        if char == '\n':
            offset.x = position.x
            offset.z += font_size + line_spacing
            continue
        if char == '~':
            wave_active = not wave_active
            continue

        wave_offset = rl.Vector3(0, 0, 0)
        if wave_active:
            wave_offset.x = math.sin(time * config.wave_speed.x + offset.x * config.wave_offset.x) * config.wave_range.x
            wave_offset.y = math.sin(time * config.wave_speed.y + offset.y * config.wave_offset.y) * config.wave_range.y
            wave_offset.z = math.sin(time * config.wave_speed.z + offset.z * config.wave_offset.z) * config.wave_range.z

        draw_text_codepoint_3d(font, ord(char), rl.Vector3(offset.x + wave_offset.x, offset.y + wave_offset.y, offset.z + wave_offset.z), font_size, backface, tint)
        offset.x += font_size + font_spacing

# Measure a text in 3D ignoring the `~~` chars.
def measure_text_wave_3d(font, text, font_size, font_spacing, line_spacing):
    # Implementation would go here - measurement function
    # This is a placeholder as the function is extensive in the C version
    return rl.Vector3(0, 0, 0)

# Generates a nice color with a random hue
def generate_random_color(s, v):
    phi = 0.618033988749895  # Golden ratio conjugate
    h = random.randint(0, 360)
    h = (h + h * phi) % 360.0
    return rl.color_from_hsv(h, s, v)

#------------------------------------------------------------------------------------
# Program main entry point
#------------------------------------------------------------------------------------
def main():
    global SHOW_LETTER_BOUNDRY, SHOW_TEXT_BOUNDRY
    
    # Initialization
    screen_width = 800
    screen_height = 450

    rl.set_config_flags(rl.FLAG_MSAA_4X_HINT | rl.FLAG_VSYNC_HINT)
    rl.init_window(screen_width, screen_height, "raylib [text] example - draw 2D text in 3D")

    spin = True        # Spin the camera?
    multicolor = False # Multicolor mode

    # Define the camera to look into our 3d world
    camera = rl.Camera3D()
    camera.position = rl.Vector3(-10.0, 15.0, -10.0)   # Camera position
    camera.target = rl.Vector3(0.0, 0.0, 0.0)          # Camera looking at point
    camera.up = rl.Vector3(0.0, 1.0, 0.0)              # Camera up vector (rotation towards target)
    camera.fovy = 45.0                                 # Camera field-of-view Y
    camera.projection = rl.CAMERA_PERSPECTIVE          # Camera projection type

    camera_mode = rl.CAMERA_ORBITAL

    cube_position = rl.Vector3(0.0, 1.0, 0.0)
    cube_size = rl.Vector3(2.0, 2.0, 2.0)

    # Use the default font
    font = rl.get_font_default()
    font_size = 0.8
    font_spacing = 0.05
    line_spacing = -0.1

    # Set the text (using markdown!)
    text = "Hello ~~World~~ in 3D!"
    tbox = rl.Vector3(0, 0, 0)
    layers = 1
    quads = 0
    layer_distance = 0.01

    wcfg = WaveTextConfig()
    wcfg.wave_speed.x = wcfg.wave_speed.y = 3.0
    wcfg.wave_speed.z = 0.5
    wcfg.wave_offset.x = wcfg.wave_offset.y = wcfg.wave_offset.z = 0.35
    wcfg.wave_range.x = wcfg.wave_range.y = wcfg.wave_range.z = 0.45

    time = 0.0

    # Setup a light and dark color
    light = rl.MAROON
    dark = rl.RED

    # Load the alpha discard shader
    alpha_discard = rl.load_shader(
        "",  # Use default vertex shader as in the C example
        str(THIS_DIR/"resources/shaders/glsl330/alpha_discard.fs")
    )

    # Array filled with multiple random colors (when multicolor mode is set)
    multi = [rl.Color(0, 0, 0, 0) for _ in range(TEXT_MAX_LAYERS)]

    rl.disable_cursor()  # Limit cursor to relative movement inside the window

    rl.set_target_fps(60)  # Set our game to run at 60 frames-per-second

    # Main game loop
    while not rl.window_should_close():  # Detect window close button or ESC key
        # Update
        rl.update_camera(rl.ffi.addressof(camera), camera_mode)
        
        # Handle font files dropped
        if rl.is_file_dropped():
            dropped_files = rl.load_dropped_files()

            # NOTE: We only support first ttf file dropped
            if rl.is_file_extension(dropped_files.paths[0], ".ttf"):
                rl.unload_font(font)
                font = rl.load_font_ex(dropped_files.paths[0], int(font_size), None, 0)
            elif rl.is_file_extension(dropped_files.paths[0], ".fnt"):
                rl.unload_font(font)
                font = rl.load_font(dropped_files.paths[0])
                font_size = float(font.baseSize)
            
            rl.unload_dropped_files(dropped_files)  # Unload filepaths from memory

        # Handle Events
        if rl.is_key_pressed(rl.KEY_F1):
            SHOW_LETTER_BOUNDRY = not SHOW_LETTER_BOUNDRY
        if rl.is_key_pressed(rl.KEY_F2):
            SHOW_TEXT_BOUNDRY = not SHOW_TEXT_BOUNDRY
        if rl.is_key_pressed(rl.KEY_F3):
            # Handle camera change
            spin = not spin
            # we need to reset the camera when changing modes
            camera = rl.Camera3D()
            camera.target = rl.Vector3(0.0, 0.0, 0.0)          # Camera looking at point
            camera.up = rl.Vector3(0.0, 1.0, 0.0)              # Camera up vector (rotation towards target)
            camera.fovy = 45.0                                  # Camera field-of-view Y
            camera.projection = rl.CAMERA_PERSPECTIVE           # Camera mode type

            if spin:
                camera.position = rl.Vector3(-10.0, 15.0, -10.0)   # Camera position
                camera_mode = rl.CAMERA_ORBITAL
            else:
                camera.position = rl.Vector3(10.0, 10.0, -10.0)   # Camera position
                camera_mode = rl.CAMERA_FREE

        # Handle clicking the cube
        if rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT):
            ray = rl.get_screen_to_world_ray(rl.get_mouse_position(), camera)

            # Check collision between ray and box
            box_min = rl.Vector3(cube_position.x - cube_size.x/2, cube_position.y - cube_size.y/2, cube_position.z - cube_size.z/2)
            box_max = rl.Vector3(cube_position.x + cube_size.x/2, cube_position.y + cube_size.y/2, cube_position.z + cube_size.z/2)
            bounding_box = rl.BoundingBox(box_min, box_max)
            collision = rl.get_ray_collision_box(ray, bounding_box)
            
            if collision.hit:
                # Generate new random colors
                light = generate_random_color(0.5, 0.78)
                dark = generate_random_color(0.4, 0.58)

        # Handle text layers changes
        if rl.is_key_pressed(rl.KEY_HOME):
            if layers > 1:
                layers -= 1
        elif rl.is_key_pressed(rl.KEY_END):
            if layers < TEXT_MAX_LAYERS:
                layers += 1

        # Handle text changes
        if rl.is_key_pressed(rl.KEY_LEFT):
            font_size -= 0.5
        elif rl.is_key_pressed(rl.KEY_RIGHT):
            font_size += 0.5
        elif rl.is_key_pressed(rl.KEY_UP):
            font_spacing -= 0.1
        elif rl.is_key_pressed(rl.KEY_DOWN):
            font_spacing += 0.1
        elif rl.is_key_pressed(rl.KEY_PAGE_UP):
            line_spacing -= 0.1
        elif rl.is_key_pressed(rl.KEY_PAGE_DOWN):
            line_spacing += 0.1
        elif rl.is_key_down(rl.KEY_INSERT):
            layer_distance -= 0.001
        elif rl.is_key_down(rl.KEY_DELETE):
            layer_distance += 0.001
        elif rl.is_key_pressed(rl.KEY_TAB):
            multicolor = not multicolor   # Enable /disable multicolor mode

            if multicolor:
                # Fill color array with random colors
                for i in range(TEXT_MAX_LAYERS):
                    multi[i] = generate_random_color(0.5, 0.8)
                    multi[i].a = random.randint(0, 255)

        # Handle text input
        ch = rl.get_char_pressed()
        
        # Drawing
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        
        rl.begin_mode_3d(camera)
        
        # Draw a cube as reference
        rl.draw_cube(cube_position, cube_size.x, cube_size.y, cube_size.z, light)
        rl.draw_cube_wires(cube_position, cube_size.x, cube_size.y, cube_size.z, dark)
        rl.draw_grid(10, 2.0)

        # Use the alpha discard shader for 3D text (as in C example)
        rl.begin_shader_mode(alpha_discard)
        # Draw the waving 3D text above the cube (approximate position)
        draw_text_wave_3d(font, text, rl.Vector3(0, 2.5, 0), font_size, font_spacing, line_spacing, True, wcfg, time, rl.DARKBLUE)
        rl.end_shader_mode()
        
        rl.end_mode_3d()

        # Draw background text on a 3D plane
        rl.begin_shader_mode(alpha_discard)
        draw_text_3d(font, "Background Text", rl.Vector3(-5, 0.1, 5), font_size * 0.5, font_spacing * 0.5, line_spacing * 0.5, True, rl.GRAY)
        rl.end_shader_mode()

        # Draw info boxes (adjusted for C example style)
        rl.draw_rectangle(0, 0, screen_width, 80, rl.fade(rl.BLACK, 0.7))
        rl.draw_text("Drag & drop a font file to change the font!", 10, 10, 20, rl.GREEN)
        rl.draw_text("Press [F3] to toggle the camera", 10, 35, 20, rl.GREEN)
        rl.draw_text(f"Text Size [L/R]: {font_size:.2f}", 10, 60, 18, rl.GREEN)
        rl.draw_text(f"Font Spacing [U/D]: {font_spacing:.2f}", 250, 60, 18, rl.GREEN)
        rl.draw_text(f"Line Spacing [PGUP/PGDN]: {line_spacing:.2f}", 500, 60, 18, rl.GREEN)
        rl.draw_text(f"Layers [HOME/END]: {layers}", 10, 80, 18, rl.GREEN)
        rl.draw_text(f"Layer Distance [INS/DEL]: {layer_distance:.2f}", 250, 80, 18, rl.GREEN)
        rl.draw_text("TAB to change layer colors", 500, 80, 18, rl.GREEN)
        rl.draw_fps(10, screen_height - 30)
        
        rl.end_drawing()

        # Update time
        time += rl.get_frame_time()

    # De-Initialization
    rl.unload_shader(alpha_discard)  # Unload shader
    rl.close_window()                # Close window and OpenGL context

if __name__ == "__main__":
    main()