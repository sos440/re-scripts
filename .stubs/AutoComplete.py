"""Version: 0.8.2.242
This module represents the scripting PythonAPI available in RazorEnhanced.
This class is NOT intended to be used as code, but to provice autocomplete in external editors and generation documentation.
"""

from typing import List, Set, Tuple, Dict, Any, Union, Optional, TypeAlias
from enum import Enum
from datetime import datetime

String: TypeAlias = str
Object: TypeAlias = object
Boolean: TypeAlias = bool
Byte: TypeAlias = int
Int: TypeAlias = int
Int16: TypeAlias = int
Int32: TypeAlias = int
UInt16: TypeAlias = int
UInt32: TypeAlias = int
Float: TypeAlias = float
Single: TypeAlias = float
Double: TypeAlias = float
DateTime: TypeAlias = datetime


class Bitmap:
    Width: int
    Height: int

    def GetPixel(self, x: int, y: int) -> "Color":
        """Get the color of the pixel at the specified coordinates.

        Parameters
        ----------
        x: int
                The x-coordinate of the pixel.
        y: int
                The y-coordinate of the pixel.

        Returns
        -------
        Color
                The color of the pixel.
        """
        ...


class Color:
    R: int
    G: int
    B: int


class AutoLoot:
    """The Autoloot class allow to interact with the Autoloot Agent, via scripting."""

    @staticmethod
    def ChangeList(listName: str):
        """Change the Autoloot's active list.

        Parameters
        ----------
        listName: str
                Name of an existing organizer list.

        """
        ...

    @staticmethod
    def GetList(lootListName: str, wantMinusOnes: bool) -> "List[AutoLoot.AutoLootItem]":
        """Given an AutoLoot list name, return a list of AutoLootItem associated.

        Parameters
        ----------
        lootListName: str
                Name of the AutoLoot list.
        wantMinusOnes: bool

        Returns
        -------
        List[AutoLoot.AutoLootItem]

        """
        ...

    @staticmethod
    def GetLootBag() -> "UInt32":
        """Get current Autoloot destination container.

        Returns
        -------
        UInt32
                Serial of the container.

        """
        ...

    @staticmethod
    def ResetIgnore():
        """Reset the Autoloot ignore list."""
        ...

    @staticmethod
    def RunOnce(lootListName: str, millisec: int, filter: "Items.Filter"):
        """Start Autoloot with custom parameters.

        Parameters
        ----------
        lootListName: str
                Name of the Autoloot listfilter for search on ground.
        millisec: int
                Delay in milliseconds. (unused)
        filter: Items.Filter
                Item filter

        """
        ...

    @staticmethod
    def SetNoOpenCorpse(noOpen: bool) -> bool:
        """Toggle "No Open Corpse" on/off. The change doesn't persist if you reopen razor.

        Parameters
        ----------
        noOpen: bool
                True: "No Open Corpse" is active - False: otherwise

        Returns
        -------
        bool
                Previous value of "No Open Corpse"

        """
        ...

    @staticmethod
    def Start():
        """Start the Autoloot Agent on the currently active list."""
        ...

    @staticmethod
    def Status() -> bool:
        """Check Autoloot Agent status

        Returns
        -------
        bool
                True: if the Autoloot is running - False: otherwise

        """
        ...

    @staticmethod
    def Stop():
        """Stop the Autoloot Agent."""
        ...

    class AutoLootItem:
        """ """

        Color: int
        Graphics: int
        List: str
        LootBagOverride: int
        Name: str
        Properties: "List[AutoLoot.AutoLootItem.Property]"
        Selected: bool

        class Property: ...


class BandageHeal:
    """ """

    @staticmethod
    def Start():
        """Start BandageHeal Agent."""
        ...

    @staticmethod
    def Status() -> bool:
        """Check BandageHeal Agent status, returns a bool value.

        Returns
        -------
        bool
                True: is running - False: otherwise

        """
        ...

    @staticmethod
    def Stop():
        """Stop BandageHeal Agent."""
        ...


class BuyAgent:
    """The BuyAgent class allow you to interect with the BuyAgent, via scripting."""

    @staticmethod
    def ChangeList(listName: str):
        """Change the BuyAgent's active list.

        Parameters
        ----------
        listName: str
                Name of an existing buy list.

        """
        ...

    @staticmethod
    def Disable():
        """Disable BuyAgent Agent."""
        ...

    @staticmethod
    def Enable():
        """Enable BuyAgent on the currently active list."""
        ...

    @staticmethod
    def Status() -> bool:
        """Check BuyAgent Agent status

        Returns
        -------
        bool
                True: if the BuyAgent is active - False: otherwise

        """
        ...


class CUO:
    """The CUO_Functions class contains invocation of CUO code using reflection
    DANGER !!
    """

    @staticmethod
    def CloseGump(serial: "UInt32"):
        """Invokes the Method close a gump

        Parameters
        ----------
        serial: UInt32

        """
        ...

    @staticmethod
    def CloseMobileHealthBar(mobileserial: Union[int, "UInt32"]):
        """Closes a Mobile Status Gump of an Entity

        Parameters
        ----------
        mobileserial: int or UInt32

        """
        ...

    @staticmethod
    def CloseMyStatusBar():
        """Invokes the Method to close your status bar gump inside the CUO code"""
        ...

    @staticmethod
    def CloseTMap() -> bool:
        """Invokes the CloseWithRightClick function inside the CUO code
        First T-Map is retrieved, and then only closed if it is a map
        Returns True if a map was closed, else False

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def Following() -> "Tuple[Boolean, UInt32]":
        """Returns the status and target of the ClassicUO client's follow
        behavior.

        Returns
        -------
        ValueTuple[Boolean, UInt32]
                bool followingMode, uint followingTarget

        """
        ...

    @staticmethod
    def FollowMobile(mobileserial: "UInt32"):
        """Make the ClassicUO client follow the specific mobile.

        This is the same behavior as alt + left-clicking, which normally
        shows the overhead message "Now following."

        Parameters
        ----------
        mobileserial: UInt32

        """
        ...

    @staticmethod
    def FollowOff():
        """Stop the ClassicUO client from following, if it was following a
        mobile.

        """
        ...

    @staticmethod
    def FreeView(free: bool):
        """Invokes the FreeView function inside the CUO code
        First value is retrieved, and then only set if its not correct

        Parameters
        ----------
        free: bool

        """
        ...

    @staticmethod
    def GetSetting(settingName: str) -> str:
        """Retrieve Current CUO Setting

        Parameters
        ----------
        settingName: str

        Returns
        -------
        str

        """
        ...

    @staticmethod
    def GoToMarker(x: int, y: int):
        """Invokes the GoToMarker function inside the CUO code
        Map must be open for this to work

        Parameters
        ----------
        x: int
        y: int

        """
        ...

    @staticmethod
    def LoadMarkers():
        """Invokes the LoadMarkers function inside the CUO code
        Map must be open for this to work

        """
        ...

    @staticmethod
    def MoveGump(serial: "UInt32", x: int, y: int):
        """Invokes the Method move a gump or container if open.

        Parameters
        ----------
        serial: UInt32
        x: int
        y: int

        """
        ...

    @staticmethod
    def OpenContainerAt(bag: Union["Item", "UInt32"], x: int, y: int):
        """Set a location that CUO will open the container at

        Parameters
        ----------
        bag: Item or UInt32
        x: int
        y: int

        """
        ...

    @staticmethod
    def OpenMobileHealthBar(mobileserial: Union["UInt32", int], x: int, y: int, custom: bool):
        """Invokes the Method to open your status bar gump inside the CUO code
        Open a mobiles health bar at a specified location on the screen

        Parameters
        ----------
        mobileserial: UInt32 or int
        x: int
        y: int
        custom: bool

        """
        ...

    @staticmethod
    def OpenMyStatusBar(x: int, y: int):
        """Invokes the Method to open your status bar gump inside the CUO code

        Parameters
        ----------
        x: int
        y: int

        """
        ...

    @staticmethod
    def PlayMacro(macroName: str):
        """Play a CUO macro by name
        Warning, limited testing !!

        Parameters
        ----------
        macroName: str

        """
        ...

    @staticmethod
    def ProfilePropertySet(propertyName: str, value: Union[str, bool, int]):
        """Set a string Config property in CUO by name
        Set a bool Config property in CUO by name
        Set a int Config property in CUO by name

        Parameters
        ----------
        propertyName: str
        value: str or bool or int

        """
        ...

    @staticmethod
    def SetGumpOpenLocation(gumpserial: "UInt32", x: int, y: int):
        """Set a location that CUO will open the next gump or container at

        Parameters
        ----------
        gumpserial: UInt32
        x: int
        y: int

        """
        ...


class DPSMeter:
    """The DPSMeter class implements a Damage Per Second meter which can be useful to tune meta-builds.(???)"""

    @staticmethod
    def GetDamage(serial: int) -> int:
        """Get total damage per Mobile.

        Parameters
        ----------
        serial: int
                Serial of the Mobile.

        Returns
        -------
        int
                Total damage.

        """
        ...

    @staticmethod
    def Pause():
        """Pause DPSMeter data recording."""
        ...

    @staticmethod
    def Start():
        """Start DPSMeter engine."""
        ...

    @staticmethod
    def Status() -> bool:
        """Check DPSMeter Agent status, returns a bool value.

        Returns
        -------
        bool
                True: is running - False: otherwise

        """
        ...

    @staticmethod
    def Stop():
        """Stop DPSMeter engine."""
        ...


class Dress:
    """ """

    @staticmethod
    def ChangeList(dresslist: str):
        """Change dress list, List must be exist in dress/undress Agent tab.

        Parameters
        ----------
        dresslist: str
                Name of the list of friend.

        """
        ...

    @staticmethod
    def DressFStart():
        """Start Dress engine."""
        ...

    @staticmethod
    def DressFStop():
        """Stop Dress engine."""
        ...

    @staticmethod
    def DressStatus() -> bool:
        """Check Dress Agent status, returns a bool value.

        Returns
        -------
        bool
                True: is running - False: otherwise

        """
        ...

    @staticmethod
    def UnDressFStart():
        """Start UnDress engine."""
        ...

    @staticmethod
    def UnDressFStop():
        """Stop UnDress engine."""
        ...

    @staticmethod
    def UnDressStatus() -> bool:
        """Check UnDress Agent status, returns a bool value.

        Returns
        -------
        bool
                True: is running - False: otherwise

        """
        ...


class Friend:
    """ """

    @staticmethod
    def AddFriendTarget():
        """ """
        ...

    @staticmethod
    def AddPlayer(friendlist: str, name: str, serial: int):
        """Add the player specified to the Friend list named in FriendListName parameter

        Parameters
        ----------
        friendlist: str
                Name of the the Friend List. (See Agent tab)
        name: str
                Name of the Friend want to add.
        serial: int
                Serial of the Friend you want to add.

        """
        ...

    @staticmethod
    def ChangeList(friendlist: str):
        """Change friend list, List must be exist in friend list GUI configuration

        Parameters
        ----------
        friendlist: str
                Name of the list of friend.

        """
        ...

    @staticmethod
    def GetList(friendlist: str) -> "List[Int32]":
        """Retrive list of serial in list, List must be exist in friend Agent tab.

        Parameters
        ----------
        friendlist: str
                Name of the list of friend.

        Returns
        -------
        List[Int32]

        """
        ...

    @staticmethod
    def IsFriend(serial: int) -> bool:
        """Check if Player is in FriendList, returns a bool value.

        Parameters
        ----------
        serial: int
                Serial you want to check

        Returns
        -------
        bool
                True: if is a friend - False: otherwise

        """
        ...

    @staticmethod
    def RemoveFriend(friendlist: str, serial: int) -> bool:
        """Remove the player specified from the Friend list named in FriendListName parameter

        Parameters
        ----------
        friendlist: str
                Name of the the Friend List. (See Agent tab)
        serial: int
                Serial of the Friend you want to remove.

        Returns
        -------
        bool

        """
        ...


class Gumps:
    """The Gumps class is used to read and interact with in-game gumps, via scripting.
    NOTE
    ----
    During development of scripts that involves interecting with Gumps, is often needed to know gumpids and buttonids.
    For this purpose, can be particularly usefull to use *Inspect Gumps* and *Record*, top right, in the internal RE script editor.
    """

    @staticmethod
    def AddAlphaRegion(gd: "Gumps.GumpData", x: int, y: int, width: int, height: int):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        width: int
        height: int

        """
        ...

    @staticmethod
    def AddBackground(gd: "Gumps.GumpData", x: int, y: int, width: int, height: int, gumpId: int):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        width: int
        height: int
        gumpId: int

        """
        ...

    @staticmethod
    def AddButton(
        gd: "Gumps.GumpData",
        x: int,
        y: int,
        normalID: int,
        pressedID: int,
        buttonID: int,
        type: int,
        param: int,
    ):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        normalID: int
        pressedID: int
        buttonID: int
        type: int
        param: int

        """
        ...

    @staticmethod
    def AddCheck(
        gd: "Gumps.GumpData",
        x: int,
        y: int,
        inactiveID: int,
        activeID: int,
        initialState: bool,
        switchID: int,
    ):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        inactiveID: int
        activeID: int
        initialState: bool
        switchID: int

        """
        ...

    @staticmethod
    def AddGroup(gd: "Gumps.GumpData", group: int):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        group: int

        """
        ...

    @staticmethod
    def AddHtml(
        gd: "Gumps.GumpData",
        x: int,
        y: int,
        width: int,
        height: int,
        text: Union[str, int],
        background: bool,
        scrollbar: bool,
    ):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        width: int
        height: int
        text: str or int
        background: bool
        scrollbar: bool

        """
        ...

    @staticmethod
    def AddHtmlLocalized(
        gd: "Gumps.GumpData",
        x: int,
        y: int,
        width: int,
        height: int,
        number: int,
        args: Union[str, int, bool],
        color: Union[int, bool],
        background: Union[bool, None] = None,
        scrollbar: Union[bool, None] = None,
    ):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        width: int
        height: int
        number: int
        args: str or int or bool
        color: int or bool
        background: bool or None
        scrollbar: bool or None

        """
        ...

    @staticmethod
    def AddImage(gd: "Gumps.GumpData", x: int, y: int, gumpId: int, hue: Union[int, None] = None):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        gumpId: int
        hue: int or None

        """
        ...

    @staticmethod
    def AddImageTiled(gd: "Gumps.GumpData", x: int, y: int, width: int, height: int, gumpId: int):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        width: int
        height: int
        gumpId: int

        """
        ...

    @staticmethod
    def AddImageTiledButton(
        gd: "Gumps.GumpData",
        x: int,
        y: int,
        normalID: int,
        pressedID: int,
        buttonID: int,
        type: "Gumps.GumpButtonType",
        param: int,
        itemID: int,
        hue: int,
        width: int,
        height: int,
        localizedTooltip: Union[int, None] = None,
    ):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        normalID: int
        pressedID: int
        buttonID: int
        type: Gumps.GumpButtonType
        param: int
        itemID: int
        hue: int
        width: int
        height: int
        localizedTooltip: int or None

        """
        ...

    @staticmethod
    def AddItem(gd: "Gumps.GumpData", x: int, y: int, itemID: int, hue: Union[int, None] = None):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        itemID: int
        hue: int or None

        """
        ...

    @staticmethod
    def AddLabel(gd: "Gumps.GumpData", x: int, y: int, hue: int, text: Union[str, int]):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        hue: int
        text: str or int

        """
        ...

    @staticmethod
    def AddLabelCropped(
        gd: "Gumps.GumpData",
        x: int,
        y: int,
        width: int,
        height: int,
        hue: int,
        text: Union[str, int],
    ):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        width: int
        height: int
        hue: int
        text: str or int

        """
        ...

    @staticmethod
    def AddPage(gd: "Gumps.GumpData", page: int):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        page: int

        """
        ...

    @staticmethod
    def AddRadio(
        gd: "Gumps.GumpData",
        x: int,
        y: int,
        inactiveID: int,
        activeID: int,
        initialState: bool,
        switchID: int,
    ):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        inactiveID: int
        activeID: int
        initialState: bool
        switchID: int

        """
        ...

    @staticmethod
    def AddSpriteImage(
        gd: "Gumps.GumpData",
        x: int,
        y: int,
        gumpId: int,
        spriteX: int,
        spriteY: int,
        spriteW: int,
        spriteH: int,
    ):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        gumpId: int
        spriteX: int
        spriteY: int
        spriteW: int
        spriteH: int

        """
        ...

    @staticmethod
    def AddTextEntry(
        gd: "Gumps.GumpData",
        x: int,
        y: int,
        width: int,
        height: int,
        hue: int,
        entryID: int,
        initialTextID: Union[int, str],
    ):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        x: int
        y: int
        width: int
        height: int
        hue: int
        entryID: int
        initialTextID: int or str

        """
        ...

    @staticmethod
    def AddTooltip(gd: "Gumps.GumpData", cliloc: Union[int, str], text: Union[str, None] = None):
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        cliloc: int or str
        text: str or None

        """
        ...

    @staticmethod
    def AllGumpIDs() -> "List[UInt32]":
        """

        Returns
        -------
        List[UInt32]

        """
        ...

    @staticmethod
    def CloseGump(gumpid: "UInt32"):
        """Close a specific Gump.

        Parameters
        ----------
        gumpid: UInt32
                ID of the gump

        """
        ...

    @staticmethod
    def CreateGump(
        movable: bool = True,
        closable: bool = True,
        disposable: bool = True,
        resizeable: bool = True,
    ) -> "Gumps.GumpData":
        """Creates an initialized GumpData structure

        Parameters
        ----------
        movable: bool
                allow the gump to be moved
        closable: bool
                allow the gump to be right clicked to close
        disposable: bool
                allow the gump to be disposed (beats me what it does)
        resizeable: bool
                allow the gump to be resized

        Returns
        -------
        Gumps.GumpData

        """
        ...

    @staticmethod
    def CurrentGump() -> "UInt32":
        """Return the ID of most recent, still open Gump.

        Returns
        -------
        UInt32
                ID of gump.

        """
        ...

    @staticmethod
    def GetGumpData(gumpid: "UInt32") -> "Gumps.GumpData":
        """

        Parameters
        ----------
        gumpid: UInt32

        Returns
        -------
        Gumps.GumpData

        """
        ...

    @staticmethod
    def GetGumpRawLayout(gumpid: "UInt32") -> str:
        """Get the Raw layout (definition) of a specific gumpid

        Parameters
        ----------
        gumpid: UInt32

        Returns
        -------
        str
                layout (definition) of the gump.

        """
        ...

    @staticmethod
    def GetGumpText(gumpid: "UInt32") -> "List[String]":
        """Get the Text of a specific Gump.
        It is the cliloc translation of the #s in the gump

        Parameters
        ----------
        gumpid: UInt32

        Returns
        -------
        List[String]
                List of Text in the gump

        """
        ...

    @staticmethod
    def GetLine(gumpId: "UInt32", line_num: int) -> str:
        """Get a specific DATA line from the gumpId if it exists. Filter by line number.
        The textual strings are not considered

        Parameters
        ----------
        gumpId: UInt32
                gump id to get data from
        line_num: int
                Number of the line.

        Returns
        -------
        str
                Text content of the line. (empty: line not found)

        """
        ...

    @staticmethod
    def GetLineList(gumpId: "UInt32", dataOnly: bool) -> "List[String]":
        """Get all text from the specified Gump if still open

        Parameters
        ----------
        gumpId: UInt32
                gump id to get data from
        dataOnly: bool

        Returns
        -------
        List[String]
                Text of the gump.

        """
        ...

    @staticmethod
    def GetTextByID(gd: "Gumps.GumpData", id: int) -> str:
        """

        Parameters
        ----------
        gd: Gumps.GumpData
        id: int

        Returns
        -------
        str

        """
        ...

    @staticmethod
    def HasGump(gumpId: Union["UInt32", None] = None) -> bool:
        """
        Get status if have a gump open or not.

        Parameters
        ----------
        gumpId: UInt32 or None

        Returns
        -------
        bool
                True: There is a Gump open - False: otherwise.

        """
        ...

    @staticmethod
    def IsValid(gumpId: int) -> bool:
        """Validates if the gumpid provided exists in the gump file

        Parameters
        ----------
        gumpId: int
                The id of the gump to check for in the gumps.mul file

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def LastGumpGetLine(line_num: int) -> str:
        """Get a specific line from the most recent and still open Gump. Filter by line number.
        The text constants on the gump ARE included in indexing

        Parameters
        ----------
        line_num: int
                Number of the line.

        Returns
        -------
        str
                Text content of the line. (empty: line not found)

        """
        ...

    @staticmethod
    def LastGumpGetLineList() -> "List[String]":
        """Get all text from the most recent and still open Gump.

        Returns
        -------
        List[String]
                Text of the gump.

        """
        ...

    @staticmethod
    def LastGumpRawLayout() -> str:
        """Get the raw layout (definition) of the most recent and still open Gump.

        Returns
        -------
        str
                layout (definition) of the gump.

        """
        ...

    @staticmethod
    def LastGumpTextExist(text: str) -> bool:
        """Search for text inside the most recent and still open Gump.

        Parameters
        ----------
        text: str
                Text to search.

        Returns
        -------
        bool
                True: Text found in active Gump - False: otherwise

        """
        ...

    @staticmethod
    def LastGumpTextExistByLine(line_num: int, text: str) -> bool:
        """Search for text, in a spacific line of the most recent and still open Gump.

        Parameters
        ----------
        line_num: int
                Number of the line.
        text: str
                Text to search.

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def LastGumpTile() -> "List[Int32]":
        """Get the list of Gump Tile (! this documentation is a stub !)

        Returns
        -------
        List[Int32]
                List of Gump Tile.

        """
        ...

    @staticmethod
    def ResetGump():
        """Clean current status of Gumps."""
        ...

    @staticmethod
    def SendAction(gumpid: "UInt32", buttonid: int):
        """Send a Gump response by gumpid and buttonid.

        Parameters
        ----------
        gumpid: UInt32
                ID of the gump.
        buttonid: int
                ID of the Button to press.

        """
        ...

    @staticmethod
    def SendAdvancedAction(
        gumpid: "UInt32",
        buttonid: int,
        switchlist_id: Union[List, "List[Int32]"],
        textlist_id: Union[List, "List[Int32]", "List[String]", None] = None,
        textlist_str: Union[List, "List[String]", None] = None,
    ):
        """Send a Gump response, with gumpid and buttonid and advanced switch in gumps.
        This function is intended for more complex Gumps, with not only Buttons, but also Switches, CheckBoxes and Text fileds.

        This method can also be used only Text fileds, without Switches.
        This method can also be used only Switches, without Text fileds.

        Parameters
        ----------
        gumpid: UInt32
                ID of the gump.
        buttonid: int
                ID of the Button.
        switchlist_id: PythonList or List[Int32]
                List of ID of ON/Active switches. (empty: all Switches OFF)
        textlist_id: PythonList or List[Int32] or List[String] or None
                List of ID of Text fileds. (empty: all text fileds empty )
        textlist_str: PythonList or List[String] or None
                List of the contents of the Text fields, provided in the same order as textlist_id.

        """
        ...

    @staticmethod
    def SendGump(
        gumpid: Union["UInt32", "Gumps.GumpData"],
        serial: "UInt32",
        x: "UInt32",
        y: Union["UInt32", None] = None,
        gumpDefinition: Union[str, None] = None,
        gumpStrings: Union["List[String]", None] = None,
    ):
        """
        Sends a gump using an existing GumpData structure

        Parameters
        ----------
        gumpid: UInt32 or Gumps.GumpData
        serial: UInt32
        x: UInt32
        y: UInt32 or None
        gumpDefinition: str or None
        gumpStrings: List[String] or None

        """
        ...

    @staticmethod
    def WaitForGump(gumpid: "UInt32", delay: int) -> bool:
        """Waits for a specific Gump to appear, for a maximum amount of time. If gumpid is 0 it will match any Gump.

        Parameters
        ----------
        gumpid: UInt32
                ID of the gump. (0: any)
        delay: int
                Maximum wait, in milliseconds.

        Returns
        -------
        bool
                True: wait found the gump - False: otherwise.

        """
        ...

    class GumpData:
        """ """

        buttonid: int
        gumpData: "List[String]"
        gumpDefinition: str
        gumpId: "UInt32"
        gumpLayout: str
        gumpStrings: "List[String]"
        gumpText: "List[String]"
        hasResponse: bool
        layoutPieces: "List[String]"
        serial: "UInt32"
        stringList: "List[String]"
        switches: "List[Int32]"
        text: "List[String]"
        textID: "List[Int32]"
        x: "UInt32"
        y: "UInt32"

    class GumpButtonType(Enum):
        Page = 0
        Reply = 1


class HotKeyEvent:
    """@nodoc"""


class UOEntity:
    """Base class for all entities in the game."""

    ...


class Item(UOEntity):
    """The Item class represent a single in-game Item object. Examples of Item are: Swords, bags, bandages, reagents, clothing.
    While the Item.Serial is unique for each Item, Item.ItemID is the unique for the Item apparence, or image. Sometimes is also called ID or Graphics ID.
    Item can also be house foriture as well as decorative items on the ground, like lamp post and banches.
    However, for Item on the ground that cannot be picked up, they might be part of the world map, see Statics class.
    """

    Amount: int
    """Read amount from item type object."""

    Color: "UInt16"
    Container: int
    """Serial of the container which contains the object."""

    ContainerOpened: bool
    """True when the container was opened"""

    Contains: "List[Item]"
    """Contains the list of Item inside a container."""

    CorpseNumberItems: int
    """-1 until corpse is checked, then # items in corpse. Used by looter to ignore empty corpses"""

    Deleted: bool
    Direction: str
    """Item direction."""

    Durability: int
    """Get the current durability of an Item. (0: no durability)"""

    Graphics: "UInt16"
    GridNum: int
    """Returns the GridNum of the item. (need better documentation)"""

    Hue: "UInt16"
    Image: "Bitmap"
    """Get the in-game image on an Item as Bitmap object.
		See MSDN: https://docs.microsoft.com/dotnet/api/system.drawing.bitmap"""

    IsBagOfSending: bool
    """True: if the item is a bag of sending - False: otherwise."""

    IsContainer: bool
    """True: if the item is a container - False: otherwise."""

    IsCorpse: bool
    """True: if the item is a corpse - False: otherwise."""

    IsDoor: bool
    """True: if the item is a door - False: otherwise."""

    IsInBank: bool
    """True: if the item is in the Player's bank - False: otherwise."""

    IsLootable: bool
    """True: For regualar items - False: for hair, beards, etc."""

    IsPotion: bool
    """True: if the item is a potion - False: otherwise."""

    IsResource: bool
    """True: if the item is a resource (ore, sand, wood, stone, fish) - False: otherwise"""

    IsSearchable: bool
    """True: if the item is a pouch - False: otherwise."""

    IsTwoHanded: bool
    """True: if the item is a 2-handed weapon - False: otherwise."""

    IsVirtueShield: bool
    """True: if the item is a virtue shield - False: otherwise."""

    ItemID: int
    """Represents the type of Item, usually unique for the Item image.  Sometime called ID or Graphics ID."""

    Layer: str
    """Gets the Layer, for werable items only. (need better documentation)"""

    Light: int
    """Item light's direction (e.g. will affect corpse's facing direction)"""

    MaxDurability: int
    """Get the maximum durability of an Item. (0: no durability)"""

    Movable: bool
    """Item is movable"""

    Name: str
    """Item name"""

    OnGround: bool
    """True: if the item is on the ground - False: otherwise."""

    Position: "Point3D"
    Properties: "List[Property]"
    """Get the list of Properties of an Item."""

    PropsUpdated: bool
    """True: if Properties are updated - False: otherwise."""

    RootContainer: int
    """Get serial of root container of item."""

    Serial: int
    Updated: bool
    """Check if the Item already have been updated with all the properties. (need better documentation)"""

    Visible: bool
    """Item is Visible"""

    Weight: int
    """Get the weight of a item. (0: no weight)"""

    def DistanceTo(self, mob: Union["Mobile", "Item"]) -> int:
        """Return the distance in number of tiles, from Item to Mobile.


        Parameters
        ----------
        mob: Mobile or Item
                Target as Mobile
                Target as Item

        Returns
        -------
        int
                Distance in number of tiles.

        """
        ...

    def Equals(self, obj: Union[object, "UOEntity"]) -> bool:
        """

        Parameters
        ----------
        obj: object or UOEntity

        Returns
        -------
        bool

        """
        ...

    def GetHashCode(self) -> int:
        """

        Returns
        -------
        int

        """
        ...

    def GetWorldPosition(self) -> "Point3D":
        """

        Returns
        -------
        Point3D

        """
        ...

    def IsChildOf(self, container: Union["Mobile", "Item"], maxDepth: int) -> bool:
        """
        Check if an Item is contained in a container. Can be a Item or a Mobile (wear by).

        Parameters
        ----------
        container: Mobile or Item
                Mobile as container.
                Item as container.
        maxDepth: int

        Returns
        -------
        bool
                True: if is contained - False: otherwise.

        """
        ...

    def ToString(self) -> str:
        """

        Returns
        -------
        str

        """
        ...


