
################################################################################
################################################################################
##
## COLOR PICKER EXAMPLES
##
################################################################################
## To quickly test these examples in your game, jump to the label
## how_to_use_color_picker i.e.
# jump how_to_use_color_picker

################################################################################
## IMAGES
################################################################################
## In order to avoid including unnecessary image files, the default version of
## these images constructs an image in code. You may, however, want to change
## it. The following code is provided as an example of how to do so.

## Used for both the spectrum thumb and the colour indicator. Can be changed.
# image selector_bg = Frame("selector.webp", 5, 5)

## The image used for the indicator showing the current colour.
# image selector = Transform("selector_bg", xysize=(15, 15))

################################################################################
## SCREENS
################################################################################
## EXAMPLE 1
## A sample screen to demonstrate the colour picker.
## Simply write `call screen color_picker()` to test it.
screen color_picker():

    ## The picker itself. Its size is 700x700 with the starting colour #ff8335.
    ## You may declare this outside of the screen to make it easier to access;
    ## see color_picker_v2 for an example of this.
    default picker = ColorPicker(700, 700, "#ff8335")
    ## The preview swatch. Needs to be provided the picker variable from above.
    ## You can specify its size as well.
    default picker_swatch = DynamicDisplayable(picker_color, picker=picker,
        xsize=100, ysize=100)
    ## The hexcode of the current colour. Demonstrates updating the picker
    ## colour information in real-time.
    default picker_hex = DynamicDisplayable(picker_hexcode, picker=picker)

    style_prefix 'cpicker' ## Simplifies some of the style property code

    add "#21212d" ## The background

    hbox:
        ## A vertical bar which lets you change the hue of the picker.
        vbar value FieldValue(picker, "hue_rotation", 1.0)

        vbox:
            ## The picker itself
            add picker
            ## A horizontal bar that lets you change the hue of the picker
            bar value FieldValue(picker, "hue_rotation", 1.0)
        vbox:
            xsize 200 spacing 10 align (0.0, 0.0)
            ## The swatch
            add picker_swatch

            ## You can display other information on the color here, as desired
            ## Some examples are provided. Note that these do not update in
            ## tandem with the picker, but when the mouse is released. You
            ## will need to use a DynamicDisplayable for real-time updates.
            ## The hex code is provided as an example.
            add picker_hex ## The DynamicDisplayable from earlier
            ## These update when the mouse button is released
            ## since they aren't a dynamic displayable
            text "R: [picker.color.rgb[0]:.2f]"
            text "G: [picker.color.rgb[1]:.2f]"
            text "B: [picker.color.rgb[2]:.2f]"

    ## In this case, the screen returns the picker's colour. The colour itself
    ## is always stored in the picker's `color` attribute.
    textbutton "Return" action Return(picker.color) align (1.0, 1.0)

################################################################################
## Styles
style cpicker_vbox:
    align (0.5, 0.5)
    spacing 25
style cpicker_hbox:
    align (0.5, 0.5)
    spacing 25
style cpicker_vbar:
    xysize (50, 700)
    base_bar At(Transform("#000", xysize=(50, 700)), spectrum(horizontal=False))
    thumb Transform("selector_bg", xysize=(50, 20))
    thumb_offset 10
style cpicker_bar:
    xysize (700, 50)
    base_bar At(Transform("#000", xysize=(700, 50)), spectrum())
    thumb Transform("selector_bg", xysize=(20, 50))
    thumb_offset 10
style cpicker_text:
    color "#fff"
style cpicker_button:
    padding (4, 4) insensitive_background "#fff"
style cpicker_button_text:
    color "#aaa"
    hover_color "#fff"
style cpicker_image_button:
    xysize (104, 104)
    padding (4, 4)
    hover_foreground "#fff2"

################################################################################
## EXAMPLE 2
## The picker itself. This one is declared outside of the screen.
default picker2 = ColorPicker(700, 700, "#f93c3e")
## The preview swatch. Needs to be provided the picker variable from above.
## You can specify its size as well.
default picker_swatch_v2 = DynamicDisplayable(picker_color, picker=picker2,
    xsize=100, ysize=100)
## The hexcode of the current colour. Demonstrates updating the picker
## colour information in real-time.
default picker_hex_v2 = DynamicDisplayable(picker_hexcode, picker=picker2)

default color1 = Color("#fff")
default color2 = Color("#fff")

init python:
    def finalize_colors(current, picker):
        """
        A helper function which ensures that the last-changed colour picker
        colour is also saved. This is a function rather than a SetVariable
        action because Ren'Py does not refresh the SetVariable value while
        the colour picker is changing colours, thus it would use an out-of-date
        value.
        """
        if current == 1:
            store.color1 = picker.color
        else:
            store.color2 = picker.color

