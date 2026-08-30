import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

const API_ROOT = "/kemmy-sequential-prompt-list";

const css = `
.dom-widget:has(> .opt-panel){background:transparent!important;border:0!important;box-shadow:none!important;outline:0!important}
.opt-panel{font:12px sans-serif;color:var(--input-text,#ddd);background:var(--comfy-input-bg,#222);padding:8px;border-radius:6px;box-sizing:border-box;width:100%;max-width:100%;overflow-x:hidden;overflow-y:auto;max-height:620px}
.opt-library-panel{height:620px;max-height:620px;overflow:hidden;display:flex;flex-direction:column}
.opt-toolbar,.opt-row-actions{display:flex;gap:5px;align-items:center;margin-bottom:6px;flex-wrap:wrap;min-width:0;max-width:100%}.opt-toolbar>*,.opt-row-actions>*{min-width:0;max-width:100%}
.opt-top-spacer{height:16px;min-height:16px;flex:none}
.opt-filter-bar{position:sticky;top:0;z-index:2;background:var(--comfy-input-bg,#222);padding:4px 0 6px}
.opt-filter-grid{display:grid;grid-template-columns:minmax(120px,1fr) minmax(90px,.6fr);gap:5px}
.opt-tabs{display:flex;gap:4px;overflow-x:auto;white-space:nowrap;padding:4px 0;scrollbar-width:thin}.opt-tab{flex:0 0 auto}.opt-tab-active{border-color:#6aa9ff!important;background:#17395d!important}
.opt-category-editor{border:1px solid #555;border-radius:6px;padding:7px;margin:6px 0}.opt-category-row{display:grid;grid-template-columns:minmax(100px,1fr) auto auto;gap:5px;align-items:center;margin:5px 0}
.opt-selection-summary{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin:6px 0}.opt-selection-summary .opt-count{font-weight:700;flex:1}
.opt-selected-pane{flex:0 1 auto;max-height:190px;min-height:0;overflow:auto;border-bottom:1px solid #555;padding-bottom:6px}
.opt-library-pane{flex:1 1 auto;min-height:160px;overflow-x:hidden;overflow-y:auto;padding-top:4px}
.opt-panel button,.opt-panel input,.opt-panel select,.opt-panel textarea{font:inherit;color:inherit;background:#292929;border:1px solid #555;border-radius:4px;padding:4px;box-sizing:border-box}
.opt-panel button{cursor:pointer}.opt-panel button:hover{background:#3a3a3a}.opt-panel input[type=text],.opt-panel textarea,.opt-panel select{width:100%}
.opt-card{border:1px solid #555;border-radius:6px;padding:6px;margin:6px 0;background:#202020;max-width:100%;box-sizing:border-box}.opt-card-head{display:flex;gap:6px;align-items:center;min-width:0;max-width:100%;flex-wrap:wrap}.opt-card img,.opt-card-head>img{width:58px;height:58px;min-width:58px;object-fit:cover;border-radius:5px;background:#111}.opt-card textarea{min-height:58px;resize:vertical;margin-top:5px}.opt-muted{opacity:.7}.opt-selected{border-color:#6aa9ff;background:#17283c;box-shadow:inset 3px 0 #6aa9ff}.opt-title{font-weight:700;margin:5px 0}.opt-hidden{display:none!important}.opt-status{min-height:16px;color:#9dccff}
`;

function ensureStyles() {
  if (document.getElementById("ordered-prompt-tools-style")) return;
  const style = document.createElement("style");
  style.id = "ordered-prompt-tools-style";
  style.textContent = css;
  document.head.appendChild(style);
}

function parseJSON(value, fallback) {
  try { return typeof value === "string" ? JSON.parse(value) : (value ?? fallback); }
  catch { return fallback; }
}

