from pathlib import Path

from aiohttp import web
from server import PromptServer

from .storage import atomic_write_json, read_json, safe_name


_REGISTERED = False


def _data_root():
    try:
        import folder_paths

        root = Path(folder_paths.get_user_directory())
    except (ImportError, AttributeError):
        root = Path(__file__).resolve().parent / "_data"
    result = root / "ordered_prompt_tools"
    (result / "lists").mkdir(parents=True, exist_ok=True)
    return result


def register_routes():
    global _REGISTERED
    if _REGISTERED:
        return
    _REGISTERED = True
    routes = PromptServer.instance.routes

    @routes.get("/kemmy-sequential-prompt-list/lists/{name}")
    async def get_list(request):
        try:
            name = safe_name(request.match_info["name"])
        except ValueError as error:
            raise web.HTTPBadRequest(text=str(error)) from error
        path = _data_root() / "lists" / name
        if not path.is_file():
            raise web.HTTPNotFound(text="list file not found")
        return web.json_response(read_json(path, {"version": 1, "records": []}))

    @routes.post("/kemmy-sequential-prompt-list/lists/{name}")
    async def save_list(request):
        try:
            name = safe_name(request.match_info["name"])
        except ValueError as error:
            raise web.HTTPBadRequest(text=str(error)) from error
        data = await request.json()
        records = data.get("records", []) if isinstance(data, dict) else []
        if not isinstance(records, list):
            raise web.HTTPBadRequest(text="records must be an array")
        payload = {"version": 1, "records": records}
        atomic_write_json(_data_root() / "lists" / name, payload)
        return web.json_response(payload)