class ItemData: ...


class Items:
    """The Items class provides a wide range of functions to search and interact with Items."""

    @staticmethod
    def ApplyFilter(filter: "Items.Filter") -> "List[Item]":
        """Filter the global list of Items according to the options specified by the filter ( see: Items.Filter ).

        Parameters
        ----------
        filter: Items.Filter
                A filter object.

        Returns
        -------
        List[Item]
                the list of Items respectinf the filter criteria.

        """
        ...

    @staticmethod
    def BackpackCount(itemid: int, color: int) -> int:
        """Count items in Player Backpack.

        Parameters
        ----------
        itemid: int
                ItemID to search.
        color: int
                Color to search. (default -1: any color)

        Returns
        -------
        int

        """
        ...

    @staticmethod
    def ChangeDyeingTubColor(dyes: "Item", dyeingTub: "Item", color: int):
        """Use the Dyes on a Dyeing Tub and select the color via color picker, using dedicated packets.
        Need to specify the dyes, the dye tube and the color to use.

        Parameters
        ----------
        dyes: Item
                Dyes as Item object.
        dyeingTub: Item
                Dyeing Tub as Item object.
        color: int
                Color to choose.

        """
        ...

    @staticmethod
    def Close(item: Union["Item", int]):
        """
        Close opened container window.
        On OSI, to close opened corpse window, you need to close the corpse's root container
        Currently corpse's root container can be found by using item filter.

        Parameters
        ----------
        item: Item or int
                Serial or Item to hide.

        """
        ...

    @staticmethod
    def ContainerCount(container: Union["Item", int], itemid: int, color: int, recursive: bool) -> int:
        """Count items inside a container, summing also the amount in stacks.


        Parameters
        ----------
        container: Item or int
                Serial or Item to search into.
        itemid: int
                ItemID of the item to search.
        color: int
                Color to match. (default: -1, any color)
        recursive: bool
                Search also in already open subcontainers.

        Returns
        -------
        int

        """
        ...

    @staticmethod
    def ContextExist(i: Union["Item", int], name: str) -> int:
        """
        Check if Context Menu entry exists for an Item.

        Parameters
        ----------
        i: Item or int
                Serial or Item to check.
        name: str
                Name of the Context Manu entry

        Returns
        -------
        int

        """
        ...

    @staticmethod
    def DropFromHand(item: "Item", container: "Item"):
        """Drop into a bag an Item currently held in-hand. ( see: Items.Lift )

        Parameters
        ----------
        item: Item
                Item object to drop.
        container: Item
                Target container.

        """
        ...

    @staticmethod
    def DropItemGroundSelf(item: Union["Item", int], amount: int):
        """Drop an Item on the ground, at the current Player position.
        NOTE: On some server is not allowed to drop Items on tiles occupied by Mobiles and the Player.
        This function seldom works because the servers dont allow drop where your standing

        Parameters
        ----------
        item: Item or int
                Item object to drop.
        amount: int
                Amount to move. (default: 0, the whole stack)

        """
        ...

    @staticmethod
    def FindAllByID(
        itemids: Union[List, int, "List[Int32]"],
        color: int,
        container: int,
        range: int,
        considerIgnoreList: bool = True,
    ) -> Union[List, "List[Item]"]:
        """Find a List of Items matching specific list of ItemID, Color and Container.
        Optionally can search in all subcontaners or to a maximum depth in subcontainers.
        Can use -1 on color for no chose color, can use -1 on container for search in all item in memory.
        The depth defaults to only the top but can search for # of sub containers.


        Parameters
        ----------
        itemids: PythonList or int or List[Int32]
        color: int
                Color filter. (-1: any, 0: natural )
        container: int
                Serial of the container to search. (-1: any Item)
        range: int
        considerIgnoreList: bool
                True: Ignore Items are excluded - False: any Item.

        Returns
        -------
        PythonList, List[Item]
                The Item matching the criteria.

        """
        ...

    @staticmethod
    def FindByID(
        itemids: Union["List[Int32]", int],
        color: int,
        container: int,
        range: Union[int, bool],
        considerIgnoreList: bool = True,
    ) -> "Item":
        """Find a single Item matching specific ItemID, Color and Container.
        Optionally can search in all subcontaners or to a maximum depth in subcontainers.
        Can use -1 on color for no chose color, can use -1 on container for search in all item in memory. The depth defaults to only the top but can search for # of sub containers.


        Parameters
        ----------
        itemids: List[Int32] or int
                ItemID filter.
        color: int
                Color filter. (-1: any, 0: natural )
        container: int
                Serial of the container to search. (-1: any Item)
        range: int or bool
                Search subcontainers.
                True: all subcontainers
                False: only main
                1,2,n: Maximum subcontainer depth
        considerIgnoreList: bool
                True: Ignore Items are excluded - False: any Item.

        Returns
        -------
        Item
                The Item matching the criteria.

        """
        ...

    @staticmethod
    def FindByName(itemName: str, color: int, container: int, range: int, considerIgnoreList: bool = True) -> "Item":
        """Find a single Item matching specific Name, Color and Container.
        Optionally can search in all subcontaners or to a maximum depth in subcontainers.
        Can use -1 on color for no chose color, can use -1 on container for search in all item in memory. The depth defaults to only the top but can search for # of sub containers.

        Parameters
        ----------
        itemName: str
                Item Name filter.
        color: int
                Color filter. (-1: any, 0: natural )
        container: int
                Serial of the container to search. (-1: any Item)
        range: int
                Search subcontainers.
                1,2,n: Maximum subcontainer depth
        considerIgnoreList: bool
                True: Ignore Items are excluded - False: any Item.

        Returns
        -------
        Item
                The Item matching the criteria.

        """
        ...

    @staticmethod
    def FindBySerial(serial: int) -> "Item":
        """Search for a specific Item by using it Serial

        Parameters
        ----------
        serial: int
                Serial of the Item.

        Returns
        -------
        Item
                Item object if found, or null if not found.

        """
        ...

    @staticmethod
    def GetImage(itemID: int, hue: int) -> "Bitmap":
        """Get the Image on an Item by specifing the ItemID. Optinally is possible to apply a color.

        Parameters
        ----------
        itemID: int
                ItemID to use.
        hue: int
                Optional: Color to apply. (Default 0, natural)

        Returns
        -------
        Bitmap

        """
        ...

    @staticmethod
    def GetProperties(itemserial: int, delay: int) -> "List[Property]":
        """Request to get immediatly the Properties of an Item, and wait for a specified amount of time.
        This only returns properties and does not attempt to update the object.
        Used in this way, properties for object not yet seen can be retrieved

        Parameters
        ----------
        itemserial: int
                Serial or Item read.
        delay: int
                Maximum waiting time, in milliseconds.

        Returns
        -------
        List[Property]

        """
        ...

    @staticmethod
    def GetPropStringByIndex(item: Union["Item", int], index: int) -> str:
        """
        Get a Property line, by index. if not found returns and empty string.

        Parameters
        ----------
        item: Item or int
                Serial or Item to read.
        index: int
                Number of the Property line.

        Returns
        -------
        str
                A property line as a string.

        """
        ...

    @staticmethod
    def GetPropStringList(item: Union["Item", int]) -> "List[String]":
        """Get string list of all Properties of an item, if item no props list is empty.


        Parameters
        ----------
        item: Item or int
                Serial or Item to read.

        Returns
        -------
        List[String]
                List of strings.

        """
        ...

    @staticmethod
    def GetPropValue(serial: Union[int, "Item"], name: str) -> float:
        """Read the value of a Property.


        Parameters
        ----------
        serial: int or Item
                Serial or Item to read.
        name: str
                Name of the Propery.

        Returns
        -------
        float

        """
        ...

    @staticmethod
    def GetPropValueString(serial: int, name: str) -> str:
        """Get a Property line, by name. if not found returns and empty string.

        Parameters
        ----------
        serial: int
                Serial or Item to read.
        name: str
                Number of the Property line.

        Returns
        -------
        str
                A property value as a string.

        """
        ...

    @staticmethod
    def GetWeaponAbility(itemId: int) -> "Tuple[String, String]":
        """NOTE: This is from an internal razor table and can be changed based on your server!
        Returns a pair of string values (Primary Ability, Secondary Ability)
        for the supplied item ID.
        "Invalid", "Invalid" for items not in the internal table

        Parameters
        ----------
        itemId: int

        Returns
        -------
        ValueTuple[String, String]

        """
        ...

    @staticmethod
    def Hide(item: Union["Item", int]):
        """
        Hied an Item, affects only the player.

        Parameters
        ----------
        item: Item or int
                Serial or Item to hide.

        """
        ...

    @staticmethod
    def IgnoreTypes(itemIdList: List):
        """Used to ignore specific types. Be careful as you wont see things you ignore,
        and could result in a mobile being able to kill you without you seeing it

        Parameters
        ----------
        itemIdList: PythonList

        """
        ...

    @staticmethod
    def Lift(item: "Item", amount: int):
        """Lift an Item and hold it in-hand. ( see: Items.DropFromHand )

        Parameters
        ----------
        item: Item
                Item object to Lift.
        amount: int
                Amount to lift. (0: the whole stack)

        """
        ...

    @staticmethod
    def Message(item: Union["Item", int], hue: int, message: str):
        """
        Display an in-game message on top of an Item, visibile only for the Player.

        Parameters
        ----------
        item: Item or int
                Serial or Item to display text on.
        hue: int
                Color of the message.
        message: str
                Message as

        """
        ...

    @staticmethod
    def Move(
        source: Union["Item", int],
        destination: Union["Mobile", int, "Item"],
        amount: int,
        x: Union[int, None] = None,
        y: Union[int, None] = None,
    ):
        """
        Move an Item to a destination, which can be an Item or a Mobile.

        Parameters
        ----------
        source: Item or int
                Serial or Item of the Item to move.
        destination: Mobile or int or Item
                Serial, Mobile or Item as destination.
        amount: int
                Amount to move (-1: the whole stack)
        x: int or None
                Optional: X coordinate inside the container.
        y: int or None
                Optional: Y coordinate inside the container.

        """
        ...

    @staticmethod
    def MoveOnGround(source: Union["Item", int], amount: int, x: int, y: int, z: int):
        """
        Move an Item on the ground to a specific location.

        Parameters
        ----------
        source: Item or int
                Serial or Item to move.
        amount: int
                Amount of Items to move (0: the whole stack )
        x: int
                X world coordinates.
        y: int
                Y world coordinates.
        z: int
                Z world coordinates.

        """
        ...

    @staticmethod
    def OpenAt(item: Union["Item", int], x: int, y: int):
        """

        Parameters
        ----------
        item: Item or int
        x: int
        y: int

        """
        ...

    @staticmethod
    def OpenContainerAt(bag: "Item", x: int, y: int):
        """Open a container at a specific location on the screen

        Parameters
        ----------
        bag: Item
                Container as Item object.
        x: int
                x location to open at
        y: int
                y location to open at

        """
        ...

    @staticmethod
    def Select(items: "List[Item]", selector: str) -> "Item":
        """

        Parameters
        ----------
        items: List[Item]
        selector: str

        Returns
        -------
        Item

        """
        ...

    @staticmethod
    def SetColor(serial: int, color: int):
        """Change/override the Color of an Item, the change affects only Player client. The change is not persistent.
        If the color is -1 or unspecified, the color of the item is restored.

        Parameters
        ----------
        serial: int
                Serial of the Item.
        color: int
                Color as number. (default: -1, reset original color)

        """
        ...

    @staticmethod
    def SingleClick(itemserial: Union[int, "Item"]):
        """
        Send a single click network event to the server.

        Parameters
        ----------
        itemserial: int or Item
                Serial or Item to click

        """
        ...

    @staticmethod
    def UseItem(
        itemSerial: Union[int, "Item"],
        targetSerial: Union[int, "UOEntity", None] = None,
        wait: Union[bool, None] = None,
    ):
        """Use an Item, optionally is possible to specify a Item or Mobile target.
        NOTE: The optional target may not work on some free shards. Use Target.Execute instead.


        Parameters
        ----------
        itemSerial: int or Item
                Serial or Item to use.
        targetSerial: int or UOEntity or None
                Optional: Serial of the Item or Mobile target.
        wait: bool or None
                Optional: Wait for confirmation by the server. (default: True)

        """
        ...

    @staticmethod
    def UseItemByID(itemid: int, color: int) -> bool:
        """Use any item of a specific type, matching Item.ItemID. Optionally also of a specific color, matching Item.Hue.

        Parameters
        ----------
        itemid: int
                ItemID to be used.
        color: int
                Color to be used. (default: -1, any)

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def WaitForContents(bag: Union["Item", int], delay: int) -> bool:
        """Open a container an wait for the Items to load, for a maximum amount of time.


        Parameters
        ----------
        bag: Item or int
                Container as Item object.
                Container as Item serial.
        delay: int
                Maximum wait, in milliseconds.
                max time to wait for contents

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def WaitForProps(itemserial: Union[int, "Item"], delay: int):
        """If not updated, request to the Properties of an Item, and wait for a maximum amount of time.


        Parameters
        ----------
        itemserial: int or Item
                Serial or Item read.
        delay: int
                Maximum waiting time, in milliseconds.

        """
        ...

    class Filter:
        """The Items.Filter class is used to store options to filter the global Item list.
        Often used in combination with Items.ApplyFilter.
        """

        CheckIgnoreObject: bool
        """Exclude from the search Items which are currently on the global Ignore List. ( default: False, any Item )"""

        Enabled: bool
        """True: The filter is used - False: Return all Item. ( default: True, active )"""

        Graphics: "List[Int32]"
        """Limit the search to a list of Grapichs ID (see: Item.ItemID ) 
			Supports .Add() and .AddRange()"""

        Hues: "List[Int32]"
        """Limit the search to a list of Colors.
			Supports .Add() and .AddRange()"""

        IsContainer: int
        """Limit the search to the Items which are also containers. (default: -1: any Item)"""

        IsCorpse: int
        """Limit the search to the corpses on the ground. (default: -1, any Item)"""

        IsDoor: int
        """Limit the search to the doors. (default: -1: any Item)"""

        Layers: "List[String]"
        """Limit the search to the wearable Items by Layer.
			Supports .Add() and .AddRange()
			
			Layers:
			RightHand
			LeftHand
			Shoes
			Pants
			Shirt
			Head
			Gloves
			Ring
			Neck
			Waist
			InnerTorso
			Bracelet
			MiddleTorso
			Earrings
			Arms
			Cloak
			OuterTorso
			OuterLegs
			InnerLegs
			Talisman"""

        Movable: int
        """Limit the search to only Movable Items. ( default: -1, any Item )"""

        Multi: int
        """Limit the search to only Multi Items. ( default: -1, any Item )"""

        Name: str
        """Limit the search by name of the Item."""

        OnGround: int
        """Limit the search to the Items on the ground. (default: -1, any Item)"""

        RangeMax: float
        """Limit the search by distance, to Items which are at most RangeMax tiles away from the Player. ( default: -1, any Item )"""

        RangeMin: float
        """Limit the search by distance, to Items which are at least RangeMin tiles away from the Player. ( default: -1, any Item )"""

        Serials: "List[Int32]"
        """Limit the search to a list of Serials of Item to find. (ex: 0x0406EFCA )
			Supports .Add() and .AddRange()"""

        ZRangeMax: float
        """Limit the search by height, to Items which are at most ZRangeMax coordinates away from the Player. ( default: -1, any Item )"""

        ZRangeMin: float
        """Limit the search by height, to Items which are at least ZRangeMin coordinates away from the Player. ( default: -1, any Item )"""


