# cn_02_kemmy_ComfyUI-Sequential-Prompt-List

Create an ordered list of prompts and process every enabled item from top to bottom with a single ComfyUI queue action.

This is useful for story sequences, scenario lists, expression variations, pose collections, camera-angle tests, or any job where each list item should produce a separate result while sharing the same character and quality prompts.

The package includes two nodes: one outputs ready-to-use `CONDITIONING`, and the other outputs ordered `STRING` values for LLMs or other text-processing workflows. Both nodes share the same editor and saved-list format.

The nodes have no Python package dependencies.

> Screenshot placeholder: both Sequential Prompt List node variants side by side.

## What it does

- Displays one title and multiline prompt editor per list item.
- Adds, deletes, duplicates, enables, disables, and reorders list items.
- Enables or disables every list item at once.
- Keeps normal line breaks inside one item; a line break does not create a new record.
- Combines an optional fixed prefix, the current list item, and an optional fixed suffix.
- Processes enabled, non-empty items from top to bottom.
- Loads and saves named prompt-list JSON files from the node UI.
- Provides separate `CONDITIONING` and `STRING` output variants.

## Installation

### Git

Open a terminal in `ComfyUI/custom_nodes` and run:

```bash
git clone https://github.com/kemmy2302/cn_02_kemmy_ComfyUI-Sequential-Prompt-List.git
```

Restart ComfyUI after cloning.

### ZIP

1. Download this repository with **Code > Download ZIP**.
2. Extract it into `ComfyUI/custom_nodes`.
3. Make sure the final path is similar to:

   ```text
   ComfyUI/custom_nodes/cn_02_kemmy_ComfyUI-Sequential-Prompt-List/__init__.py
   ```

4. Restart ComfyUI.

## Finding the nodes

In ComfyUI, open the `Ordered Prompt Tools` category.

| Node | Output | Choose this when... |
|---|---|---|
| `cn_02_kemmy_Sequential Prompt List` | ordered `CONDITIONING` | you want to connect directly to KSampler or another conditioning input |
| `cn_02_kemmy_Sequential Prompt List (String)` | ordered `STRING` | you want each completed prompt to pass through Ollama, another LLM, a text node, or standard CLIP Text Encode |

Existing workflows created with the original `CONDITIONING` node remain compatible.

If the nodes do not appear, restart the ComfyUI backend, not only the browser page. After restarting, refresh the browser with `Ctrl+F5`.

## Core concept

For each enabled list item, the node builds:

```text
prefix_prompt
current list item's prompt
suffix_prompt
```

Given this setup:

```text
prefix_prompt: 1girl, Alice, long blonde hair

List Item 001: walking to school, morning
List Item 002: sitting in a classroom, studying
List Item 003: sleeping with her head on a desk

suffix_prompt: anime illustration, soft daylight, high quality
```

one queue action processes these completed prompts in order:

```text
1girl, Alice, long blonde hair
walking to school, morning
anime illustration, soft daylight, high quality

1girl, Alice, long blonde hair
sitting in a classroom, studying
anime illustration, soft daylight, high quality

1girl, Alice, long blonde hair
sleeping with her head on a desk
anime illustration, soft daylight, high quality
```

Each block above is one output item, not one combined prompt.

## Quick start: CONDITIONING version

Use `cn_02_kemmy_Sequential Prompt List` when you do not need an LLM or another text processor between the list and image generation.

1. Add the node to the workflow.
2. Connect your model's final `CLIP` output to `clip`.
3. Click **+ Add List Item** to create records.
4. Enter one image's variable prompt in each record.
5. Optionally connect fixed `STRING` nodes to `prefix_prompt` and `suffix_prompt`.
6. Connect `conditioning` to KSampler's positive input.
7. Queue the workflow once.

```text
CLIP ---------------------------> Sequential Prompt List (clip)
Character STRING --------------> Sequential Prompt List (prefix_prompt)
Style / quality STRING --------> Sequential Prompt List (suffix_prompt)
Sequential Prompt List --------> KSampler (positive)
```

The node performs CLIP text encoding internally for every enabled list item.

> Screenshot placeholder: basic CONDITIONING workflow connection.

## Quick start: STRING version

Use `cn_02_kemmy_Sequential Prompt List (String)` when the complete prompt must be processed before CLIP encoding.

1. Add the String node.
2. Connect fixed character or reusable prompts to `prefix_prompt`.
3. Connect fixed style or quality prompts to `suffix_prompt`.
4. Enter the changing scene or instruction in each list item.
5. Connect `prompt` to an Ollama/LLM node or directly to `CLIP Text Encode.text`.
6. Connect the resulting conditioning to the image-generation workflow.
7. Queue once.