function uuid() {
  return globalThis.crypto?.randomUUID?.() || `opt-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function findWidget(node, name) {
  return node.widgets?.find((widget) => widget.name === name);
}

function hideWidget(widget) {
  if (!widget) return;
  widget.hidden = true;
  widget.type = "hidden";
  widget.draw = () => {};
  widget.computeSize = () => [0, 0];
  widget.computeLayoutSize = () => ({ minHeight: 0, maxHeight: 0, minWidth: 0, maxWidth: 0 });
  widget.serializeValue = async () => widget.value;
}

function element(tag, properties = {}, children = []) {
  const item = document.createElement(tag);
  Object.assign(item, properties);
  for (const child of children) item.append(child);
  return item;
}

async function jsonRequest(url, options = {}) {
  const response = await api.fetchApi(url, options);
  if (!response.ok) throw new Error((await response.text()) || `${response.status}`);
  return response.json();
}

function addDomEditor(node, name, container, minHeight = 520) {
  const widgetMargin = 0;
  const syncWidth = () => {
    const width = Math.max(100, Number(node.size?.[0] || 0) - widgetMargin * 2);
    container.style.width = `${width}px`;
    container.style.maxWidth = `${width}px`;
    container.style.minWidth = "0";
  };
  const widget = node.addDOMWidget(name, "custom", container, {
    serialize: false,
    hideOnZoom: false,
    getValue: () => null,
    setValue: () => {},
    margin: widgetMargin,
    onDraw: syncWidth,
    afterResize: syncWidth,
  });
  syncWidth();
  container.style.setProperty("--comfy-widget-min-height", `${minHeight}px`);
  container.style.setProperty("--comfy-widget-height", `${minHeight}px`);
  widget.computeSize = () => [0, minHeight];
  node.setSize([node.size[0], Math.max(node.size[1], minHeight + 150)]);
  return widget;
}
function setupListNode(node) {
  ensureStyles();
  const stateWidget = findWidget(node, "records_json");
  hideWidget(stateWidget);
  let state = parseJSON(stateWidget?.value, { version: 1, records: [] });
  state.records ||= [];
  const container = element("div", { className: "opt-panel" });
  const topSpacer = element("div", { className: "opt-top-spacer" });
  const status = element("div", { className: "opt-status" });
  const listArea = element("div");
  const fileName = element("input", { type: "text", value: "prompt_list.json", placeholder: "prompt_list.json", style: "flex:1" });

  function sync() {
    if (stateWidget) { stateWidget.value = JSON.stringify(state); stateWidget.callback?.(stateWidget.value); }
    node.graph?.setDirtyCanvas(true, true);
  }

  function move(index, delta) {
    const next = index + delta;
    if (next < 0 || next >= state.records.length) return;
    [state.records[index], state.records[next]] = [state.records[next], state.records[index]];
    sync(); render();
  }

  function addRecord(record = {}) {
    state.records.push({ id: uuid(), enabled: true, title: `List Item ${String(state.records.length + 1).padStart(3, "0")}`, prompt: "", ...record });
    sync(); render();
  }

  function render() {
    listArea.replaceChildren();
    state.records.forEach((record, index) => {
      const card = element("div", { className: "opt-card" });
      const enabled = element("input", { type: "checkbox", checked: record.enabled !== false, onchange: () => { record.enabled = enabled.checked; sync(); } });
      const title = element("input", { type: "text", value: record.title || `List Item ${String(index + 1).padStart(3, "0")}`, style: "flex:1", oninput: () => { record.title = title.value; sync(); } });
      const head = element("div", { className: "opt-card-head" }, [enabled, element("span", { textContent: `#${String(index + 1).padStart(3, "0")}` }), title]);
      const prompt = element("textarea", { value: record.prompt || "", placeholder: "One list item's prompt. Line breaks remain inside this item.", oninput: () => { record.prompt = prompt.value; sync(); } });
      const actions = element("div", { className: "opt-row-actions" }, [
        element("button", { textContent: "↑", onclick: () => move(index, -1) }),
        element("button", { textContent: "↓", onclick: () => move(index, 1) }),
        element("button", { textContent: "Duplicate", onclick: () => addRecord({ ...record, id: uuid(), title: `${record.title || "List Item"} copy` }) }),
        element("button", { textContent: "Delete", onclick: () => { state.records.splice(index, 1); sync(); render(); } }),
      ]);
      card.append(head, prompt, actions); listArea.append(card);
    });
    if (!state.records.length) listArea.append(element("div", { className: "opt-muted", textContent: "No list items. Add one below." }));
  }

  const fileBar = element("div", { className: "opt-toolbar" }, [
    fileName,
    element("button", { textContent: "Load", onclick: async () => { try { state = await jsonRequest(`${API_ROOT}/lists/${encodeURIComponent(fileName.value)}`); state.records ||= []; sync(); render(); status.textContent = `Loaded ${fileName.value}`; } catch (error) { status.textContent = error.message; } } }),
    element("button", { textContent: "Save", onclick: async () => { try { state = await jsonRequest(`${API_ROOT}/lists/${encodeURIComponent(fileName.value)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(state) }); sync(); render(); status.textContent = `Saved ${fileName.value}`; } catch (error) { status.textContent = error.message; } } }),
  ]);
  const enableBar = element("div", { className: "opt-toolbar" }, [
    element("button", { textContent: "Enable all", onclick: () => {
      state.records.forEach((record) => { record.enabled = true; });
      sync(); render();
    } }),
    element("button", { textContent: "Disable all", onclick: () => {
      state.records.forEach((record) => { record.enabled = false; });
      sync(); render();
    } }),
  ]);
  const addButton = element("button", { textContent: "+ Add List Item", onclick: () => addRecord() });
  container.append(topSpacer, fileBar, enableBar, status, listArea, addButton);
  addDomEditor(node, "sequential_prompt_list_editor", container, 600);
  render();
  setTimeout(() => {
    state = parseJSON(stateWidget?.value, state);
    state.records ||= [];
    render();
  }, 0);
}


app.registerExtension({
  name: "KemmySequentialPromptList.Editor",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (["OPTSequentialPromptList", "OPTSequentialPromptListString"].includes(nodeData.name)) {
      const original = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = function () { original?.apply(this, arguments); setupListNode(this); };
    }
  },
});
