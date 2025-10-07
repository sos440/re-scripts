from AutoComplete import *
from System.Collections.Generic import List as CList  # type: ignore
from enum import Enum
from typing import List, Tuple, Dict, Callable, Any, Optional, Union


################################################################################
# Primitive Gump Components
################################################################################


Position: "TypeAlias" = Tuple[int, int]
Dimension: "TypeAlias" = Tuple[int, int]


class ButtonType(Enum):
    Page = 0
    Reply = 1


class Primitive:
    class Base:
        """Base class for all gump components."""

        def compile(self, **kwargs) -> List[Any]:
            """Compile the component into the gump instruction string."""
            raise NotImplementedError("Compile method not implemented.")

    class Placeable:
        x: int
        """The x-coordinate (left) of the component."""
        y: int
        """The y-coordinate (top) of the component."""

        @property
        def left(self):
            """Returns the left x-coordinate of the component."""
            return self.x

        @property
        def top(self):
            """Returns the top y-coordinate of the component."""
            return self.y

        @property
        def pos(self) -> Position:
            """Returns the position as a tuple (x, y)."""
            return (self.x, self.y)

        @pos.setter
        def pos(self, value: Position):
            self.x, self.y = value

    class Sizeable(Placeable):
        width: int
        """The width of the component."""
        height: int
        """The height of the component."""

        @property
        def right(self):
            """Returns the right x-coordinate of the component."""
            return self.x + self.width

        @property
        def bottom(self):
            """Returns the bottom y-coordinate of the component."""
            return self.y + self.height

        @property
        def size(self) -> Dimension:
            """Returns the size as a tuple (width, height)."""
            return (self.width, self.height)

        @size.setter
        def size(self, value: Dimension):
            self.width, self.height = value

    class Serializable:
        id: int
        """The unique identifier for the component."""

    class ContainsText:
        text: str
        """The text content of the component."""

    class PlaceableComponent(Base, Placeable):
        pass

    class SizeableComponent(Base, Sizeable):
        pass

    class ClickableComponent(Base, Placeable, Serializable):
        normal: int
        """The ID of the normal state gumpart."""
        pressed: int
        """The ID of the pressed state gumpart."""

    class Button(ClickableComponent):
        """
        This class represents a button component in the Gump UI.
        """

        action: ButtonType
        """The action to perform when the button is clicked. Default is `Button.Page`."""
        page: int
        """The page to switch to (if action is `Button.Page`)."""
        id: int
        """The ID of the button to be sent (if action is `Button.Reply`)."""

        def __init__(
            self,
            x: int = 0,
            y: int = 0,
            normal: int = 0,
            pressed: int = 0,
            action: Union[ButtonType, int] = ButtonType.Page,
            page: int = 0,
            id: int = 0,
        ):
            self.x = x
            self.y = y
            self.normal = normal
            self.pressed = pressed
            if isinstance(action, int):
                self.action = ButtonType(action)
            else:
                self.action = action
            self.page = page
            self.id = id

        def compile(self, **kwargs):
            return [
                "button",
                self.x,
                self.y,
                self.normal,
                self.pressed,
                self.action.value,
                self.page,
                self.id,
            ]

    class ButtonTileArt(Button):
        """
        This class represents a button with tileart (item) component in the Gump UI.
        """

        tileart: int
        """The ID of the tileart to display on the button."""
        hue: int
        """The hue of the tileart."""
        tx: int
        """The x-coordinate of the tileart relative to the button."""
        ty: int
        """The y-coordinate of the tileart relative to the button."""

        def __init__(
            self,
            x: int = 0,
            y: int = 0,
            normal: int = 0,
            pressed: int = 0,
            action: Union[ButtonType, int] = ButtonType.Page,
            page: int = 0,
            id: int = 0,
            tileart: int = 0,
            hue: int = 0,
            tx: int = 0,
            ty: int = 0,
        ):
            super().__init__(x, y, normal, pressed, action, page, id)
            self.tileart = tileart
            self.hue = hue
            self.tx = tx
            self.ty = ty

        def compile(self, **kwargs):
            return [
                "buttontileart",
                self.x,
                self.y,
                self.normal,
                self.pressed,
                self.action.value,
                self.page,
                self.id,
                self.tileart,
                self.hue,
                self.tx,
                self.ty,
            ]

    class AlphaRegion(SizeableComponent):
        """
        This class represents an alpha region component in the Gump UI.

        An alpha region is an area that allows for transparency effects,
        masking a portion of the gump to create see-through effects.
        """

        def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0):
            self.x = x
            self.y = y
            self.width = width
            self.height = height

        def compile(self, **kwargs):
            return ["checkertrans", self.x, self.y, self.width, self.height]

    class Text(PlaceableComponent, ContainsText):
        """
        A text component in the Gump UI.

        This component displays plain text at the specified coordinates,
        without cropping or formatting.
        """

        hue: int
        """
        The hue of the text.
        Unlike in other components, this is 0-based, with 0 being true black.
        For example, if you want to use the snow white color 1153, you should set hue to 1152.
        """

        def __init__(self, x: int = 0, y: int = 0, hue: int = 0, text: str = ""):
            self.x = x
            self.y = y
            self.hue = hue
            self.text = text

        def compile(self, **kwargs):
            text_index = kwargs.get("text_index")
            if text_index is None:
                raise ValueError("text_index is required to compile `Text` component.")
            return ["text", self.x, self.y, self.hue, text_index]

    class CroppedText(Text):
        """
        A cropped text component in the Gump UI.

        The cropped text component displays text within a defined rectangular area,
        cropping any overflow text that exceeds the specified width and height
        and adding ellipses ("...") to indicate that the text has been truncated.
        """

        def __init__(
            self,
            x: int = 0,
            y: int = 0,
            width: int = 0,
            height: int = 0,
            hue: int = 0,
            text: str = "",
        ):
            super().__init__(x, y, hue, text)
            self.width = width
            self.height = height

        def compile(self, **kwargs):
            text_index = kwargs.get("text_index")
            if text_index is None:
                raise ValueError("text_index is required to compile `CroppedText` component.")
            return ["croppedtext", self.x, self.y, self.width, self.height, self.hue, text_index]

    class GumpArt(PlaceableComponent):
        """
        A gumpart component in the Gump UI.

        This displays a gumpart image at the specified coordinates.
        """

        gumpart: int
        """The ID of the gumpart to display."""
        hue: int
        """The hue of the gumpart."""

        def __init__(self, x: int = 0, y: int = 0, gumpart: int = 0, hue: int = 0):
            self.x = x
            self.y = y
            self.gumpart = gumpart
            self.hue = hue

        def compile(self, **kwargs):
            if self.hue == 0:
                return ["gumppic", self.x, self.y, self.gumpart]
            return ["gumppichued", self.x, self.y, self.gumpart, self.hue]

    class TiledGumpArt(GumpArt, SizeableComponent):
        """
        A tiled gumpart component in the Gump UI.

        This displays a gumpart image tiled to fill the specified width and height.
        """

        def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0, gumpart: int = 0):
            super().__init__(x, y, gumpart)
            self.width = width
            self.height = height

        def compile(self, **kwargs):
            return ["gumppictiled", self.x, self.y, self.width, self.height, self.gumpart]

    class Html(SizeableComponent, ContainsText):
        """
        An HTML text component in the Gump UI.
        """

        text: str
        """The HTML text to display."""
        background: bool
        """Whether to display a background."""
        scrollbar: int
        """Type of scrollbar (0 = none, 1 = normal, 2 = flag)."""

        def __init__(
            self,
            x: int = 0,
            y: int = 0,
            width: int = 0,
            height: int = 0,
            text: str = "",
            background: bool = False,
            scrollbar: int = 0,
        ):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.text = text
            self.background = background
            self.scrollbar = scrollbar

        def compile(self, **kwargs):
            text_index = kwargs.get("text_index")
            if text_index is None:
                raise ValueError("text_index is required to compile `Html` component.")
            bg_flag = 1 if self.background else 0
            return ["htmlgump", self.x, self.y, self.width, self.height, text_index, bg_flag, self.scrollbar]

    class HtmlLocalized(Html):
        """
        A localized HTML text component in the Gump UI.

        This component displays localized text using a cliloc ID
        (unique identifier of the text), with optional formatting arguments.
        """

        cliloc: int
        """The ID of the localized text to display."""
        color: Optional[int]
        """Optional color override for the localized text."""
        args: List[Union[str, int]]
        """Arguments to format the localized text, if any."""

        def __init__(
            self,
            x: int = 0,
            y: int = 0,
            width: int = 0,
            height: int = 0,
            cliloc: int = 0,
            background: bool = False,
            scrollbar: int = 0,
            color: Optional[int] = None,
            args: Optional[List[Union[str, int]]] = None,
        ):
            super().__init__(x, y, width, height, "", background, scrollbar)
            self.cliloc = cliloc
            self.color = color
            self.args = args or []

        def compile(self, **kwargs):
            bg_flag = 1 if self.background else 0
            if len(self.args) > 0:
                args_compiled: List[str] = []
                for arg in self.args:
                    if isinstance(arg, str):
                        args_compiled.append(arg)
                    elif isinstance(arg, int):
                        args_compiled.append(f"#{arg}")
                    else:
                        raise ValueError("Arguments must be either strings or integers.")
                return [
                    "xmfhtmltok",
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    bg_flag,
                    self.scrollbar,
                    self.color if self.color is not None else 0,
                    self.cliloc,
                    "@" + "@".join(args_compiled) + "@",
                ]
            elif self.color is not None:
                return [
                    "xmfhtmlgumpcolor",
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    self.cliloc,
                    bg_flag,
                    self.scrollbar,
                    self.color,
                ]
            else:
                return [
                    "xmfhtmlgump",
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    self.cliloc,
                    bg_flag,
                    self.scrollbar,
                ]

    class Page(Base):
        """
        A page declaration in the Gump UI.
        """

        page: int
        """The page number. The value 0 is reserved for the background, 
        and switchable pages start from 1."""

        def __init__(self, page: int = 0):
            self.page = page

        def compile(self, **kwargs):
            return ["page", self.page]

    class Background(SizeableComponent):
        """
        A resizable background component in the Gump UI.

        This element creates a window-like background using a series of 9 gumparts.
        4 corners, 4 edges, and a center piece that tiles to fill the area.
        """

        gumpart: int
        """The ID of the gumpart to use as background.
        This should be the ID of the first gumpart (left-top corner) in a series of 9 gumparts that comprise a "window"."""

        def __init__(self, x: int = 0, y: int = 0, width: int = 0, height: int = 0, gumpart: int = 0):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.gumpart = gumpart

        def compile(self, **kwargs):
            return ["resizepic", self.x, self.y, self.gumpart, self.width, self.height]

    class TextEntry(SizeableComponent, Serializable, ContainsText):
        """
        A text entry component in the Gump UI.

        This component provides an input field where users can enter text.
        The entered text can be retrieved using the unique ID assigned to the component.
        """

        hue: int
        """The hue of the text entry."""
        text: str
        """The default text to display in the entry."""
        max_char: int
        """The maximum number of characters allowed in the text entry. The default is -1, which means no limit."""

        def __init__(
            self,
            x: int = 0,
            y: int = 0,
            width: int = 0,
            height: int = 0,
            hue: int = 0,
            id: int = 0,
            text: str = "",
            max_char: int = -1,
        ):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.hue = hue
            self.id = id
            self.text = text
            self.max_char = max_char

        def compile(self, **kwargs):
            text_index = kwargs.get("text_index")
            if text_index is None:
                raise ValueError("text_index is required to compile `TextEntry` component.")
            if self.max_char == -1:
                return ["textentry", self.x, self.y, self.width, self.height, self.hue, self.id, text_index]
            return ["textentrylimited", self.x, self.y, self.width, self.height, self.hue, self.id, text_index, self.max_char]

    class TileArt(PlaceableComponent):
        """
        A tile art component in the Gump UI.

        This component displays a tile art (item) at the specified coordinates.
        """

        tileart: int
        """The ID of the tileart to display."""
        hue: int
        """The hue of the tileart."""

        def __init__(self, x: int = 0, y: int = 0, tileart: int = 0, hue: int = 0):
            self.x = x
            self.y = y
            self.tileart = tileart
            self.hue = hue

        def compile(self, **kwargs):
            if self.hue == 0:
                return ["tilepic", self.x, self.y, self.tileart]
            return ["tilepichue", self.x, self.y, self.tileart, self.hue]

    class RadioGroup(Base):
        """
        A radio button group in the Gump UI.

        This component declares a group of radio buttons,
        allowing only one button in the group to be selected at a time.
        """

        group: int
        """The ID of the radio button group."""

        def __init__(self, group: int = 0):
            self.group = group

        def compile(self, **kwargs):
            return ["group", self.group]

    class Checkbox(ClickableComponent):
        """
        A checkbox component in the Gump UI.

        This component provides a checkbox that can be checked or unchecked.
        The state of the checkbox can be retrieved using the unique ID assigned to the component.
        """

        checked: bool
        """Whether the checkbox is checked by default."""

        def __init__(
            self,
            x: int = 0,
            y: int = 0,
            normal: int = 0,
            pressed: int = 0,
            checked: bool = False,
            id: int = 0,
        ):
            self.x = x
            self.y = y
            self.normal = normal
            self.pressed = pressed
            self.checked = checked
            self.id = id

        def compile(self, **kwargs):
            status = 1 if self.checked else 0
            return ["checkbox", self.x, self.y, self.normal, self.pressed, status, self.id]

    class Radio(Checkbox):
        """
        A radio button component in the Gump UI.

        This component provides a radio button that can be selected as part of a radio group.
        The ID of the selected radio button can be retrieved using the unique ID assigned to the component.
        """

        checked: bool
        """Whether the radio button is checked by default."""

        def compile(self, **kwargs):
            status = 1 if self.checked else 0
            return ["radio", self.x, self.y, self.normal, self.pressed, status, self.id]

    class Tooltip(Base):
        """
        A tooltip declaration in the Gump UI.

        This component adds a tooltip to the previous component.
        """

        cliloc: int
        """The ID of the localized text to display in the tooltip."""
        args: List[Union[str, int]]
        """Arguments to format the localized text, if any."""

        def __init__(self, cliloc: int = 1114778, args: Optional[Union[str, int, List[Union[str, int]]]] = None):
            self.cliloc = cliloc
            if args is None:
                self.args = []
            elif isinstance(args, (str, int)):
                self.args = [args]
            elif isinstance(args, list):
                self.args = args
            else:
                raise ValueError("args must be a string, integer, or list of strings/integers.")

        def compile(self, **kwargs):
            args_parsed = []
            for arg in self.args:
                if isinstance(arg, str):
                    args_parsed.append(arg)
                elif isinstance(arg, int):
                    args_parsed.append(f"#{arg}")
                else:
                    raise ValueError("A cliloc argument must be a string or integer.")
            if len(args_parsed) > 0:
                return ["tooltip", self.cliloc, "@" + "\t".join(args_parsed) + "@"]
            return ["tooltip", self.cliloc]

    class ItemProperty(Base):
        """
        An item property declaration in the Gump UI.

        This component adds an item property tooltip to the previous component.
        """

        item_id: int
        """The ID of the item whose properties to display."""

        def __init__(self, item_id: int = 0):
            self.item_id = item_id

        def compile(self, **kwargs):
            return ["itemproperty", self.item_id]

    class CroppedGumpArt(GumpArt, SizeableComponent):
        """
        A cropped gumpart component in the Gump UI.

        This component displays a portion of a gumpart image,
        defined by the specified width and height, starting from the top-left corner.
        """

        sx: int
        """The x-coordinate of the top-left corner of the cropped area within the gumpart."""
        sy: int
        """The y-coordinate of the top-left corner of the cropped area within the gumpart."""
        width: int
        """The width of the cropped area."""
        height: int
        """The height of the cropped area."""
        partial_hued: bool
        """Whether to apply partial hueing."""

        def __init__(
            self,
            x: int = 0,
            y: int = 0,
            gumpart: int = 0,
            sx: int = 0,
            sy: int = 0,
            width: int = 0,
            height: int = 0,
            hue: int = 0,
            partial_hued: bool = False,
        ):
            self.x = x
            self.y = y
            self.gumpart = gumpart
            self.sx = sx
            self.sy = sy
            self.width = width
            self.height = height
            self.hue = hue
            self.partial_hued = partial_hued

        def compile(self, **kwargs):
            if self.hue == 0:
                return ["picinpic", self.x, self.y, self.gumpart, self.sx, self.sy, self.width, self.height]
            elif self.partial_hued:
                return ["picinpicphued", self.x, self.y, self.gumpart, self.sx, self.sy, self.width, self.height, self.hue]
            return ["picinpichued", self.x, self.y, self.gumpart, self.sx, self.sy, self.width, self.height, self.hue]