class Journal:
    """The Journal class provides access to the message Journal."""

    @staticmethod
    def Clear(toBeRemoved: Union[str, None] = None):
        """Removes all matching entry from the Jorunal.
        Removes all entry from the Jorunal.

        Parameters
        ----------
        toBeRemoved: str or None

        """
        ...

    @staticmethod
    def FilterText(text: str):
        """Store a string that if matched, will block journal message ( case insensitive )

        Parameters
        ----------
        text: str
                Text to block. case insensitive, and will match if the incoming message contains the text

        """
        ...

    @staticmethod
    def GetJournalEntry(
        afterTimestap: Union[float, "Journal.JournalEntry"],
    ) -> "List[Journal.JournalEntry]":
        """Get a copy of all Journal lines as JournalEntry. The list can be filtered to include *only* most recent events.

        Parameters
        ----------
        afterTimestap: float or Journal.JournalEntry
                Timestap as UnixTime, the number of seconds elapsed since 01-Jan-1970. (default: -1, no filter)
                A JournalEntry object (default: null, no filter)

        Returns
        -------
        List[Journal.JournalEntry]
                List of JournalEntry

        """
        ...

    @staticmethod
    def GetLineText(text: str, addname: bool) -> str:
        """Search and return the most recent line Journal containing the given text. (case sensitive)

        Parameters
        ----------
        text: str
                Text to search.
        addname: bool
                Prepend source name. (default: False)

        Returns
        -------
        str
                Return the full line - Empty string if not found.

        """
        ...

    @staticmethod
    def GetSpeechName() -> "List[String]":
        """Get list of speakers.

        Returns
        -------
        List[String]
                List of speakers as text.

        """
        ...

    @staticmethod
    def GetTextByColor(color: int, addname: bool) -> "List[String]":
        """Returns all the lines present in the Journal for a given color.

        Parameters
        ----------
        color: int
                Color of the source.
        addname: bool
                Prepend source name. (default: False)

        Returns
        -------
        List[String]
                A list of Journal as lines of text.

        """
        ...

    @staticmethod
    def GetTextByName(name: str, addname: bool) -> "List[String]":
        """Returns all the lines present in the Journal for a given source name. (case sensitive)

        Parameters
        ----------
        name: str
                Name of the source.
        addname: bool
                Prepend source name. (default: False)

        Returns
        -------
        List[String]
                A list of Journal as lines of text.

        """
        ...

    @staticmethod
    def GetTextBySerial(serial: int, addname: bool) -> "List[String]":
        """Returns all the lines present in the Journal for a given serial.

        Parameters
        ----------
        serial: int
                Serial of the source.
        addname: bool
                Prepend source name. (default: False)

        Returns
        -------
        List[String]
                A list of Journal as lines of text.

        """
        ...

    @staticmethod
    def GetTextByType(type: str, addname: bool) -> "List[String]":
        """Returns all the lines present in the Journal for a given type. (case sensitive)

        Parameters
        ----------
        type: str
                Regular
                System
                Emote
                Label
                Focus
                Whisper
                Yell
                Spell
                Guild
                Alliance
                Party
                Encoded
                Special
        addname: bool
                Prepend source name. (default: False)

        Returns
        -------
        List[String]
                A list of Journal as lines of text.

        """
        ...

    @staticmethod
    def RemoveFilterText(text: str):
        """Remove a stored a string that if matched, would block journal message ( case insensitive )

        Parameters
        ----------
        text: str
                Text to no longer block. case insensitive

        """
        ...

    @staticmethod
    def Search(text: str) -> bool:
        """Search in the Journal for the occurrence of text. (case sensitive)

        Parameters
        ----------
        text: str
                Text to search.

        Returns
        -------
        bool
                True: Text is found - False: otherwise

        """
        ...

    @staticmethod
    def SearchByColor(text: str, color: int) -> bool:
        """Search in the Journal for the occurrence of text, for a given color. (case sensitive)

        Parameters
        ----------
        text: str
                Text to search.
        color: int
                Color of the message.

        Returns
        -------
        bool
                True: Text is found - False: otherwise

        """
        ...

    @staticmethod
    def SearchByName(text: str, name: str) -> bool:
        """Search in the Journal for the occurrence of text, for a given source. (case sensitive)

        Parameters
        ----------
        text: str
                Text to search.
        name: str
                Name of the source.

        Returns
        -------
        bool
                True: Text is found - False: otherwise

        """
        ...

    @staticmethod
    def SearchByType(text: str, type: str) -> bool:
        """Search in the Journal for the occurrence of text, for a given type. (case sensitive)

        Parameters
        ----------
        text: str
                Text to search.
        type: str
                Regular
                System
                Emote
                Label
                Focus
                Whisper
                Yell
                Spell
                Guild
                Alliance
                Party
                Encoded
                Special

        Returns
        -------
        bool
                True: Text is found - False: otherwise

        """
        ...

    @staticmethod
    def WaitByName(name: str, delay: int) -> bool:
        """Pause script and wait for maximum amount of time, for a specific source to appear in Journal. (case sensitive)

        Parameters
        ----------
        name: str
                Name of the source.
        delay: int
                Maximum pause in milliseconds.

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def WaitJournal(text: Union[str, "List[String]"], delay: int) -> Tuple[bool, str]:
        """Pause script and wait for maximum amount of time, for a specific text to appear in Journal. (case sensitive)


        Parameters
        ----------
        text: str or List[String]
                Text to search.
        delay: int
                Maximum pause in milliseconds.

        Returns
        -------
        bool, str
                True: Text is found - False: otherwise

        """
        ...

    class JournalEntry:
        """The JournalEntry class rapresents a line in the Journal."""

        Color: int
        """Color of the text."""

        Name: str
        """Name of the source, can be a Mobile or an Item."""

        Serial: int
        """Name of the source, can be a Mobile or an Item."""

        Text: str
        """Actual content of the Journal Line."""

        Timestamp: float
        """Timestamp as UnixTime, the number of seconds elapsed since 01-Jan-1970."""

        Type: str
        """Regular
			System
			Emote
			Label
			Focus
			Whisper
			Yell
			Spell
			Guild
			Alliance
			Party
			Encoded
			Special"""

        def Copy(self) -> "Journal.JournalEntry":
            """

            Returns
            -------
            Journal.JournalEntry

            """
            ...


class Misc:
    """The Misc class contains general purpose functions of common use."""

    @staticmethod
    def AllSharedValue() -> "List[String]":
        """

        Returns
        -------
        List[String]

        """
        ...

    @staticmethod
    def AppendNotDupToFile(fileName: str, lineOfData: str) -> bool:
        """Allows creation and append of a file within RE ValidLocations.
        For OSI/RE this is only the RE directory / sub-directories
        For CUO/RE this is only CUO or RE directory / sub-directories
        The filename MUST end in a limited file suffix list
        Checks to see if an identical line is already in the file, and does not add if it exists

        Parameters
        ----------
        fileName: str
        lineOfData: str

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def AppendToFile(fileName: str, lineOfData: str) -> bool:
        """Allows creation and append of a file within RE ValidLocations.
        For OSI/RE this is only the RE directory / sub-directories
        For CUO/RE this is only CUO or RE directory / sub-directories
        The filename MUST end in a limited file suffix list

        Parameters
        ----------
        fileName: str
        lineOfData: str

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def Beep():
        """Play Beep system sound."""
        ...

    @staticmethod
    def CancelPrompt():
        """Cancel a prompt request."""
        ...

    @staticmethod
    def CaptureNow() -> str:
        """Creates a snapshot of the current UO window.

        Returns
        -------
        str
                The path to the saved file.

        """
        ...

    @staticmethod
    def ChangeProfile(profileName: str):
        """Allow the scripted loading of a profile

        Parameters
        ----------
        profileName: str
                Name of profile to load

        """
        ...

    @staticmethod
    def CheckIgnoreObject(serial: Union[int, "UOEntity"]) -> bool:
        """Check object from ignore list, return true if present. Can check Serial, Items or Mobiles


        Parameters
        ----------
        serial: int or UOEntity
                Serial to check.

        Returns
        -------
        bool
                True: Object is ignored - False: otherwise.

        """
        ...

    @staticmethod
    def CheckSharedValue(name: str) -> bool:
        """Check if a shared value exixts.

        Parameters
        ----------
        name: str
                Name of the value.

        Returns
        -------
        bool
                True: Shared value exists - False: otherwise.

        """
        ...

    @staticmethod
    def ClearDragQueue():
        """Clear the Drag-n-Drop queue."""
        ...

    @staticmethod
    def ClearIgnore():
        """Clear ignore list from all object"""
        ...

    @staticmethod
    def CloseBackpack():
        """Close the backpack.
        (OSI client only, no ClassicUO)

        """
        ...

    @staticmethod
    def CloseMenu():
        """Close opened Old Menu."""
        ...

    @staticmethod
    def ConfigDirectory() -> str:
        """Get the full path to the Config Directory.

        Returns
        -------
        str
                Full path to the Scripts Directory.

        """
        ...

    @staticmethod
    def ContextReply(serial: Union[int, "UOEntity"], respone_num: Union[int, str]):
        """Respond to a context menu on mobile or item. Menu ID is base zero, or can use string of menu text.


        Parameters
        ----------
        serial: int or UOEntity
                Serial of the Entity
                serial number of the item to get a context menu from
        respone_num: int or str
                Poition of the option in the menu. Starts from 0.
                Name of the Entry as wirtten in-game.

        """
        ...

    @staticmethod
    def DataDirectory() -> str:
        """Get the full path to the Config Directory.

        Returns
        -------
        str
                Full path to the Config Directory.

        """
        ...

    @staticmethod
    def DeleteFile(fileName: str) -> bool:
        """Allows deletion of a file within RE ValidLocations.
        For OSI/RE this is only the RE directory / sub-directories
        For CUO/RE this is only CUO or RE directory / sub-directories
        The filename MUST end in a limited file suffix list

        Parameters
        ----------
        fileName: str

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def Disconnect():
        """Force client to disconnect."""
        ...

    @staticmethod
    def Distance(X1: int, Y1: int, X2: int, Y2: int) -> int:
        """Returns the UO distance between the 2 sets of co-ordinates.

        Parameters
        ----------
        X1: int
                X co-ordinate of first place.
        Y1: int
                Y co-ordinate of first place.
        X2: int
                X co-ordinate of second place.
        Y2: int
                Y co-ordinate of second place.

        Returns
        -------
        int

        """
        ...

    @staticmethod
    def DistanceSqrt(point_a: "Point3D", point_b: "Point3D") -> float:
        """Compute the distance between 2 Point3D using pythagorian.

        Parameters
        ----------
        point_a: Point3D
                First coordinates.
        point_b: Point3D
                Second coordinates.

        Returns
        -------
        float

        """
        ...

    @staticmethod
    def ExportPythonAPI(path: str, pretty: bool):
        """Return a string containing list RE Python API list in JSON format.

        Parameters
        ----------
        path: str
                Name of the output file. (default: Config/AutoComplete.json )
        pretty: bool
                Print a readable JSON. (default: True )

        """
        ...

    @staticmethod
    def FilterSeason(enable: bool, seasonFlag: "UInt32"):
        """Enable or disable the Seasons filter forcing a specific season
        Season filter state will be saved on logout but not the season flag that will be recovered.

        Parameters
        ----------
        enable: bool
                True: enable seasons filter
        seasonFlag: UInt32
                0: Spring (default fallback)
                1: Summer
                2: Fall
                3: Winter
                4: Desolation

        """
        ...

    @staticmethod
    def FocusUOWindow():
        """Set UoClient window in focus or restore if minimized."""
        ...

    @staticmethod
    def GetContPosition() -> "Point2D":
        """Get the position of the currently active Gump/Container.
        (OSI client only, no ClassicUO)

        Returns
        -------
        Point
                Return X,Y coordinates as a Point2D

        """
        ...

    @staticmethod
    def GetMapInfo(serial: "UInt32") -> "Misc.MapInfo":
        """Get MapInfo about a Mobile or Item using the serial

        Parameters
        ----------
        serial: UInt32
                Serial of the object.

        Returns
        -------
        Misc.MapInfo
                A MapInfo object.

        """
        ...

    @staticmethod
    def GetMenuTitle() -> str:
        """Get the title of title for open Old Menu.

        Returns
        -------
        str
                Text of the title.

        """
        ...

    @staticmethod
    def GetWindowSize() -> "Rectangle":
        """Get a Rectangle representing the window size.
        See also: https://docs.microsoft.com/dotnet/api/system.drawing.rectangle

        Returns
        -------
        Rectangle
                Rectangle object. Properties: X, Y, Width, Height.

        """
        ...

    @staticmethod
    def HasMenu() -> bool:
        """Check if an Old Menu is open.

        Returns
        -------
        bool
                True: is open - False: otherwise

        """
        ...

    @staticmethod
    def HasPrompt() -> bool:
        """Check if have a prompt request.

        Returns
        -------
        bool
                True: there is a prompt - False: otherwise

        """
        ...

    @staticmethod
    def HasQueryString() -> bool:
        """Check if a have a query string menu opened, return true or false.

        Returns
        -------
        bool
                True: Has quesy - False: otherwise.

        """
        ...

    @staticmethod
    def IgnoreObject(serial: Union[int, "UOEntity"]):
        """
        Add an entiry to the ignore list. Can ignore Serial, Items or Mobiles.

        Parameters
        ----------
        serial: int or UOEntity
                Serial to ignore.

        """
        ...

    @staticmethod
    def Inspect():
        """Prompt the user with a Target. Open the inspector for the selected target."""
        ...

    @staticmethod
    def IsItem(serial: "UInt32") -> bool:
        """Determine if the serial is an item

        Parameters
        ----------
        serial: UInt32
                Serial number of object to test is Item

        Returns
        -------
        bool
                Return True - is an Item False - is not an item

        """
        ...

    @staticmethod
    def IsMobile(serial: "UInt32") -> bool:
        """Determine if the serial is a mobile

        Parameters
        ----------
        serial: UInt32
                Serial number of object to test is Mobile

        Returns
        -------
        bool
                Return True - is a mobile False - is not a mobile

        """
        ...

    @staticmethod
    def LastHotKey() -> "HotKeyEvent":
        """Returns the latest HotKey recorded by razor as HotKeyEvent object.

        Returns
        -------
        HotKeyEvent

        """
        ...

    @staticmethod
    def LeftMouseClick(xpos: int, ypos: int, clientCoords: bool):
        """Perform a phisical left click on the window using Windows API.
        Is possible to use abolute Screen Coordinates by setting clientCoords=False.

        Parameters
        ----------
        xpos: int
                X click coordinate.
        ypos: int
                Y click coordinate.
        clientCoords: bool
                True: Client coordinates.- False:Screen coordinates (default: True, client).

        """
        ...

    @staticmethod
    def MenuContain(text: str) -> bool:
        """Search in open Old Menu if contains a specific text.

        Parameters
        ----------
        text: str
                Text to search.

        Returns
        -------
        bool
                True: Text found - False: otherwise.

        """
        ...

    @staticmethod
    def MenuResponse(text: str):
        """Perform a menu response by subitem name. If item not exist close menu.

        Parameters
        ----------
        text: str
                Name of subitem to respond.

        """
        ...

    @staticmethod
    def MouseLocation() -> "Point2D":
        """Returns a point with the X and Y coordinates of the mouse relative to the UO Window

        Returns
        -------
        Point
                Return X,Y coords as Point object.

        """
        ...

    @staticmethod
    def MouseMove(posX: int, posY: int):
        """Moves the mouse pointer to the position X,Y relative to the UO window

        Parameters
        ----------
        posX: int
                X screen coordinate.
        posY: int
                Y screen coordinate.

        """
        ...

    @staticmethod
    def NextContPosition(x: int, y: int):
        """Return the X,Y of the next container, relative to the game window.
        (OSI client only, no ClassicUO)

        Parameters
        ----------
        x: int
                X coordinate.
        y: int
                Y coordinate.

        """
        ...

    @staticmethod
    def NoOperation():
        """Just do nothing and enjot the present moment."""
        ...

    @staticmethod
    def NoRunStealthStatus() -> bool:
        """Get the status of "No Run When Stealth" via scripting.

        Returns
        -------
        bool
                True: Open is active - False: otherwise.

        """
        ...

    @staticmethod
    def NoRunStealthToggle(enable: bool):
        """Set "No Run When Stealth" via scripting. Changes via scripting are not persistents.

        Parameters
        ----------
        enable: bool
                True: enable the option.

        """
        ...

    @staticmethod
    def OpenPaperdoll():
        """Open the backpack.
        (OSI client only, no ClassicUO)

        """
        ...

    @staticmethod
    def Pause(millisec: int):
        """Pause the script for a given amount of time.

        Parameters
        ----------
        millisec: int
                Pause duration, in milliseconds.

        """
        ...

    @staticmethod
    def PetRename(serial: Union[int, "Mobile"], name: str):
        """Rename a specific pet.


        Parameters
        ----------
        serial: int or Mobile
                Serial of the pet.
                Mobile object representing the pet.
        name: str
                New name to set.
                name to assign to the pet

        """
        ...

    @staticmethod
    def PlaySound(sound: int, x: int, y: int, z: int):
        """Send a sound to the client.

        Parameters
        ----------
        sound: int
                The sound to play.
        x: int
                The x point to send sound to.
        y: int
                The y point to send sound to.
        z: int
                The z point to send sound to.

        """
        ...

    @staticmethod
    def QueryStringResponse(okcancel: bool, response: str):
        """Perform a query string response by ok or cancel button and specific response string.

        Parameters
        ----------
        okcancel: bool
                OK Button
        response: str
                Cancel Button

        """
        ...

    @staticmethod
    def RazorDirectory() -> str:
        """Get the full path to the main Razor Enhanced folder.
        This path maybe be different from the Python starting folder when RE is loaded as plugin (ex: ClassicUO)

        Returns
        -------
        str
                Path as text

        """
        ...

    @staticmethod
    def ReadSharedValue(name: str) -> object:
        """Get a Shared Value, if value not exist return null.
        Shared values are accessible by every script.

        Parameters
        ----------
        name: str
                Name of the value.

        Returns
        -------
        object
                The stored object.

        """
        ...

    @staticmethod
    def RemoveLineInFile(fileName: str, lineOfData: str) -> bool:
        """Allows removal of a line in a file within RE ValidLocations.
        For OSI/RE this is only the RE directory / sub-directories
        For CUO/RE this is only CUO or RE directory / sub-directories
        The filename MUST end in a limited file suffix list
        Checks to see if an identical line is in the file, and if it exists, it is removed and file written

        Parameters
        ----------
        fileName: str
        lineOfData: str

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def RemoveSharedValue(name: str):
        """Remove a Shared Value.

        Parameters
        ----------
        name: str
                Name of the value.

        """
        ...

    @staticmethod
    def ResetPrompt():
        """Reset a prompt response."""
        ...

    @staticmethod
    def ResponsePrompt(text: str):
        """Response a prompt request. Often used to rename runes and similar.

        Parameters
        ----------
        text: str
                Text of the response.

        """
        ...

    @staticmethod
    def Resync():
        """Trigger a client ReSync."""
        ...

    @staticmethod
    def RightMouseClick(xpos: int, ypos: int, clientCoords: bool):
        """Perform a phisical Right click on the window.

        Parameters
        ----------
        xpos: int
                X click coordinate.
        ypos: int
                Y click coordinate.
        clientCoords: bool
                True: Client coordinates - False: Screen coordinates (default: True, client).

        """
        ...

    @staticmethod
    def ScriptCurrent(fullpath: bool) -> str:
        """Returns the path of the current script.

        Parameters
        ----------
        fullpath: bool
                True:Returns the full path. False: Returns the filename. (Dafault: true)

        Returns
        -------
        str

        """
        ...

    @staticmethod
    def ScriptDirectory() -> str:
        """Get the full path to the Scripts Directory.

        Returns
        -------
        str
                Full path to the Scripts Directory.

        """
        ...

    @staticmethod
    def ScriptIsSuspended(scriptfile: str) -> bool:
        """Get status of script if is suspended or not, Script must be present in script grid.

        Parameters
        ----------
        scriptfile: str

        Returns
        -------
        bool
                True: Script is suspended - False: otherwise.

        """
        ...

    @staticmethod
    def ScriptResume(scriptfile: str):
        """Resume a script by file name, Script must be present in script grid.

        Parameters
        ----------
        scriptfile: str
                Name of the script.

        """
        ...

    @staticmethod
    def ScriptRun(scriptfile: str):
        """Run a script by file name, Script must be present in script grid.

        Parameters
        ----------
        scriptfile: str
                Name of the script.

        """
        ...

    @staticmethod
    def ScriptStatus(scriptfile: str) -> bool:
        """Get status of script if running or not, Script must be present in script grid.

        Parameters
        ----------
        scriptfile: str

        Returns
        -------
        bool
                True: Script is running - False: otherwise.

        """
        ...

    @staticmethod
    def ScriptStop(scriptfile: str):
        """Stop a script by file name, Script must be present in script grid.

        Parameters
        ----------
        scriptfile: str
                Name of the script.

        """
        ...

    @staticmethod
    def ScriptStopAll(skipCurrent: bool):
        """Stop all script running.

        Parameters
        ----------
        skipCurrent: bool
                True: Stop all scripts, but the current one - False: stop all scripts. (Dafault: false)

        """
        ...

    @staticmethod
    def ScriptSuspend(scriptfile: str):
        """Suspend a script by file name, Script must be present in script grid.

        Parameters
        ----------
        scriptfile: str
                Name of the script.

        """
        ...

    @staticmethod
    def SendMessage(
        msg: Union[str, float, object, int, "UInt32", bool, float],
        color: Union[int, bool, None] = None,
        wait: Union[bool, None] = None,
    ):
        """Send a message to the client.


        Parameters
        ----------
        msg: str or float or object or int or UInt32 or bool or float
                The object to print.
        color: int or bool or None
                Color of the message.
        wait: bool or None
                True: Wait for confimation. - False: Returns instatnly.

        """
        ...

    @staticmethod
    def SendToClient(keys: str):
        """Send to the client a list of keystrokes. Can contain control characters:
        - Send Control+Key: ctrl+u: ^u
        - Send ENTER: {Enter}
        Note: some keys don't work with ClassicUO (es: {Enter} )

        Parameters
        ----------
        keys: str
                List of keys.

        """
        ...

    @staticmethod
    def SetSharedValue(name: str, value: object):
        """Set a Shared Value by specific name, if value exist he repalce value.
        Shared values are accessible by every script.

        Parameters
        ----------
        name: str
                Name of the value.
        value: object
                Value to set.

        """
        ...

    @staticmethod
    def ShardName() -> str:
        """Get the name of the shard.

        Returns
        -------
        str
                Name of the shard

        """
        ...

    @staticmethod
    def UnIgnoreObject(serial: Union[int, "UOEntity"]):
        """Remove object from ignore list. Can remove serial, items or mobiles


        Parameters
        ----------
        serial: int or UOEntity
                Serial to unignore.
                Item to unignore.

        """
        ...

    @staticmethod
    def UseContextMenu(serial: int, choice: str, delay: int) -> bool:
        """Open and click the option of Context menu, given the serial of Mobile or Item, via packets.

        Parameters
        ----------
        serial: int
                Serial of the Item or Mobile.
        choice: str
                Option as Text or integer.
        delay: int
                Maximum wait for the action to complete.

        Returns
        -------
        bool
                True: Optiona selected succesfully - False: otherwise.

        """
        ...

    @staticmethod
    def WaitForContext(serial: Union[int, "Mobile", "Item"], delay: int, showContext: bool) -> "List[Misc.Context]":
        """Return the List entry of a Context menu, of Mobile or Item objects.
        The function will ask the server for the List and wait for a maximum amount of time.


        Parameters
        ----------
        serial: int or Mobile or Item
                Serial of the entity.
                Entity as Item object.
        delay: int
                Maximum wait.
                max time to wait for context
        showContext: bool
                Show context menu in-game. (default: True)

        Returns
        -------
        List[Misc.Context]
                A List of Context objects.

        """
        ...

    @staticmethod
    def WaitForMenu(delay: int) -> bool:
        """Pause script until server send an Old Menu, for a maximum amount of time.

        Parameters
        ----------
        delay: int
                Maximum wait, in milliseconds.

        Returns
        -------
        bool
                True: if the Old Menu is open - False: otherwise.

        """
        ...

    @staticmethod
    def WaitForPrompt(delay: int) -> bool:
        """Wait for a prompt for a maximum amount of time.

        Parameters
        ----------
        delay: int
                Maximum wait time.

        Returns
        -------
        bool
                True: Prompt is present - False: otherwise

        """
        ...

    @staticmethod
    def WaitForQueryString(delay: int) -> bool:
        """Pause script until server send query string request, for a maximum amount of time.

        Parameters
        ----------
        delay: int
                Maximum wait, in milliseconds.

        Returns
        -------
        bool
                True: if player has a query - False: otherwise.

        """
        ...

    class Context:
        """The Context class holds information about a single entry in the Context Menu."""

        Entry: str
        Response: int

    class MapInfo:
        """The MapInfo class is used to store information about the Map location."""

        Facet: "UInt16"
        MapEnd: "Point2D"
        MapOrigin: "Point2D"
        PinPosition: "Point2D"
        Serial: "UInt32"


class Mobile(UOEntity):
    """The Mobile class represents an single alive entity.
    While the Mobile.Serial is unique for each Mobile, Mobile.MobileID is the unique for the Mobile apparence, or image. Sometimes is also called Body or Body ID.
    Mobiles which dies and leave a corpse behind, they stop existing as Mobiles and instead leave a corpse as a Item object appears.
    """

    Backpack: "Item"
    """Get the Item representing the backpack of a Mobile. Return null if it doesn't have one."""

    CanRename: bool
    """Determine if a mobile can be renamed. (Ex: pets, summons, etc )"""

    Color: "UInt16"
    """Color of the mobile."""

    Contains: "List[Item]"
    """Returns the list of items present in the Paperdoll (or equivalent) of the Mobile.
		Might not match the items found using via Layer."""

    Deleted: bool
    Direction: str
    """Returns the direction of the Mobile."""

    Fame: int
    """Fame has to be reverse engineered from the title so it is just ranges:
		0: neutaral - 3 is highest fame"""

    Female: bool
    """The Mobile is a female."""

    Flying: bool
    """The mobile is Flying ( Gragoyle )"""

    Graphics: "UInt16"
    Hits: int
    """The current hit point of a Mobile. To be read as propotion over Mobile.HitsMax."""

    HitsMax: int
    """Maximum hitpoint of a Mobile."""

    Hue: "UInt16"
    InParty: bool
    """True: if the Mobile is in your party. - False: otherwise."""

    IsGhost: bool
    """If is a Ghost
		Match any MobileID  in the list:
		402, 403, 607, 608, 694, 695, 970"""

    IsHuman: bool
    """Check is the Mobile has a human body.
		Match any MobileID in the list:
		183, 184, 185, 186, 400, 
		401, 402, 403, 605, 606,
		607, 608, 666, 667, 694, 
		744, 745, 747, 748, 750,  
		751, 970, 695"""

    ItemID: int
    Karma: int
    """Karma has to be reverse engineered from the title so it is just ranges:
		-5: most evil, 0: neutaral, 5 most good"""

    KarmaTitle: str
    """This is the title string returned from the server"""

    Mana: int
    """The current mana of a Mobile. To be read as propotion over Mobile.ManaMax."""

    ManaMax: int
    """Maximum mana of a Mobile."""

    Map: int
    """Current map or facet."""

    MobileID: int
    """Represents the type of Mobile, usually unique for the Mobile image. ( Alias: Mobile.Body )"""

    Mount: "Item"
    """Returns the Item assigned to the "Mount" Layer."""

    Name: str
    """Name of the Mobile."""

    Notoriety: int
    """Get the notoriety of the Mobile.
		
		Notorieties:
		1: blue, innocent
		2: green, friend
		3: gray, neutral
		4: gray, criminal
		5: orange, enemy
		6: red, hostile 
		6: yellow, invulnerable"""

    Paralized: bool
    """The mobile is Paralized."""

    Poisoned: bool
    """The mobile is Poisoned."""

    Position: "Point3D"
    Properties: "List[Property]"
    """Get all properties of a Mobile as list of lines of the tooltip."""

    PropsUpdated: bool
    """True: Mobile.Propertires are updated - False: otherwise."""

    Quiver: "Item"
    """Get the Item representing the quiver of a Mobile. Return null if it doesn't have one."""

    Serial: int
    Stam: int
    """The current stamina of a Mobile. To be read as propotion over Mobile.StamMax."""

    StamMax: int
    """Maximum stamina of a Mobile."""

    Visible: bool
    """True: The Mobile is visible - Flase: The mobile is hidden."""

    WarMode: bool
    """Mobile is in War mode."""

    YellowHits: bool
    """The mobile healthbar is not blue, but yellow."""

    def DistanceTo(self, other_mobile: "Mobile") -> int:
        """Returns the UO distance between the current Mobile and another one.

        Parameters
        ----------
        other_mobile: Mobile
                The other mobile.

        Returns
        -------
        int

        """
        ...

    def Equals(self, entity: Union["UOEntity", object]) -> bool:
        """

        Parameters
        ----------
        entity: UOEntity or object

        Returns
        -------
        bool

        """
        ...

    def GetHashCode(self) -> int:
        """

        Returns
        -------
        int

        """
        ...

    def GetItemOnLayer(self, layer: str) -> "Item":
        """Returns the Item associated with a Mobile Layer.

        Parameters
        ----------
        layer: str
                Layers:
                Layername
                RightHand
                LeftHand
                Shoes
                Pants
                Shirt
                Head
                Gloves
                Ring
                Neck
                Waist
                InnerTorso
                Bracelet
                MiddleTorso
                Earrings
                Arms
                Cloak
                OuterTorso
                OuterLegs
                InnerLegs

        Returns
        -------
        Item
                Item for the layer. Return null if not found or Layer invalid.

        """
        ...

    def UpdateKarma(self) -> bool:
        """Costly!
        Updates the Fame and Karma of the Mobile, but it can take as long as 1 second to complete.

        Returns
        -------
        bool
                True if successful, False if not server packet received

        """
        ...


