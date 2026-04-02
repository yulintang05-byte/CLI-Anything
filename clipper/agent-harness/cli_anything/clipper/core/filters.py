"""Clipper CLI - Filter registry and clip filter management."""

from typing import Dict, Any, List, Optional

from cli_anything.clipper.core.session import Session


FILTER_REGISTRY: Dict[str, Dict[str, Any]] = {
    "brightness": {
        "category": "color",
        "description": "Adjust image brightness",
        "ffmpeg_filter": "eq",
        "params": {
            "level": {
                "type": "float",
                "default": 0.0,
                "min": -1.0,
                "max": 1.0,
                "description": "Brightness adjustment (-1.0 to 1.0, 0 = no change)",
                "ffmpeg_param": "brightness",
            },
        },
    },
    "contrast": {
        "category": "color",
        "description": "Adjust image contrast",
        "ffmpeg_filter": "eq",
        "params": {
            "level": {
                "type": "float",
                "default": 1.0,
                "min": -1000.0,
                "max": 1000.0,
                "description": "Contrast multiplier (1.0 = no change)",
                "ffmpeg_param": "contrast",
            },
        },
    },
    "saturation": {
        "category": "color",
        "description": "Adjust color saturation",
        "ffmpeg_filter": "eq",
        "params": {
            "level": {
                "type": "float",
                "default": 1.0,
                "min": 0.0,
                "max": 3.0,
                "description": "Saturation multiplier (0=grayscale, 1=normal, 3=vivid)",
                "ffmpeg_param": "saturation",
            },
        },
    },
    "blur": {
        "category": "video",
        "description": "Apply Gaussian blur",
        "ffmpeg_filter": "boxblur",
        "params": {
            "radius": {
                "type": "int",
                "default": 5,
                "min": 1,
                "max": 50,
                "description": "Blur radius in pixels",
                "ffmpeg_param": "luma_radius",
            },
        },
    },
    "fade_in": {
        "category": "transition",
        "description": "Fade in from black at the start of the clip",
        "ffmpeg_filter": "fade",
        "params": {
            "duration": {
                "type": "float",
                "default": 1.0,
                "min": 0.1,
                "max": 10.0,
                "description": "Fade duration in seconds",
            },
        },
    },
    "fade_out": {
        "category": "transition",
        "description": "Fade out to black at the end of the clip",
        "ffmpeg_filter": "fade",
        "params": {
            "duration": {
                "type": "float",
                "default": 1.0,
                "min": 0.1,
                "max": 10.0,
                "description": "Fade duration in seconds",
            },
        },
    },
    "crop": {
        "category": "geometry",
        "description": "Crop the video frame",
        "ffmpeg_filter": "crop",
        "params": {
            "x": {
                "type": "int",
                "default": 0,
                "min": 0,
                "max": 9999,
                "description": "Left crop offset in pixels",
                "ffmpeg_param": "x",
            },
            "y": {
                "type": "int",
                "default": 0,
                "min": 0,
                "max": 9999,
                "description": "Top crop offset in pixels",
                "ffmpeg_param": "y",
            },
            "width": {
                "type": "int",
                "default": 1920,
                "min": 1,
                "max": 9999,
                "description": "Output width in pixels",
                "ffmpeg_param": "w",
            },
            "height": {
                "type": "int",
                "default": 1080,
                "min": 1,
                "max": 9999,
                "description": "Output height in pixels",
                "ffmpeg_param": "h",
            },
        },
    },
    "speed": {
        "category": "time",
        "description": "Adjust playback speed",
        "ffmpeg_filter": "setpts",
        "params": {
            "factor": {
                "type": "float",
                "default": 1.0,
                "min": 0.1,
                "max": 10.0,
                "description": "Speed multiplier (0.5=half speed, 2.0=double speed)",
            },
        },
    },
    "scale": {
        "category": "geometry",
        "description": "Scale/resize the video",
        "ffmpeg_filter": "scale",
        "params": {
            "width": {
                "type": "int",
                "default": 1920,
                "min": 1,
                "max": 9999,
                "description": "Output width in pixels (-1 to maintain aspect ratio)",
                "ffmpeg_param": "w",
            },
            "height": {
                "type": "int",
                "default": 1080,
                "min": 1,
                "max": 9999,
                "description": "Output height in pixels (-1 to maintain aspect ratio)",
                "ffmpeg_param": "h",
            },
        },
    },
    "volume": {
        "category": "audio",
        "description": "Adjust audio volume",
        "ffmpeg_filter": "volume",
        "params": {
            "level": {
                "type": "float",
                "default": 1.0,
                "min": 0.0,
                "max": 10.0,
                "description": "Volume multiplier (0=mute, 1=normal, 2=double)",
                "ffmpeg_param": "volume",
            },
        },
    },
    "mute": {
        "category": "audio",
        "description": "Mute the audio track",
        "ffmpeg_filter": "volume",
        "params": {},
    },
}