################################################################################
# Primitive Gump Builder
################################################################################


class GumpBuilder:
    """A builder class to create gump instructions from components and strings."""

    noclose: bool
    """When True, the gump cannot be closed by right-clicking."""
    nodispose: bool
    """When True, the gump cannot be closed by pressing the ESC key."""
    nomove: bool
    """When True, the gump cannot be moved."""

    class Response:
        button: str
        switches: List[str]
        texts: Dict[str, str]

        def __init__(self):
            self.button = ""
            self.switches = []
            self.texts = {}

    def __init__(self, id: Union[str, int], noclose: bool = False, nodispose: bool = False, nomove: bool = False):
        if isinstance(id, str):
            self.id = hash(id) & 0xFFFFFFFF
        else:
            self.id = id
        self.noclose = noclose
        self.nodispose = nodispose
        self.nomove = nomove

        self._components: List[Primitive.Base] = []
        self._instructions: List[Any] = []

        self._strings: List[str] = []
        self._string_to_index: Dict[str, int] = {}

        self._button_ids: List[str] = [""]
        self._switch_ids: List[str] = []
        self._textentry_ids: List[str] = []

        self._button_ids_to_index: Dict[str, int] = {"": 0}
        self._switch_ids_to_index: Dict[str, int] = {}
        self._textentry_ids_to_index: Dict[str, int] = {}

        self._radio_group_count = 0

    # Internal Methods

    def _add(self, component: Primitive.Base):
        """
        Add a gump component to the builder.

        Args:
            component (Primitive.Base): The gump component to add.
        """
        if not isinstance(component, Primitive.Base):
            raise ValueError("Component must be an instance of Primitive.Base.")
        self._components.append(component)

    def _remove(self, component: Primitive.Base):
        """
        Remove a gump component from the builder.

        Args:
            component (Primitive.Base): The gump component to remove.
        """
        if component in self._components:
            self._components.remove(component)

    def _extend(self, components: List[Primitive.Base]):
        """
        Add multiple gump components to the builder.

        Args:
            components (List[Primitive.Base]): The list of gump components to add.
        """
        for component in components:
            self._add(component)

    def _compile(self):
        """
        An internal method to build the gump instructions from components and strings.
        """

        self._instructions = []
        self._strings = []
        self._string_to_index = {}

        # Add initial flags
        if self.noclose:
            self._instructions.append("{ noclose }")
        if self.nodispose:
            self._instructions.append("{ nodispose }")
        if self.nomove:
            self._instructions.append("{ nomove }")

        # Compile components
        for component in self._components:
            if isinstance(component, Primitive.ContainsText):
                if component.text not in self._string_to_index:
                    self._string_to_index[component.text] = len(self._strings)
                    self._strings.append(component.text)
                text_index = self._string_to_index[component.text]
                compiled = component.compile(text_index=text_index)
            else:
                compiled = component.compile()
            self._instructions.append("{ " + " ".join(map(str, compiled)) + " }")

    # Public Methods

    def Launch(self, x: int, y: int, *, delay: int = 3600000, wait_for_response: bool = False) -> Optional["GumpBuilder.Response"]:
        """
        Launch the gump for the player.

        Args:
            x (int): The x-coordinate on the screen where the gump will be displayed.
            y (int): The y-coordinate on the screen where the gump will be displayed.
            delay (int, optional): The time in milliseconds to wait for a response. Defaults to 3600000 (1 hour).
            wait_for_response (bool, optional): Whether to wait for a response from the player. Defaults to False.

        Returns:
            Optional[GumpBuilder.Response]: The response from the player, or `None` if no response is received or if `wait_for_response` is `False`.
        """
        self._compile()
        gump_def = "".join(self._instructions)

        Gumps.SendGump(self.id, Player.Serial, x, y, gump_def, CList[str](self._strings))

        if not wait_for_response:
            return None

        if not Gumps.WaitForGump(self.id, delay):
            return None
        gd = Gumps.GetGumpData(self.id)
        if gd is None:
            return None

        response = GumpBuilder.Response()
        response.button = self._button_ids[gd.buttonid]
        response.switches = sorted([self._switch_ids[i] for i in gd.switches])
        response.texts = {self._textentry_ids[i]: text for i, text in zip(gd.textID, gd.text)}
        return response

    def AddAlphaRegion(self, pos: Position, *, size: Dimension) -> Primitive.AlphaRegion:
        """
        Add an alpha region component to the gump.

        Args:
            pos (Position): The (x, y) position of the alpha region.
            size (Dimension): The (width, height) size of the alpha region.

        Returns:
            Primitive.AlphaRegion: The created alpha region component.
        """
        alpha_region = Primitive.AlphaRegion(x=pos[0], y=pos[1], width=size[0], height=size[1])
        self._add(alpha_region)
        return alpha_region

    def AddBackground(self, pos: Position, *, size: Dimension, gumpart: int) -> Primitive.Background:
        """
        Add a resizable background component to the gump.

        Args:
            pos (Position): The (x, y) position of the background.
            size (Dimension): The (width, height) size of the background.
            gumpart (int): The ID of the gumpart to use as background.

        Returns:
            Primitive.Background: The created background component.
        """
        background = Primitive.Background(x=pos[0], y=pos[1], width=size[0], height=size[1], gumpart=gumpart)
        self._add(background)
        return background

    def AddPage(self, *, page: int) -> Primitive.Page:
        """
        Add a page declaration to the gump.

        Args:
            page (int): The page number. The value 0 is reserved for the background, and switchable pages start from 1.

        Returns:
            Primitive.Page: The created page component.
        """
        page_component = Primitive.Page(page=page)
        self._add(page_component)
        return page_component

    def AddPageButton(self, pos: Position, *, normal: int, pressed: int, page: int) -> Primitive.Button:
        """
        Add a page button to the gump.

        Args:
            pos (Position): The (x, y) position of the button.
            normal (int): The ID of the normal state gumpart.
            pressed (int): The ID of the pressed state gumpart.
            page (int): The page to switch to when clicked.

        Returns:
            Primitive.Button: The created button component.
        """
        button = Primitive.Button(x=pos[0], y=pos[1], normal=normal, pressed=pressed, action=ButtonType.Page, page=page)
        self._add(button)
        return button

    def AddReplyButton(self, pos: Position, *, normal: int, pressed: int, id: str) -> Primitive.Button:
        """
        Add a reply button to the gump.

        Args:
            pos (Position): The (x, y) position of the button.
            normal (int): The ID of the normal state gumpart.
            pressed (int): The ID of the pressed state gumpart.
            id (str): The unique string ID for the button.

        Returns:
            Primitive.Button: The created button component.
        """
        if not id:
            raise ValueError("Button ID cannot be empty.")
        if id in self._button_ids_to_index:
            id_num = self._button_ids_to_index[id]
        else:
            id_num = len(self._button_ids)
            self._button_ids.append(id)
            self._button_ids_to_index[id] = id_num
        button = Primitive.Button(x=pos[0], y=pos[1], normal=normal, pressed=pressed, action=ButtonType.Reply, id=id_num)
        self._add(button)
        return button

    def AddTileArtToButton(self, pos: Position, *, tileart: int, hue: int = 0) -> Primitive.ButtonTileArt:
        """
        Add a tile art to the last added component, which must be a button.

        Args:
            pos (Position): The (x, y) position of the tileart relative to the button.
            tileart (int): The ID of the tileart to display on the button.
            hue (int, optional): The hue of the tileart. Defaults to 0.

        Returns:
            Primitive.ButtonTileArt: The created button component with tileart.
        """
        button = self._components[-1] if self._components else None
        if button is None or not isinstance(button, Primitive.Button):
            raise ValueError("The last added component is not a Button.")
        button_with_tileart = Primitive.ButtonTileArt(
            x=button.x,
            y=button.y,
            normal=button.normal,
            pressed=button.pressed,
            action=button.action,
            page=button.page,
            id=button.id,
            tileart=tileart,
            hue=hue,
            tx=pos[0],
            ty=pos[1],
        )
        self._components.pop()  # Remove the old button
        self._components.append(button_with_tileart)
        return button_with_tileart

    def AddTileArt(self, pos: Position, *, tileart: int, hue: int = 0) -> Primitive.TileArt:
        """
        Add a tile art component to the gump.

        Args:
            pos (Position): The (x, y) position of the tileart.
            tileart (int): The ID of the tileart to display.
            hue (int, optional): The hue of the tileart. Defaults to 0.

        Returns:
            Primitive.TileArt: The created tileart component.
        """
        tile_art = Primitive.TileArt(x=pos[0], y=pos[1], tileart=tileart, hue=hue)
        self._add(tile_art)
        return tile_art

    def AddText(self, pos: Position, text: str, hue: int = 0, width: int = 100, cropped: bool = False) -> Primitive.Text:
        """
        Add a text component to the gump.

        Args:
            pos (Position): The (x, y) position of the text.
            hue (int): The hue of the text.
            text (str): The text content.
            width (int, optional): The width of the text box. Defaults to 100.
            cropped (bool, optional): Whether to crop the text. Defaults to False.

        Returns:
            Primitive.Text: The created text component.
        """
        if cropped:
            text_component = Primitive.CroppedText(x=pos[0], y=pos[1], width=width, height=22, hue=hue, text=text)
        else:
            text_component = Primitive.Text(x=pos[0], y=pos[1], hue=hue, text=text)
        self._add(text_component)
        return text_component

    def AddGumpArt(
        self,
        pos: Position,
        *,
        gumpart: int,
        hue: int = 0,
        partial_hued: bool = False,
        size: Optional[Dimension] = None,
        crop: Optional[Position] = None,
    ) -> Primitive.GumpArt:
        """
        Add a gump art component to the gump.

        * When both `size` and `crop` are provided, a cropped gump art is created. The clipped area starts from `crop` position and has the specified `size`.
        * When only `size` is provided, a tiled gump art is created. The gump art is tiled to fill the specified `size`.
        * When neither `size` nor `crop` are provided, a standard gump art is created.

        Args:
            pos (Position): The (x, y) position of the gump art.
            gumpart (int): The ID of the gump art to display.
            hue (int, optional): The hue of the gump art. Defaults to 0. This does not apply when tiling is used.
            partial_hued (bool, optional): Whether to apply partial hueing. Defaults to False. This only applies when `crop` is provided.
            size (Optional[Dimension], optional): The (width, height) size of the gump art. Defaults to None.
            crop (Optional[Position], optional): The (x, y) position to crop the gump art. Defaults to None.

        Returns:
            Primitive.GumpArt: The created gump art component.
        """
        if crop is not None:
            if size is None:
                raise ValueError("Size must be provided when crop is specified.")
            gump_art = Primitive.CroppedGumpArt(x=pos[0], y=pos[1], gumpart=gumpart, sx=crop[0], sy=crop[1], width=size[0], height=size[1], hue=hue, partial_hued=partial_hued)
        elif size is not None:
            gump_art = Primitive.TiledGumpArt(x=pos[0], y=pos[1], width=size[0], height=size[1], gumpart=gumpart)
        else:
            gump_art = Primitive.GumpArt(x=pos[0], y=pos[1], gumpart=gumpart, hue=hue)
        self._add(gump_art)
        return gump_art

    def AddHtml(
        self,
        pos: Position,
        *,
        size: Dimension,
        text: str,
        background: bool = False,
        scrollbar: int = 0,
        center: bool = False,
        html_color: Optional[str] = None,
    ) -> Primitive.Html:
        """
        Add an HTML text component to the gump.

        Args:
            pos (Position): The (x, y) position of the HTML text.
            size (Dimension): The (width, height) size of the HTML text area.
            text (str): The HTML text content.
            background (bool, optional): Whether to display a background. Defaults to False.
            scrollbar (int, optional): Type of scrollbar (0 = none, 1 = normal, 2 = flag). Defaults to 0.
            center (bool, optional): Whether to center the text. Defaults to False.
            html_color (Optional[str], optional): The HTML color code (e.g., "#FFFFFF") to apply to the text. Defaults to None.

        Returns:
            Primitive.Html: The created HTML text component.
        """
        if center:
            text = f"<center>{text}</center>"
        if html_color is not None:
            text = f'<basefont color="{html_color}">{text}</basefont>'
        html = Primitive.Html(x=pos[0], y=pos[1], width=size[0], height=size[1], text=text, background=background, scrollbar=scrollbar)
        self._add(html)
        return html

    def AddHtmlLocalized(
        self,
        pos: Position,
        *,
        size: Dimension,
        cliloc: int,
        args: Optional[Union[Union[str, int], List[Union[str, int]]]] = None,
        background: bool = False,
        scrollbar: int = 0,
        color: Optional[int] = None,
    ) -> Primitive.HtmlLocalized:
        """
        Add a localized HTML text component to the gump.

        Args:
            pos (Position): The (x, y) position of the HTML text.
            size (Dimension): The (width, height) size of the HTML text area.
            cliloc (int): The ID of the localized text to display.
            background (bool, optional): Whether to display a background. Defaults to False.
            scrollbar (int, optional): Type of scrollbar (0 = none, 1 = normal, 2 = flag). Defaults to 0.
            color (Optional[int], optional): Optional color override for the localized text. Defaults to None.
            args (Optional[Union[Union[str, int], List[Union[str, int]]]], optional): Arguments to format the localized text. Can be a single string/int or a list of strings/ints. Defaults to None.

        Returns:
            Primitive.HtmlLocalized: The created localized HTML text component.
        """
        if args is None:
            args_list: List[Union[str, int]] = []
        elif isinstance(args, (str, int)):
            args_list = [args]
        elif isinstance(args, list):
            args_list = args
        else:
            raise ValueError("args must be a string, integer, or list of strings/integers.")
        html_localized = Primitive.HtmlLocalized(
            x=pos[0],
            y=pos[1],
            width=size[0],
            height=size[1],
            cliloc=cliloc,
            background=background,
            scrollbar=scrollbar,
            color=color,
            args=args_list,
        )
        self._add(html_localized)
        return html_localized

    def AddTextEntry(self, pos: Position, *, size: Dimension, id: str, hue: int = 0, text: str = "", max_char: int = -1) -> Primitive.TextEntry:
        """
        Add a text entry component to the gump.

        Args:
            pos (Position): The (x, y) position of the text entry.
            size (Dimension): The (width, height) size of the text entry.
            hue (int): The hue of the text entry.
            id (str): The unique string ID for the text entry.
            text (str, optional): The default text to display in the entry. Defaults to "".
            max_char (int, optional): The maximum number of characters allowed in the text entry. The default is -1, which means no limit. Defaults to -1.

        Returns:
            Primitive.TextEntry: The created text entry component.
        """
        if not id:
            raise ValueError("TextEntry ID cannot be empty.")
        if id in self._textentry_ids_to_index:
            id_num = self._textentry_ids_to_index[id]
        else:
            id_num = len(self._textentry_ids)
            self._textentry_ids.append(id)
            self._textentry_ids_to_index[id] = id_num
        text_entry = Primitive.TextEntry(x=pos[0], y=pos[1], width=size[0], height=size[1], hue=hue, id=id_num, text=text, max_char=max_char)
        self._add(text_entry)
        return text_entry

    def AddCheckbox(self, pos: Position, *, normal: int = 210, pressed: int = 211, checked: bool = False, id: str) -> Primitive.Checkbox:
        """
        Add a checkbox component to the gump.

        Args:
            pos (Position): The (x, y) position of the checkbox.
            normal (int): The ID of the normal state gumpart.
            pressed (int): The ID of the pressed state gumpart.
            checked (bool): Whether the checkbox is checked by default.
            id (str): The unique string ID for the checkbox.

        Returns:
            Primitive.Checkbox: The created checkbox component.
        """
        if not id:
            raise ValueError("Checkbox ID cannot be empty.")
        if id in self._switch_ids_to_index:
            id_num = self._switch_ids_to_index[id]
        else:
            id_num = len(self._switch_ids)
            self._switch_ids.append(id)
            self._switch_ids_to_index[id] = id_num
        checkbox = Primitive.Checkbox(x=pos[0], y=pos[1], normal=normal, pressed=pressed, checked=checked, id=id_num)
        self._add(checkbox)
        return checkbox

    def AddRadio(self, pos: Position, *, normal: int = 208, pressed: int = 209, checked: bool = False, id: str) -> Primitive.Radio:
        """
        Add a radio button component to the gump.

        Args:
            pos (Position): The (x, y) position of the radio button.
            normal (int): The ID of the normal state gumpart.
            pressed (int): The ID of the pressed state gumpart.
            checked (bool): Whether the radio button is checked by default.
            id (str): The unique string ID for the radio button.

        Returns:
            Primitive.Radio: The created radio button component.
        """
        if not id:
            raise ValueError("Radio ID cannot be empty.")
        if id in self._switch_ids_to_index:
            id_num = self._switch_ids_to_index[id]
        else:
            id_num = len(self._switch_ids)
            self._switch_ids.append(id)
            self._switch_ids_to_index[id] = id_num
        radio = Primitive.Radio(x=pos[0], y=pos[1], normal=normal, pressed=pressed, checked=checked, id=id_num)
        self._add(radio)
        return radio

    def AddRadioGroup(self) -> Primitive.RadioGroup:
        """
        Add a radio button group to the gump.

        Returns:
            Primitive.RadioGroup: The created radio group component.
        """
        radio_group = Primitive.RadioGroup(group=self._radio_group_count)
        self._radio_group_count += 1
        self._add(radio_group)
        return radio_group

    def AddTooltip(self, *, cliloc: int = 1114778, args: Optional[Union[Union[str, int], List[Union[str, int]]]] = None) -> Primitive.Tooltip:
        """
        Add a tooltip declaration to the last added component.

        Args:
            cliloc (int, optional): The ID of the localized text to display in the tooltip. Defaults to 1114778.
            args (Optional[Union[Union[str, int], List[Union[str, int]]]], optional): Arguments to format the localized text. Can be a single string/int or a list of strings/ints. Defaults to None.

        Returns:
            Primitive.Tooltip: The created tooltip component.
        """
        tooltip = Primitive.Tooltip(cliloc=cliloc, args=args)
        self._add(tooltip)
        return tooltip

    def AddItemProperty(self, *, item_id: int) -> Primitive.ItemProperty:
        """
        Add an item property declaration to the last added component.

        Args:
            item_id (int): The ID of the item whose properties to display.

        Returns:
            Primitive.ItemProperty: The created item property component.
        """
        item_property = Primitive.ItemProperty(item_id=item_id)
        self._add(item_property)
        return item_property


__export__ = ["GumpBuilder"]