screen color_picker_v2():

    ## This is an example of how you can swap between multiple colour swatches
    default current_color = 1

    style_prefix 'cpicker'

    add "#21212d"

    hbox:
        ## A vertical bar which lets you change the hue of the picker.
        vbar value FieldValue(picker2, "hue_rotation", 1.0)

        ## The picker itself
        vbox:
            add picker2
            ## A horizontal bar that lets you change the hue of the picker
            bar value FieldValue(picker2, "hue_rotation", 1.0)

        vbox:
            xsize 200 spacing 10 align (0.0, 0.0)
            ## The following code lets you switch between
            ## two different swatches to choose more than one colour:
            if current_color == 1:
                button:
                    ## An insensitive button which just shows the currently
                    ## selected colour.
                    add picker_swatch_v2
            else:
                imagebutton:
                    idle color1
                    ## Switch the picker to track the second colour, using
                    ## the `set_color` method.
                    action [SetVariable("color2", picker2.color),
                        Function(picker2.set_color, color1),
                        SetScreenVariable("current_color", 1)]
            if current_color == 2:
                button:
                    add picker_swatch_v2
            else:
                imagebutton:
                    idle color2
                    action [SetVariable("color1", picker2.color),
                        Function(picker2.set_color, color2),
                        SetScreenVariable("current_color", 2)]

            ## The hex code
            add picker_hex_v2 ## The DynamicDisplayable from earlier
            ## The RGB values
            text "R: [picker2.color.rgb[0]:.2f]"
            text "G: [picker2.color.rgb[1]:.2f]"
            text "B: [picker2.color.rgb[2]:.2f]"

    ## Ensure that the last-changed colour picker colour is also saved, and
    ## then just Return because this screen uses global variables.
    textbutton "Return" align (1.0, 1.0):
        action [Function(finalize_colors, current_color, picker2), Return()]

################################################################################
## EXAMPLE 3
## A sample screen to demonstrate the four corner colour picker.
## Simply write `call screen four_corner_picker()` to test it.
screen four_corner_picker():

    ## The picker itself. Its size is 700x700, and it's given a colour for
    ## all four corners (top right, bottom right, bottom left, top left)
    ## You may declare this outside of the screen to make it easier to access.
    default picker = ColorPicker(700, 700,
        four_corners=("#ff8335", "#f93c3e", "#292835", "#f7f7ed"))
    ## The preview swatch. Needs to be provided the picker variable from above.
    ## You can specify its size as well.
    default picker_swatch = DynamicDisplayable(picker_color, picker=picker,
        xsize=100, ysize=100)
    ## The hexcode of the current colour. Demonstrates updating the picker
    ## colour information in real-time.
    default picker_hex = DynamicDisplayable(picker_hexcode, picker=picker)

    style_prefix 'cpicker'

    add "#21212d"

    hbox:
        spacing 25 align (0.5, 0.5)

        vbox:
            ## The picker itself
            add picker
            ## A horizontal bar that lets you change the hue of the picker
            ## For a four-corner picker, you may not need this.
            bar value FieldValue(picker, "hue_rotation", 1.0) base_bar "#fff"
        vbox:
            xsize 200 spacing 10 align (0.0, 0.0)
            ## The swatch
            add picker_swatch

            ## The hex code
            add picker_hex ## The DynamicDisplayable from earlier
            ## The RGB values
            text "R: [picker.color.rgb[0]:.2f]"
            text "G: [picker.color.rgb[1]:.2f]"
            text "B: [picker.color.rgb[2]:.2f]"

    ## In this case, the screen returns the picker's colour. The colour itself
    ## is always stored in the picker's `color` attribute.
    textbutton "Return" action Return(picker.color) align (1.0, 1.0)

################################################################################
## TESTING LABEL
################################################################################
default chosen_color = "#8b0f55"
label how_to_use_color_picker():
    "Soon, you will be shown a colour picker."

    ## EXAMPLE 1
    call screen color_picker()
    ## The colour the picker returns is a Color object. It has a hexcode
    ## field to easily get the hexadecimal colour code.
    $ chosen_color = _return.hexcode
    ## This is used to put the returned colour into a colour text tag
    $ color_tag = "{color=%s}" % chosen_color
    "[color_tag]You chose the colour [chosen_color].{/color}"

    ## EXAMPLE 2
    "The next picker will let you select two different colours."
    call screen color_picker_v2()
    $ color1_tag = "{color=%s}" % color1.hexcode
    $ color2_tag = "{color=%s}" % color2.hexcode
    "[color1_tag]The first colour was [color1.hexcode],{/color}[color2_tag] and the second was [color2.hexcode].{/color}"

    ## EXAMPLE 3
    "Next, you will be shown a four-corner colour picker."
    call screen four_corner_picker()
    $ chosen_color = _return.hexcode
    $ color_tag = "{color=%s}" % chosen_color
    "[color_tag]You chose the colour [chosen_color].{/color}"
    return
