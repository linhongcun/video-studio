import {rehypeHeadingIds} from '@astrojs/markdown-remark';

const heading = (node) => node.type === 'element' && /^h[1-6]$/.test(node.tagName);
const tag = (node) => node.type === 'element' ? node.tagName : node.name;
const excluded = new Set(['figure', 'svg', 'pre', 'code', 'script', 'style', 'template', 'details', 'Figure', 'SourceQuote']);
const walk = (node, visit) => { visit(node); for (const child of node.children ?? []) walk(child, visit); };

function jsxValue(node, name) {
  const attribute = node.attributes?.find((item) => item.type === 'mdxJsxAttribute' && item.name === name);
  if (!attribute) return undefined;
  if (attribute.value === null) return true;
  if (typeof attribute.value === 'string') return attribute.value;
  const expression = attribute.value?.data?.estree?.body?.[0]?.expression;
  if (expression?.type === 'ObjectExpression') return Object.fromEntries(expression.properties
    .filter((item) => item.type === 'Property' && item.value.type === 'Literal')
    .map((item) => [item.key.name ?? item.key.value, item.value.value]));
  return expression?.type === 'Literal' ? expression.value : undefined;
}

function hidden(node) {
  const props = node.properties ?? {};
  const hiddenValue = props.hidden ?? jsxValue(node, 'hidden');
  const aria = props.ariaHidden ?? props['aria-hidden'] ?? jsxValue(node, 'aria-hidden');
  const style = props.style ?? jsxValue(node, 'style');
  return (hiddenValue !== undefined && hiddenValue !== false)
    || aria === true || aria === 'true'
    || (typeof style === 'string' && /(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)\s*(?:!important\s*)?(?:;|$)/i.test(style))
    || (style && typeof style === 'object' && (style.display === 'none' || style.visibility === 'hidden'))
    || Object.hasOwn(props, 'dataFootnotes') || Object.hasOwn(props, 'data-footnotes')
    || (node.attributes ?? []).some((item) => item.name === 'data-footnotes');
}

export function remarkHeadingId() {
  return (tree) => walk(tree, (node) => {
    if (node.type !== 'heading') return;
    const last = node.children.at(-1);
    const match = last?.type === 'text' && last.value.match(/\s*\{#([\w-]+)\}\s*$/);
    if (!match) return;
    last.value = last.value.slice(0, match.index);
    node.data = {...node.data, hProperties: {...node.data?.hProperties, id: match[1]}};
  });
}

const literal = (value) => {
  if (Array.isArray(value)) return {type: 'ArrayExpression', elements: value.map(literal)};
  if (value !== null && typeof value === 'object') return {type: 'ObjectExpression', properties: Object.entries(value).map(([name, item]) => ({
    type: 'Property', key: {type: 'Identifier', name}, value: literal(item), kind: 'init', method: false, shorthand: false, computed: false,
  }))};
  return {type: 'Literal', value};
};

/** Run after reader-facing heading transforms, before Astro exports getHeadings(). */
export function rehypeArticleHeadings() {
  return (tree, file) => {
    const nodes = [], reserved = new Set(), idCounts = new Map();
    walk(tree, (node) => {
      const id = node.properties?.id ?? jsxValue(node, 'id');
      if (typeof id === 'string') {
        reserved.add(id);
        idCounts.set(id, (idCounts.get(id) ?? 0) + 1);
      }
      if (!heading(node)) return;
      nodes.push(node);
    });
    const hadId = new Set(nodes.filter((node) => typeof node.properties?.id === 'string'));
    // Reuse Astro's text/slug semantics, including Chinese and inline code.
    // Its normal pass follows ours and will retain these final IDs.
    rehypeHeadingIds()(tree, file);
    const titles = new Map(nodes.map((node, index) => [node, file.data.astro.headings[index].text]));
    for (const node of nodes) {
      if (hadId.has(node)) continue;
      const base = node.properties.id;
      let id = base, suffix = 0;
      while (reserved.has(id)) id = `${base}-${++suffix}`;
      node.properties.id = id;
      reserved.add(id);
    }
    const headings = [];
    const visit = (node, blocked = false) => {
      blocked ||= excluded.has(tag(node)) || hidden(node);
      if (blocked) return;
      if (heading(node) && ['h2', 'h3'].includes(node.tagName)) {
        const title = titles.get(node)?.trim();
        if (title) {
          if (hadId.has(node) && idCounts.get(node.properties.id) > 1)
            throw new Error(`Duplicate article heading id: ${node.properties.id}`);
          headings.push({id: node.properties.id, title, depth: Number(node.tagName[1])});
        }
      }
      for (const child of node.children ?? []) visit(child, blocked);
    };
    visit(tree);
    tree.children.unshift({
      type: 'mdxjsEsm', value: `export function getArticleHeadings() { return ${JSON.stringify(headings)}; }`,
      data: {estree: {type: 'Program', sourceType: 'module', body: [{
        type: 'ExportNamedDeclaration', specifiers: [], source: null,
        declaration: {type: 'FunctionDeclaration', id: {type: 'Identifier', name: 'getArticleHeadings'}, params: [], generator: false, async: false,
          body: {type: 'BlockStatement', body: [{type: 'ReturnStatement', argument: literal(headings)}]}},
      }]}},
    });
  };
}
