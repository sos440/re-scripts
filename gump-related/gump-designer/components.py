from AutoComplete import *
from enum import Enum


COMPONENTS_AVAILABLE = [
    "button",  # button
    "buttontileart",  # button with tile art
    "checkertrans",  # checker transparent
    "croppedtext",
    "tilepicasgumppic",
    "gumppic",
    "gumppictiled",
    "htmlgump",
    "xmfhtmlgump",
    "xmfhtmlgumpcolor",
    "xmfhtmltok",
    "page",
    "resizepic",  # background
    "text",
    "textentrylimited",
    "textentry",
    "tilepichue",  # colored item
    "tilepic",  # item
    "noclose",  # do not close when right-clicked
    "nodispose",  # do not close when ESC pressed
    "nomove",  # do not move
    "group",
    "endgroup",
    "radio",
    "checkbox",
    "tooltip",
    "itemproperty",
    "noresize",  # not implemented
    "mastergump",
    "picinpichued",
    "picinpicphued",
    "picinpic",
    "gumppichued",
    "gumppicphued",
    "togglelimitgumpscale",  # not implemented
]


class GumpComponent:
    def compile(self) -> str:
        """
        Compile the object into the gump instruction.
        """
        raise NotImplementedError()


class PlaceableComponent(GumpComponent):
    x: int
    y: int


class SizeableComponent(PlaceableComponent):
    width: int
    height: int


class Button(PlaceableComponent):
    """
    A button component in the Gump UI.

    Raw command syntax:
    ```
    button x y normal pressed action page buttonid
    ```

    * x: The x-coordinate of the button
    * y: The y-coordinate of the button
    * normal: The normal state graphic
    * pressed: The pressed state graphic
    * action: The action to perform when the button is clicked (0 = switch page, 1 = send action)
    * page: The page to switch to (if action is 0)
    * buttonid: The ID of the button
    """

    normal: int
    """The normal state graphic."""
    pressed: int
    """The pressed state graphic."""
    action: int
    """The action to perform when the button is clicked. (0 = switch page, 1 = send action)"""
    page: int
    """The page to switch to (if action is 0)"""
    buttonid: int
    """The ID of the button."""

    def __init__(self, x: int, y: int, normal: int, pressed: int, action: int, page: int, buttonid: int):
        self.x = x
        self.y = y
        self.normal = normal
        self.pressed = pressed
        self.action = action
        self.page = page
        self.buttonid = buttonid

    def compile(self) -> str:
        """
        Compile the button component into the gump instruction.
        """
        return f"{{ button {self.x} {self.y} {self.normal} {self.pressed} {self.action} {self.page} {self.buttonid} }}"


class ButtonTileArt(Button):
    """
    A button component with tile art (item).

    Raw command syntax:
    ```
    buttontileart x y normal pressed action page buttonid tileid hue tile_x tile_y
    ```

    * x: The x-coordinate of the button
    * y: The y-coordinate of the button
    * normal: The normal state graphic
    * pressed: The pressed state graphic
    * action: The action to perform when the button is clicked (0 = switch page, 1 = send action)
    * page: The page to switch to (if action is 0)
    * buttonid: The ID of the button
    * tileid: The ID of the tile art (item ID)
    * hue: The hue of the tile art
    * tile_x: The x-coordinate of the tile art relative to the button
    * tile_y: The y-coordinate of the tile art relative to the button
    """


class CheckerTrans(SizeableComponent):
    """
    A checker transparent component in the Gump UI.

    Raw command syntax:
    ```
    checkertrans x y width height
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * width: The width of the component
    * height: The height of the component
    """


class CroppedText(SizeableComponent):
    """
    A cropped text component in the Gump UI.

    ```
    croppedtext x y width height hue textidx
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * width: The width of the component
    * height: The height of the component
    * hue: The hue of the text (strangely, you need to subtract 1 from the actual hue)
    * textidx: The index of the text in the string list
    """


class GumpPic(PlaceableComponent):
    """
    ```
    gumppic x y graphicid hue
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * graphicid: The ID of the gump art
    * hue: The hue of the gump art
    """


class GumpPicHued(GumpPic):
    """
    ```
    gumppichued x y graphicid hue
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * graphicid: The ID of the gump art
    * hue: The hue of the gump art
    """


