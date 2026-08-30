# cn_02_kemmy_ComfyUI-Sequential-Prompt-List

A dependency-free ComfyUI custom node that processes an ordered list of multiline prompts from top to bottom.

## Features

- One vertically stacked multiline editor per list item.
- Add, delete, duplicate, enable/disable, and reorder list items.
- Normal line breaks stay inside one item and do not create extra records.
- Load and save prompt-list JSON files from the node UI.
- Optional `STRING` inputs for fixed prefix and suffix prompts.
- Includes a `CONDITIONING` node that accepts `CLIP` and performs text encoding internally.
- Includes a separate `STRING` node for Ollama, other text-processing nodes, or standard CLIP Text Encode nodes.
- Queue once to process every enabled, non-empty list item in order.

## Installation

Clone into `ComfyUI/custom_nodes`, then restart ComfyUI.

```bash
git clone https://github.com/kemmy2302/cn_02_kemmy_ComfyUI-Sequential-Prompt-List.git
```

The nodes appear under `Ordered Prompt Tools`:

- `cn_02_kemmy_Sequential Prompt List`: outputs ordered `CONDITIONING`.
- `cn_02_kemmy_Sequential Prompt List (String)`: outputs ordered completed prompt strings.

Both nodes use the same editor and JSON file format. Existing workflows using the
`CONDITIONING` node remain compatible.

For quick prefix or suffix testing, connect ComfyUI's standard `Text (Multiline)` node.

## Storage

Saved lists are stored in:

```text
ComfyUI/user/ordered_prompt_tools/lists/
```

Existing data created by the combined Ordered Prompt Tools package remains compatible.

## License

MIT