Direct CLIP example:

```text
Character STRING -----> Sequential Prompt List (String) <----- Style STRING
                               |
                               v
                        CLIP Text Encode
                               |
                               v
                            KSampler
```

Ollama/LLM example:

```text
Prompt Library (character/items) ---> prefix_prompt
Prompt Library (style/quality) -----> suffix_prompt
                                      |
                                      v
                         Sequential Prompt List (String)
                                      |
                                      v
                              Ollama / other LLM
                                      |
                                      v
                               CLIP Text Encode
                                      |
                                      v
                                   KSampler
```

Because the String node emits a ComfyUI list, compatible downstream nodes are mapped over the values in order. In the Ollama example, the LLM receives the character, current scene, and style together for every item, so it can produce a coherent final prompt before CLIP encoding.

> Screenshot placeholder: STRING version connected between two Prompt Library nodes and Ollama.

## Editing list items

Each record contains:

- an enable checkbox;
- an automatically displayed list number such as `#001`;
- an editable title;
- a multiline prompt field;
- up, down, duplicate, and delete buttons.

Use **Enable all** to check every record, or **Disable all** to clear every record's checkbox. These actions do not delete or change the prompt text.

The title is for your organization and is not included in the generated prompt. Only the multiline prompt field is sent downstream.

A multiline record remains one record. For example:

```text
walking through the school gate
carrying a shoulder bag
morning sunlight
```

produces one image prompt, not three prompts.

Disable a record when you want to keep it in the list but skip it temporarily. Empty records are also skipped. Queueing fails with a clear error if no enabled, non-empty records remain.

## Prefix and suffix inputs

Both inputs accept standard ComfyUI `STRING` connections.

Useful sources include:

- `cn_01_kemmy_Prompt Library Selector`;
- ComfyUI's standard multiline text node;
- another compatible custom text node.

Both inputs are optional. If an input is not connected, that part is omitted. There are no hidden fallback text fields inside the node.

Typical usage:

- `prefix_prompt`: characters, outfits, items, poses, fixed concepts;
- list records: scenes, actions, expressions, camera variations;
- `suffix_prompt`: style, lighting, quality, fixed finishing instructions.

## Saving and loading lists

The filename field at the top defaults to `prompt_list.json`.

- **Save** writes the current records to that filename.
- **Load** replaces the current records with the contents of that filename.
- If `.json` is omitted, it is added automatically.
- Directory components and unsupported filename characters are removed for safety.

Saved list files can be used by both node variants.

> Screenshot placeholder: filename field with Load and Save buttons.

## Data storage and backup

Saved lists are stored outside the plugin directory:

```text
ComfyUI/user/ordered_prompt_tools/lists/
```

This means updating or replacing the custom-node repository does not normally delete saved lists.

To back up all saved lists, copy the `lists` directory. The exact `ComfyUI/user` location can differ if ComfyUI was launched with a custom user directory.

Existing data created by the earlier combined Ordered Prompt Tools package remains compatible.

The current records are also stored in the ComfyUI workflow JSON, so a saved workflow retains the list that was visible when it was saved.

## Execution order and seeds

Enabled records are emitted from top to bottom. ComfyUI-compatible downstream nodes process the resulting list in that order.

Seed behavior is controlled by downstream sampling nodes, not by Sequential Prompt List. For repeatable comparisons, set KSampler's seed behavior to fixed. If a downstream custom node does not support ComfyUI list mapping, it may need a list-aware alternative.

## Updating

From the repository directory:

```bash
git pull
```

Restart ComfyUI and refresh the browser with `Ctrl+F5` after updating frontend files.

## Troubleshooting

### The nodes are missing

- Confirm the repository is directly inside `ComfyUI/custom_nodes`.
- Confirm `__init__.py` is not nested inside an extra ZIP folder.
- Restart the ComfyUI backend and check its startup log for import errors.

### The editor is blank or looks incorrect

- Refresh the browser with `Ctrl+F5` to clear cached JavaScript.
- Make sure only one copy of this custom node is installed.

### Queueing reports that no records are available

At least one record must be enabled and contain non-whitespace prompt text.

### Only one result is produced after the STRING node

The String node outputs a ComfyUI list. Confirm that the downstream custom node supports normal ComfyUI list mapping. Standard CLIP Text Encode and the tested Ollama Generate workflow process the values in order.

### Load reports that the file was not found

Only files previously saved in `ComfyUI/user/ordered_prompt_tools/lists/` can be loaded by filename. Confirm the spelling and `.json` extension.

## License

MIT