def available_filters(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List available filters, optionally filtered by category."""
    result = []
    for name, f in FILTER_REGISTRY.items():
        if category and f["category"] != category:
            continue
        result.append({
            "name": name,
            "category": f["category"],
            "description": f["description"],
            "param_count": len(f["params"]),
        })
    return result


def filter_info(filter_name: str) -> Dict[str, Any]:
    """Return detailed info about a filter including all parameters."""
    if filter_name not in FILTER_REGISTRY:
        available = list(FILTER_REGISTRY.keys())
        raise ValueError(f"Unknown filter '{filter_name}'. Available: {available}")

    f = FILTER_REGISTRY[filter_name]
    return {
        "name": filter_name,
        "category": f["category"],
        "description": f["description"],
        "ffmpeg_filter": f["ffmpeg_filter"],
        "params": f["params"],
    }


def add_filter(
    session: Session,
    clip_id: str,
    filter_name: str,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Add a filter to a clip."""
    project = session.get_project()

    if filter_name not in FILTER_REGISTRY:
        available = list(FILTER_REGISTRY.keys())
        raise ValueError(f"Unknown filter '{filter_name}'. Available: {available}")

    clip = _find_clip(project, clip_id)
    spec = FILTER_REGISTRY[filter_name]

    # Build filter params with defaults
    filter_params: Dict[str, Any] = {}
    for pname, pspec in spec["params"].items():
        filter_params[pname] = pspec["default"]

    # Apply user-provided params
    if params:
        for k, v in params.items():
            if k not in spec["params"]:
                raise ValueError(
                    f"Unknown param '{k}' for filter '{filter_name}'. "
                    f"Valid params: {list(spec['params'].keys())}"
                )
            _validate_param(filter_name, k, v, spec["params"][k])
            filter_params[k] = v

    filter_entry = {
        "name": filter_name,
        "params": filter_params,
    }

    session.snapshot(f"Add filter {filter_name} to {clip_id}")
    clip.setdefault("filters", []).append(filter_entry)

    return {
        "success": True,
        "clip_id": clip_id,
        "filter_index": len(clip["filters"]) - 1,
        "filter_name": filter_name,
        "params": filter_params,
    }


def remove_filter(session: Session, clip_id: str, filter_index: int) -> Dict[str, Any]:
    """Remove a filter from a clip by index."""
    project = session.get_project()
    clip = _find_clip(project, clip_id)
    filters = clip.get("filters", [])

    if filter_index < 0 or filter_index >= len(filters):
        raise IndexError(
            f"Filter index {filter_index} out of range (0-{len(filters) - 1})"
        )

    removed = filters[filter_index]
    session.snapshot(f"Remove filter {removed['name']} from {clip_id}")
    clip["filters"].pop(filter_index)

    return {
        "success": True,
        "clip_id": clip_id,
        "removed_filter": removed["name"],
        "filter_index": filter_index,
    }


def set_filter_param(
    session: Session,
    clip_id: str,
    filter_index: int,
    param_name: str,
    value: Any,
) -> Dict[str, Any]:
    """Update a single parameter on an existing clip filter."""
    project = session.get_project()
    clip = _find_clip(project, clip_id)
    filters = clip.get("filters", [])

    if filter_index < 0 or filter_index >= len(filters):
        raise IndexError(
            f"Filter index {filter_index} out of range (0-{len(filters) - 1})"
        )

    f_entry = filters[filter_index]
    filter_name = f_entry["name"]
    spec = FILTER_REGISTRY[filter_name]

    if param_name not in spec["params"]:
        raise ValueError(
            f"Unknown param '{param_name}' for filter '{filter_name}'. "
            f"Valid params: {list(spec['params'].keys())}"
        )

    _validate_param(filter_name, param_name, value, spec["params"][param_name])

    session.snapshot(f"Set {filter_name}.{param_name} = {value} on {clip_id}")
    f_entry["params"][param_name] = value

    return {
        "success": True,
        "clip_id": clip_id,
        "filter_index": filter_index,
        "filter_name": filter_name,
        "param": param_name,
        "value": value,
    }


def list_clip_filters(session: Session, clip_id: str) -> List[Dict[str, Any]]:
    """List all filters applied to a clip."""
    project = session.get_project()
    clip = _find_clip(project, clip_id)

    result = []
    for i, f_entry in enumerate(clip.get("filters", [])):
        result.append({
            "index": i,
            "name": f_entry["name"],
            "params": f_entry["params"],
            "description": FILTER_REGISTRY.get(f_entry["name"], {}).get("description", ""),
        })
    return result


def _find_clip(project: Dict[str, Any], clip_id: str) -> Dict[str, Any]:
    for clip in project["clips"]:
        if clip["id"] == clip_id:
            return clip
    available = [c["id"] for c in project["clips"]]
    raise ValueError(f"Clip not found: '{clip_id}'. Available: {available}")


def _validate_param(
    filter_name: str, param_name: str, value: Any, spec: Dict[str, Any]
) -> None:
    """Validate a filter parameter value against its spec."""
    ptype = spec.get("type")

    if ptype == "float":
        try:
            v = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"Filter '{filter_name}' param '{param_name}' must be a float, got: {value!r}"
            )
        mn = spec.get("min")
        mx = spec.get("max")
        if mn is not None and v < mn:
            raise ValueError(
                f"Filter '{filter_name}' param '{param_name}' minimum is {mn}, got {v}"
            )
        if mx is not None and v > mx:
            raise ValueError(
                f"Filter '{filter_name}' param '{param_name}' maximum is {mx}, got {v}"
            )

    elif ptype == "int":
        try:
            v = int(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"Filter '{filter_name}' param '{param_name}' must be an int, got: {value!r}"
            )
        mn = spec.get("min")
        mx = spec.get("max")
        if mn is not None and v < mn:
            raise ValueError(
                f"Filter '{filter_name}' param '{param_name}' minimum is {mn}, got {v}"
            )
        if mx is not None and v > mx:
            raise ValueError(
                f"Filter '{filter_name}' param '{param_name}' maximum is {mx}, got {v}"
            )