class GumpPicPartialHued(GumpPic):
    """
    ```
    gumppicphued x y graphicid hue
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * graphicid: The ID of the gump art
    * hue: The hue of the gump art
    """


class GumpPicTiled(SizeableComponent):
    """

    ```
    gumppictiled x y width height graphicid
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * width: The width of the component
    * height: The height of the component
    * graphicid: The ID of the gump art
    """


class HtmlGump(SizeableComponent):
    """

    ```
    htmlgump x y width height textidx has_bg scrollbar
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * width: The width of the component
    * height: The height of the component
    * textidx: The index of the text in the string list
    * has_bg: Whether the component has the background or not (0 = no, 1 = yes)
    * scrollbar: The type of the scrollbar (0 = no scrollbar, 1 = scrollbar, 2 = flag scrollbar)
    """


class XmfHtmlGump(HtmlGump):
    """

    ```
    xmfhtmlgump x y width height cliloc has_bg scrollbar
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * width: The width of the component
    * height: The height of the component
    * cliloc: The ID of the cliloc string
    * has_bg: Whether the component has the background or not (0 = no, 1 = yes)
    * scrollbar: The type of the scrollbar (0 = no scrollbar, 1 = scrollbar, 2 = flag scrollbar)
    """


class XmfHtmlGumpColor(HtmlGump):
    """

    ```
    xmfhtmlgumpcolor x y width height cliloc has_bg scrollbar color
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * width: The width of the component
    * height: The height of the component
    * cliloc: The ID of the cliloc string
    * has_bg: Whether the component has the background or not (0 = no, 1 = yes)
    * scrollbar: The type of the scrollbar (0 = no scrollbar, 1 = scrollbar, 2 = flag scrollbar)
    * color: The color of the text in RGB format (0x7FFF translates to 0xFFFFFF)
    """


class XmfHtmlToken(HtmlGump):
    """

    ```
    xmfhtmltok x y width height has_bg scrollbar color cliloc (token_1 token_2 ...|@token_1@token_2@...@)
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * width: The width of the component
    * height: The height of the component
    * cliloc: The ID of the cliloc string
    * has_bg: Whether the component has the background or not (0 = no, 1 = yes)
    * scrollbar: The type of the scrollbar (0 = no scrollbar, 1 = scrollbar, 2 = flag scrollbar)
    * color: The color of the text in RGB format (0x7FFF translates to 0xFFFFFF)
    * token_i: The i-th tokens to replace in the cliloc string. This is either a string or cliloc (prefixed with #)

    Ex) The code below will create a text "Cart: 0/10"

    ```
    xmfhtmltok 628 39 123 25 0 0 32767 1156593 @0@10@
    ```


    """


class GumpPicInPic(SizeableComponent):
    """

    ```
    picinpic x y graphicid sx xy width height
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * graphicid: The ID of the outer gump art
    * sx: The x-coordinate of the cropping area relative to the outer gump art
    * sy: The y-coordinate of the cropping area relative to the outer gump art
    * width: The width of the component (as well as the cropping area)
    * height: The height of the component (as well as the cropping area)
    """


class GumpPicInPicHued(GumpPicInPic):
    """

    ```
    picinpichued x y graphicid sx xy width height hue
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * graphicid: The ID of the outer gump art
    * sx: The x-coordinate of the cropping area relative to the outer gump art
    * sy: The y-coordinate of the cropping area relative to the outer gump art
    * width: The width of the component (as well as the cropping area)
    * height: The height of the component (as well as the cropping area)
    * hue: The hue of the gump art
    """


class GumpPicInPicPartialHued(GumpPicInPic):
    """

    ```
    picinpicphued x y graphicid sx xy width height hue
    ```

    * x: The x-coordinate of the component
    * y: The y-coordinate of the component
    * graphicid: The ID of the outer gump art
    * sx: The x-coordinate of the cropping area relative to the outer gump art
    * sy: The y-coordinate of the cropping area relative to the outer gump art
    * width: The width of the component (as well as the cropping area)
    * height: The height of the component (as well as the cropping area)
    * hue: The hue of the gump art
    """
