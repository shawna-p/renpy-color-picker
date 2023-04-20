################################################################################
## SHADERS
################################################################################
init python:
    ## A shader which creates a gradient for a colour picker.
    renpy.register_shader("feniks.color_picker", variables="""
        uniform vec4 u_gradient_top_right;
        uniform vec2 u_model_size;
        varying float v_gradient_x_done;
        varying float v_gradient_y_done;
        attribute vec4 a_position;
    """, vertex_300="""
        v_gradient_x_done = a_position.x / u_model_size.x;
        v_gradient_y_done = a_position.y / u_model_size.y;
    """, fragment_300="""
        float left_gradient = v_gradient_x_done;
        float top_gradient = v_gradient_y_done;
        vec4 white = vec4(1.0);
        vec4 black = vec4(0.0, 0.0, 0.0, 1.0);
        // Mix white and the colour
        gl_FragColor = mix(white, u_gradient_top_right, left_gradient);
        // Mix that with black
        gl_FragColor = mix(black, gl_FragColor, 1.0-top_gradient);
    """)

    ## A shader which creates a spectrum. Generally for colour pickers.
    renpy.register_shader("feniks.spectrum", variables="""
        uniform float u_lightness;
        uniform float u_saturation;
        uniform float u_horizontal;
        uniform vec2 u_model_size;
        varying float v_gradient_x_done;
        varying float v_gradient_y_done;
        attribute vec4 a_position;
    """, vertex_300="""
        v_gradient_x_done = a_position.x / u_model_size.x;
        v_gradient_y_done = a_position.y / u_model_size.y;
    """, fragment_functions="""
    // HSL to RGB conversion adapted from https://stackoverflow.com/questions/2353211/hsl-to-rgb-color-conversion
    float hue2rgb(float p, float q, float t){
        if(t < 0.) t += 1.;
        if(t > 1.) t -= 1.;
        if(t < 1./6.) return p + (q - p) * 6. * t;
        if(t < 1./2.) return q;
        if(t < 2./3.) return p + (q - p) * (2./3. - t) * 6.;
        return p;
    }
    vec3 hslToRgb(float h, float l, float s) {
        float q = l < 0.5 ? l * (1. + s) : l + s - l * s;
        float p = 2 * l - q;
        float r = hue2rgb(p, q, h + 1./3.);
        float g = hue2rgb(p, q, h);
        float b = hue2rgb(p, q, h - 1./3.);
        return vec3(r, g, b);
    }
    """, fragment_300="""
        float hue = u_horizontal > 0.5 ? v_gradient_x_done : 1.0-v_gradient_y_done;
        vec3 rgb = hslToRgb(hue, u_lightness, u_saturation);
        gl_FragColor = vec4(rgb.r, rgb.g, rgb.b, 1.0);
    """)

## A transform which creates a spectrum.
## If horizontal is True, the spectrum goes from left to right instead of
## top to bottom. You can also adjust the lightness and saturation (between 0 and 1).
transform spectrum(horizontal=True, light=0.5, sat=1.0):
    shader "feniks.spectrum"
    u_lightness light
    u_saturation sat
    u_horizontal float(horizontal)

## A transform which creates a square with a gradient from the top right
transform color_picker(color):
    shader "feniks.color_picker"
    u_gradient_top_right Color(color).rgba