class Mobiles:
    """The Mobiles class provides a wide range of functions to search and interact with Mobile."""

    @staticmethod
    def ApplyFilter(filter: "Mobiles.Filter") -> "List[Mobile]":
        """

        Parameters
        ----------
        filter: Mobiles.Filter

        Returns
        -------
        List[Mobile]

        """
        ...

    @staticmethod
    def ContextExist(serial: Union[int, "Mobile"], name: str, showContext: bool) -> int:
        """

        Parameters
        ----------
        serial: int or Mobile
        name: str
        showContext: bool

        Returns
        -------
        int

        """
        ...

    @staticmethod
    def FindBySerial(serial: int) -> "Mobile":
        """Find the Mobile with a specific Serial.

        Parameters
        ----------
        serial: int
                Serial of the Mobile.

        Returns
        -------
        Mobile

        """
        ...

    @staticmethod
    def FindMobile(
        graphics: Union["List[Int32]", int],
        notoriety: "List[Byte]",
        rangemax: int,
        selector: str,
        highlight: bool,
    ) -> "Mobile":
        """

        Parameters
        ----------
        graphics: List[Int32] or int
        notoriety: List[Byte]
        rangemax: int
        selector: str
        highlight: bool

        Returns
        -------
        Mobile

        """
        ...

    @staticmethod
    def GetPropStringByIndex(mob: Union["Mobile", int], index: int) -> str:
        """

        Parameters
        ----------
        mob: Mobile or int
        index: int

        Returns
        -------
        str

        """
        ...

    @staticmethod
    def GetPropStringList(serial: Union[int, "Mobile"]) -> "List[String]":
        """

        Parameters
        ----------
        serial: int or Mobile

        Returns
        -------
        List[String]

        """
        ...

    @staticmethod
    def GetPropValue(serial: Union[int, "Mobile"], name: str) -> float:
        """

        Parameters
        ----------
        serial: int or Mobile
        name: str

        Returns
        -------
        float

        """
        ...

    @staticmethod
    def GetTargetingFilter(target_name: str) -> "Mobiles.Filter":
        """

        Parameters
        ----------
        target_name: str

        Returns
        -------
        Mobiles.Filter

        """
        ...

    @staticmethod
    def GetTrackingInfo() -> "Mobiles.TrackingInfo":
        """Get the most updated information about tracking.

        Returns
        -------
        Mobiles.TrackingInfo

        """
        ...

    @staticmethod
    def Message(mobile: Union["Mobile", int], hue: int, message: str, wait: bool):
        """

        Parameters
        ----------
        mobile: Mobile or int
        hue: int
        message: str
        wait: bool

        """
        ...

    @staticmethod
    def Select(mobiles: "List[Mobile]", selector: str) -> "Mobile":
        """

        Parameters
        ----------
        mobiles: List[Mobile]
        selector: str

        Returns
        -------
        Mobile

        """
        ...

    @staticmethod
    def SingleClick(mobile: Union["Mobile", int]):
        """

        Parameters
        ----------
        mobile: Mobile or int

        """
        ...

    @staticmethod
    def UseMobile(mobile: Union["Mobile", int]):
        """

        Parameters
        ----------
        mobile: Mobile or int

        """
        ...

    @staticmethod
    def WaitForProps(m: Union["Mobile", int], delay: int) -> bool:
        """

        Parameters
        ----------
        m: Mobile or int
        delay: int

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def WaitForStats(mobileserial: Union[int, "Mobile"], delay: int) -> bool:
        """

        Parameters
        ----------
        mobileserial: int or Mobile
        delay: int

        Returns
        -------
        bool

        """
        ...

    class Filter:
        """The Mobiles.Filter class is used to store options to filter the global Mobile list.
        Often used in combination with Mobiles.ApplyFilter.
        """

        Blessed: int
        """Limit the search to only Blessed Mobiles.  (default: -1, any Mobile)"""

        Bodies: "List[Int32]"
        """Limit the search to a list of MobileID (see: Mobile.ItemID or Mobile.Body ) 
			Supports .Add() and .AddRange()"""

        CheckIgnoreObject: bool
        """Exclude from the search Mobiles which are currently on the global Ignore List. ( default: False, any Item )"""

        CheckLineOfSight: bool
        """Limit the search only to the Mobiles which are in line of sight. (default: false, any Mobile)"""

        Enabled: bool
        """True: The filter is used - False: Return all Mobile. ( default: True, active )"""

        Female: int
        """Limit the search to female Mobile.  (default: -1, any)"""

        Friend: int
        """Limit the search to friend Mobile. (default: -1, any)"""

        Graphics: "List[Int32]"
        Hues: "List[Int32]"
        """Limit the search to a list of Colors.
			Supports .Add() and .AddRange()"""

        IgnorePets: bool
        """Include the Mobiles which are currently on the Pet List. ( default: True, include Pets )"""

        IsGhost: int
        """Limit the search to Ghost only. (default: -1, any Mobile )
			Match any MobileID in the list:
			402, 403, 607, 608, 694, 695, 970"""

        IsHuman: int
        """Limit the search to Humans only. (default: -1, any Mobile )
			Match any MobileID in the list:
			183, 184, 185, 186, 400, 
			401, 402, 403, 605, 606,
			607, 608, 666, 667, 694, 
			744, 745, 747, 748, 750,  
			751, 970, 695"""

        Name: str
        """Limit the search by name of the Mobile."""

        Notorieties: "List[Byte]"
        """Limit the search to the Mobile by notoriety.
			Supports .Add() and .AddRange()
			
			Notorieties:
			1: blue, innocent
			2: green, friend
			3: gray, neutral
			4: gray, criminal
			5: orange, enemy
			6: red, hostile 
			6: yellow, invulnerable"""

        Paralized: int
        """Limit the search to paralized Mobile. (default: -1, any)"""

        Poisoned: int
        """Limit the search to only Poisoned Mobiles.  (default: -1, any Mobile)"""

        RangeMax: float
        """Limit the search by distance, to Mobiles which are at most RangeMax tiles away from the Player. ( default: -1, any Mobile )"""

        RangeMin: float
        """Limit the search by distance, to Mobiles which are at least RangeMin tiles away from the Player. ( default: -1, any Mobile )"""

        Serials: "List[Int32]"
        """Limit the search to a list of Serials of Mobile to find. (ex: 0x0406EFCA )
			Supports .Add() and .AddRange()"""

        Warmode: int
        """Limit the search to Mobile War mode. (default: -1, any Mobile)
			-1: any
			0: peace
			1: war"""

        ZLevelMax: float
        """Limit the search by z-level, to Mobiles which are at most z-level specified. ( default: 4096, all z-levels )"""

        ZLevelMin: float
        """Limit the search by z-level, to Mobiles which are at least z-level specified. ( default: -4096, all z-levels )"""

    class TrackingInfo:
        """The TrackingInfo class hold the latest information about."""

        lastUpdate: "DateTime"
        serial: "UInt32"
        x: "UInt16"
        y: "UInt16"


class Organizer:
    """The Organizer class allow you to interect with the Scavenger Agent, via scripting."""

    @staticmethod
    def ChangeList(listName: str):
        """Change the Organizer's active list.

        Parameters
        ----------
        listName: str
                Name of an existing organizer list.

        """

    @staticmethod
    def FStart():
        """Start the Organizer Agent on the currently active list."""

    @staticmethod
    def FStop():
        """Stop the Organizer Agent."""

    @staticmethod
    def RunOnce(organizerName: str, sourceBag: int, destBag: int, dragDelay: int):
        """

        Parameters
        ----------
        organizerName: str
        sourceBag: int
        destBag: int
        dragDelay: int

        """

    @staticmethod
    def Status() -> bool:
        """Check Organizer Agent status

        Returns
        -------
        bool
                True: if the Organizer is running - False: otherwise

        """
        ...


class PacketLogger:
    """RazorEnhanced packet logger."""

    PathToString: "Dict[PacketPath, String]"
    StringToPath: "Dict[String, PacketPath]"

    @staticmethod
    def AddBlacklist(packetID: int):
        """Add the packetID to the blacklist. Packets in the backlist will not be logged. (See PacketLogger.DiscardAll() )

        Parameters
        ----------
        packetID: int
                PacketID to blacklist

        """

    @staticmethod
    def AddTemplate(packetTemplate: str):
        """Add a custom template for RazorEnhanced packet logger.
        Example of "Damage" (0x0B) packet:
        {
        'packetID': 0x0B,
        'name': 'Damage 0x0B',
        'showHexDump': true,
        'fields':[
        { 'name':'packetID', 'length':1, 'type':'packetID'},
        { 'name':'Serial', 'length':4, 'type':'serial'},
        { 'name':'Damage', 'length': 2, 'type':'int'},
        ]
        }

        Parameters
        ----------
        packetTemplate: str
                Add a PacketTemplate, check ./Config/packets/ folder.

        """

    @staticmethod
    def AddWhitelist(packetID: int):
        """Add the packetID to the whitelist. Packets in the whitelist are always. (See PacketLogger.DiscardAll() )

        Parameters
        ----------
        packetID: int
                PacketID to whitelist

        """

    @staticmethod
    def DiscardAll(discardAll: bool):
        """Packet logger will discard all packets, except the one in the whitelist.  (See PacketLogger.AddWhitelist() )

        Parameters
        ----------
        discardAll: bool
                True: Log only the packet in the whitelist - False: Log everything, but the packets in the blacklist

        """

    @staticmethod
    def DiscardShowHeader(showHeader: bool):
        """Packet logger will show the headers of discarded packets.

        Parameters
        ----------
        showHeader: bool
                True: Always show headers - False: Hide everything.

        """

    @staticmethod
    def ListenPacketPath(packetPath: str, active: bool) -> "List[String]":
        """Packet logger will discard all packets, except the one in the whitelist.  (See PacketLogger.AddWhitelist() )
        If the packetPath is not set or not resognized, the function simply returns the current active paths.

        Parameters
        ----------
        packetPath: str
                Possible values:
                ClientToServer
                ServerToClient
                RazorToServer (TODO)
                RazorToClient (TODO)
                PacketVideo   (TODO)
        active: bool

        Returns
        -------
        String[][]
                List of strings of currently active packet paths.

        """
        ...

    @staticmethod
    def RemoveTemplate(packetID: int):
        """Remove a PacketTemplate for RazorEnhanced packet logger.

        Parameters
        ----------
        packetID: int
                Remove a spacific packetID. (Default: -1 Remove All)

        """

    @staticmethod
    def Reset():
        """Reset the packet logger to defaults."""

    @staticmethod
    def SendToClient(packetData: Union[List, "List[Byte]"]):
        """Send a packet to the client.


        Parameters
        ----------
        packetData: PythonList or List[Byte] or Byte[][]

        """

    @staticmethod
    def SendToServer(packetData: Union[List, "List[Byte]"]):
        """
        Send a packet to the server.

        Parameters
        ----------
        packetData: PythonList or List[Byte] or Byte[][]

        """

    @staticmethod
    def SetOutputPath(outputpath: str) -> str:
        """Set the RazorEnhanced packet logger. Calling it without a path it rester it to the default path.

        Parameters
        ----------
        outputpath: str
                (Optional) Custom output path (Default: reset to ./Desktop/Razor_Packets.log)

        Returns
        -------
        str
                The path to the saved file.

        """
        ...

    @staticmethod
    def Start(outputpath: Union[str, bool], appendLogs: Union[bool, None] = None) -> str:
        """Start the RazorEnhanced packet logger.


        Parameters
        ----------
        outputpath: str or bool
                Custom output path (Default: ./Desktop/Razor_Packets.log)
        appendLogs: bool or None
                True: Append - False: Overwrite (Default: False)

        Returns
        -------
        str
                The path to the saved file.

        """
        ...

    @staticmethod
    def Stop() -> str:
        """Stop the RazorEnhanced packet logger.

        Returns
        -------
        str
                The path to the saved file.

        """
        ...

    class FieldTemplate:
        """Class representing the fields inside a packet template.
        Example of "Damage" (0x0B) packet:
        {
        'packetID': 0x0B,
        'name': 'Damage 0x0B',
        'showHexDump': true,
        'fields':[
        { 'name':'packetID', 'length':1, 'type':'packetID'},
        { 'name':'Serial', 'length':4, 'type':'serial'},
        { 'name':'Damage', 'length': 2, 'type':'int'},
        ]
        }
        """

        fields: "List[PacketLogger.FieldTemplate]"
        """List of subfields present in this Field."""

        length: int
        """Length in bytes. length &gt; 0 maybe a mandatory for some FieldType."""

        name: str
        """Dysplay Name of the field."""

        subpacket: "PacketLogger.PacketTemplate"
        """A subpacket Field."""

        type: str
        """Type of field. See FieldType for details on each type."""

    class FieldType:
        """Type of Fields available for FieldTemplate
        Example of "Damage" (0x0B) packet:
        {
        'packetID': 0x0B,
        'name': 'Damage 0x0B',
        'showHexDump': true,
        'fields':[
        { 'name':'packetID', 'length':1, 'type':'packetID'},
        { 'name':'Serial', 'length':4, 'type':'serial'},
        { 'name':'Damage', 'length': 2, 'type':'int'},
        ]
        }
        """

        BOOL: str
        """Boolean type, length is fixed to 1 byte.
			
			Example:
			{'name':'Paralized', 'type':'bool'}"""

        DUMP: str
        """Dump a certain amount of data as raw bytes-by-bytes HEX 
			Length is mandatory.
			
			Example:
			{'name':'unused', 'type':'dump', 'length': 40}"""

        FIELDS: str
        """A special field which has subfields, useful for displaying stucts. 
			'length' is ignored, 'type' is optional, 'fields' is mandatory.
			
			Example:
			{'name':'Player Position', 'type':'fields',
			'fields':[
			{'name':'X', 'type':'uint', 'length': 2}
			{'name':'Y', 'type':'uint', 'length': 2}
			{'name':'Z', 'type':'uint', 'length': 1}
			]
			}"""

        FIELDSFOR: str
        HEX: str
        """Hex type is equivalent to unsigned integers but the contents is displayed as 0x hex.
			Length is mandatory and can range between 1 and 4 bytes.
			
			Example:
			{'name':'Hue', 'type':'hex', 'length': 2}"""

        INT: str
        """Integers type used for positive and negative integers.
			Length is mandatory and can range between 1 and 4 bytes.
			
			Example:
			{'name':'Z Level', 'type':'int', 'length': 2}"""

        MODELID: str
        """ModelID type like Item.ItemdID, Mobile.Body, etc.
			Length is fixed to 2 bytes and is displayed as 0x hex.
			
			Example:
			{'name':'Item ID', 'type':'modelID'}
			{'name':'Mobile Body', 'type':'modelID'}
			{'name':'Static ID', 'type':'modelID'}"""

        PACKETID: str
        """Common type present in every packet, packetID, length is fixed to 1 byte.
			
			Example:
			{'name':'packetID', 'type':'packetID'}"""

        SERIAL: str
        """Serial type, length is fixed to 4 bytes and is displayed as 0x hex.
			
			Example:
			{'name':'Target Serial', 'type':'serial'}"""

        SKIP: str
        """Skip a certain amount of data.
			Length is mandatory.
			
			Example:
			{'name':'unused', 'type':'skip', 'length': 40}"""

        SUBPACKET: str
        """A special field which denotes the beginning of a subpacket. 
			'length' is ignored, 'type' is optional, 'subpacket' is mandatory.
			
			Example:
			{'name':'action', 'type':'subpacket',
			'subpacket':{
			'name':'my subpacket'
			'fields':[
			...
			]
			}
			
			}"""

        TEXT: str
        """Text reads bytes as text.
			Length is mandatory.
			
			Example:
			{'name':'Name', 'type':'text', 'length': 20}"""

        UINT: str
        """Unsigned integers type used for positive integers.
			Length is mandatory and can range between 1 and 4 bytes.
			
			Example:
			{'name':'Z Level', 'type':'uint', 'length': 2}"""

        UTF8: str
        """Text reads bytes as UTF8 text.
			Length is mandatory.
			
			Example:
			{'name':'Pet name', 'type':'utf8', 'length': 40}"""

        VALID_TYPES: "List[String]"
        """List of valid types"""

        @staticmethod
        def IsValid(typename: str) -> bool:
            """Check if the name of type is a valid Template filed type.

            Parameters
            ----------
            typename: str
                    Name of the types

            Returns
            -------
            bool
                    True: is resognized. - False: not recognized.

            """
            ...

    class PacketTemplate:
        """Rapresents a general purpose template system for packets.
        The templates allow to format packets in the logger, making them readable.
        Example of "Damage" (0x0B) packet:
        {
        'packetID': 0x0B,
        'name': 'Damage 0x0B',
        'showHexDump': true,
        'fields':[
        { 'name':'packetID', 'length':1, 'type':'packetID'},
        { 'name':'Serial', 'length':4, 'type':'serial'},
        { 'name':'Damage', 'length': 2, 'type':'int'},
        ]
        }
        """

        dynamicLength: bool
        """Advanced settings for PacketReader. Ask Crezdba about DLLImport.Razor.IsDynLength(buff[0])"""

        fields: "List[PacketLogger.FieldTemplate]"
        """List of fields present in this Packet."""

        name: str
        """A readable name for the packet, optional but useful."""

        packetID: int
        """packetID, mandatory."""

        showHexDump: bool
        """If showHexDump is true the packet logger will show also the hex dump."""

        version: int
        """Template version,optional"""


PacketPath: TypeAlias = str


class PacketHandlerEventArgs: ...


class PacketReader: ...


class PathFinding:
    """This class implements the PathFinding algorithm using A-Star."""

    @staticmethod
    def GetPath(dst_x: int, dst_y: int, ignoremob: bool) -> "List[Tile]":
        """Compute the path for the given destination and returns a list of Tile (coordinates).

        Parameters
        ----------
        dst_x: int
                Destination X.
        dst_y: int
                Destination Y.
        ignoremob: bool
                Ignores any mobiles with the path calculation.

        Returns
        -------
        List[Tile]
                List of Tile objects, each holds a .X and .Y coordinates.

        """
        ...

    @staticmethod
    def Go(r: "PathFinding.Route") -> bool:
        """Check if a destination is reachable.

        Parameters
        ----------
        r: PathFinding.Route
                A customized Route object.

        Returns
        -------
        bool
                True: if a destination is reachable.

        """
        ...

    @staticmethod
    def PathFindTo(x: Union[int, "Point3D"], y: Union[int, None] = None, z: Union[int, None] = None):
        """Go to the given coordinates using Razor pathfinding.

        Parameters
        ----------
        x: int or Point3D
                X map coordinates or Point3D
        y: int or None
                Y map coordinates
        z: int or None
                Z map coordinates

        """

    def runPath(self, timeout: float, debugMessage: bool, useResync: bool) -> bool:
        """

        Parameters
        ----------
        timeout: float
                Maximum amount of time to run the path. (default: -1, no limit)
        debugMessage: bool
                Outputs a debug message.
        useResync: bool
                ReSyncs the path calculation.

        Returns
        -------
        bool
                True: if it finish the path in time. False: otherwise

        """
        ...

    @staticmethod
    def RunPath(path: "List[Tile]", timeout: float, debugMessage: bool, useResync: bool) -> bool:
        """

        Parameters
        ----------
        path: List[Tile]
        timeout: float
        debugMessage: bool
        useResync: bool

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def Tile(x: int, y: int) -> "Tile":
        """Create a Tile starting from X,Y coordinates (see PathFindig.RunPath)

        Parameters
        ----------
        x: int
                X coordinate
        y: int
                Y coordinate

        Returns
        -------
        Tile
                Returns a Tile object

        """
        ...

    def walkPath(self, timeout: float, debugMessage: bool, useResync: bool) -> bool:
        """

        Parameters
        ----------
        timeout: float
        debugMessage: bool
        useResync: bool

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def WalkPath(path: "List[Tile]", timeout: float, debugMessage: bool, useResync: bool) -> bool:
        """

        Parameters
        ----------
        path: List[Tile]
        timeout: float
        debugMessage: bool
        useResync: bool

        Returns
        -------
        bool

        """
        ...

    class Route:
        """The Route class is used to configure the PathFinding."""

        DebugMessage: bool
        """Outputs a debug message. (default: False)"""

        IgnoreMobile: bool
        """Ignores any mobiles with the path calculation. (default: 0)"""

        MaxRetry: int
        """Number of attempts untill the path calculation is halted. (default: -1, no limit)"""

        Run: bool
        """Maximum amount of time to run the path. (default: -1, no limit)"""

        StopIfStuck: bool
        """Halts the pathfinding fail to walk the path. (default: 0)"""

        Timeout: float
        """Maximum amount of time to run the path. (default: -1, no limit)"""

        UseResync: bool
        """ReSyncs the path calculation. (default: False)"""

        X: int
        """Sets the destination position X. (default: 0)"""

        Y: int
        """Sets the destination position Y. (default: 0)"""


class BuffInfo: ...


class Player:
    """The Player class represent the currently logged in character."""

    AR: int
    """Resistance to Phisical damage."""

    Backpack: "Item"
    """Player backpack, as Item object."""

    Bank: "Item"
    """Player bank chest, as Item object."""

    Body: int
    """Player Body or MobileID (see: Mobile.Body)"""

    Buffs: "List[String]"
    """List of Player active buffs:
		Meditation
		Agility
		Animal Form
		Arcane Enpowerment
		Arcane Enpowerment (new)
		Arch Protection
		Armor Pierce
		Attunement
		Aura of Nausea
		Bleed
		Bless
		Block
		Bload Oath (caster)
		Bload Oath (curse)
		BloodWorm Anemia
		City Trade Deal
		Clumsy
		Confidence
		Corpse Skin
		Counter Attack
		Criminal
		Cunning
		Curse
		Curse Weapon
		Death Strike
		Defense Mastery
		Despair
		Despair (target)
		Disarm (new)
		Disguised
		Dismount Prevention
		Divine Fury
		Dragon Slasher Fear
		Enchant
		Enemy Of One
		Enemy Of One (new)
		Essence Of Wind
		Ethereal Voyage
		Evasion
		Evil Omen
		Faction Loss
		Fan Dancer Fan Fire
		Feeble Mind
		Feint
		Force Arrow
		Berserk
		Fly
		Gaze Despair
		Gift Of Life
		Gift Of Renewal
		Healing
		Heat Of Battle
		Hiding
		Hiryu Physical Malus
		Hit Dual Wield
		Hit Lower Attack
		Hit Lower Defense
		Honorable Execution
		Honored
		Horrific Beast
		Hawl Of Cacophony
		Immolating Weapon
		Incognito
		Inspire
		Invigorate
		Invisibility
		Lich Form
		Lighting Strike
		Magic Fish
		Magic Reflection
		Mana Phase
		Mass Curse
		Medusa Stone
		Mind Rot
		Momentum Strike
		Mortal Strike
		Night Sight
		NoRearm
		Orange Petals
		Pain Spike
		Paralyze
		Perfection
		Perseverance
		Poison
		Poison Resistance
		Polymorph
		Protection
		Psychic Attack
		Consecrate Weapon
		Rage
		Rage Focusing
		Rage Focusing (target)
		Reactive Armor
		Reaper Form
		Resilience
		Rose Of Trinsic
		Rotworm Blood Disease
		Rune Beetle Corruption
		Skill Use Delay
		Sleep
		Spell Focusing
		Spell Focusing (target)
		Spell Plague
		Splintering Effect
		Stone Form
		Strangle
		Strength
		Surge
		Swing Speed
		Talon Strike
		Vampiric Embrace
		Weaken
		Wraith Form"""

    BuffsInfo: "List[BuffInfo]"
    """Returns a list with every detailed active buff"""

    ColdResistance: int
    """Resistance to Cold damage."""

    Connected: bool
    """Retrieves Connected State"""

    Corpses: "Set[Item]"
    """Each Death Player corpse item is added here"""

    DamageChanceIncrease: int
    """Get total Damage Chance Increase."""

    DefenseChanceIncrease: int
    """Get total Defense Chance Increase."""

    Dex: int
    """Stats value for Dexterity."""

    DexterityIncrease: int
    """Get total Dexterity Increase."""

    Direction: str
    """Player current direction, as text."""

    EnergyResistance: int
    """Resistance to Energy damage."""

    EnhancePotions: int
    """Get total Enhance Potions."""

    Fame: int
    """Fame has to be reverse engineered from the title so it is just ranges:
		0: neutaral - 3 is highest fame"""

    FasterCasting: int
    """Get total Faster Casting."""

    FasterCastRecovery: int
    """Get total Faster Cast Recovery."""

    Female: bool
    """Player is a female."""

    FireResistance: int
    """Resistance to Fire damage."""

    Followers: int
    """Player current amount of pet/followers."""

    FollowersMax: int
    """Player maximum amount of pet/followers."""

    Gold: int
    """Player total gold, in the backpack."""

    HasPrimarySpecial: bool
    HasSecondarySpecial: bool
    HasSpecial: bool
    """Player have a special abilities active."""

    HitPointsIncrease: int
    """Get total Hit Points Increase."""

    HitPointsRegeneration: int
    """Get total Hit Points Regeneration."""

    Hits: int
    """Current hit points."""

    HitsMax: int
    """Maximum hit points."""

    InParty: bool
    """Player is in praty."""

    Int: int
    """Stats value for Intelligence."""

    IntelligenceIncrease: int
    """Get total Intelligence Increase."""

    IsGhost: bool
    """Player is a Ghost"""

    Karma: int
    """Karma has to be reverse engineered from the title so it is just ranges:
		-5: most evil, 0: neutaral, 5 most good"""

    KarmaTitle: str
    """This is the title string returned from the server"""

    LowerManaCost: int
    """Get total Lower Mana Cost."""

    LowerReagentCost: int
    """Get total Lower Reagent Cost."""

    Luck: int
    """Player total luck."""

    Mana: int
    """Current mana."""

    ManaIncrease: int
    """Get total Mana Increase."""

    ManaMax: int
    """Maximum mana."""

    ManaRegeneration: int
    """Get total Mana Regeneration."""

    Map: int
    """Player current map, or facet."""

    MaximumHitPointsIncrease: int
    """Get total Maximum Hit Points Increase."""

    MaximumStaminaIncrease: int
    """Get total Maximum Stamina Increase."""

    MaxWeight: int
    """Player maximum weight."""

    MobileID: int
    """Player MobileID or Body (see: Mobile.MobileID)"""

    Mount: "Item"
    """Player current Mount, as Item object.
		NOTE: On some server the Serial return by this function doesn't match the mount serial."""

    Name: str
    """Player name."""

    Notoriety: int
    """Player notoriety
		1: blue, innocent
		2: green, friend
		3: gray, neutral
		4: gray, criminal
		5: orange, enemy
		6: red, hostile 
		6: yellow, invulnerable"""

    Paralized: bool
    """Player is Paralized. True also while frozen because of casting of spells."""

    Pets: "List[Mobile]"
    """Finds all neutral pets in the area that can be renamed.
		This isn't the server information on your pets, but its good enough for most cases"""

    Poisoned: bool
    """Player is Poisoned"""

    PoisonResistance: int
    """Resistance to Poison damage."""

    Position: "Point3D"
    """Current Player position as Point3D object."""

    PrimarySpecial: "UInt32"
    Quiver: "Item"
    """Player quiver, as Item object."""

    ReflectPhysicalDamage: int
    """Get total Reflect Physical Damage."""

    SecondarySpecial: "UInt32"
    Serial: int
    """Player unique Serial."""

    SpellDamageIncrease: int
    """Get total Spell Damage Increase."""

    Stam: int
    """Current stamina."""

    StaminaIncrease: int
    """Get total Stamina Increase."""

    StaminaRegeneration: int
    """Get total Stamina Regeneration."""

    StamMax: int
    """Maximum stamina."""

    StatCap: int
    """Get the stats cap."""

    StaticMount: int
    """Retrieves serial of mount set in Filter/Mount GUI."""

    Str: int
    """Stats value for Strenght."""

    StrengthIncrease: int
    """Get total Strength Increase."""

    SwingSpeedIncrease: int
    """Get total Swing Speed Increase."""

    Visible: bool
    """Player is visible, false if hidden."""

    WarMode: bool
    """Player has war mode active."""

    Weight: int
    """Player current weight."""

    YellowHits: bool
    """Player HP bar is not blue, but yellow."""

    @staticmethod
    def Area() -> str:
        """Get the name of the area in which the Player is currently in. (Ex: Britain, Destard, Vesper, Moongate, etc)
        Regions are defined inside by Config/regions.json.

        Returns
        -------
        str
                Name of the area. Unknown if not recognized.

        """
        ...

    @staticmethod
    def Attack(mobile: Union["Mobile", int]):
        """
        Attack a Mobile.

        Parameters
        ----------
        mobile: Mobile or int
                Serial or Mobile to attack.

        """

    @staticmethod
    def AttackLast():
        """Attack last target."""

    @staticmethod
    def AttackType(
        graphics: Union["List[Int32]", int],
        rangemax: int,
        selector: str,
        color: "List[Int32]",
        notoriety: "List[Byte]",
    ) -> bool:
        """

        Parameters
        ----------
        graphics: List[Int32] or int
        rangemax: int
        selector: str
        color: List[Int32]
        notoriety: List[Byte]

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def BuffsExist(buffname: str, okayToGuess: bool) -> bool:
        """Check if a buff is active, by buff name.

        Parameters
        ----------
        buffname: str
                Meditation
                Agility
                Animal Form
                Arcane Enpowerment
                Arcane Enpowerment (new)
                Arch Protection
                Armor Pierce
                Attunement
                Aura of Nausea
                Bleed
                Bless
                Block
                Bload Oath (caster)
                Bload Oath (curse)
                BloodWorm Anemia
                City Trade Deal
                Clumsy
                Confidence
                Corpse Skin
                Counter Attack
                Criminal
                Cunning
                Curse
                Curse Weapon
                Death Strike
                Defense Mastery
                Despair
                Despair (target)
                Disarm (new)
                Disguised
                Dismount Prevention
                Divine Fury
                Dragon Slasher Fear
                Enchant
                Enemy Of One
                Enemy Of One (new)
                Essence Of Wind
                Ethereal Voyage
                Evasion
                Evil Omen
                Faction Loss
                Fan Dancer Fan Fire
                Feeble Mind
                Feint
                Force Arrow
                Berserk
                Fly
                Gaze Despair
                Gift Of Life
                Gift Of Renewal
                Healing
                Heat Of Battle
                Hiding
                Hiryu Physical Malus
                Hit Dual Wield
                Hit Lower Attack
                Hit Lower Defense
                Honorable Execution
                Honored
                Horrific Beast
                Hawl Of Cacophony
                Immolating Weapon
                Incognito
                Inspire
                Invigorate
                Invisibility
                Lich Form
                Lighting Strike
                Magic Fish
                Magic Reflection
                Mana Phase
                Mass Curse
                Medusa Stone
                Mind Rot
                Momentum Strike
                Mortal Strike
                Night Sight
                NoRearm
                Orange Petals
                Pain Spike
                Paralyze
                Perfection
                Perseverance
                Poison
                Poison Resistance
                Polymorph
                Protection
                Psychic Attack
                Consecrate Weapon
                Rage
                Rage Focusing
                Rage Focusing (target)
                Reactive Armor
                Reaper Form
                Resilience
                Rose Of Trinsic
                Rotworm Blood Disease
                Rune Beetle Corruption
                Skill Use Delay
                Sleep
                Spell Focusing
                Spell Focusing (target)
                Spell Plague
                Splintering Effect
                Stone Form
                Strangle
                Strength
                Surge
                Swing Speed
                Talon Strike
                Vampiric Embrace
                Weaken
                Wraith Form
        okayToGuess: bool

        Returns
        -------
        bool
                True: if the buff is active - False: otherwise.

        """
        ...

    @staticmethod
    def BuffTime(buffname: str) -> int:
        """

        Parameters
        ----------
        buffname: str

        Returns
        -------
        int

        """
        ...

    @staticmethod
    def ChatAlliance(msg: Union[int, str]):
        """
        Send message to the alliace chat.

        Parameters
        ----------
        msg: int or str
                Message to send.

        """
        ...

    @staticmethod
    def ChatChannel(msg: Union[str, int]):
        """
        Send an chat channel message.

        Parameters
        ----------
        msg: str or int
                Message to send.

        """
        ...

    @staticmethod
    def ChatEmote(color: int, msg: Union[int, str]):
        """
        Send an emote in game.

        Parameters
        ----------
        color: int
                Color of the text
        msg: int or str
                Message to send.

        """
        ...

    @staticmethod
    def ChatGuild(msg: Union[int, str]):
        """
        Send message to the guild chat.

        Parameters
        ----------
        msg: int or str
                Message to send.

        """
        ...

    @staticmethod
    def ChatParty(msg: str, recepient_serial: int):
        """Send message in arty chat. If a recepient_serial is specified, the message is private.

        Parameters
        ----------
        msg: str
                Text to send.
        recepient_serial: int
                Optional: Target of private message.

        """
        ...

    @staticmethod
    def ChatSay(color: Union[int, str], msg: Union[str, int, None] = None):
        """Send message in game.

        Send message in game using 1153 for color.

        Parameters
        ----------
        color: int or str
                Color of the text

                Message to send.
        msg: str or int or None
                Message to send.

        """
        ...

    @staticmethod
    def ChatWhisper(color: int, msg: Union[str, int]):
        """Send an wishper message.


        Parameters
        ----------
        color: int
                Color of the text
        msg: str or int
                Message to send.

        """
        ...

    @staticmethod
    def ChatYell(color: int, msg: Union[str, int]):
        """
        Send an yell message.

        Parameters
        ----------
        color: int
                Color of the text
        msg: str or int
                Message to send.

        """
        ...

    @staticmethod
    def CheckLayer(layer: str) -> bool:
        """Check if a Layer is equipped by the Item.

        Parameters
        ----------
        layer: str
                Layers:
                RightHand
                LeftHand
                Shoes
                Pants
                Shirt
                Head
                Gloves
                Ring
                Neck
                Hair
                Waist
                InnerTorso
                Bracelet
                FacialHair
                MiddleTorso
                Earrings
                Arms
                Cloak
                OuterTorso
                OuterLegs
                InnerLegs
                Talisman

        Returns
        -------
        bool
                True: the Layer is occupied by an Item - False: otherwise.

        """
        ...

    @staticmethod
    def ClearCorpseList():
        """Clear the Player corpse item list"""
        ...

    @staticmethod
    def DistanceTo(target: Union["UOEntity", int]) -> int:
        """Returns the distance between the Player and a Mobile or an Item.


        Parameters
        ----------
        target: UOEntity or int
                The other Mobile or Item

        Returns
        -------
        int
                Distance in number of tiles.

        """
        ...

    @staticmethod
    def EmoteAction(action: str):
        """

        Parameters
        ----------
        action: str

        """
        ...

    @staticmethod
    def EquipItem(item: Union["Item", int]):
        """
        Equip an Item

        Parameters
        ----------
        item: Item or int
                Serial or Item to equip.

        """
        ...

    @staticmethod
    def EquipLastWeapon():
        """Equip the last used weapon"""
        ...

    @staticmethod
    def EquipUO3D(serials: Union["List[Int32]", List]):
        """Equip a python list of item by using UO3D packet.


        Parameters
        ----------
        serials: List[Int32] or PythonList

        """
        ...

    @staticmethod
    def Fly(status: bool):
        """Enable or disable Gargoyle Flying.

        Parameters
        ----------
        status: bool
                True: Gargoyle Fly ON - False: Gargoyle fly OFF

        """
        ...

    @staticmethod
    def GetBuffInfo(buffName: str, okayToGuess: bool) -> "BuffInfo":
        """Check if buff information is active by buff name and returns it.

        Parameters
        ----------
        buffName: str
                buff name
        okayToGuess: bool

        Returns
        -------
        BuffInfo
                Buff information

        """
        ...

    @staticmethod
    def GetItemOnLayer(layer: str) -> "Item":
        """Returns the Item associated with a Mobile Layer.

        Parameters
        ----------
        layer: str
                Layers:
                RightHand
                LeftHand
                Shoes
                Pants
                Shirt
                Head
                Gloves
                Ring
                Neck
                Hair
                Waist
                InnerTorso
                Bracelet
                FacialHair
                MiddleTorso
                Earrings
                Arms
                Cloak
                OuterTorso
                OuterLegs
                InnerLegs
                Talisman

        Returns
        -------
        Item
                Item for the layer. Return null if not found or Layer invalid.

        """
        ...

    @staticmethod
    def GetPropStringByIndex(index: int) -> str:
        """Get a single line of Properties of the Player, from the tooltip, as text.

        Parameters
        ----------
        index: int
                Line number, start from 0.

        Returns
        -------
        str
                Single line of text.

        """
        ...

    @staticmethod
    def GetPropStringList() -> "List[String]":
        """Get the list of Properties of the Player, as list of lines of the tooltip.

        Returns
        -------
        List[String]
                List of text lines.

        """
        ...

    @staticmethod
    def GetPropValue(name: str) -> int:
        """Get the numeric value of a specific Player property, from the tooltip.

        Parameters
        ----------
        name: str
                Name of the property.

        Returns
        -------
        int
                n: value of the propery
                0: property not found.
                1: property found, but not numeric.

        """
        ...

    @staticmethod
    def GetRealSkillValue(skillname: str) -> float:
        """Get the base/real value of the skill for the given the skill name.

        Parameters
        ----------
        skillname: str
                Alchemy
                Anatomy
                Animal Lore
                Item ID
                Arms Lore
                Parry
                Begging
                Blacksmith
                Fletching
                Peacemaking
                Camping
                Carpentry
                Cartography
                Cooking
                Detect Hidden
                Discordance
                EvalInt
                Healing
                Fishing
                Forensics
                Herding
                Hiding
                Provocation
                Inscribe
                Lockpicking
                Magery
                Magic Resist
                Mysticism
                Tactics
                Snooping
                Musicianship
                Poisoning
                Archery
                Spirit Speak
                Stealing
                Tailoring
                Animal Taming
                Taste ID
                Tinkering
                Tracking
                Veterinary
                Swords
                Macing
                Fencing
                Wrestling
                Lumberjacking
                Mining
                Meditation
                Stealth
                Remove Trap
                Necromancy
                Focus
                Chivalry
                Bushido
                Ninjitsu
                Spell Weaving
                Imbuing

        Returns
        -------
        float
                Value of the skill.

        """
        ...

    @staticmethod
    def GetSkillCap(skillname: str) -> float:
        """Get the skill cap for the given the skill name.

        Parameters
        ----------
        skillname: str
                Alchemy
                Anatomy
                Animal Lore
                Item ID
                Arms Lore
                Parry
                Begging
                Blacksmith
                Fletching
                Peacemaking
                Camping
                Carpentry
                Cartography
                Cooking
                Detect Hidden
                Discordance
                EvalInt
                Healing
                Fishing
                Forensics
                Herding
                Hiding
                Provocation
                Inscribe
                Lockpicking
                Magery
                Magic Resist
                Mysticism
                Tactics
                Snooping
                Musicianship
                Poisoning
                Archery
                Spirit Speak
                Stealing
                Tailoring
                Animal Taming
                Taste ID
                Tinkering
                Tracking
                Veterinary
                Swords
                Macing
                Fencing
                Wrestling
                Lumberjacking
                Mining
                Meditation
                Stealth
                Remove Trap
                Necromancy
                Focus
                Chivalry
                Bushido
                Ninjitsu
                Spell Weaving
                Imbuing

        Returns
        -------
        float
                Value of the skill cap.

        """
        ...

    @staticmethod
    def GetSkillStatus(skillname: str) -> int:
        """Get lock status for a specific skill.

        Parameters
        ----------
        skillname: str
                Alchemy
                Anatomy
                Animal Lore
                Item ID
                Arms Lore
                Parry
                Begging
                Blacksmith
                Fletching
                Peacemaking
                Camping
                Carpentry
                Cartography
                Cooking
                Detect Hidden
                Discordance
                EvalInt
                Healing
                Fishing
                Forensics
                Herding
                Hiding
                Provocation
                Inscribe
                Lockpicking
                Magery
                Magic Resist
                Mysticism
                Tactics
                Snooping
                Musicianship
                Poisoning
                Archery
                Spirit Speak
                Stealing
                Tailoring
                Animal Taming
                Taste ID
                Tinkering
                Tracking
                Veterinary
                Swords
                Macing
                Fencing
                Wrestling
                Lumberjacking
                Mining
                Meditation
                Stealth
                Remove Trap
                Necromancy
                Focus
                Chivalry
                Bushido
                Ninjitsu
                Spell Weaving
                Imbuing

        Returns
        -------
        int
                Lock status:
                0: Up
                1: Down
                2: Locked
                -1: Error

        """
        ...

    @staticmethod
    def GetSkillValue(skillname: str) -> float:
        """Get the value of the skill, with modifiers, for the given the skill name.

        Parameters
        ----------
        skillname: str
                Alchemy
                Anatomy
                Animal Lore
                Item ID
                Arms Lore
                Parry
                Begging
                Blacksmith
                Fletching
                Peacemaking
                Camping
                Carpentry
                Cartography
                Cooking
                Detect Hidden
                Discordance
                EvalInt
                Healing
                Fishing
                Forensics
                Herding
                Hiding
                Provocation
                Inscribe
                Lockpicking
                Magery
                Magic Resist
                Mysticism
                Tactics
                Snooping
                Musicianship
                Poisoning
                Archery
                Spirit Speak
                Stealing
                Tailoring
                Animal Taming
                Taste ID
                Tinkering
                Tracking
                Veterinary
                Swords
                Macing
                Fencing
                Wrestling
                Lumberjacking
                Mining
                Meditation
                Stealth
                Remove Trap
                Necromancy
                Focus
                Chivalry
                Bushido
                Ninjitsu
                Spell Weaving
                Imbuing

        Returns
        -------
        float
                Value of the skill.

        """
        ...

    @staticmethod
    def GetStatStatus(statname: str) -> int:
        """Get lock status for a specific stats.

        Parameters
        ----------
        statname: str
                Strength
                Dexterity
                Intelligence

        Returns
        -------
        int
                Lock status:
                0: Up
                1: Down
                2: Locked

        """
        ...

    @staticmethod
    def GuildButton():
        """Press the Guild menu button in the paperdoll."""
        ...

    @staticmethod
    def HeadMessage(color: int, msg: Union[int, str]):
        """Display a message above the Player. Visible only by the Player.


        Parameters
        ----------
        color: int
                Color of the Text.
        msg: int or str
                Text of the message.

        """
        ...

    @staticmethod
    def InRange(entity: Union["UOEntity", int], range: int) -> bool:
        """Check if the mobile or item is within a certain range (&lt;=).
        Check if the serial is within a certain range (&lt;=).

        Parameters
        ----------
        entity: UOEntity or int
        range: int
                Maximum distance in tiles.

        Returns
        -------
        bool
                True: Item is in range - False: otherwise.
                True: serial is in range - False: otherwise.

        """
        ...

    @staticmethod
    def InRangeItem(item: Union[int, "Item"], range: int) -> bool:
        """Check if the Item is within a certain range (&lt;=).


        Parameters
        ----------
        item: int or Item
                Serial or Item object.
        range: int
                Maximum distance in tiles.

        Returns
        -------
        bool
                True: Item is in range - False: otherwise.

        """
        ...

    @staticmethod
    def InRangeMobile(mobile: Union["Mobile", int], range: int) -> bool:
        """Check if the mobile is within a certain range (&lt;=).
        Check if the Mobile is within a certain range (&lt;=).

        Parameters
        ----------
        mobile: Mobile or int
                Serial or Mobile object.
        range: int
                Maximum distance in tiles.

        Returns
        -------
        bool
                True: Item is in range - False: otherwise.
                True: Mobile is in range - False: otherwise.

        """
        ...

    @staticmethod
    def InvokeVirtue(virtue: Union[str, int]):
        """Invoke a virtue by name.

        Parameters
        ----------
        virtue: str or int
                Honor
                Sacrifice
                Valor
                Compassion
                Honesty
                Humility
                Justice
                Spirituality

        """
        ...

    @staticmethod
    def KickMember(serial: int):
        """Kick a member from party by serial. Only for party leader

        Parameters
        ----------
        serial: int
                Serial of the Mobile to remove.

        """
        ...

    @staticmethod
    def LeaveParty(force: bool):
        """Leaves a party.

        Parameters
        ----------
        force: bool
                True: Leave the party invite even you notin any party.

        """
        ...

    @staticmethod
    def MapSay(msg: Union[str, int]):
        """
        Send message in the Map chat.

        Parameters
        ----------
        msg: str or int
                Message to send

        """
        ...

    @staticmethod
    def OpenPaperDoll():
        """Open Player's Paperdoll"""
        ...

    @staticmethod
    def PartyAccept(from_serial: int, force: bool) -> bool:
        """Accept an incoming party offer. In case of multiple party oebnding invitation, from_serial is specified,

        Parameters
        ----------
        from_serial: int
                Optional: Serial to accept party from.( in case of multiple offers )
        force: bool
                True: Accept the party invite even you are already in a party.

        Returns
        -------
        bool
                True: if you are now in a party - False: otherwise.

        """
        ...

    @staticmethod
    def PartyCanLoot(CanLoot: bool):
        """Set the Party loot permissions.

        Parameters
        ----------
        CanLoot: bool

        """
        ...

    @staticmethod
    def PartyInvite():
        """Invite a person to a party. Prompt for a in-game Target."""
        ...

    @staticmethod
    def PathFindTo(x: Union[int, "Point3D"], y: Union[int, None] = None, z: Union[int, None] = None):
        """Go to the given coordinates using Client-provided pathfinding.
        Go to the position supplied using Client-provided pathfinding.

        Parameters
        ----------
        x: int or Point3D
                X map coordinates or Point3D
        y: int or None
                Y map coordinates
        z: int or None
                Z map coordinates

        """
        ...

    @staticmethod
    def QuestButton():
        """Press the Quest menu button in the paperdoll."""
        ...

    @staticmethod
    def Run(direction: str) -> bool:
        """Run one step in the specified direction and wait for the confirmation of the new position by the server.
        If the character is not facing the direction, the first step only "turn" the Player in the required direction.

        Info:
        Walking:  5 tiles/sec (~200ms between each step)
        Running: 10 tiles/sec (~100ms between each step)

        Parameters
        ----------
        direction: str
                North
                South
                East
                West
                Up
                Down
                Left
                Right

        Returns
        -------
        bool
                True: Destination reached - False: Coudn't reach the destination.

        """
        ...

    @staticmethod
    def SetSkillStatus(skillname: str, status: int):
        """Set lock status for a specific skill.

        Parameters
        ----------
        skillname: str
                Alchemy
                Anatomy
                Animal Lore
                Item ID
                Arms Lore
                Parry
                Begging
                Blacksmith
                Fletching
                Peacemaking
                Camping
                Carpentry
                Cartography
                Cooking
                Detect Hidden
                Discordance
                EvalInt
                Healing
                Fishing
                Forensics
                Herding
                Hiding
                Provocation
                Inscribe
                Lockpicking
                Magery
                Magic Resist
                Mysticism
                Tactics
                Snooping
                Musicianship
                Poisoning
                Archery
                Spirit Speak
                Stealing
                Tailoring
                Animal Taming
                Taste ID
                Tinkering
                Tracking
                Veterinary
                Swords
                Macing
                Fencing
                Wrestling
                Lumberjacking
                Mining
                Meditation
                Stealth
                Remove Trap
                Necromancy
                Focus
                Chivalry
                Bushido
                Ninjitsu
                Spell Weaving
                Imbuing
        status: int
                Lock status:
                0: Up
                1: Down
                2: Locked

        """
        ...

    @staticmethod
    def SetStaticMount(serial: int):
        """Sets serial of mount set in Filter/Mount GUI.

        Parameters
        ----------
        serial: int

        """
        ...

    @staticmethod
    def SetStatStatus(statname: str, status: int):
        """Set lock status for a specific skill.

        Parameters
        ----------
        statname: str
                Strength
                Dexterity
                Intelligence
        status: int
                Lock status:
                0: Up
                1: Down
                2: Locked

        """
        ...

    @staticmethod
    def SetWarMode(warflag: bool):
        """Set war Mode on on/off.

        Parameters
        ----------
        warflag: bool
                True: War - False: Peace

        """
        ...

    @staticmethod
    def SpellIsEnabled(spellname: str) -> bool:
        """Check if spell is active using the spell name (for spells that have this function).

        Parameters
        ----------
        spellname: str
                Name of the spell.

        Returns
        -------
        bool
                True: the spell is enabled - False: otherwise,.

        """
        ...

    @staticmethod
    def SumAttribute(attributename: str) -> float:
        """Scan all the equipped Item, returns the total value of a specific property. (ex: Lower Reagent Cost )
        NOTE: This function is slow.

        Parameters
        ----------
        attributename: str
                Name of the property.

        Returns
        -------
        float
                The total value as number.

        """
        ...

    @staticmethod
    def ToggleAlwaysRun():
        """Toggle on/off the awlays run flag.
        NOTE: Works only on OSI client.

        """
        ...

    @staticmethod
    def TrackingArrow(x: "UInt16", y: "UInt16", display: bool, target: "UInt32"):
        """Display a fake tracking arrow

        Parameters
        ----------
        x: UInt16
                X coordinate.
        y: UInt16
                Y coordinate.
        display: bool
                True = On, False = off
        target: UInt32
                object serial targeted

        """
        ...

    @staticmethod
    def UnEquipItemByLayer(layer: str, wait: bool):
        """Unequip the Item associated with a specific Layer.

        Parameters
        ----------
        layer: str
                Layers:
                RightHand
                LeftHand
                Shoes
                Pants
                Shirt
                Head
                Gloves
                Ring
                Neck
                Hair
                Waist
                InnerTorso
                Bracelet
                FacialHair
                MiddleTorso
                Earrings
                Arms
                Cloak
                OuterTorso
                OuterLegs
                InnerLegs
                Talisman
        wait: bool
                Wait for confirmation from the server.

        """
        ...

    @staticmethod
    def UnEquipUO3D(_layers: Union["List[String]", List]):
        """
        UnEquip a python list of layer names by using UO3D packet.

        Parameters
        ----------
        _layers: List[String] or PythonList

        """
        ...

    def UpdateKarma(self) -> bool:
        """Costly!
        Updates the Fame and Karma of the Mobile, but it can take as long as 1 second to complete.

        Returns
        -------
        bool
                True if successful, False if not server packet received

        """
        ...

    @staticmethod
    def UseSkill(
        skillname: str,
        target: Union["Mobile", "Item", int, bool, None] = None,
        wait: Union[bool, None] = None,
    ):
        """Use a specific skill, and optionally apply that skill to the target specified.


        Parameters
        ----------
        skillname: str
                Alchemy
                Anatomy
                Animal Lore
                Item ID
                Arms Lore
                Parry
                Begging
                Blacksmith
                Fletching
                Peacemaking
                Camping
                Carpentry
                Cartography
                Cooking
                Detect Hidden
                Discordance
                EvalInt
                Healing
                Fishing
                Forensics
                Herding
                Hiding
                Provocation
                Inscribe
                Lockpicking
                Magery
                Magic Resist
                Mysticism
                Tactics
                Snooping
                Musicianship
                Poisoning
                Archery
                Spirit Speak
                Stealing
                Tailoring
                Animal Taming
                Taste ID
                Tinkering
                Tracking
                Veterinary
                Swords
                Macing
                Fencing
                Wrestling
                Lumberjacking
                Mining
                Meditation
                Stealth
                Remove Trap
                Necromancy
                Focus
                Chivalry
                Bushido
                Ninjitsu
                Spell Weaving
                Imbuing
        target: Mobile or Item or int or bool or None
                Optional: Serial, Mobile or Item to target. (default: null)
        wait: bool or None
                Optional: True: wait for confirmation from the server (default: False)

        """
        ...

    @staticmethod
    def UseSkillOnly(skillname: str, wait: bool):
        """

        Parameters
        ----------
        skillname: str
        wait: bool

        """
        ...

    @staticmethod
    def Walk(direction: str) -> bool:
        """

        Parameters
        ----------
        direction: str

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def WeaponClearSA():
        """Disable any active Special Ability of the weapon."""
        ...

    @staticmethod
    def WeaponDisarmSA():
        """Toggle Disarm Ability."""
        ...

    @staticmethod
    def WeaponPrimarySA():
        """Toggle on/off the primary Special Ability of the weapon."""
        ...

    @staticmethod
    def WeaponSecondarySA():
        """Toggle on/off the secondary Special Ability of the weapon."""
        ...

    @staticmethod
    def WeaponStunSA():
        """Toggle Stun Ability."""
        ...

    @staticmethod
    def Zone() -> str:
        """Get the type of zone in which the Player is currently in.
        Regions are defined inside by Config/regions.json.

        Returns
        -------
        str
                Towns
                Dungeons
                Guarded
                Forest
                Unknown

        """
        ...


class Point2D:
    """ """

    X: int
    Y: int

    def ToString(self) -> str:
        """

        Returns
        -------
        str

        """
        ...


class Point3D:
    """ """

    X: int
    Y: int
    Z: int

    def ToString(self) -> str:
        """

        Returns
        -------
        str

        """
        ...


class Property:
    """ """

    Args: str
    Number: int

    def ToString(self) -> str:
        """

        Returns
        -------
        str

        """
        ...


class Rectangle:
    X: int
    Y: int
    Width: int
    Height: int


class Restock:
    """The Restock class allow you to interact with the Restock Agent, via scripting."""

    @staticmethod
    def ChangeList(listName: str):
        """Change the Restock's active list.

        Parameters
        ----------
        listName: str
                Name of an existing restock list.

        """

    @staticmethod
    def FStart():
        """Start the Restock Agent on the currently active list."""

    @staticmethod
    def FStop():
        """Stop the Restock Agent."""

    @staticmethod
    def RunOnce(restockerName: str, sourceBag: int, destBag: int, dragDelay: int):
        """

        Parameters
        ----------
        restockerName: str
        sourceBag: int
        destBag: int
        dragDelay: int

        """

    @staticmethod
    def Status() -> bool:
        """Check Restock Agent status

        Returns
        -------
        bool
                True: if the Restock is running - False: otherwise

        """
        ...


class Scavenger:
    """The Scavenger class allow you to interect with the Scavenger Agent, via scripting."""

    @staticmethod
    def ChangeList(listName: str):
        """Change the Scavenger's active list.

        Parameters
        ----------
        listName: str
                Name of an existing organizer list.

        """

    @staticmethod
    def GetScavengerBag() -> "UInt32":
        """Get current Scravenger destination container.

        Returns
        -------
        UInt32
                Serial of the container.

        """
        ...

    @staticmethod
    def ResetIgnore():
        """ """

    @staticmethod
    def RunOnce(
        scavengerList: "List[Scavenger.ScavengerItem]",
        millisec: int,
        filter: "Items.Filter",
    ):
        """

        Parameters
        ----------
        scavengerList: List[Scavenger.ScavengerItem]
        millisec: int
        filter: Items.Filter

        """
        ...

    @staticmethod
    def Start():
        """Start the Scavenger Agent on the currently active list."""

    @staticmethod
    def Status() -> bool:
        """Check Scavenger Agent status

        Returns
        -------
        bool
                True: if the Scavenger is running - False: otherwise

        """
        ...

    @staticmethod
    def Stop():
        """Stop the Scavenger Agent."""

    class ScavengerItem: ...


class SellAgent:
    """The SellAgent class allow you to interect with the SellAgent, via scripting."""

    @staticmethod
    def ChangeList(listName: str):
        """

        Parameters
        ----------
        listName: str

        """

    @staticmethod
    def Disable():
        """ """

    @staticmethod
    def Enable():
        """ """

    @staticmethod
    def Status() -> bool:
        """

        Returns
        -------
        bool

        """
        ...


class Sound:
    """The Sound class provides an api to manipulate Sounds.
    For now it just turns logging for sounds on / off or waits for a list of sounds
    All the WeakRef stuff seems like overkill and a pia.
    The problem was if you started the wait and then killed the python script, the entry in the waiters list just stayed forever
    The only way around this is to have a weakref stored in the list, then if the local var ManualResetEvent went out of scope,
    the WeakRef will go to null.  At end of loop we clean up all null entries so the list stays clean.
    """

    @staticmethod
    def AddFilter(name: str, sounds: "List[Int32]"):
        """

        Parameters
        ----------
        name: str
        sounds: List[Int32]

        """

    @staticmethod
    def Log(activateLogging: bool):
        """Enables/Disables logging of incoming sound requests

        Parameters
        ----------
        activateLogging: bool
                True= activate sound logging/ False Deactivate sound logging

        """

    @staticmethod
    def OnFilter(p: "PacketReader", args: "PacketHandlerEventArgs"):
        """

        Parameters
        ----------
        p: PacketReader
        args: PacketHandlerEventArgs

        """

    @staticmethod
    def RemoveFilter(name: str):
        """Removes a filter of incoming sound requests

        Parameters
        ----------
        name: str
                The name of the filter to be removed

        """

    @staticmethod
    def WaitForSound(sounds: "List[Int32]", timeout: int) -> bool:
        """

        Parameters
        ----------
        sounds: List[Int32]
        timeout: int

        Returns
        -------
        bool

        """
        ...


class Spells:
    """The Spells class allow you to cast any spell and use abilities, via scripting."""

    @staticmethod
    def Cast(
        SpellName: str,
        target: Union["UInt32", "Mobile", int] = 0,
        wait: Union[bool, None] = None,
        waitAfter: Union[int, None] = None,
    ):
        """Cast spell using the spell name. See the skill-specific functions to get the full list of spell names.
        Optionally is possible to specify the Mobile or a Serial as target of the spell. Upon successful casting, the target will be executed automatiaclly by the server.
        NOTE: The "automatic" target is not supported by all shards, but you can restort to the Target class to handle it manually.


        Parameters
        ----------
        SpellName: str
                Name of the spell to cast.
        target: UInt32 or Mobile or int
                Optional: Serial or Mobile to target (default: null)
        wait: bool or None
                Optional: Wait server to confirm. (default: True)
        waitAfter: int or None

        """

    @staticmethod
    def CastBushido(SpellName: str, wait: bool, waitAfter: int):
        """Cast a Bushido spell using the spell name.

        Parameters
        ----------
        SpellName: str
                Honorable Execution
                Confidence
                Counter Attack
                Lightning Strike
                Evasion
                Momentum Strike
        wait: bool
                Optional: Wait server to confirm. (default: True)
        waitAfter: int

        """

    @staticmethod
    def CastChivalry(
        SpellName: str,
        target: Union["UInt32", "Mobile", int, None] = None,
        wait: Union[bool, None] = None,
        waitAfter: Union[int, None] = None,
    ):
        """Cast a Chivalry spell using the spell name.
        Optionally is possible to specify the Mobile or a Serial as target of the spell. Upon successful casting, the target will be executed automatiaclly by the server.
        NOTE: The "automatic" target is not supported by all shards, but you can restort to the Target class to handle it manually.


        Parameters
        ----------
        SpellName: str
                Cleanse By Fire
                Close Wounds
                Consecrate Weapon
                Dispel Evil
                Divine Fury
                Enemy Of One
                Holy Light
                Noble Sacrifice
                Remove Curse
                Sacred Journey
        target: UInt32 or Mobile or int
                Optional: Serial or Mobile to target (default: null)
        wait: bool or None
                Optional: Wait server to confirm. (default: True)
        waitAfter: int or None

        """

    @staticmethod
    def CastCleric(
        SpellName: str,
        mobile: Union["Mobile", "UInt32", int],
        wait: Union[bool, None] = None,
        waitAfter: Union[int, None] = None,
    ):
        """Cast a Cleric spell using the spell name.
        Optionally is possible to specify the Mobile or a Serial as target of the spell. Upon successful casting, the target will be executed automatiaclly by the server.
        NOTE: The "automatic" target is not supported by all shards, but you can restort to the Target class to handle it manually.


        Parameters
        ----------
        SpellName: str
                Bark Skin : Turns the druid's skin to bark, increasing physical, poison and energy resistence while reducing fire resistence.
                Circle Of Thorns : Creates a ring of thorns preventing an enemy from moving.
                Deadly Spores : The enemy is afflicted by poisonous spores.
                Enchanted Grove : Causes a grove of magical trees to grow, hiding the player for a short time.
                Firefly : Summons a tiny firefly to light the Druid's path. The Firefly is a weak creature with little or no combat skills.
                Forest Kin : Summons from a list of woodland spirits that will fight for the druid and assist him in different ways.
                Grasping Roots : Summons roots from the ground to entangle a single target.
                Hibernate : Causes the target to go to sleep.
                Hollow Reed : Increases both the strength and the intelligence of the Druid.
                Hurricane : Calls forth a violent hurricane that damages any enemies within range.
                Lure Stone : Creates a magical stone that calls all nearby animals to it.
                Mana Spring : Creates a magical spring that restores mana to the druid and any party members within range.
                Mushroom Gateway : A magical circle of mushrooms opens, allowing the Druid to step through it to another location.
                Pack Of Beasts : Summons a pack of beasts to fight for the Druid. Spell length increases with skill.
                Restorative Soil : Saturates a patch of land with power, causing healing mud to seep through . The mud can restore the dead to life.
                Shield Of Earth : A quick-growing wall of foliage springs up at the bidding of the Druid.
                Spring Of Life : Creates a magical spring that heals the Druid and their party.
                Swarm Of Insects : Summons a swarm of insects that bite and sting the Druid's enemies.
                Treefellow : Summons a powerful woodland spirit to fight for the Druid.
                Volcanic Eruption : A blast of molten lava bursts from the ground, hitting every enemy nearby.
        mobile: Mobile or UInt32 or int
                Optional: Serial or Mobile to target (default: null)
        wait: bool or None
                Optional: Wait server to confirm. (default: True)
        waitAfter: int or None

        """

    @staticmethod
    def CastDruid(
        SpellName: str,
        target: Union["UInt32", "Mobile", int],
        wait: Union[bool, None] = None,
        waitAfter: Union[int, None] = None,
    ):
        """Cast a Druid spell using the spell name.
        Optionally is possible to specify the Mobile or a Serial as target of the spell. Upon successful casting, the target will be executed automatiaclly by the server.
        NOTE: The "automatic" target is not supported by all shards, but you can restort to the Target class to handle it manually.


        Parameters
        ----------
        SpellName: str
                Angelic Faith : Turns you into an angel, boosting your stats. At 100 Spirit Speak you get +20 Str/Dex/Int. Every 5 points of SS = +1 point to each stat, at a max of +24. Will also boost your Anatomy, Mace Fighting and Healing, following the same formula.
                Banish Evil : Banishes Undead targets. Auto kills rotting corpses, lich lords, etc. Works well at Doom Champ. Does not produce a corpse however
                Dampen Spirit : Drains the stamina of your target, according to the description
                Divine Focus : Heal for more, but may be broken.
                Hammer of Faith : Summons a War Hammer with Undead Slayer on it for you
                Purge : Cleanses Poison. Better than Cure
                Restoration : Resurrection. Brings the target back with 100% HP/Mana
                Sacred Boon : A HoT, heal over time spell, that heals 10-15 every few seconds
                Sacrifice : Heals your party members when you take damage. Sort of like thorns, but it heals instead of hurts
                Smite : Causes energy damage
                Touch of Life : Heals even if Mortal Strike or poison are active on the target
                Trial by Fire : Attackers receive damage when they strike you, sort of like a temporary RPD buff
        target: UInt32 or Mobile or int
                target to use the druid spell on
        wait: bool or None
        waitAfter: int or None

        """

    @staticmethod
    def CastLastSpell(m: Union["Mobile", "UInt32", bool], wait: Union[bool, None] = None):
        """
        Cast again the last casted spell, on last target.

        Parameters
        ----------
        m: Mobile or UInt32 or bool
                Optional: Serial or Mobile to target (default: null)
        wait: bool or None
                Optional: Wait server to confirm. (default: True)

        """

    @staticmethod
    def CastLastSpellLastTarget():
        """Cast again the last casted spell, on last target."""

    @staticmethod
    def CastMagery(
        SpellName: str,
        target: Union["UInt32", "Mobile", int],
        wait: Union[bool, None] = None,
        waitAfter: Union[int, None] = None,
    ):
        """Cast a Magery spell using the spell name.
        Optionally is possible to specify the Mobile or a Serial as target of the spell. Upon successful casting, the target will be executed automatiaclly by the server.
        NOTE: The "automatic" target is not supported by all shards, but you can restort to the Target class to handle it manually.


        Parameters
        ----------
        SpellName: str
                Clumsy
                Create Food
                Feeblemind
                Heal
                Magic Arrow
                Night Sight
                Reactive Armor
                Weaken
                Agility
                Cunning
                Cure
                Harm
                Magic Trap
                Magic Untrap
                Protection
                Strength
                Bless
                Fireball
                Magic Lock
                Poison
                Telekinesis
                Teleport
                Unlock
                Wall of Stone
                Arch Cure
                Arch Protection
                Curse
                Fire Field
                Greater Heal
                Lightning
                Mana Drain
                Recall
                Blade Spirits
                Dispel Field
                Incognito
                Magic Reflection
                Mind Blast
                Paralyze
                Poison Field
                Summon Creature
                Dispel
                Energy Bolt
                Explosion
                Invisibility
                Mark
                Mass Curse
                Paralyze Field
                Reveal
                Chain Lightning
                Energy Field
                Flamestrike
                Gate Travel
                Mana Vampire
                Mass Dispel
                Meteor Swarm
                Polymorph
                Earthquake
                Energy Vortex
                Resurrection
                Summon Air Elemental
                Summon Daemon
                Summon Earth Elemental
                Summon Fire Elemental
                Summon Water Elemental
        target: UInt32 or Mobile or int
                Optional: Serial or Mobile to target (default: null)
        wait: bool or None
                Optional: Wait server to confirm. (default: True)
        waitAfter: int or None

        """

    @staticmethod
    def CastMastery(
        SpellName: str,
        target: Union["UInt32", "Mobile", int],
        wait: Union[bool, None] = None,
        waitAfter: Union[int, None] = None,
    ):
        """Cast a Mastery spell using the spell name.
        Optionally is possible to specify the Mobile or a Serial as target of the spell. Upon successful casting, the target will be executed automatiaclly by the server.
        NOTE: The "automatic" target is not supported by all shards, but you can restort to the Target class to handle it manually.


        Parameters
        ----------
        SpellName: str
                Inspire
                Invigorate
                Resilience
                Perseverance
                Tribulation
                Despair
                Death Ray
                Ethereal Blast
                Nether Blast
                Mystic Weapon
                Command Undead
                Conduit
                Mana Shield
                Summon Reaper
                Enchanted Summoning
                Anticipate Hit
                Warcry
                Intuition
                Rejuvenate
                Holy Fist
                Shadow
                White Tiger Form
                Flaming Shot
                Playing The Odds
                Thrust
                Pierce
                Stagger
                Toughness
                Onslaught
                Focused Eye
                Elemental Fury
                Called Shot
                Saving Throw
                Shield Bash
                Bodyguard
                Heighten Senses
                Tolerance
                Injected Strike
                Potency
                Rampage
                Fists Of Fury
                Knockout
                Whispering
                Combat Training
                Boarding
        target: UInt32 or Mobile or int
                Optional: Serial or Mobile to target (default: null)
        wait: bool or None
                Optional: Wait server to confirm. (default: True)
        waitAfter: int or None

        """

    @staticmethod
    def CastMysticism(
        SpellName: str,
        target: Union["UInt32", "Mobile", int],
        wait: Union[bool, None] = None,
        waitAfter: Union[int, None] = None,
    ):
        """Cast a Mysticism spell using the spell name.
        Optionally is possible to specify the Mobile or a Serial as target of the spell. Upon successful casting, the target will be executed automatiaclly by the server.
        NOTE: The "automatic" target is not supported by all shards, but you can restort to the Target class to handle it manually.


        Parameters
        ----------
        SpellName: str
                Animated Weapon
                Healing Stone
                Purge
                Enchant
                Sleep
                Eagle Strike
                Stone Form
                SpellTrigger
                Mass Sleep
                Cleansing Winds
                Bombard
                Spell Plague
                Hail Storm
                Nether Cyclone
                Rising Colossus
        target: UInt32 or Mobile or int
                Optional: Serial or Mobile to target (default: null)
        wait: bool or None
                Optional: Wait server to confirm. (default: True)
        waitAfter: int or None

        """

    @staticmethod
    def CastNecro(
        SpellName: str,
        target: Union["UInt32", "Mobile", int],
        wait: Union[bool, None] = None,
        waitAfter: Union[int, None] = None,
    ):
        """Cast a Necromany spell using the spell name.
        Optionally is possible to specify the Mobile or a Serial as target of the spell. Upon successful casting, the target will be executed automatiaclly by the server.
        NOTE: The "automatic" target is not supported by all shards, but you can restort to the Target class to handle it manually.


        Parameters
        ----------
        SpellName: str
                Curse Weapon
                Pain Spike
                Corpse Skin
                Evil Omen
                Blood Oath
                Wraith Form
                Mind Rot
                Summon Familiar
                Horrific Beast
                Animate Dead
                Poison Strike
                Wither
                Strangle
                Lich Form
                Exorcism
                Vengeful Spirit
                Vampiric Embrace
        target: UInt32 or Mobile or int
                Optional: Serial or Mobile to target (default: null)
        wait: bool or None
                Optional: Wait server to confirm. (default: True)
        waitAfter: int or None

        """

    @staticmethod
    def CastNinjitsu(
        SpellName: str,
        mobile: Union["Mobile", "UInt32", int],
        wait: Union[bool, None] = None,
        waitAfter: Union[int, None] = None,
    ):
        """
        Cast a Ninjitsu spell using the spell name.
        Optionally is possible to specify the Mobile or a Serial as target of the spell. Upon successful casting, the target will be executed automatiaclly by the server.
        NOTE: The "automatic" target is not supported by all shards, but you can restort to the Target class to handle it manually.

        Parameters
        ----------
        SpellName: str
                Animal Form
                Backstab
                Surprise Attack
                Mirror Image
                Shadow jump
                Focus Attack
                Ki Attack
        mobile: Mobile or UInt32 or int
                Optional: Serial or Mobile to target (default: null)
        wait: bool or None
                Optional: Wait server to confirm. (default: True)
        waitAfter: int or None

        """

    @staticmethod
    def CastSpellweaving(
        SpellName: str,
        target: Union["UInt32", "Mobile", int],
        wait: Union[bool, None] = None,
        waitAfter: Union[int, None] = None,
    ):
        """Cast a Spellweaving spell using the spell name.
        Optionally is possible to specify the Mobile or a Serial as target of the spell. Upon successful casting, the target will be executed automatiaclly by the server.
        NOTE: The "automatic" target is not supported by all shards, but you can restort to the Target class to handle it manually.


        Parameters
        ----------
        SpellName: str
                Arcane Circle
                Gift Of Renewal
                Immolating Weapon
                Attune Weapon
                Thunderstorm
                Natures Fury
                Summon Fey
                Summoniend
                Reaper Form
                Wildfire
                Essence Of Wind
                Dryad Allure
                Ethereal Voyage
                Word Of Death
                Gift Of Life
                Arcane Empowerment
        target: UInt32 or Mobile or int
                Optional: Serial or Mobile to target (default: null)
        wait: bool or None
                Optional: Wait server to confirm. (default: True)
        waitAfter: int or None

        """

    @staticmethod
    def Interrupt():
        """Interrupt the casting of a spell by performing an equip/unequip."""


class Statics:
    """The Statics class provides access to informations about the Map, down to the individual tile.
    When using this function it's important to remember the distinction between Land and Tile:
    Land
    ----
    For a given (X,Y,map) there can be only 1 (0 zero) Land item, and has 1 specific Z coordinate.
    Tile
    ----
    For a given (X,Y,map) there can be any number of Tile items.
    """

    @staticmethod
    def CheckDeedHouse(x: int, y: int) -> bool:
        """Check if the given Tile is occupied by a private house.
        Need to be in-sight, on most servers the maximum distance is 18 tiles.

        Parameters
        ----------
        x: int
                X coordinate.
        y: int
                Y coordinate.

        Returns
        -------
        bool
                True: The tile is occupied - False: otherwise

        """
        ...

    @staticmethod
    def GetItemData(StaticID: int) -> "ItemData":
        """

        Parameters
        ----------
        StaticID: int

        Returns
        -------
        ItemData

        """
        ...

    @staticmethod
    def GetLandFlag(staticID: int, flagname: str) -> bool:
        """Land: Check Flag value of a given Land item.

        Parameters
        ----------
        staticID: int
                StaticID of a Land item.
        flagname: str
                None
                Translucent
                Wall
                Damaging
                Impassable
                Surface
                Bridge
                Window
                NoShoot
                Foliage
                HoverOver
                Roof
                Door
                Wet

        Returns
        -------
        bool
                True: if the Flag is active - False: otherwise

        """
        ...

    @staticmethod
    def GetLandID(x: int, y: int, map: int) -> int:
        """Land: Return the StaticID of the Land item, give the coordinates and map.

        Parameters
        ----------
        x: int
                X coordinate.
        y: int
                Y coordinate.
        map: int
                0 = Felucca
                1 = Trammel
                2 = Ilshenar
                3 = Malas
                4 = Tokuno
                5 = TerMur

        Returns
        -------
        int
                Return the StaticID of the Land tile

        """
        ...

    @staticmethod
    def GetLandName(StaticID: int) -> str:
        """Land: Get the name of a Land item given the StaticID.

        Parameters
        ----------
        StaticID: int
                Land item StaticID.

        Returns
        -------
        str
                The name of the Land item.

        """
        ...

    @staticmethod
    def GetLandZ(x: int, y: int, map: int) -> int:
        """Land: Return the Z coordinate (height) of the Land item, give the coordinates and map.

        Parameters
        ----------
        x: int
                X coordinate.
        y: int
                Y coordinate.
        map: int
                0 = Felucca
                1 = Trammel
                2 = Ilshenar
                3 = Malas
                4 = Tokuno
                5 = TerMur

        Returns
        -------
        int

        """
        ...

    @staticmethod
    def GetStaticsLandInfo(x: int, y: int, map: int) -> "Statics.TileInfo":
        """Land: Return a TileInfo representing the Land item for a given X,Y, map.

        Parameters
        ----------
        x: int
                X coordinate.
        y: int
                Y coordinate.
        map: int
                0 = Felucca
                1 = Trammel
                2 = Ilshenar
                3 = Malas
                4 = Tokuno
                5 = TerMur

        Returns
        -------
        Statics.TileInfo
                A single TileInfo related a Land item.

        """
        ...

    @staticmethod
    def GetStaticsTileInfo(x: int, y: int, map: int) -> "List[Statics.TileInfo]":
        """Tile: Return a list of TileInfo representing the Tile items for a given X,Y, map.

        Parameters
        ----------
        x: int
                X coordinate.
        y: int
                Y coordinate.
        map: int
                0 = Felucca
                1 = Trammel
                2 = Ilshenar
                3 = Malas
                4 = Tokuno
                5 = TerMur

        Returns
        -------
        List[Statics.TileInfo]
                A list of TileInfo related to Tile items.

        """
        ...

    @staticmethod
    def GetTileFlag(StaticID: int, flagname: str) -> bool:
        """Tile: Check Flag value of a given Tile item.

        Parameters
        ----------
        StaticID: int
                StaticID of a Tile item.
        flagname: str
                None
                Translucent
                Wall
                Damaging
                Impassable
                Surface
                Bridge
                Window
                NoShoot
                Foliage
                HoverOver
                Roof
                Door
                Wet

        Returns
        -------
        bool
                True: if the Flag is active - False: otherwise

        """
        ...

    @staticmethod
    def GetTileHeight(StaticID: int) -> int:
        """Tile: Get hight of a Tile item, in Z coordinate reference.

        Parameters
        ----------
        StaticID: int
                Tile item StaticID.

        Returns
        -------
        int
                Height of a Tile item.

        """
        ...

    @staticmethod
    def GetTileName(StaticID: int) -> str:
        """Tile: Get the name of a Tile item given the StaticID.

        Parameters
        ----------
        StaticID: int
                Tile item StaticID.

        Returns
        -------
        str
                The name of the Land item.

        """
        ...

    class TileInfo:
        """The TileInfo class hold the values represeting Tile or Land items for a given X,Y coordinate."""

        Hue: int
        ID: "UInt16"
        StaticHue: int
        StaticID: int
        StaticZ: int
        Z: int


class Target:
    """The Target class provides various methods for targeting Land, Items and Mobiles in game."""

    @staticmethod
    def AttackTargetFromList(target_name: str):
        """Attack Target from gui filter selector, in Targetting tab.

        Parameters
        ----------
        target_name: str

        """

    @staticmethod
    def Cancel():
        """Cancel the current target."""

    @staticmethod
    def ClearLast():
        """Clear the last target."""

    @staticmethod
    def ClearLastandQueue():
        """Clear last target and target queue."""

    @staticmethod
    def ClearLastAttack():
        """Clear the last attacked target"""

    @staticmethod
    def ClearQueue():
        """Clear Queue Target."""

    @staticmethod
    def GetLast() -> int:
        """Get serial number of last target

        Returns
        -------
        int
                Serial as number.

        """
        ...

    @staticmethod
    def GetLastAttack() -> int:
        """Get serial number of last attack target

        Returns
        -------
        int
                Serial as number.

        """
        ...

    @staticmethod
    def GetTargetFromList(target_name: str) -> "Mobile":
        """Get Mobile object from GUI filter selector, in Targetting tab.

        Parameters
        ----------
        target_name: str
                Name of the target filter.

        Returns
        -------
        Mobile
                Mobile object matching. None: not found

        """
        ...

    @staticmethod
    def HasTarget(targetFlag: str) -> bool:
        """Get the status of the in-game target cursor
        Optionally specify the target flag and check if the cursor is "Beneficial", "Harmful", or "Neutral".

        Parameters
        ----------
        targetFlag: str
                The target flag to check for can be "Any", "Beneficial", "Harmful", or "Neutral".

        Returns
        -------
        bool
                True if the client has a target cursor and the optional flag matches; otherwise, false.

        """
        ...

    @staticmethod
    def Last():
        """Execute the target on the last Item or Mobile targeted."""

    @staticmethod
    def LastQueued():
        """Enqueue the next target on the last Item or Mobile targeted."""

    @staticmethod
    def LastUsedObject() -> int:
        """Returns the serial of last object used by the player.

        Returns
        -------
        int

        """
        ...

    @staticmethod
    def PerformTargetFromList(target_name: str):
        """Execute Target from GUI filter selector, in Targetting tab.

        Parameters
        ----------
        target_name: str
                Name of the target filter.

        """
        ...

    @staticmethod
    def PromptGroundTarget(message: str, color: int) -> "Point3D":
        """Prompt a target in-game, wait for the Player to select the ground. Can also specific a text message for prompt.

        Parameters
        ----------
        message: str
                Hint on what to select.
        color: int
                Color of the message. (default: 945, gray)

        Returns
        -------
        Point3D
                A Point3D object, containing the X,Y,Z coordinate

        """
        ...

    @staticmethod
    def PromptTarget(message: str, color: int) -> int:
        """Prompt a target in-game, wait for the Player to select an Item or a Mobile. Can also specific a text message for prompt.

        Parameters
        ----------
        message: str
                Hint on what to select.
        color: int
                Color of the message. (default: 945, gray)

        Returns
        -------
        int
                Serial of the selected object.

        """
        ...

    @staticmethod
    def Self():
        """Execute the target on the Player."""

    @staticmethod
    def SelfQueued():
        """Enqueue the next target on the Player."""

    @staticmethod
    def SetLast(serial: Union[int, "Mobile"], wait: Union[bool, None] = None):
        """Set the last target to specific mobile, using the serial.


        Parameters
        ----------
        serial: int or Mobile
                Serial of the Mobile.
        wait: bool or None
                Wait confirmation from the server.

        """

    @staticmethod
    def SetLastTargetFromList(target_name: str):
        """Set Last Target from GUI filter selector, in Targetting tab.

        Parameters
        ----------
        target_name: str
                Name of the target filter.

        """

    @staticmethod
    def TargetExecute(
        x: Union[int, "UOEntity"],
        y: Union[int, None] = None,
        z: Union[int, None] = None,
        StaticID: Union[int, None] = None,
    ):
        """Execute target on specific serial, item, mobile, X Y Z point.

        Targets the Mobil or Item specified

        Parameters
        ----------
        x: int or UOEntity
                X coordinate.

                Serial of the Target
                object can be a Mobil or an Item.
        y: int or None
                Y coordinate.
        z: int or None
                Z coordinate.
        StaticID: int or None
                ID of Land/Tile

        """

    @staticmethod
    def TargetExecuteRelative(mobile: Union["Mobile", int], offset: int):
        """
        Execute target on specific land point with offset distance from Mobile. Distance is calculated by target Mobile.Direction.

        Parameters
        ----------
        mobile: Mobile or int
                Mobile object to target.
                Serial of the mobile
        offset: int
                Distance from the target.
                +- distance to offset from the mobile identified with serial

        """

    @staticmethod
    def TargetResource(item_serial: Union[int, "Item"], resource_number: Union[int, str]):
        """Find and target a resource using the specified item.


        Parameters
        ----------
        item_serial: int or Item
                Item object to use.
        resource_number: int or str
                Resource as standard name or custom number
                0: ore
                1: sand
                2: wood
                3: graves
                4: red_mushrooms
                n: custom

                name of the resource to be targeted. ore, sand, wood, graves, red mushroom

        """

    @staticmethod
    def TargetType(graphic: int, color: int, range: int, selector: str, notoriety: "List[Byte]") -> bool:
        """

        Parameters
        ----------
        graphic: int
        color: int
        range: int
        selector: str
        notoriety: List[Byte]

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def WaitForTarget(delay: int, noshow: bool) -> bool:
        """Wait for the cursor to show the target, pause the script for a maximum amount of time. and optional flag True or False. True Not show cursor, false show it

        Parameters
        ----------
        delay: int
                Maximum amount to wait, in milliseconds
        noshow: bool
                Pevent the cursor to display the target.

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def WaitForTargetOrFizzle(delay: int, noshow: bool) -> bool:
        """Wait for the cursor to show the target, or the sound for fizzle (0x5c) or pause the script for a maximum amount of time.
        and an optional flag True or False. True Not show cursor, false show it

        Parameters
        ----------
        delay: int
                Maximum amount to wait, in milliseconds
        noshow: bool
                Prevent the cursor to display the target.

        Returns
        -------
        bool

        """
        ...


class Tile:
    """Class representing an (X,Y) coordinate. Optimized for pathfinding tasks."""

    Conflict: bool
    X: int
    """Coordinate X."""

    Y: int
    """Coordinate Y."""

    def Equals(self, obj: object) -> bool:
        """

        Parameters
        ----------
        obj: object

        Returns
        -------
        bool

        """
        ...

    def GetHashCode(self) -> int:
        """

        Returns
        -------
        int

        """
        ...

    def ToString(self) -> str:
        """

        Returns
        -------
        str

        """
        ...


class Timer:
    """Timer are normally used to display messages after a certain period of time.
    They are also often used to keep track of the maximum amount of time for an action to complete.
    """

    @staticmethod
    def Check(name: str) -> bool:
        """Check if a timer object is expired or not.

        Parameters
        ----------
        name: str

        Returns
        -------
        bool
                true if not expired, false if expired

        """
        ...

    @staticmethod
    def Create(name: str, delay: int, message: Union[str, None] = None):
        """Create a timer with the provided name that will expire in ms_timer time (in milliseconds)


        Parameters
        ----------
        name: str
                Timer name.
        delay: int
                Delay in milliseconds.
        message: str or None
                Message displayed at timeouit.

        """
        ...

    @staticmethod
    def Remaining(name: str) -> int:
        """Get remaining time for a named timer

        Parameters
        ----------
        name: str
                Timer name

        Returns
        -------
        int
                Returns the milliseconds remaining for a timer.

        """
        ...


class Trade:
    """ """

    @staticmethod
    def Accept(TradeID: Union[int, bool], accept: Union[bool, None] = None) -> bool:
        """Set the accept state of the trade


        Parameters
        ----------
        TradeID: int or bool
                ID of the Trade (Default = -1: Pick a random active trade)
        accept: bool or None
                Set the state ofthe checkbox

        Returns
        -------
        bool
                True: Trade found, False: Trade not found

        """
        ...

    @staticmethod
    def Cancel(TradeID: Union[int, None] = None) -> bool:
        """Set the accept state of the trade


        Parameters
        ----------
        TradeID: int or None
                ID of the Trade (Default = -1: Pick a random active trade)

        Returns
        -------
        bool
                True: Trade found, False: Trade not found

        """
        ...

    @staticmethod
    def Offer(
        TradeID: int,
        gold: int,
        platinum: Union[int, bool],
        quiet: Union[bool, None] = None,
    ) -> bool:
        """Update the amount of gold and platinum in the trade. ( client view dosen't update )


        Parameters
        ----------
        TradeID: int
                ID of the Trade (Default = -1: Pick latest active trade)
        gold: int
                Amount of Gold to offer
        platinum: int or bool
                Amount of Platinum to offer
        quiet: bool or None
                Suppress output (Default: false - Show warning)

        Returns
        -------
        bool
                True: Trade found, False: Trade not found

        """
        ...

    @staticmethod
    def TradeList() -> "List[Trade.TradeData]":
        """Returns the list of currently active Secure Trading gumps, sorted by LastUpdate.

        Returns
        -------
        List[Trade.TradeData]
                A list of Player.SecureTrade objects. Each containing the details of each trade window.

        """
        ...

    class TradeData:
        """SecureTrades holds the information about a single tradeing window."""

        AcceptMe: bool
        """Trade has been accepted by the Player (me)."""

        AcceptTrader: bool
        """Trade has been accepted by the Trader (other)."""

        ContainerMe: int
        """Serial of the container holding the items offerd by the Player (me)."""

        ContainerTrader: int
        """Serial of the container holding the items offerd by the Trader (other)."""

        GoldMax: int
        """Maximum amount of Gold available for the Player (me)."""

        GoldMe: int
        """Amount of Gold offerd by the Player (me)."""

        GoldTrader: int
        """Amount of Gold offerd by the Trader (other)."""

        LastUpdate: float
        """Last update of the Trade as UnixTime ( format: "Seconds,Milliseconds" from 1-1-1970 )"""

        NameTrader: str
        """Name of the Trader (other)."""

        PlatinumMax: int
        """Maximum amount of Platinum available for the Player (me)."""

        PlatinumMe: int
        """Amount of Platinum offerd by the Player (me)."""

        PlatinumTrader: int
        """Amount of Platinum offerd by the Trader (other)."""

        SerialTrader: int
        """Serial of the Trader (other) ."""

        TradeID: int
        """ID of the Trade."""


class Vendor:
    """@experimental
    The Vendor class allow you to read the list items purchased last.
    """

    LastBuyList: "List[Item]"
    LastResellList: "List[Item]"

    @staticmethod
    def Buy(vendorSerial: int, itemName: Union[str, int], amount: int, maxPrice: int) -> bool:
        """Attempts to buy the item from the vendor specified.
        <param name="vendorSerial">The Vendor to buy from</param>
        <param name="itemName">the name of the item to buy (can be partial)</param>
        <param name="amount">amount to attempt to buy</param>
        <param name="maxPrice">Don't buy them if the cost exceeds this price.
        default value = -1 means don't check price</param>
        Returns True if a purchase is made, False otherwise
        Attempts to buy the item from the vendor specified.
        <param name="vendorSerial">The Vendor to buy from</param>
        <param name="itemID">the itemID of the type of item to buy</param>
        <param name="amount">amount to attempt to buy</param>
        <param name="maxPrice">Don't buy them if the cost exceeds this price.
        default value = -1 means don't check price</param>
        Returns True if a purchase is made, False otherwise

        Parameters
        ----------
        vendorSerial: int
                The Vendor to buy from
        itemName: str or int
                the name of the item to buy (can be partial)
                the itemID of the type of item to buy
        amount: int
                amount to attempt to buy
        maxPrice: int
                Don't buy them if the cost exceeds this price.
                default value = -1 means don't check price

        Returns
        -------
        bool

        """
        ...

    @staticmethod
    def BuyList(vendorSerial: int) -> "List[Vendor.BuyItem]":
        """Get the list of items purchased in the last trade, with a specific Vendor.

        Parameters
        ----------
        vendorSerial: int
                Serial of the Vendor (default: -1 - most recent trade)

        Returns
        -------
        List[Vendor.BuyItem]
                A list of BuyItem

        """
        ...

    class BuyItem:
        """The BuyItem class store informations about a recently purchased item."""

        Amount: int
        ItemID: int
        Name: str
        Price: int
        Serial: int
