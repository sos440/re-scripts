from typing import Optional, Union

from placeholders import Mobile

Serial = int  # Razor Enhanced uses UInt32 serials
Targetable = Union[Serial, Mobile]

# ---------------------------------------------------------------------------
# Core static class
# ---------------------------------------------------------------------------
class Spells:
    """
    Static helper class for casting any spell or mastery ability via scripting.
    Every cast method returns `None` and raises no exception on failure; check
    Journal or Target classes yourself if you need confirmation.
    """

    # ---------------------------------------------------------------------
    # Generic casting helpers
    # ---------------------------------------------------------------------
    @classmethod
    def Cast(
        cls,
        spell_name: str,
        target: Optional[Targetable] = None,
        wait: bool = True,
        wait_after: int = 0,
    ) -> None:
        """Cast *any* spell by name."""

    @classmethod
    def CastLastSpell(
        cls,
        target: Optional[Targetable] = None,
        wait: bool = True,
    ) -> None:
        """Re‑cast the last spell on an optional target."""

    @classmethod
    def CastLastSpellLastTarget(cls) -> None:
        """Re‑cast the last spell on the last target."""

    @classmethod
    def Interrupt(cls) -> None:
        """Force‑interrupt an in‑progress spell (equip/unequip trick)."""
    # ---------------------------------------------------------------------
    # Skill‑specific helpers
    # Each method accepts the spell name exactly as shown in the RE docs.
    # ---------------------------------------------------------------------
    @classmethod
    def CastBushido(
        cls,
        spell_name: str,
        wait: bool = True,
        wait_after: int = 0,
    ) -> None: ...
    @classmethod
    def CastChivalry(
        cls,
        spell_name: str,
        target: Optional[Targetable] = None,
        wait: bool = True,
        wait_after: int = 0,
    ) -> None: ...
    @classmethod
    def CastCleric(
        cls,
        spell_name: str,
        target: Optional[Targetable] = None,
        wait: bool = True,
        wait_after: int = 0,
    ) -> None: ...
    @classmethod
    def CastDruid(
        cls,
        spell_name: str,
        target: Optional[Targetable] = None,
        wait: bool = True,
        wait_after: int = 0,
    ) -> None: ...
    @classmethod
    def CastMagery(
        cls,
        spell_name: str,
        target: Optional[Targetable] = None,
        wait: bool = True,
        wait_after: int = 0,
    ) -> None: ...
    @classmethod
    def CastMastery(
        cls,
        spell_name: str,
        target: Optional[Targetable] = None,
        wait: bool = True,
        wait_after: int = 0,
    ) -> None: ...
    @classmethod
    def CastMysticism(
        cls,
        spell_name: str,
        target: Optional[Targetable] = None,
        wait: bool = True,
        wait_after: int = 0,
    ) -> None: ...
    @classmethod
    def CastNecro(
        cls,
        spell_name: str,
        target: Optional[Targetable] = None,
        wait: bool = True,
        wait_after: int = 0,
    ) -> None: ...
    @classmethod
    def CastNinjitsu(
        cls,
        spell_name: str,
        target: Optional[Targetable] = None,
        wait: bool = True,
        wait_after: int = 0,
    ) -> None: ...
    @classmethod
    def CastSpellweaving(
        cls,
        spell_name: str,
        target: Optional[Targetable] = None,
        wait: bool = True,
        wait_after: int = 0,
    ) -> None: ...