################################################################################
## CLASSES AND FUNCTIONS
################################################################################
init python:

    import pygame
    class ColorPicker(renpy.Displayable):
        """
        A CDD which allows the player to pick a colour between four
        quadrants, with the top left being pure white, the bottom left
        and right being pure black, and the top right being a pure hue.

        Attributes
        ----------
        xsize : int
            The width of the colour picker.
        ysize : int
            The height of the colour picker.
        color : Color
            The current colour the colour picker is focused over.
        selector_xpos : float
            The xpos of the colour selector.
        selector_ypos : float
            The ypos of the colour selector.
        picker : Displayable
            A square that is used to display the colour picker.
        hue_rotation : float
            The amount the current hue is rotated by.
        dragging : bool
            True if the indicator is currently being dragged around.
        """
        RED = Color("#f00")
        def __init__(self, xsize, ysize, start_color="#f00", **kwargs):
            """
            Create a ColorPicker object.

            Parameters:
            -----------
            xsize : int
                The width of the colour picker.
            ysize : int
                The height of the colour picker.
            start_color : str
                A hexadecimal colour code corresponding to the starting colour.
            """
            super(ColorPicker, self).__init__(**kwargs)
            self.xsize = xsize
            self.ysize = ysize

            self.set_color(start_color)
            self.picker = Transform("#fff", xysize=(self.xsize, self.ysize))
            self.dragging = False

        def set_color(self, color):
            """
            Set the current colour of the colour picker.

            Parameters
            ----------
            color : Color
                The new colour to set the colour picker to.
            """
            self.color = Color(color)
            self.selector_xpos = self.color.hsv[1]
            self.selector_ypos = 1.0 - self.color.hsv[2]
            self.hue_rotation = self.color.hsv[0]

        def visit(self):
            return [Image("selector")]

        def render(self, width, height, st, at):
            """
            Render the displayable to the screen.
            """
            r = renpy.Render(self.xsize, self.ysize)

            trc = self.RED.rotate_hue(self.hue_rotation)
            # Colorize the picker into a gradient
            picker = At(self.picker, color_picker(trc))
            # Position the selector
            selector = Transform("selector", anchor=(0.5, 0.5),
                xpos=self.selector_xpos, ypos=self.selector_ypos)
            final = Fixed(picker, selector, xysize=(self.xsize, self.ysize))
            # Render it to the screen
            ren = renpy.render(final, self.xsize, self.ysize, st, at)
            r.blit(ren, (0, 0))
            renpy.redraw(self, 0)
            return r

        def event(self, ev, x, y, st):
            """Allow the user to drag their mouse to select a colour."""
            relative_x = x/float(self.xsize)
            relative_y = y/float(self.ysize)

            in_range = ((0.0 <= relative_x <= 1.0) and (0.0 <= relative_y <= 1.0))

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and in_range:
                self.dragging = True
                self.selector_xpos = relative_x
                self.selector_ypos = relative_y
            elif ev.type == pygame.MOUSEMOTION and self.dragging:
                self.selector_xpos = relative_x
                self.selector_ypos = relative_y
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                self.dragging = False
                ## Update the screen
                renpy.restart_interaction()

            # Limit x/ypos
            self.selector_xpos = min(max(self.selector_xpos, 0.0), 1.0)
            self.selector_ypos = min(max(self.selector_ypos, 0.0), 1.0)

            # Figure out the colour under the selector
            trc = self.RED.rotate_hue(self.hue_rotation)
            self.color = Color("#fff").interpolate(trc, self.selector_xpos)
            self.color = self.color.interpolate(Color("#000"), self.selector_ypos)
            return None

    def picker_color(st, at, picker, xsize=100, ysize=100):
        """
        A DynamicDisplayable function to update the colour picker swatch.

        Parameters:
        -----------
        picker : ColorPicker
            The picker this swatch is made from.
        xsize : int
            The width of the swatch.
        ysize : int
            The height of the swatch.
        """
        return Transform(picker.color, xysize=(xsize, ysize)), 0.01

    def picker_hexcode(st, at, picker):
        """
        A brief DynamicDisplayable demonstration of how to display color
        information in real-time.
        """
        return Fixed(Text(picker.color.hexcode), xysize=(200, 40)), 0.01

################################################################################
## IMAGES
################################################################################
## Used for both the spectrum thumb and the colour indicator. Can be changed.
image selector_bg = Frame("selector.webp", 5, 5)
## The image used for the indicator showing the current colour.
image selector = Transform("selector_bg", xysize=(15, 15), anchor=(0.5, 0.5))

