"""
utils/icons.py
--------------
Reusable inline SVG icons for EduMetrics (Lucide/Heroicons clean line style).
All icons default to size=20 and stroke="currentColor" so they adapt cleanly to text color.
"""

def icon_academic_cap(size: int = 20, color: str = "currentColor") -> str:
    """Graduation / Academic Cap Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/>'
        '<path d="M6 12v5c3 3 9 3 12 0v-5"/>'
        '</svg>'
    )

def icon_chart_bar(size: int = 20, color: str = "currentColor") -> str:
    """Bar Chart / Analytics Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<line x1="18" y1="20" x2="18" y2="10"/>'
        '<line x1="12" y1="20" x2="12" y2="4"/>'
        '<line x1="6" y1="20" x2="6" y2="14"/>'
        '</svg>'
    )

def icon_clipboard(size: int = 20, color: str = "currentColor") -> str:
    """Clipboard / Breakdown Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>'
        '<rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>'
        '</svg>'
    )

def icon_alert(size: int = 20, color: str = "currentColor") -> str:
    """Alert / Warning Triangle Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/>'
        '<line x1="12" y1="17" x2="12.01" y2="17"/>'
        '</svg>'
    )

def icon_search(size: int = 20, color: str = "currentColor") -> str:
    """Search / Magnifying Glass Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<circle cx="11" cy="11" r="8"/>'
        '<line x1="21" y1="21" x2="16.65" y2="16.65"/>'
        '</svg>'
    )

def icon_download(size: int = 20, color: str = "currentColor") -> str:
    """Download Arrow Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<polyline points="7 10 12 15 17 10"/>'
        '<line x1="12" y1="15" x2="12" y2="3"/>'
        '</svg>'
    )

def icon_folder(size: int = 20, color: str = "currentColor") -> str:
    """Folder Dataset Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'
        '</svg>'
    )

def icon_check(size: int = 18, color: str = "currentColor") -> str:
    """Checkmark Circle Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>'
        '<polyline points="22 4 12 14.01 9 11.01"/>'
        '</svg>'
    )

def icon_trophy(size: int = 20, color: str = "currentColor") -> str:
    """Trophy / Award Medal Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>'
        '<path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>'
        '<path d="M4 22h16"/>'
        '<path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>'
        '<path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>'
        '<path d="M18 2H6v7a6 6 0 0 0 12 0V2z"/>'
        '</svg>'
    )

def icon_trending_down(size: int = 20, color: str = "currentColor") -> str:
    """Trending Down / Analytics Chart Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>'
        '<polyline points="17 18 23 18 23 12"/>'
        '</svg>'
    )

def icon_info(size: int = 18, color: str = "currentColor") -> str:
    """Info Circle Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="12" y1="16" x2="12" y2="12"/>'
        '<line x1="12" y1="8" x2="12.01" y2="8"/>'
        '</svg>'
    )

def icon_sparkles(size: int = 20, color: str = "currentColor") -> str:
    """Sparkles / AI Magic Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>'
        '<path d="M5 3v4M3 5h4M19 17v4M17 19h4"/>'
        '</svg>'
    )

def icon_user(size: int = 20, color: str = "currentColor") -> str:
    """User / Student Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>'
        '<circle cx="12" cy="7" r="4"/>'
        '</svg>'
    )

def icon_users(size: int = 20, color: str = "currentColor") -> str:
    """Users / Group Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
        '</svg>'
    )

def icon_shield_check(size: int = 16, color: str = "currentColor") -> str:
    """Shield Check Privacy Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
        '<path d="m9 12 2 2 4-4"/>'
        '</svg>'
    )

def icon_scale(size: int = 16, color: str = "currentColor") -> str:
    """Scale / Terms & Conditions Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1z"/>'
        '<path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1z"/>'
        '<path d="M7 21h10"/>'
        '<path d="M12 3v18"/>'
        '<path d="M3 7h18"/>'
        '</svg>'
    )

def icon_file_text(size: int = 16, color: str = "currentColor") -> str:
    """File Text License Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>'
        '<polyline points="14 2 14 8 20 8"/>'
        '<line x1="16" y1="13" x2="8" y2="13"/>'
        '<line x1="16" y1="17" x2="8" y2="17"/>'
        '<line x1="10" y1="9" x2="8" y2="9"/>'
        '</svg>'
    )

def icon_target(size: int = 16, color: str = "currentColor") -> str:
    """Target / Goal Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<circle cx="12" cy="12" r="10"/>'
        '<circle cx="12" cy="12" r="6"/>'
        '<circle cx="12" cy="12" r="2"/>'
        '</svg>'
    )

def icon_bot(size: int = 16, color: str = "currentColor") -> str:
    """Bot / AI Assistant Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<rect x="3" y="11" width="18" height="10" rx="2"/>'
        '<circle cx="12" cy="5" r="2"/>'
        '<path d="M12 7v4"/>'
        '<line x1="8" y1="16" x2="8" y2="16"/>'
        '<line x1="16" y1="16" x2="16" y2="16"/>'
        '</svg>'
    )

def icon_edumetrics_logo(size: int = 38, color: str = "#2563eb") -> str:
    """EduMetrics Official Combined Graduation Cap + Bar Chart Logo SVG"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; display: inline-block;">'
        f'<path d="M50 6L6 34L50 62L94 34L50 6Z" fill="{color}"/>'
        f'<path d="M50 20L20 40L50 54L80 40L50 20Z" fill="#ffffff"/>'
        f'<path d="M17 44V76C17 79 21 82 23 81V44Z" fill="{color}"/>'
        f'<path d="M83 44V76C83 79 79 82 77 81V44Z" fill="{color}"/>'
        f'<rect x="27" y="74" width="13" height="22" rx="3" fill="{color}"/>'
        f'<rect x="44" y="60" width="13" height="36" rx="3" fill="{color}"/>'
        f'<rect x="61" y="46" width="13" height="50" rx="3" fill="{color}"/>'
        '</svg>'
    )

def icon_external_link(size: int = 14, color: str = "currentColor") -> str:
    """External Link Icon"""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align: middle; display: inline-block;">'
        '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>'
        '<polyline points="15 3 21 3 21 9"/>'
        '<line x1="10" y1="14" x2="21" y2="3"/>'
        '</svg>'
    )


