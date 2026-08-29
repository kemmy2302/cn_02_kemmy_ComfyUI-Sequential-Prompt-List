# cn_02_kemmy_ComfyUI-Sequential-Prompt-List

A dependency-free ComfyUI custom node that processes an ordered list of multiline prompts from top to bottom.

## Features

- One vertically stacked multiline editor per list item.
- Add, delete, duplicate, enable/disable, and reorder list items.
- Normal line breaks stay inside one item and do not create extra records.
- Load and save prompt-list JSON files from the node UI.
- Optional `STRING` inputs for fixed prefix and suffix prompts.
- Accepts `CLIP`, performs text encoding internally, and outputs ordered `CONDITIONING`.
- Queue once to process every enabled, non-empty list item in order.

## Installation

Clone into `ComfyUI/custom_nodes`, then restart ComfyUI.

```bash
git clone https://github.com/kemmy2302/cn_02_kemmy_ComfyUI-Sequential-Prompt-List.git
```

The node appears as `cn_02_kemmy_Sequential Prompt List` under `Ordered Prompt Tools`.

For quick prefix or suffix testing, connect ComfyUI's standard `Text (Multiline)` node.

## Storage

Saved lists are stored in:

```text
ComfyUI/user/ordered_prompt_tools/lists/
```

Existing data created by the combined Ordered Prompt Tools package remains compatible.

## License

MIT