################################################################################
## SCREENS
################################################################################
## A sample screen to demonstrate the colour picker.
## Simply write `call screen color_picker()` to test it.
screen color_picker():

    ## The picker itself. Its size is 700x700 with the starting colour #8b0f55.
    ## You may declare this outside of the screen to make it easier to access.
    default picker = ColorPicker(700, 700, "#8b0f55")
    ## The preview swatch. Needs to be provided the picker variable from above.
    ## You can specify its size as well.
    default picker_color = DynamicDisplayable(picker_color, picker=picker,
        xsize=100, ysize=100)
    ## The hexcode of the current colour. Demonstrates updating the picker
    ## colour information in real-time.
    default picker_hex = DynamicDisplayable(picker_hexcode, picker=picker)

    ## This is an example of how you can swap between multiple colour swatches
    default color1 = "#fff"
    default color2 = "#fff"
    default current_color = 1

    add "#333"

    vbox:
        align (0.5, 0.5) spacing 25
        hbox:
            spacing 25
            ## A vertical bar which lets you change the hue of the picker.
            vbar value FieldValue(picker, "hue_rotation", 1.0):
                xysize (80, 700)
                base_bar At(Transform("#000", xysize=(50, 700)), spectrum(horizontal=False))
                thumb Transform("selector_bg", xysize=(50, 20))
                thumb_offset 10

            ## The picker itself
            add picker
            vbox:
                xsize 200 spacing 10
                ## The swatch
                ## If you only need one swatch, use this:
                add picker_color
                ## Otherwise, the following code lets you switch between
                ## two different swatches to choose more than one colour.
                # if current_color == 1:
                #     button:
                #         padding (4, 4) background "#fff"
                #         add picker_color
                # else:
                #     imagebutton:
                #         xysize (100, 100) padding (4, 4)
                #         idle color1 hover_foreground "#fff2"
                #         action [SetScreenVariable("color2", picker.color),
                #             Function(picker.set_color, color1),
                #             SetScreenVariable("current_color", 1)]
                # if current_color == 2:
                #     button:
                #         padding (4, 4) background "#fff"
                #         add picker_color
                # else:
                #     imagebutton:
                #         xysize (100, 100) padding (4, 4)
                #         idle color2 hover_foreground "#fff2"
                #         action [SetScreenVariable("color1", picker.color),
                #             Function(picker.set_color, color2),
                #             SetScreenVariable("current_color", 2)]
                ## End of multiple swatch code

                ## You can display other information on the color here, as desired
                ## Some examples are provided. Note that these do not update in
                ## tandem with the picker, but when the mouse is released. You
                ## will need to use a DynamicDisplayable for real-time updates.
                ## The hex code is provided as an example.
                add picker_hex ## The DynamicDisplayable from earlier
                ## These update when the mouse button is released
                text "R: [picker.color.rgb[0]:.2f]"
                text "G: [picker.color.rgb[1]:.2f]"
                text "B: [picker.color.rgb[2]:.2f]"

        ## A horizontal bar that lets you change the hue of the picker
        bar value FieldValue(picker, "hue_rotation", 1.0):
            xysize (700, 80) xpos 25+80
            base_bar At(Transform("#000", xysize=(700, 50)), spectrum())
            thumb Transform("selector_bg", xysize=(20, 50))
            thumb_offset 10

    ## In this case, the screen returns the picker's colour. The colour itself
    ## is always stored in the picker's `color` attribute.
    textbutton "Return" action Return(picker.color) align (1.0, 1.0)

################################################################################
## TESTING
################################################################################
default chosen_color = "#8b0f55"
label how_to_use_color_picker():
    "Soon, you will be shown a colour picker."
    call screen color_picker()
    ## The colour the picker returns is a Color object. It has a hexcode
    ## field to easily get the hexadecimal colour code.
    $ chosen_color = _return.hexcode
    ## This is used to put the returned colour into a colour text tag
    $ color_tag = "{color=%s}" % chosen_color
    "[color_tag]You chose the colour [chosen_color].{/color}"
    return

